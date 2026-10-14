# api, aux y phonix
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from fastapi import BackgroundTasks
import os
import subprocess #sirve para ejecutar comandos del sistema, como pandoc para convertir md a pdf
from fastapi.responses import FileResponse
from dotenv import load_dotenv, find_dotenv
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register

# LangChain y MCP
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_community.callbacks.manager import get_openai_callback

# Comunicacion proveedores LLM
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Agentes
from Script_agentes.juez import run_juez
from Script_agentes.Corrector import run_corrector
from Script_agentes.Agente_extractor import run_extractor
from Script_agentes.Agente_Ejecutor import run_ejecutor
from Script_agentes.Agente_supervisor import run_supervisor


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Configuración de conexiones con el servidor MCP
MCP_CONFIG = {
    "my-mcp-server-main": {
        "transport": "stdio", # tipo de transporte
        "command": os.getenv("MCP_PYTHON"), # ubicación del ejecutable de Python
        "args": [os.getenv("MCP_SCRIPT")], # ubicación del script mcp_server.py
    }
}
# Directorio para guardar archivos Markdown
MD_DIR= os.getenv("MD_DIR")

# Variables de entorno para proveedores LLM
OPENAI_API_KEY=os.getenv("GITHUB_TOKEN") 
COLAB_OLLAMA_URL=os.getenv("COLAB_OLLAMA_URL")
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
GROK_API_KEY=os.getenv("GROK_API_KEY")
NVIDIA_API_KEY=os.getenv("NVIDIA_API_KEY")



# Diccionario global para guardar el estado de la aplicación (LLM y Tools)
app_state = {}

