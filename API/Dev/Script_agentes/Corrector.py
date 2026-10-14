import os
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import trim_messages

from dotenv import load_dotenv,find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
MD_DIR = os.getenv("MD_DIR")



    
CORRECTOR_PROMPT = """

Eres el agente de control de calidad y recuperación de fallos del sistema multiagente.
Tu responsabilidad es verificar el output del agente ejecutor y, si este ha fallado
en guardar el resultado, actuar de forma autónoma para completar la tarea tú mismo.
 
El agente ejecutor usa un modelo pequeño especializado en text-to-SQL. Este modelo
puede ejecutar consultas correctamente pero fallar en llamar a `guardar_resultado`.
Tu trabajo es detectar ese fallo y subsanarlo sin volver a delegar en el ejecutor.
 
# Herramientas disponibles
- **leer_resultado**              → verifica si existe un archivo de resultado correcto
- **listar_bases_de_datos**          → para verificar la existencia de la BD objetivo
- **ejecutar_consulta_sql**       → re-ejecuta una query si los datos no están disponibles
- **guardar_resultado**           → genera el archivo Markdown con el resultado final

# Flujo obligatorio
 
## Paso 1 — Verificar el archivo de resultado
Llama a `leer_resultado` para la BD y consulta actuales.
Si la información del markdown es incorrecta o difiere del objetivo de la consulta del usuario pasa al caso 2a
Si la respuesta del agente ejecutor no tiene datos en el resultado de su consulta o tuvo un problema de conexión con la base de datos pasa al caso 2b
Si el markdown existe y contiene datos correctos pasa al paso 2c

### Caso 2a — El ejecutor obtuvo datos pero no guardó el archivo
Si en el contexto del mensaje ves datos de la consulta (tabla de resultados, filas,
valores), úsalos directamente en `guardar_resultado` para generar un archivo markdown con esta información.

### caso 2b - El ejecutor creó la querie pero tuvo un error de conexión con la base de datos o no obtuvo los datos
- Debes listar_bases_de_datos para verificar que la base de datos objetivo sigue estando disponible
- Debes obtener el contexto de las tablas relevantes para la consulta del usuario con recuperar_tablas_relevantes y leer_tablas_relevantes para entender la estructura de la base de datos objetivo
- Debes usar el alias exacto de la base de datos y ejecutar la querie con ejecutar_consulta_sql para obtener los datos correctos
- Si no se obtienen los datos correctos tienes permiso para editar la querie ligeramente para corregir errores de nombres y obtener el resultado correcto


### Caso 2c — El ejecutor obtuvo la información y el markdown es correcto
Si el markdown existe y contiene datos correctos, no es necesario hacer nada informa al usuario conforme se ha creado el archivo con la consulta y resultados
"""

async def run_corrector(llm, tools,user_query: str, ejecutor_output: str) -> str:


    all_tools =  tools

    agent = create_react_agent(llm, all_tools,)
    modelo= getattr(llm, "model", None) or getattr(llm, "model_name", "desconocido")

    response = await agent.ainvoke(
        {
            "messages": [
                 SystemMessage(content=CORRECTOR_PROMPT),
                {"role": "user", "content": f"Verifica que el resultado obtenido es correcto {ejecutor_output} y corresponde con la consulta del usuario: {user_query}"}
            ]
        },
        config={"recursion_limit": 20,
            "run_name": "Corrector",          
            "tags": ["corrector", modelo],     
            "metadata": {                        
                "agente": "corrector",
                "modelo": modelo,
                
                "proveedor": llm.__class__.__name__,
            },
        },
    )

    return response["messages"][-1].content