# Configuración general (base de datos, variables de entorno, etc.)
import os


#os.getenv para obtener la URL de la base de datos desde una variable de entorno
DATABASE_URL = os.getenv("postgresql://postgres:distridb1234@localhost:5432/distridb")
