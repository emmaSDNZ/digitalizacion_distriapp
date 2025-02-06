from fastapi import APIRouter
from digitalizacion_distriapp.backend.src.app.servicios.servicios_masterproductos import get_products_service

router = APIRouter()

@router.get("/master-productos")  # Ruta correcta
async def get_products():
    return await get_products_service()  # Asegúrate de llamar al servicio correctamente