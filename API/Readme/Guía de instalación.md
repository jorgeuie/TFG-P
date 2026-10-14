# Pasos
- Primer paso: Debes instalar las dependencias ubicadas en el archivo de requirements.txt

- Segundo paso: Debes gestionar la instalación de pandoc y el motor de conversion xelatex para el correcto funcionamiento de la conversión de archivos markdown a PDF
https://pandoc.org/
https://miktex.org/download

- Tercer paso: Colocar las API keys que se utilicen para el funcionamiento de los modelos de lenguaje en el archivo .env y cambiar en el archivo API el modelo utilizado según tus necesidades.

- Cuarto paso: Tienes que acceder a la carpeta .vscode y cambiar los parámetros que están en el mcp.json, en el command tienes que poner el workspace donde está alojado el proyecto y el intérprete de python en args tienes que poner la ruta del servidor mcp en este caso se llamaría 'main.py' 

- Quinto paso: Gestionar las bases de datos en la carpeta de Bases de datos utilizadas existen archivos para restaurar la información de las bases de datos utilizadas en este proyecto.

- Sexto paso: Una vez se haya instalado todos los elementos necesarios ejecuta la api esto iniciará el proceso de inicio de los diferentes elementos relevantes: el servidor MCP, los agentes, opcionalmente podrás iniciar la interfaz gráfica desde ejecutandola desde una terminal externa con el comando cmd : cd/API/DEV/UI/interfaz_grafica.py (cambiar en función de tu ruta) en caso de no utilizarla se puede desde el navegador con la url (http://localhost:8000/docs) para interactuar con ella.

