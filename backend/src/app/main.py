import asyncpg
from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
import pandas as pd 
import io 
import math


DATABASE_URL = "postgresql://postgres:distridb1234@localhost:5432/distridb"

app = FastAPI()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    try:
        # Intentar conectarse a la base de datos PostgreSQL usando asyncpg
        app.state.db_connection = await asyncpg.connect(DATABASE_URL)
        logger.info("Conexión a la base de datos exitosa.")
    except asyncpg.PostgresError as e:
        logger.error(f"Error de conexión a la base de datos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@app.on_event("shutdown")
async def shutdown():
    # Cerrar la conexión cuando se apaga la aplicación
    if app.state.db_connection:
        await app.state.db_connection.close()
        logger.info("Conexión a la base de datos cerrada.")

@app.get("/check_db_connection")
async def check_db_connection():
    try:
        # Realizar una consulta simple para verificar la conexión
        result = await app.state.db_connection.fetch("SELECT 1")
        return {"status": "connected", "result": result}
    except asyncpg.PostgresError as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


@app.get('/')
def get_main_App():
    text=  { 'DsitriAPI' : 'WELCOME TO API REST DISTRIMED'}
    return text

#ROUTE CSV 
@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Leer el archivo CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        """
        Se desarrolla el SPRINT  2

        """
        #PROCESO PROCESAMIENTO DE DATOS.

        # Limpiar valores no válidos (NaN, Inf, -Inf)
        df = df.apply(lambda col: col.apply(lambda x: None if isinstance(x, float) and (math.isnan(x) or math.isinf(x)) else x))
        
        # Asegurarse de que los valores no válidos no causen problemas con JSON
        df = df.replace([float('inf'), float('-inf'), float('nan')], None)
        
        # Imprimir para depuración
        print(f"DataFrame cargado: {df.head()}")
        
        # Respuesta con los datos del CSV
        return {
            "filename": file.filename,
            "columns": df.columns.tolist(),
            "rows": df.head(5).to_dict(orient="records"),
        }
    except Exception as e:
        # Imprimir el error detallado para depuración
        print(f"Error al procesar el archivo: {e}")
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo CSV: {str(e)}")