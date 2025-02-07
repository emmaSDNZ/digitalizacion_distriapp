
from fastapi import FastAPI
from db.session import lifespan 

app = FastAPI(lifespan=lifespan)


###
import asyncpg
from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
import pandas as pd 
from io import BytesIO
import io 
import os
import math
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
import sys
from pydantic import BaseModel
import numpy as np
# Configurar logging
logger = logging.getLogger(__name__)



#Variables
from data_utils.configuraciones.variables import Variables_data
variables_data = Variables_data()

#Modulo Productos
from data_utils.manipulacion_de_datos.maniuplacion_de_datos import  cargar_datos,\
                                                                    remover_filas_columnas_nulas,\
                                                                    generar_descripcion,\
                                                                    estandarizado_columnas,\
                                                                    procesar_descripcion  
from data_utils.funciones_de_busqueda.busqueda_por_filtro import filtrar_por_laboratorio


# Configurar logging
logging.basicConfig(level=logging.INFO)

# Inicializar FastAPI con lifespan
app = FastAPI(lifespan=lifespan)


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


"""
MODULO DE MASTER PRODUCTO
"""
variables_data.csv_producto = 'df_MasterProductos.csv'
df_Producto = cargar_datos(variables_data.csv_producto)
df_Producto = remover_filas_columnas_nulas(df_Producto)
df_MasterProductos = generar_descripcion(df_Producto,variables_data.name_columna_1_MasterProductos,variables_data.name_columna_2_MasterProductos,variables_data.descripcion_limpia_MasterProductos) 
df_MasterProductos = procesar_descripcion(df_MasterProductos, variables_data.descripcion_limpia_MasterProductos)


""" Modulo Filtar Por LABORATORIO"""
#
#
#

# Servicio PROVEEDOR
df_Proveedor = None
@app.post("/upload-csv-proveedor")