# Diccionario global para compartir resultados usado especialmente para los modelos pequeños especializados en SQL
compartir: dict = {"ejecutor_output": ""}

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Arranca servidor Phoenix en http://localhost:6006
    px.launch_app()

    # Registra el tracer de OpenTelemetry apuntando a Phoenix
    tracer_provider = register(
        project_name="multiagente_SQL",  
        endpoint="http://localhost:6006/v1/traces",
    )

    # Captura todos los agentes y tools
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)


    print(" Inicializando LLM y conectando al servidor MCP...")
    # Modelos probados durante el desarrollo y pruebas unitarias
    
    '''
    llm = ChatOllama(
        model="gemma4:26b",
        temperature=0.1,
        base_url=COLAB_OLLAMA_URL     
    )
    '''
    '''
    llm_sql = ChatOpenAI(
        #model="arctic-text2sql-r1-7b:2",
        #model="xiyansql-qwencoder-7b-2504",
        api_key="lm-studio",         
        base_url="http://localhost:1234/v1", # puerto por defecto de LM Studio
        temperature=0.1,
        max_tokens=502048
        )
    '''
    '''
    #nube
    llm = ChatOpenAI(
        model="gpt-4o-mini", 
        api_key=OPENAI_API_KEY,
        base_url="https://models.inference.ai.azure.com",
        temperature=0.1,
    )
    '''
   
    '''
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1,
    )
    #'''
    '''
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROK_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        temperature=0.1,
    )'''
   # ''' Configuraciones alternativas probadas
    llm_sql = ChatOpenAI(
    model="openrouter/owl-alpha",
    #model="openai/gpt-oss-120b:free",
    #model="nvidia/nemotron-3-ultra-550b-a55b:free",
    #model="z-ai/glm-4.5-air:free",
    #model="nex-agi/nex-n2-pro:free",
    #model="google/gemma-4-31b-it:free",
    #model="nvidia/nemotron-3-super-120b-a12b:free",
    #model="qwen/qwen3-next-80b-a3b-instruct:free",
    #model="meta-llama/llama-3.3-70b-instruct:free",
    #model="nousresearch/hermes-3-llama-3.1-405b:free",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1,
    )
    #'''
    #'''
    llm = ChatOpenAI(
    model="openai/gpt-oss-120b:free",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1,
    )
    #'''
    
    
    llm_eval = ChatOpenAI(
    model="openrouter/owl-alpha",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.1,
    )
    

    
    
    
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    nvidia_model_eval = os.getenv("NVIDIA_MODEL", "mistralai/mistral-large-3-675b-instruct-2512")
    nvidia_base_url = os.getenv("NVIDIA_BASE_URL")

    if not nvidia_api_key:
        raise RuntimeError(
            "Falta NVIDIA_API_KEY. Configura la variable de entorno antes de arrancar la API."
        )

    '''
    llm = ChatNVIDIA(
        model=nvidia_model_eval,
        nvidia_api_key=nvidia_api_key,
        base_url=nvidia_base_url or None,
        temperature=0.1
    )
    '''
   


    #Inicialiación del servidore MCP 
    client = MultiServerMCPClient(MCP_CONFIG)
    mcp_tools = await client.get_tools()
    print(f" Conectado al MCP. Tools SQL disponibles ({len(mcp_tools)})")
    
    

    # Llamada de agentes para el orquestador
    @tool
    async def agente_extractor(nombre_schema: str = "public") -> str:
        """
        Analiza el esquema de la base de datos PostgreSQL indicado y genera
         el archivo Markdown con toda la estructura: tablas,
        columnas, tipos, claves primarias/foráneas y relaciones.
        Úsalo SIEMPRE como primer paso antes de generar consultas SQL.
        Argumento: nombre del schema de PostgreSQL (por defecto 'public').
        """
        return await run_extractor(llm, mcp_tools, nombre_schema)

    @tool
    async def agente_ejecutor(consulta: str) -> str:
        """
        Analiza el esquema de la BD indicada. 
        base_datos debe ser el alias exacto eg ('Escuela' , 'DVD').
        Llama a cambiar_base_datos antes de extraer nada.
        """
        resultado =await run_ejecutor(llm_sql, mcp_tools, consulta)
            
        compartir["ejecutor_output"] = resultado if isinstance(resultado, str) else str(resultado)
        return compartir["ejecutor_output"]

    @tool
    async def agente_corrector(consulta: str) -> str:
        """
        Verifica que el resultado obtenido es correcto y corresponde con la consulta del usuario.
        """
        return await run_corrector(llm, mcp_tools, consulta,ejecutor_output=compartir["ejecutor_output"])

       

    # Guardado en estado global para acceso desde endpoints
    all_tools = mcp_tools + [agente_extractor, agente_ejecutor, agente_corrector]


    app_state["llm_sql"] = llm_sql 
    app_state["llm_eval"] = llm_eval   
    app_state["llm"] = llm
    app_state["tools"] = all_tools
    app_state["mcp_client"] = client

    
    print(" Sistema Multi-Agente Listo para recibir peticiones por API.")
    
    yield # Aquí la aplicación FastAPI se queda corriendo y recibiendo peticiones
    

    print(" Cerrando el servidor y desconectando MCP...")


   
#################### ENDPOINTS DE LA API #######################

#Incialización de la aplicación FastAPI con el lifespan definido para manejar la inicialización y cierre de recursos
app = FastAPI(lifespan=lifespan, title="API Agentes DB", version="1.0")

#################### GESTION DE LA BD #######################

# Clase de validación de datos para la base de datos PostgreSQL 
class DatabaseEntry(BaseModel):
    alias: str
    host: str
    port: int = 5432
    dbname: str
    user: str
    password: str

