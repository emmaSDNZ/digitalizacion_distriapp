import asyncpg
from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
import pandas as pd 
from io import BytesIO
import io 
import math
from contextlib import asynccontextmanager
from datetime import datetime

import asyncpg
from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
import pandas as pd 
from io import BytesIO
import os
from pathlib import Path

DATABASE_URL = "postgresql://postgres:distridb1234@localhost:5432/distridb"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Nueva forma de manejar eventos con lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.db_connection = await asyncpg.connect(DATABASE_URL)
        logger.info("✅ Conexión a la base de datos exitosa.")
        yield  # Continúa con la ejecución de la app
    finally:
        await app.state.db_connection.close()
        logger.info("🔴 Conexión a la base de datos cerrada.")

# Inicializar FastAPI con lifespan
app = FastAPI(lifespan=lifespan)

@app.get('/')
def get_main_App():
    return { 'DsitriAPI' : 'WELCOME TO API REST DISTRIMED'}

#
#
#
#
""" LOGICA SERVICIO PRODUCTOS  """

#
#
#
#

#Funcion para obtener la ruta del escritorio del usuario
def obtener_ruta_escritorio():
    # Usamos pathlib para obtener la ruta del escritorio en función del sistema operativo
    escritorio = Path.home()/ "Desktop"  # Esto funciona en la mayoría de los sistemas
    return escritorio

# Creación de Carpeta
def crear_carpeta_ruta(directorio_base="archivos_subidos"):
    # Se define la ruta de la carpeta
    ruta_escritorio = obtener_ruta_escritorio()

    # Definir la ruta completa para la carpeta
    ruta_carpeta = ruta_escritorio / directorio_base

    # Verificar si la carpeta existe y crearla si no
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)  # Crea la carpeta si no existe

    return ruta_carpeta


# Función para guardar el archivo CSV con la fecha y hora
def guardar_archivo_con_fecha(df, filename, directorio_base="archivos_subidos"):
    # Generar un nombre de archivo único basado en la fecha y hora
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")  # Cambiar los dos puntos por guion bajo
    nombre_archivo = f"{fecha_hora_actual}_{filename}"

    # Crear la carpeta en el escritorio
    ruta_carpeta = crear_carpeta_ruta(directorio_base)

    # Ruta completa para guardar el archivo
    ruta_archivo = ruta_carpeta / nombre_archivo

    # Guardar el DataFrame como un CSV en la ruta especificada
    df.to_csv(ruta_archivo, index=False)
    return ruta_archivo  # Retornar la ruta del archivo guardado


# Función para convertir XLSX a CSV
def convertir_xlsx_a_csv(xlsx_file):
    df = pd.read_excel(xlsx_file, engine='openpyxl')
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Volver al inicio del buffer
    return csv_buffer.getvalue()  # Devuelve el CSV en formato binario

#Funcion para estandarizar el nombre de las columnas
def estandarizar_nombre_columnas(df):

    # Normalizar nombres de columnas: minúsculas, sin espacios, reemplazar espacios por "_"
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    columnas_requeridas = {
        "cod_de_producto": ["codigo_producto", "cod_producto", "producto_id"],
        "cod_de_barra": ["codigo_barra", "cod_barra", "barcode"],
        "descripcion": ["desc", "nombre", "detalle"],
        "presentacion": ["formato", "tipo_presentacion"],
        "unidad_medida": ["unidad", "medida", "u_medida"],
        "contenido": ["cantidad", "contenido_neto", "volumen"],
        "laboratorio": ["marca", "fabricante", "proveedor"],
        "precio_base": ["precio", "costo", "precio_unitario"]
    }

   
    # Crear un mapeo inverso para renombrar
    mapping = {alias: key for key, values in columnas_requeridas.items() for alias in values}
    df = df.rename(columns=lambda col: mapping.get(col, col))

    return df


