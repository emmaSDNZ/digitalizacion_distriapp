import pandas as pd
import orjson
import gzip
import io
import json

from pydantic import BaseModel

from fastapi import APIRouter, Response, UploadFile, File, status, HTTPException
from fastapi.responses import JSONResponse

from data_utils.funciones_de_busqueda.busqueda_por_columna import busqueda_codigo_por_columna 

router = APIRouter(
    prefix= "/upload_csv",
    tags=["upload_csv"],)

# Variables globales.
df_MasterProducto = pd.read_csv('df_MasterProductos_xx.csv')
path = 'ABBVIE.csv'
df_upload_csv = pd.read_csv(path,low_memory=False)
nombre_laboratorio_global = "",
df_proveedor = None

async def convert_file_to_csv(file: UploadFile) -> str:
    """
    Convierte un archivo cargado (CSV o XLSX) a una cadena CSV.

    Parámetros:
      - file (UploadFile): Archivo cargado, que debe ser de tipo CSV o XLSX.

    Retorna:
      - str: El contenido del archivo convertido a formato CSV (cadena).

    Lanza:
      - HTTPException: Si el archivo no es CSV o XLSX, o si ocurre algún error en el procesamiento.
    """
    filename = file.filename.lower()
    contents = await file.read()
    
    try:
        if filename.endswith('.csv'):
            # Leer el archivo CSV: se decodifica de bytes a string
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        elif filename.endswith('.xlsx'):
            # Leer el archivo XLSX usando BytesIO
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="El archivo debe ser CSV o XLSX.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {e}")
    
    # Convertir el DataFrame a CSV (cadena) sin incluir el índice
    csv_str = df.to_csv(index=False)
    return csv_str

@router.get('/busqueda_codigo', status_code=status.HTTP_200_OK)
async def get_upload_csv():
    try:
        # Rellenar los valores faltantes
        get_upload_csv = df_upload_csv.fillna("") 
        cod_producto_master = "cod_prod"
        cod_producto_proveedor = "cod_de_producto"
        
        cod_de_barras_master = "codbarra"
        cod_de_barras_proveedor = "cod_de_barra" 
        
        columna_codigo_master = cod_producto_master
        columna_codigo_proveedor = cod_producto_proveedor
        # Verificar si la columna "cod_de_producto" existe en el DataFrame antes de acceder a ella
        if columna_codigo_proveedor not in get_upload_csv.columns:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo cargado debe contener la columna '{columna_codigo_proveedor}'."
            )
        # Si la columna existe, se procede a llamar a la función de búsqueda
        df_original, df_coincidentes, df_no_coincidentes = busqueda_codigo_por_columna(df_MasterProducto, get_upload_csv, columna_codigo_master, columna_codigo_proveedor)

        JSON_response = {
            "df_original": df_original.fillna("").to_dict(orient='records'),
            "df_coincidentes": df_coincidentes.fillna("").to_dict(orient='records'),
            "df_no_coincidentes": df_no_coincidentes.fillna("").to_dict(orient='records')
        }
        return  JSON_response

    except Exception as e:
        # Capturar error y retornar una respuesta de error 
        error_message = f"Error al procesar la solicitud: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": error_message}
        )


@router.get('/', status_code=status.HTTP_200_OK)

async def get_upload_csv():
    try:
        #Rellenar los valores faltantes
        get_upload_csv =  df_upload_csv.fillna("")
        #Compresion del JSON   #Convertir el Df en diccionario de registro
        json_data = orjson.dumps(get_upload_csv.to_dict(orient="records"))
        
        compressed_date = gzip.compress(json_data)
        
        return Response(
            content=compressed_date,
            media_type="application/json",
            headers={"Content-Encoding": "gzip"}  # Indicar que la respuesta está comprimida
        )
    except Exception as e:
        #Capturar error y retornar una  respuesta de error 
        error_message = f"Error al procesar la solicitud: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": error_message}
        )

# Clase NombreLaboratorio
class NombreLaboratorio(BaseModel):
    nombre_Laboratorio: str | None = None  # Tipificación opcional

@router.post('/', )
async def upload_file(file: UploadFile = File(...)):
    global df_proveedor
    """
    Endpoint para cargar un archivo CSV o XLSX.
    
    - Si el archivo es CSV: se lee directamente.
    - Si es XLSX: se lee y se convierte a CSV.
    
    Retorna el contenido en formato json.
    """
    # Utiliza la función modular para convertir el archivo a CSV (cadena)
    csv_str = await convert_file_to_csv(file)
  
    # Opcional: Si deseas transformar el CSV a un objeto Python (por ejemplo, una lista de diccionarios)
    try:
        # Leer el CSV convertido nuevamente con pandas
        df_proveedor = pd.read_csv(io.StringIO(csv_str))
        content = df_proveedor.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al convertir CSV a diccionario: {e}")
    
    # Convertir el objeto a JSON utilizando orjson
    json_data = orjson.dumps(content)
    
    # Retornar la respuesta JSON

    return Response(content=json_data, media_type="application/json")


@router.put('/', status_code=status.HTTP_200_OK)
async def put_upload_csv(response: Response):
    put_upload_csv_servicio = {"message": "METODO PUT: upload_csv"}
    return put_upload_csv_servicio

@router.delete('/', status_code=status.HTTP_200_OK)
async def delete_upload_csv(response: Response):
    delete_upload_csv_servicio = {"message": "METODO DELETED: upload_csv"}
    return delete_upload_csv_servicio

print(df_proveedor)