# Funciones auxiliares para leer y guardar la lista de bases de datos en un archivo JSON
def leer_json_bd() -> list:
    try:
        with open(os.getenv("DB_FILE"), "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("databases", [])  # extraer lista de bases de datos
    except FileNotFoundError:
        return []


def guardar_json_bd(data: list) -> None:
    path = os.getenv("DB_FILE")
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump({"databases": data}, f, indent=4, ensure_ascii=False)  # Envuelve al guardar
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

# Endpoints principales
@app.get("/listar_bases_datos")
async def listar_bases_datos():
    data=leer_json_bd()
    if not data:
        return {"mensaje": "No se encontró ningún archivo de bases de datos."}
    return {"bases_datos": data}

@app.post("/agregar_base_datos")
def agregar_base_datos(entry: DatabaseEntry):
    data = leer_json_bd()
    for db in data:
        if db["alias"].lower() == entry.alias.lower():
            raise HTTPException(status_code=400, detail=f"Ya existe una base de datos con el alias '{entry.alias}'.")
    data.append(entry.dict())
    guardar_json_bd(data)
    return {"mensaje": f"Base de datos '{entry.alias}' agregada exitosamente."}

@app.put("/actualizar_base_datos/{alias}")
def actualizar_base_datos(alias: str, entry: DatabaseEntry):
    data = leer_json_bd()
    for i, db in enumerate(data):
        if db["alias"].lower() == alias.lower():
            data[i] = entry.dict()
            guardar_json_bd(data)
            return {"mensaje": f"Base de datos '{alias}' actualizada exitosamente."}
    raise HTTPException(status_code=404, detail=f"No se encontró una base de datos con el alias '{alias}'.")

@app.delete("/eliminar_base_datos/{alias}")
def eliminar_base_datos(alias: str):
    data = leer_json_bd()
    for i, db in enumerate(data):
        if db["alias"].lower() == alias.lower():
            del data[i]
            guardar_json_bd(data)
            return {"mensaje": f"Base de datos '{alias}' eliminada exitosamente."}
    raise HTTPException(status_code=404, detail=f"No se encontró una base de datos con el alias '{alias}'.")

#################### Preguntas y evaluaciones #############################################

class QueryRequest(BaseModel):
    pregunta: str

@app.post("/preguntar")
async def preguntar(request: QueryRequest):
    """
    Endpoint principal para enviar preguntas al supervisor.
    """
    llm = app_state.get("llm")
    tools = app_state.get("tools")

    
    if not llm or not tools:
        raise HTTPException(status_code=503, detail="El sistema multi-agente aún no está inicializado.")


    print(f"\n Petición recibida en API: '{request.pregunta}'...\n")

    
    try:
        
        respuesta_final = await asyncio.wait_for( run_supervisor(llm, tools, request.pregunta),timeout=10000)  #timeout para evita que se quede colgado no se cumplen los 5 minutos de objetivos

        print(respuesta_final)
        return {"respuesta": respuesta_final}
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout: el agente tardó demasiado.")
    
    
    except Exception as e:

        print(f"\n Error durante la ejecución: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

class EvalRequest(BaseModel):
    pregunta: str
    respuesta: str

# Usado por el agente evaluador y usado para pruebas unitarias no mostrado en la interfaz gráfica
@app.post("/evaluar")
async def evaluar(request: EvalRequest):
    llm       = app_state.get("llm")
    tools = app_state.get("tools")

    if not llm or not tools:
        raise HTTPException(status_code=503, detail="Sistema no inicializado.")

    consulta = f"Pregunta del usuario: {request.pregunta}\nRespuesta dada por el sistema: {request.respuesta}"
    veredicto = await run_juez(llm, tools, consulta, ejecutor_output=compartir["ejecutor_output"])
    return {"veredicto": veredicto}


    

@app.get("/conversion/{nombre_archivo}")
async def convertir_markdown_pdf(nombre_archivo: str):
    
    
    nombre_md  = f"{nombre_archivo.strip().lower()}.md"
    nombre_pdf = f"{nombre_archivo.strip().lower()}.pdf"
    ruta_md    = os.path.join(MD_DIR, nombre_md)
    ruta_pdf   = os.path.join(MD_DIR, nombre_pdf)
    
    if not os.path.exists(ruta_md):
        return f"Error: No existe '{ruta_md}'. Asegúrate de que el archivo Markdown existe."
    
    ruta_pandoc=os.getenv("PANDOC")
    ruta_xealtex=os.getenv("XELATEX")
   
    

    comando = [
        ruta_pandoc,
        ruta_md,
        "-o", ruta_pdf,
        f"--pdf-engine={ruta_xealtex}"
    ]
    
    try:
        
        resultado = subprocess.run(comando, capture_output=True, text=True, check=True)
        return FileResponse(path=ruta_pdf, media_type='application/pdf', filename=nombre_pdf)
        
    except subprocess.CalledProcessError as e:
        
        return f"Error interno de Pandoc al convertir el archivo.\nDetalles: {e.stderr}"
        
    except FileNotFoundError:
        
        return "Error crítico: 'pandoc' no está instalado en el sistema o no se encuentra en el PATH."
    
    


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


