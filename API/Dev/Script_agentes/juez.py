import os
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import trim_messages

from dotenv import load_dotenv,find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
MD_DIR = os.getenv("MD_DIR")



    
JUEZ_PROMPT = """
Eres el encargado de puntuar la precision de respuestas dadas por un sistema multi agente que responde a consultas a usuarios sobre bases de datos. 

# Herramientas disponibles 
- leer_resultado
- ejecutar_querie (MCP)



# Flujo obligatorio

## Paso 1 — Verificar la respuesta dada por el agente ejecutor en los markdowns de resultados
- Debes revisar los resultados obtenidos por el agente ejecutor
- Si el resultado obtenido es una querie ir al paso 2
- Si el resultado obtenido es una línea que dice que se ha subido un archivo con el resultado debes buscar el archivo con leer_resultado

## paso 2 - Comprobar la querie
- Debes ejecutar la querie que hay en el archivo de resultados y comprobar que el resultado es correcto y corresponde con la consulta del usuario

## paso 3 - Puntuar la respuesta
- Si la respuesta es correcta y corresponde con la consulta del usuario, puntua con un 10
- Si la respuesta es parcialmente correcta o no corresponde del todo con la consulta del usuario, puntua con un 5
- Si la respuesta es incorrecta o no corresponde con la consulta del usuario, puntua con un 0

- Debes siempre justificar la puntuacion que das con una explicación detallada y exponer si se ha generado el archivo con los resultados actuales de la querie


Excepciones:
- Si el fallo viene dado por un ligero error en el nombre de la tabla por ejemplo alumno en vez de alumnos ignora ese error y puntua la respuesta como correcta
"""

async def run_juez(llm, tools,user_query: str, ejecutor_output: str) -> str:


    all_tools =  tools

    agent = create_react_agent(llm, all_tools,)
    modelo= getattr(llm, "model", None) or getattr(llm, "model_name", "desconocido")

    response = await agent.ainvoke(
        {
            "messages": [
                 SystemMessage(content=JUEZ_PROMPT),
                {"role": "user", "content": f"Verifica que el resultado obtenido es correcto y corresponde con la consulta del usuario: {user_query}\n\nResultado obtenido: {ejecutor_output}"}
            ]
        },
        config={"recursion_limit": 20,
            "run_name": "Juez",           
            "tags": ["juez", modelo],     
            "metadata": {                        
                "agente": "juez",
                "modelo": modelo,
                
                "proveedor": llm.__class__.__name__,
            },
        },
    )

    return response["messages"][-1].content