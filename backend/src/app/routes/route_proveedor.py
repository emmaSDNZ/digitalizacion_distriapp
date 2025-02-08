import pandas as pd
import orjson
import gzip
import io
import json

from pydantic import BaseModel

from fastapi import APIRouter, Response, UploadFile, File, status, HTTPException
from fastapi.responses import JSONResponse

from data_utils.funciones_de_busqueda.busqueda_por_filtro import filtrar_por_laboratorio
from data_utils.funciones_de_busqueda.busqueda_por_columna import busqueda_codigo_por_columna 
from data_utils.manipulacion_de_datos.maniuplacion_de_datos import convert_file_to_csv



router = APIRouter(
    prefix= "/upload_csv",
    tags=["upload_csv"],)

# Variables globales.
df_MasterProducto = pd.read_csv('df_MasterProductos_xx.csv')
path = 'ABBVIE.csv'
df_upload_csv = pd.read_csv(path,low_memory=False)

cache = {}

@router.get('/master_productos_filtro/{nombre_laboratorio}', status_code=status.HTTP_200_OK)
async def get_master_productos_filtro(nombre_laboratorio: str):  # Parámetro directamente como str
    try:
        if not nombre_laboratorio:
            raise ValueError("El nombre del laboratorio es obligatorio.")
        
        nombre_laboratorio = nombre_laboratorio.lower()
        get_master_productos_filtro = filtrar_por_laboratorio(df_MasterProducto, nombre_laboratorio)

        if get_master_productos_filtro is None or get_master_productos_filtro.empty:
            return {"message": f"No se encontraron productos del laboratorio '{nombre_laboratorio.upper()}'."}
        
        # Almacenar el resultado en el cache
        cache[nombre_laboratorio] = get_master_productos_filtro
 
        # Convertir el DataFrame a JSON
        json_data = orjson.dumps(get_master_productos_filtro.to_dict(orient="records"))
        
        return Response(
            content=json_data,
            media_type="application/json"
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e)}
        )
    except Exception as e:
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

@router.get('/busqueda_codigo', status_code=status.HTTP_200_OK)
async def get_upload_csv():
    try:
        # Rellenar los valores faltantes en el DataFrame cargado
        get_upload_csv = df_upload_csv.fillna("")
        
        # Definición de las columnas a verificar
        cod_producto_master = "cod_prod"
        cod_producto_proveedor = "cod_de_producto"
        cod_de_barras_master = "codbarra"
        cod_de_barras_proveedor = "cod_de_barra"
        
        # Verificar si la columna cod_producto_proveedor existe
        if cod_producto_proveedor not in get_upload_csv.columns:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo cargado debe contener la columna '{cod_producto_proveedor}'."
            )
        
        # Si la columna existe, ejecutar la búsqueda por código de producto
        df_original, df_coincidentes_cod_prod, df_no_coincidentes_cod_prod = busqueda_codigo_por_columna(
            df_MasterProducto, get_upload_csv, cod_producto_master, cod_producto_proveedor
        )

        # Verificar si la columna cod_de_barras_proveedor existe
        if cod_de_barras_proveedor not in get_upload_csv.columns:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo cargado debe contener la columna '{cod_de_barras_proveedor}'."
            )
        
        # Si la columna existe, ejecutar la búsqueda por código de barras
        df_original, df_coincidentes_cod_barras, df_no_coincidentes_cod_barras = busqueda_codigo_por_columna(
            df_MasterProducto, get_upload_csv, cod_de_barras_master, cod_de_barras_proveedor
        )
    
        #Funsion de valores 
        columna_niprod = "niprod"
        df_original[columna_niprod] = (df_original[columna_niprod]
                                       .combine_first(df_coincidentes_cod_prod[columna_niprod])
                                       .combine_first(df_coincidentes_cod_barras[columna_niprod]))
        
        # Construcción de la respuesta JSON con todos los DataFrames
        JSON_response = {
            "df_original": df_original.fillna("").to_dict(orient='records'),
            "df_coincidentes_cod_PRODUCTO": df_coincidentes_cod_prod.fillna("").to_dict(orient='records'),
            "df_no_coincidentes_cod_PRODUCTO": df_no_coincidentes_cod_prod.fillna("").to_dict(orient='records'),
            "df_coincidentes_cod_BARRAS": df_coincidentes_cod_barras.fillna("").to_dict(orient='records'),
            "df_no_coincidentes_cod_BARRAS": df_no_coincidentes_cod_barras.fillna("").to_dict(orient='records')
        }
        return JSON_response

    except Exception as e:
        # Capturar error y retornar una respuesta de error
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

