import os
from fastmcp import FastMCP
from sqlalchemy import create_engine, inspect, text

from uvicorn import logging
from datetime import datetime

import json

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from llama_index.core import SQLDatabase
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from dotenv import load_dotenv,find_dotenv


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

mcp = FastMCP("Postgres MCP")

app_state = {}
MD_DIR   = os.getenv("MD_DIR")


DB_FILE=os.getenv("DB_FILE")
ENGINE_CACHE={}

@mcp.tool
def guardar_resultado(alias_bd: str, solicitud_usuario: str, query_sql: str, datos_obtenidos: str, notas: str = "") -> str:
    """
    Guarda el resultado final de una consulta SQL en un archivo Markdown.
    """
    alias = alias_bd.strip().lower()
    nombre_archivo = f"resultado_{alias}.md"
    ruta = os.path.join(MD_DIR, nombre_archivo)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    contenido_md = (
        f"# Resultado de consulta — {alias_bd}\n"
        f"> Generado: {fecha}\n\n"
        f"## Solicitud\n{solicitud_usuario.strip()}\n\n"
        f"## Query SQL ejecutada\n```sql\n{query_sql.strip()}\n```\n\n"
        f"## Datos obtenidos\n{datos_obtenidos.strip()}\n"
    )

    if notas.strip():
        contenido_md += f"\n## Notas y observaciones\n{notas.strip()}\n"

    try:
        os.makedirs(MD_DIR, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido_md)
        return f"Resultado guardado correctamente en '{ruta}'"
    except Exception as e:
        return f"Error al guardar el resultado: {e}"
    
