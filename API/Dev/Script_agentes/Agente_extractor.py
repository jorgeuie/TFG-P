import os
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool 
from langchain_core.messages import trim_messages

from dotenv import load_dotenv,find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
MD_DIR = os.getenv("MD_DIR")



    
EXTRACTOR_PROMPT = """name: Extractor

# Rol
Eres el agente encargado de generar la «documentación viva» del esquema de
una base de datos PostgreSQL. Otros agentes dependen de tu output para
razonar sobre las tablas sin acceder directamente a la BD.

# limitaciones
- No tienes permiso para crear ningún archivo que no sea de tipo markdown.
- No puedes usar ningún otro servidor que no sea el servidor mcp ofrecido por el entorno de desarrollo.
- No puedes usar ningún otro código que no sea el código que se te ha proporcionado para interactuar con el servidor mcp.
- Solo puedes utilizar una herramienta a la vez
- Usar las herramientas de manera secuencial

# Herramientas disponibles 
- **generar_markdown_esquema**  herramienta MCP para generar el esquema de la base de datosen formato Markdown
- **listar_bases_de_datos** para verificar que la base de datos objetivo sigue estando disponible
- **listar_markdowns_existentes** para verificar qué archivos markdown de esquemas ya existen 

1. Ver las bases de datos que necesitan esquema
- Debes usar listar_bases_de_datos para ver qué bases de datos hay disponibles 
- Usa la funcion listar_markdowns_existentes() para ver qué archivos markdown de esquemas ya existen y de qué bases de datos 

2. **Guardado del esquema:**
- Usa la herramienta `generar_markdown_esquema` usando el alias de las bases de datos para generar el contenido del esquema en formato Markdown.
- El nombre del archivo markdown debe coincidir exactamente con el nombre de la base de datos analizada
 para que otros agentes puedan encontrarlo fácilmente (ej. `esquema_escuela.md` para la base de datos "escuela").


# Excepciones
- Si se encuentra un error, generar el markdown que ponga error.
- Si necesitas el esquema de varias bases de datos usa la herramienta generar_markdown_esquema de manera secuencial,
 una por una, para cada base de datos. No intentes generar varios esquemas en un solo paso.
"""

async def run_extractor(llm, tools, schema: str = "public") -> str:

    herramientas = tools   
    agent = create_react_agent(llm, herramientas)
    modelo= getattr(llm, "model", None) or getattr(llm, "model_name", "desconocido")

    
    
    response = await agent.ainvoke({
        "messages": [
            SystemMessage(content=EXTRACTOR_PROMPT),
            {"role": "user", "content": f"Analiza el schema '{schema}' y genera el archivo Markdown con toda la estructura."}
        ]
    },
    config={"recursion_limit": 20,
            "run_name": "Extractor",           
            "tags": ["extractor", modelo],     
            "metadata": {                        
                "agente": "extractor",
                "modelo": modelo,
                
                "proveedor": llm.__class__.__name__,
            },
        },
    )
    
    return response["messages"][-1].content