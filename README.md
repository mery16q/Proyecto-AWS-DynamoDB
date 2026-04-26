# Proyecto-AWS-DynamoDB
**Asignatura:** Complemento de base de datos (Grado en Ingeniería Informática del Software, Universidad de Sevilla)
**Curso académico:** 2025/2026
**Repositorio:** https://github.com/mery16q/Proyecto-AWS-DynamoDB
**Integrantes:** Mónica Jingling Núñez Regidor, María Auxiliadora Quintana Fernández

## Descripción
Sistema de gestión de catálogo bibliográfico en la nube con DynamoDB.

# Índice
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Configuración del entorno](#configuración-del-entorno)
- [Ejecución](#ejecución)
- [Manual de Uso de la Aplicación Web](#manual-de-uso-de-la-aplicación-web)
- [Documentación Técnica](#documentación-técnica)
## Estructura del Proyecto
- `src/`: Código fuente para infraestructura, poblar la base de datos y consultas.
- `awsDynamo/`: Aplicación web con Django para interactuar con el catálogo.

## Configuración del entorno
1. Clonar el repositorio.
2. Crear entorno virtual: `python -m venv venv`
3. Activar: `.\venv\Scripts\activate` (o `source venv/bin/activate`)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Añadir variables de entorno de AWS (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)

## Ejecución
Es posible interactuar con el proyecto a través de la terminal usando los siguientes comandos:
- Para crear la infraestructura: `python src/infraestructura.py`
- Para poblar con datos: `python src/poblar_db.py`
- Para consultar datos: `python src/consultas.py`

Para ejecutar la aplicación web:
1. Navegar a la carpeta awsDynamo: `cd awsDynamo`
2. Ejecutar el archivo principal: `python manage.py runserver`

## Manual de Uso de la Aplicación Web
Es muy importarte haber ejecutado los comandos anteriores para ejecutar la aplicación web.

Para acceder a la aplicación hay dos maneras:

1. De forma manual: `http://127.0.0.1:8000/` en tu navegador, que habría que seguir los pasos previamente especificados
2. Accediendo a través del despliegue en Render: https://proyecto-aws-dynamodb.onrender.com


Las funcionalidades disponibles incluyen:
1. **Gestión de la base de datos (Poblado masivo)**: 
- Acceso: En el inicio y en la sección "Poblar DB" desde la NavBar.
- Configuración: El usuario puede definir el número exacto de libros a generar, el número de autores por libro y el número de usuarios.
- Ejecución: Al hacer clic en "Poblar Base de Datos", se iniciará el proceso de generación y almacenamiento de datos en DynamoDB. Se mostrará un mensaje de éxito al finalizar, esto puede tardar unos segundos.
- Nota: Es recomendable no interrumpir el proceso de poblar la base de datos, para asegurar que todos los índices se propaguen correctamente.
2. **Búsqueda de Libros, Usuarios y Préstamos**:
- Acceso: En la navbar se encuentran las secciones "Libros", "Usuarios" y "Préstamos". Cada uno de ellos despliega un dropdown con opciones de búsqueda. 
- Funcionalidad: Cada opción de búsqueda permite al usuario ingresar criterios específicos (por ejemplo, título del libro, nombre del autor, nombre del usuario, etc.) para filtrar los resultados. Al enviar la consulta, se mostrarán los resultados correspondientes en la misma página.
3. **Flujo de Préstamos**:
- Acceso: En la sección "Registrar Préstamo" desde la NavBar.
- Funcionalidad: El usuario debe indicar la fecha de inicio y fin junto con el id del usuario y el isbn del libro. Al hacer clic en "Registrar Préstamo", se validará la disponibilidad del libro y se registrará el préstamo en la base de datos. Se mostrará un mensaje de éxito o error según corresponda.
5. **Interpretación de Resultados**:

En cada sección de búsqueda, los resultados se presentan en una tabla con columnas relevantes (por ejemplo, título del libro, autor, usuario, fecha de préstamo, etc.). Además, se muestra un contador que indica el número de resultados encontrados frente al total disponible en la base de datos para esa consulta específica. Esto permite al usuario tener una visión clara de la cantidad de datos que cumplen con los criterios de búsqueda.
6. **Resolución de Problemas Frecuentes (FAQ)**:
|Problema|Probable causa| Solución|
|---|---|---|
|La aplicación no muestra resultados después de poblar la base de datos.|El proceso de poblar la base de datos no ha finalizado o los índices no se han propagado completamente.|Espera unos segundos después de poblar la base de datos para asegurarte de que el proceso haya finalizado y los índices estén disponibles. Si el problema persiste, verifica los logs para identificar posibles errores durante el proceso de poblar la base de datos.|
|Error al registrar un préstamo, indicando que el libro no está disponible.|El libro ya está prestado a otro usuario durante el período seleccionado.|Verifica la disponibilidad del libro antes de intentar registrar el préstamo, esto es posible en la sección "Préstamos" filtrando por isbn. Asegúrate de que las fechas de inicio y fin no se solapen con otros préstamos registrados para el mismo libro.|
|Los contadores totales (X de Y) no cambian|Los datos están almacenados en caché|Los contadores se actualizan tras una hora o al reiniciar el proceso de población|

## Documentación Técnica
- [Contrato de Datos (Esquema de DynamoDB)](DATA_CONTRACT.md)
