import os
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import trim_messages

from dotenv import load_dotenv,find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
MD_DIR = os.getenv("MD_DIR")



SUPERVISOR_PROMPT = """
Eres un operador secuencial de un sistema multiagente sobre PostgreSQL.
Tu objetivo es decidir el siguiente paso necesario para obtener el resultado deseado por el usuario.


# Reglas 
- Una sola herramienta por turno, en orden secuencial.
- No inventes datos ni resultados.
- No hagas suposiciones sobre el usuario o la base de datos sin antes verificar con las herramientas disponibles.
- Debes delegar al agente ejecutor la creación y ejecucción de SQL

# Herramientas disponibles 
- **listar_esquemas**   para identificar qué BDs tienen esquema disponible
- **leer_esquema_bd** para obtener el esquema de una BD concreta en formato Markdown


# Flujo obligatorio

## Paso 1 — Identificar la BD objetivo
- Llama a listar_esquemas.

## Paso 2 — Verificar esquema
- Si la BD objetivo NO tiene esquema → ir al Paso 3a.
- Si la BD objetivo SÍ tiene esquema → ir al Paso 3b.


## Paso 3a — Extraer esquema
- Llama a agente_extractor con:
  - base_datos: alias exacto (ej: 'Escuela', 'DVD')
  - schema: 'public' por defecto

  es válido y no está vacío.
    - Si el esquema es válido → ir al Paso 3b.
    - Si el esquema está vacío o hay error → ERROR.

## Paso 3b — Ejecutar consulta
- Llama a agente_ejecutor con:
  - La solicitud original del usuario sin modificar.
  - El esquema de la base de datos en formato Markdown.
- Espera la respuesta completa antes de continuar.
Debes llamar al agente corrector para la verificación final del resultado
"""


async def run_supervisor(llm, tools, user_query: str) -> str:

    
    all_tools =  tools

    agent = create_react_agent(llm, all_tools,)
    modelo= getattr(llm, "model", None) or getattr(llm, "model_name", "desconocido")

    response = await agent.ainvoke(
        {
            "messages": [
                SystemMessage(content=SUPERVISOR_PROMPT),
                {"role": "user", "content": user_query},
            ]
        },
        config={"recursion_limit": 40,
            "run_name": "Supervisor",          
            "tags": ["supervisor", modelo],     
            "metadata": {                        
                "agente": "supervisor",
                "modelo": modelo,
                
                "proveedor": llm.__class__.__name__,
            },
        },
    )

    return response["messages"][-1].content