async def upload_csv(file: UploadFile = File(..., media_type='text/csv')):
    global df_Proveedor 
    try:
        contents = await file.read()

        # Cargar archivo
        df_Proveedor = carga_archivo_FastApi(contents, file.filename)

        # Verificar si el DataFrame está vacío
        if df_Proveedor.empty:
            raise ValueError("El archivo CSV está vacío o no contiene datos válidos.")

        # 🔹 Aplicar estandarización de nombres de columnas
        df_Proveedor = estandarizar_nombre_columnas(df_Proveedor)
        logger.info(f"Columnas después de estandarizar: {df_Proveedor.columns.tolist()}")

        # Verificar columnas requeridas
        verificar_columnas_proveedor(df_Proveedor)

        # Reemplazar NaN, inf o -inf por un valor válido (None o 0, según corresponda)
        df_Proveedor.replace([float('inf'), float('-inf'), float('nan')], None, inplace=True)

        #Guardar el archivo csv conl a fecha y hora
        ruta_archivo_guardado = guardar_archivo_con_fecha(df_Proveedor, file.filename)
        logger.info(f"✅ Archivo guardado en: {ruta_archivo_guardado}")
        
        return {
            "filename": file.filename,
            "total_rows": df_Proveedor.shape[0],  
            "columns": df_Proveedor.columns.tolist(),
            "sample_rows": df_Proveedor.head(5).to_dict(orient="records"),
        }

    except ColumnasFaltantesError as e:
        logger.error(f"❌ Error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    
    except Exception as e:
        logger.error(f"❌ Error al procesar el archivo: {e}")
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo CSV: {str(e)}")

@app.get('/upload-csv-proveedor')
async def get_upload_csv_proveedor():
    global df_Proveedor
    if df_Proveedor is None or df_Proveedor.empty:
        return {"Error": "No se encontraron productos para este laboratorio."}
    #Limpiar los dantos antes de devolverlos
    df_Proveedor = limpiar_datos(df_Proveedor)

    return df_Proveedor.head(5).to_dict(orient="records")


#Modulos de Comparacion
@app.put('/upload-csv-proveedor')
async def get_upload_csv_proveedor():
    global df_Proveedor
    if df_Proveedor is None or df_Proveedor.empty:
        return {"Error": "No se encontraron productos para este laboratorio."}
    #Limpiar los dantos antes de devolverlos
    df_Proveedor = limpiar_datos(df_Proveedor)

    return df_Proveedor.head(5).to_dict(orient="records")

#Modulos de Comparacion
@app.delete('/upload-csv-proveedor')
async def get_upload_csv_proveedor():
    global df_Proveedor
    if df_Proveedor is None or df_Proveedor.empty:
        return {"Error": "No se encontraron productos para este laboratorio."}
    #Limpiar los dantos antes de devolverlos
    df_Proveedor = limpiar_datos(df_Proveedor)

    return df_Proveedor.head(5).to_dict(orient="records")


# Función para limpiar los valores no válidos (NaN o inf)
def limpiar_datos(df):
    # Reemplazar NaN o inf con None o 0 (según prefieras)
    df = df.replace([float('inf'), float('-inf')], None)  # Reemplazar inf por None
    df = df.fillna('')  # Opcional: Reemplazar NaN con un valor predeterminado como 'Datos no disponibles'
    return df

# Endpoint para subir archivo CSV Master 
@app.get("/master-productos")
async def ver_master_productos():
    if df_MasterProductos is None or df_MasterProductos.empty:
        raise HTTPException(status_code=404, detail="El DataFrame de productos está vacío o no se cargó correctamente.")
    
    # Limpiar los datos antes de devolverlos
    df_limpio = limpiar_datos(df_MasterProductos)
    
    # Convertir el DataFrame limpio a un formato que pueda ser devuelto como JSON
    return df_limpio.head(5).to_dict(orient="records")



#Endpoint para subir archivo CSV Master
class LabInput (BaseModel):
    laboratorio: str

##Mejorar el rendimiento de la varible global. 
df_MasterProductos_Filtro = None
# POST - Filtra productos por laboratorio
@app.post('/buscar-laboratorio')
async def buscar_laboratorio(data: LabInput):
    global df_MasterProductos_Filtro  # Usamos la variable global para modificarla
    
    laboratorio = data.laboratorio.strip().lower()  # Normalizamos el input

    # Filtrar productos del laboratorio
    df_MasterProductos_Filtro = filtrar_por_laboratorio(df_MasterProductos, laboratorio)
    
    # Verificar si se encontraron productos
    if df_MasterProductos_Filtro is None or df_MasterProductos_Filtro.empty:
        return {"Error": "No se encontraron productos para este laboratorio."}
    
    # Reemplazar valores inf y -inf por NaN
    df_MasterProductos_Filtro.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Reemplazar NaN por una cadena vacía o un valor adecuado para tu caso
    df_MasterProductos_Filtro.fillna("", inplace=True)  # O puedes reemplazar por otro valor como "Desconocido"
    
    # Convertir el DataFrame a un formato JSON
    return df_MasterProductos_Filtro.to_dict(orient="records")

# GET - Obtener productos filtrados o error si no se ha realizado el filtrado
@app.get('/buscar-laboratorio')
async def buscar_laboratorio_get():
    global df_MasterProductos_Filtro  # Usamos la variable global para acceder al DataFrame filtrado
    
    # Verificar si ya se ha realizado un filtrado
    if df_MasterProductos_Filtro is None or df_MasterProductos_Filtro.empty:
        return {"Error": "No se ha realizado un filtrado aún."}
    
    # Convertir el DataFrame filtrado a formato JSON
    return df_MasterProductos_Filtro.to_dict(orient="records")


#Servicio COMPARACION CODIGO PRODUCTO
from data_utils.funciones_de_busqueda.busqueda_por_columna import busqueda_codigo_por_columna

@app.post('/comparacion-codigo-producto')
async def post_comparacion_codigo_producto():
    return {"message": "Comparacion_codigo_producto"}

@app.get('/comparacion-codigo-producto')
async def get_comparacion_codigo_producto():
    global df_MasterProductos_Filtro
    global df_Proveedor
    df_MasterProductos_Filtro_cod_prod = df_MasterProductos_Filtro
    df_Proveedor_cod_prod = df_Proveedor
    df_busqueda_codigo_por_columna = await busqueda_codigo_por_columna(df_MasterProductos_Filtro_cod_prod, 
                                                                 df_Proveedor_cod_prod,
                                                                 variables_data.columna_codigo_producto_master,
                                                                 variables_data.columna_codigo_producto_proveedor)
    
    return df_busqueda_codigo_por_columna.to_dict(orient="records")

#Modulos de Comparacion
@app.put('/comparacion-codigo-producto')
async def put_comparacion_codigo_producto():
    return {"message": "Comparacion_codigo_producto"}

#Modulos de Comparacion
@app.delete('/comparacion-codigo-producto')
async def delet_comparacion_codigo_producto():
    return {"message": "Comparacion_codigo_producto"}
