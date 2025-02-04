Descripción de cada carpeta y su función:
db: Aquí colocas todo lo relacionado con la conexión a la base de datos y las consultas directas que ejecutas con asyncpg. La idea es centralizar la conexión y las consultas SQL.

database.py: Aquí configuras la conexión a PostgreSQL usando asyncpg como hiciste en el ejemplo.
queries.py: En este archivo defines las funciones que realizan las consultas específicas a la base de datos. Esto incluye las consultas de selección, inserción, actualización y eliminación.
models: Aquí defines las estructuras de datos que representan las entidades que usas en tu aplicación (aunque no sean modelos ORM, pueden ser clases Python que simplemente estructuran los datos).

user.py: Ejemplo de un modelo para representar un "Usuario" o cualquier entidad que tengas en tu aplicación.
routes: Aquí defines todas las rutas o endpoints de la API. Cada archivo contiene los endpoints relacionados con una entidad o funcionalidad específica.

user_routes.py: Aquí colocarías las rutas como /users, /users/{id}, etc.
schemas: Esta carpeta contiene los esquemas de validación, utilizando Pydantic para validar los datos que entran en la API (por ejemplo, el cuerpo de la solicitud).

user_schema.py: Definirías los esquemas para los datos de usuario que quieres recibir o enviar. Por ejemplo, podrías tener un UserCreateSchema para recibir datos de usuario en una solicitud POST y un UserResponseSchema para la respuesta GET.
services: Esta carpeta contiene la lógica de negocio. Los servicios gestionan la interacción entre la base de datos, los modelos y las rutas. Aquí centralizas toda la lógica que no debe estar en las rutas directamente.

user_service.py: Aquí implementarías las funciones de negocio relacionadas con los usuarios, como crear un usuario, obtener un usuario por ID, actualizar o eliminar usuarios. Los servicios llaman a las funciones de consulta en queries.py.
main.py: Este es el archivo principal de FastAPI donde se inicializan las rutas, la base de datos y la configuración general de la aplicación.


APP/
│
├── db/               # Conexión a la base de datos y funciones relacionadas con el acceso a la base de datos
│   ├── __init__.py   # Inicialización de la conexión y configuración
│   ├── database.py   # Configuración de la conexión a PostgreSQL (usando asyncpg)
│   └── queries.py    # Consultas específicas a la base de datos (no ORM)
│
├── models/           # Definición de los modelos (estructuras de datos)
│   ├── __init__.py   # Archivo de inicialización de modelos
│   └── user.py       # Ejemplo de modelo (si tienes entidades como "User", por ejemplo)
│
├── routes/           # Definición de las rutas (endpoints de la API)
│   ├── __init__.py   # Archivo de inicialización de rutas
│   └── user_routes.py  # Rutas relacionadas con los usuarios (ejemplo)
│
├── schemas/          # Esquemas de validación (Pydantic para validaciones de entrada)
│   ├── __init__.py   # Archivo de inicialización de esquemas
│   └── user_schema.py  # Esquema para los datos de usuario (ejemplo)
│
├── services/         # Lógica de negocio (servicios que realizan la interacción entre DB, modelos y rutas)
│   ├── __init__.py   # Inicialización de los servicios
│   └── user_service.py  # Lógica de negocio relacionada con los usuarios
│
└── main.py           # Archivo principal para iniciar la aplicación FastAPI




