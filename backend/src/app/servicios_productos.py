import asyncpg
from fastapi import FastAPI, HTTPException, UploadFile, File
import logging
import pandas as pd 
from io import BytesIO
import io 



# Función para convertir XLSX a CSV
def convertir_xlsx_a_csv(xlsx_file):
    df = pd.read_excel(xlsx_file, engine='openpyxl')
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Volver al inicio del buffer
    return csv_buffer.getvalue()  # Devuelve el CSV en formato binario


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
