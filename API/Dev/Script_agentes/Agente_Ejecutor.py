import os
from datetime import datetime
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import trim_messages
from dotenv import load_dotenv,find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
MD_DIR = os.getenv("MD_DIR")


EJECUTOR_PROMPT = """ name: Ejecutor

# Rol
Eres un experto Analista de Datos y especialista en Postgres SQL. Tu tarea es transformar solicitudes en lenguaje natural utilizando 
la información proporcionada en archivos markdown con la siguiente información
( esquemas de bases de datos, estructuras de tablas) para escribir consultas SQL precisas, eficientes y sintácticamente 
correctas que recuperen exactamente la información solicitada.

# Herramientas disponibles (úsalas en orden secuencial, una a la vez)
- **ejecutar_consulta_sql** para probar la consulta SQL contra la base de datos y obtener los resultados
- **guardar_resultado** para dar la respuesta final al usuario y guardar la consulta utilizada con los resultados obtenidos en un archivo Markdown


# pasos a seguir

1 **Construir la query**
Antes de ejecutar, razona internamente paso por paso
  ¿Qué tablas necesito unir? ¿Por qué columna?
  ¿Hay filtros (WHERE), agregaciones (GROUP BY), ordenación (ORDER BY) o límites (LIMIT)?
   ¿Puede haber NULLs que afecten al resultado? ¿Uso LEFT JOIN o INNER JOIN?


2. **Prueba y validación**
   - Ejecuta la consulta con ejecutar_consulta_sql.
   - Si devuelve error: lee el mensaje, identifica la causa (nombre incorrecto, tipo, sintaxis)
    y vuelve a intentarlo Máximo 2 veces 
     
3  **Guardar resultado** 
- Llama a `guardar_resultado` con:
    - alias_bd: el alias exacto de la BD
    - solicitud_usuario: la pregunta original sin modificar
    - query_sql: la query final que funcionó
    - datos_obtenidos: el resultado completo
    - notas: suposiciones aplicadas, advertencias sobre NULLs o sugerencias adicionales

Restricciones:

- Debes utilizar las herramientas proporcionadas en el archivo mcp principal para ejecutar y probar tus consultas contra la base de datos.

- Si necesitas más informacion solicitala al usuario

- Siempre debes mostrar la consulta SQL utilizada como output final

- Siempre debes guardar el resultado final con la herramienta **`guardar_resultado`** antes de responder al usuario
"""


    
async def run_ejecutor(llm, tools, user_query: str) -> str:
    
    herramientas = tools  
    agent = create_react_agent(llm, herramientas)
    modelo = getattr(llm, "model", None) or getattr(llm, "model_name", "desconocido")

    

    response = await agent.ainvoke(
        {
            "messages": [
                SystemMessage(content=EJECUTOR_PROMPT),
                {"role": "user", "content": f"{user_query}"}
            ]
        },
        config={"recursion_limit": 40,
            "run_name": "Ejecutor",           
            "tags": ["ejecutor", modelo],     
            "metadata": {                        
                "agente": "ejecutor",
                "modelo": modelo,
                
                "proveedor": llm.__class__.__name__,
            },
        },
    )
    
    return response["messages"][-1].content, response["messages"]  # Devuelve el contenido de la última respuesta y todo el historial de mensajes para análisis posterior por corrector
