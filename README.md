## Integración de un Sistema Multi-Agente para Consultas en Lenguaje Natural sobre Bases de Datos Relacionales PostgreSQL
Este proyecto diseña e implementa un sistema multi-agente jerárquico capaz de convertir consultas en lenguaje natural en sentencias SQL ejecutables sobre bases de datos relacionales PostgreSQL. La arquitectura coordina cinco agentes especializados basados en LLMs a través de una estructura de supervisor-trabajador, exponiendo las herramientas de la base de datos mediante un servidor FastMCP y una capa REST de FastAPI monitoreada con Arize Phoenix.

## Arquitectura
El sistema se estructura en torno a tres componentes principales:

Servidor MCP: Implementa todas las herramientas de la base de datos utilizando SQLAlchemy y FastMCP. Garantiza la ejecución de consultas de solo lectura (SELECT) a nivel de protocolo, eliminando el riesgo de operaciones destructivas independientemente de la respuesta del modelo.

Sistema Multi-Agente: Cinco agentes ReAct basados en LangGraph orquestador, extractor, ejecutor, corrector y juez cada uno con un rol delimitado. El orquestador coordina el flujo de trabajo bajo un patrón CPDE (Centralised Planning, Decentralised Execution / Planificación Centralizada, Ejecución Descentralizada). El contexto del esquema se proporciona a los agentes a través de un archivo Markdown determinista generado a partir de los catálogos del sistema de PostgreSQL, combinado con un pipeline RAG de LlamaIndex para la recuperación semántica del esquema.

API e Interfaces: Una capa REST de FastAPI gestiona la inicialización del sistema, la configuración de los LLMs y la observabilidad a través de Arize Phoenix y OpenTelemetry. También está disponible un cliente gráfico ligero en Tkinter para usuarios no técnicos.

## Instalación
Consulta Guía_de_instalación.md ubicado en la carpeta Readme para ver todos los pasos de configuración.

## Evaluación
Se evaluaron seis configuraciones de modelos a través de 12 preguntas en cuatro bases de datos PostgreSQL (Northwind, DVD, escuela, Netflix). Owl-Alpha alcanzó un 100% de precisión de ejecución con una latencia promedio de 751 s. Las configuraciones basadas en GPT-OSS-120B alcanzaron un 91.7%. Por otro lado, los modelos especializados en SQL de 7B (Arctic-Text2SQL-R1-7B, XiYanSQL-QwenCoder-7B) solo lograron un 8.3% debido a una discrepancia en la distribución de entrenamiento entre el contexto del esquema formateado en Markdown y el formato exclusivo de DDL utilizado en sus evaluaciones de ajuste fino (fine-tuning).

## Requisitos
Dependencias de Python: requirements.txt

Pandoc + XeLaTeX (para la conversión de Markdown a PDF)

PostgreSQL

Claves de API para los proveedores de LLM configurados  y Rutas para el MCP y repositorio de archivos de los agentes donde trabajan (.env)
