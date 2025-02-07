import pandas as pd
import orjson
import gzip

from pydantic import BaseModel

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from data_utils.funciones_de_busqueda.busqueda_por_filtro import filtrar_por_laboratorio


router = APIRouter(
    prefix= "/master_productos",
    tags=["Master Productos"],)

# Variables globales.
path = 'df_MasterProductos_xx.csv'
df_Master_Prductos = pd.read_csv(path,low_memory=False)
nombre_laboratorio_global = "",


@router.get('/', status_code=status.HTTP_200_OK)
async def get_master_productos():
    try:
        #Rellenar los valores faltantes
        get_master_productos_servicio =  df_Master_Prductos.fillna("")
        
        #Convertir el Df en diccionario de registro
        json_data = orjson.dumps(get_master_productos_servicio.to_dict(orient="records"))
        
        #Compresion del JSON
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

@router.get('/master_productos_filtro', status_code=status.HTTP_200_OK)
async def get_master_productos_filtro():
    global nombre_laboratorio_global
    global df_Master_Prductos
    try:
                #Rellenar los valores faltantes
        get_master_productos_filtro =  filtrar_por_laboratorio(df_Master_Prductos, nombre_laboratorio_global)

        if get_master_productos_filtro is None: return {"message" : f"No se encontraron productos del laboratorio '{nombre_laboratorio_global.upper()}'."}
        else:
        #Convertir el Df en diccionario de registro
            json_data = orjson.dumps(get_master_productos_filtro.to_dict(orient="records"))
        
        #Compresion del JSON
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

@router.post('/', status_code=status.HTTP_200_OK)
async def post_master_productos_filtro(nombre_Laboratorio: NombreLaboratorio):
    global nombre_laboratorio_global
    try:
        nombre_laboratorio_global = nombre_Laboratorio.nombre_Laboratorio.lower()
        post_master_productos_filtro_servicio = nombre_Laboratorio
        return post_master_productos_filtro_servicio
    except Exception as e:
        #Capturar error y retornar una  respuesta de error 
        error_message = f"Error al procesar la solicitud: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_500s_INTERNAL_SERVER_ERROR,
            content={"message": error_message}
        )


@router.put('/', status_code=status.HTTP_200_OK)
async def put_master_productos(response: Response):
    put_master_productos_servicio = {"message": "METODO PUT: master-productos"}
    return put_master_productos_servicio

@router.delete('/', status_code=status.HTTP_200_OK)
async def delete_master_productos(response: Response):
    delete_master_productos_servicio = {"message": "METODO DELETED: master-productos"}
    return delete_master_productos_servicio