def _get_engine(alias_bd: str):
    if not alias_bd:
        return None
    
    alias_limpio = alias_bd.strip().lower()
    
    
    if alias_limpio in ENGINE_CACHE:
        return ENGINE_CACHE[alias_limpio]
    
  
    if not os.path.exists(DB_FILE):
        print(f"Error: No se encuentra el archivo de configuración {DB_FILE}")
        return None
        
    try:
        with open(DB_FILE, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
            
        
        databases = data if isinstance(data, list) else data.get("databases", [])
        
        
        conf = next((db for db in databases if db["alias"].strip().lower() == alias_limpio), None)
        
        if conf:
            
            url = f"postgresql://{conf['user']}:{conf['password']}@{conf['host']}:{conf['port']}/{conf['dbname']}"
            engine = create_engine(url,
                                   connect_args={
                                       "client_encoding": "utf8", "options": "-c lc_messages=C"}
            )
            
            # Guardado en motor de caché para futuras llamadas
            ENGINE_CACHE[alias_limpio] = engine
            return engine
        else:
            print(f"No se encontró ninguna base de datos configurada con el alias: '{alias_bd}'")
            
    except Exception as e:
        print(f"Error al cargar credenciales dinámicas desde JSON: {e}")
        
    return None



@mcp.tool
def listar_bases_datos():
    """Lista todas las bases de datos disponibles en el archivo de configuración.
    Llama a esta herramienta antes de explorar datos para saber qué bases de datos existen."""
    if not os.path.exists(DB_FILE):
        return {"bases_datos": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        databases = data if isinstance(data, list) else data.get("databases", [])
        return {"bases_datos": [db["alias"] for db in databases]}
    except Exception as e:
        return {"error": f"No se pudo leer el archivo de configuración: {e}"}
    


@mcp.tool

def Info_version(alias_bd: str) -> str:
    """Obtiene la versión de PostgreSQL."""

    try:
        engine = _get_engine(alias_bd)
        if not engine:
            return "No se pudo establecer conexión con la base de datos."

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version_info = result.fetchone()
            return json.dumps(version_info[0] if version_info else "Versión desconocida")
    
        
        
        
    except Exception as e:
        print(f"Error al obtener versión de PostgreSQL: {e}")
        return f"Error: {e}"
    
@mcp.tool
def generar_markdown_esquema(alias_bd: str, schema: str = "public") -> str:
    """
    Con esta herramienta se genera el archivo Markdown con el esquema completo de la base de datos.
    input: alias_bd (ej. 'escuela') y schema (por defecto 'public').
    """
    if not alias_bd:
        return "Error: Debes especificar el alias de la base de datos."
    
    
    engine = _get_engine(alias_bd)
    if not engine:
        return f"Error: La base de datos '{alias_bd}' no está configurada o no se pudo conectar."

    alias = alias_bd.strip().lower()
    nombre_archivo = f"esquema_{alias}.md"
    ruta_completa = os.path.join(MD_DIR, nombre_archivo)

    try:
        inspector = inspect(engine)
        tablas = inspector.get_table_names(schema=schema)
    except Exception as e:
        return f"Error al conectar con la base de datos: {e}"

    if not tablas:
        return f"No se encontraron tablas en el schema '{schema}'."

   
    md = (
        f"# Esquema: {alias}\n"
        f"> Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
        f"> Tablas: {len(tablas)}  \n\n---\n\n"
    )

    for tabla in tablas:
        try:
            columnas = inspector.get_columns(tabla, schema=schema)
            pk_info  = inspector.get_pk_constraint(tabla, schema=schema)
            fks      = inspector.get_foreign_keys(tabla, schema=schema)
            pks      = set(pk_info.get("constrained_columns", []))
            fk_map   = {
                col: f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                for fk in fks for col in fk["constrained_columns"]
            }

            md += f"## Tabla: `{tabla}`\n\n"
            md += "| Columna | Tipo | PK | FK | Nulo |\n"
            md += "|---------|------|----|----|------|\n"
            for col in columnas:
                n = col["name"]
                md += f"| `{n}` | {col['type']} | {'Si' if n in pks else ''} | {fk_map.get(n,'')} | {'Sí' if col.get('nullable') else 'No'} |\n"

            if fks:
                md += "\n**Relaciones FK:**\n"
                for fk in fks:
                    for col in fk["constrained_columns"]:
                        md += f"- `{tabla}.{col}` → `{fk['referred_table']}.{fk['referred_columns'][0]}`\n"
            md += "\n---\n\n"

        except Exception as e:
            md += f"## Tabla: `{tabla}`\n\n>  Error: {e}\n\n---\n\n"

    os.makedirs(MD_DIR, exist_ok=True)
    with open(ruta_completa, "w", encoding="utf-8") as f:
        f.write(md)

    return f"Éxito: Esquema guardado en '{ruta_completa}' ({len(tablas)} tablas)."

@mcp.tool()
def listar_markdowns_existentes() -> str:
    """
    Lista todos los archivos de esquema Markdown ya generados en el directorio
    de trabajo. Útil para saber qué bases de datos ya han sido extraídas y
    evitar sobreescribir información sin necesidad.

    Returns:
        Lista de ficheros encontrados o mensaje indicando que no hay ninguno.
    """
    try:
        if not os.path.exists(MD_DIR):
            return "No se encontró ningún archivo de esquema (el directorio no existe todavía)."

        # Solo buscamos archivos que sigan nuestro patrón estándar
        archivos = [f for f in os.listdir(MD_DIR) if f.startswith("esquema_") and f.endswith(".md")]

        if not archivos:
            return "No se encontró ningún archivo de esquema en el directorio."

        lineas = ["Archivos de esquema existentes:"]
        for fichero in sorted(archivos):
            alias = fichero.replace("esquema_", "").replace(".md", "")
            ruta = os.path.join(MD_DIR, fichero)
            lineas.append(f"- {alias}  →  {ruta}")
            
        return "\n".join(lineas)
        
    except Exception as e:
        return f"Error al listar los archivos: {e}"


@mcp.tool()
def leer_esquema_bd(nombre_base_datos: str) -> str:
    """
    Lee el archivo Markdown de esquema de una base de datos concreta, si existe.

    Args:
        nombre_base_datos: Nombre de la base de datos (ej. 'escuela').
    Returns:
        Contenido del fichero o mensaje de error si no existe.
    """
    alias = nombre_base_datos.strip().lower()
    nombre_archivo = f"esquema_{alias}.md"
    ruta_completa = os.path.join(MD_DIR, nombre_archivo)
    
    if not os.path.exists(ruta_completa):
        return f"No existe el archivo '{nombre_archivo}'. Procede a extraer el esquema desde cero."
        
    try:
        with open(ruta_completa, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        if not contenido.strip():
            return f"El archivo '{nombre_archivo}' está vacío. Procede a extraer el esquema de nuevo."
            
        return contenido
        
    except Exception as e:
        return f"Error al leer el archivo '{nombre_archivo}': {e}"

@mcp.tool()
def ejecutar_consulta(alias_bd: str, sql: str): #funcion general
    """Ejecuta una consulta SQL en la base de datos."""
    try:
        engine = _get_engine(alias_bd)
        if not engine:
            return "No se pudo establecer conexión con la base de datos."

        query = sql.strip().lower()
        if not query.startswith(("select")):
            return "Error: Solo se permiten consultas SELECT"

        with engine.connect() as conn:
            try:
                result = conn.execute(text(sql))
                if not result.returns_rows:
                    return "Error: La consulta no devolvio filas."

                filas = result.fetchall()
                
                return [dict(fila._mapping) for fila in filas]
            except Exception as e:
                return f"Error al ejecutar consulta: {e}"
            
    except Exception as e:
        print(f"Error al ejecutar consulta SQL: {e}")
        return f"Error: {e}"
    

@mcp.tool()
def leer_resultado(nombre_base_datos: str) -> str:
    """
    Lee el archivo Markdown de resultado de una base de datos concreta o resultados.

    Args:
        nombre_base_datos: Nombre de la BD (ej. 'Escuela', 'DVD').
    Returns:
        Contenido del Markdown o mensaje de error con instrucciones.
    """
    # Estandariza el nombre con la regla que se aplica en el main.py
    alias = nombre_base_datos.strip().lower()
    nombre_archivo = f"resultado_{alias}.md"
    ruta = os.path.join(MD_DIR, nombre_archivo)

    if not os.path.exists(ruta):
        return (
            f"RESULTADO_NO_ENCONTRADO: No existe el archivo '{nombre_archivo}'. "
            f"Solicita al Agente Extractor que analice la BD '{nombre_base_datos}'."
        )

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        if not contenido.strip():
            return (
                f"RESULTADO_VACIO: El archivo '{nombre_archivo}' está vacío. "
                f"El Agente Extractor debe volver a ejecutarse para '{nombre_base_datos}'."
            )
            
        return contenido
        
    except Exception as e:
        return f"Error al leer '{nombre_archivo}': {e}"
    


if __name__ == "__main__":
    mcp.run()