# Función para cargar el archivo y convertir si es necesario
def carga_archivo_FastApi(contents, filename):
    try:
        # Si el archivo es un CSV, lo procesamos directamente
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        # Si el archivo es un XLSX, lo convertimos a CSV primero
        elif filename.endswith('.xlsx'):
            csv_data = convertir_xlsx_a_csv(BytesIO(contents))
            df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
        else:
            raise ValueError("El archivo debe ser CSV o XLSX.")

        return df
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {e}")



# Definir la excepción personalizada
class ColumnasFaltantesError(Exception):
    def __init__(self, columnas_faltantes):
        self.columnas_faltantes = columnas_faltantes
        self.message = f"Faltan las siguientes columnas: {', '.join(columnas_faltantes)}"
        super().__init__(self.message)

# Función para verificar las columnas
def verificar_columnas_proveedor(df: pd.DataFrame):
    """
    Verifica si un DataFrame (df) contiene las columnas obligatorias para un proveedor.

    Args:
        df (pd.DataFrame): El DataFrame de pandas a verificar.

    Returns:
        bool: True si todas las columnas requeridas están presentes, False en caso contrario.
              Lanza una excepción con el mensaje correspondiente si faltan columnas.
    """

    # Lista de las columnas requeridas para los datos del proveedor.
    columnas_requeridas = [
        "cod_de_producto",  # Código del producto.
        "cod_de_barra",  # Código de barras del producto.
        "descripcion",  # Descripción del producto.
        "presentacion",  # Presentación del producto (ej: caja, unidad, etc.).
        "unidad_medida",  # Unidad de medida del producto (ej: kg, l, unidades, etc.).
        "contenido",  # Contenido del producto (ej: cantidad, peso, volumen, etc.).
        "laboratorio",  # Laboratorio fabricante del producto.
        "precio_base",  # Precio base del producto.
    ]

    # Crea una lista con las columnas que *faltan* en el DataFrame.
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]

    # Si hay columnas faltantes, lanzar la excepcion con el mensaje correspondiente
    if columnas_faltantes:
        # Unir las columnas faltantes en un solo mensaje
        columnas_faltantes_str = ', '.join(columnas_faltantes)
        raise ColumnasFaltantesError(columnas_faltantes)
    #print("Columnas cargadas en el DataFrame:", df.columns.tolist())

    # Si todas las columnas requeridas están presentes, se imprime un mensaje
    logger.info("✅ Todas las columnas requeridas están presentes.")
    return True  # Retorna True si están todas las columnas.

#
#
#
#

# Endpoint para subir archivo CSV
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(..., media_type='text/csv')):
    try:
        contents = await file.read()

        # Cargar archivo
        df = carga_archivo_FastApi(contents, file.filename)

        # Verificar si el DataFrame está vacío
        if df.empty:
            raise ValueError("El archivo CSV está vacío o no contiene datos válidos.")

        # 🔹 Aplicar estandarización de nombres de columnas
        df = estandarizar_nombre_columnas(df)
        logger.info(f"Columnas después de estandarizar: {df.columns.tolist()}")

        # Verificar columnas requeridas
        verificar_columnas_proveedor(df)

        # Reemplazar NaN, inf o -inf por un valor válido (None o 0, según corresponda)
        df.replace([float('inf'), float('-inf'), float('nan')], None, inplace=True)

        #Guardar el archivo csv conl a fecha y hora
        ruta_archivo_guardado = guardar_archivo_con_fecha(df, file.filename)
        logger.info(f"✅ Archivo guardado en: {ruta_archivo_guardado}")

        # Crear respuesta con detalles del archivo cargado
        response = {
            "filename": file.filename,
            "total_rows": df.shape[0],  
            "columns": df.columns.tolist(),
            "sample_rows": df.head(5).to_dict(orient="records"),
        }

        return response
    
    except ColumnasFaltantesError as e:
        logger.error(f"❌ Error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    
    except Exception as e:
        logger.error(f"❌ Error al procesar el archivo: {e}")
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo CSV: {str(e)}")
