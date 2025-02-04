from fastapi import APIRouter, HTTPException
from services.product_services import get_health_status
from schemas.product_schema import HealthCheckSchema

router = APIRouter()

@router.get("/check_db_connection", response_model=HealthCheckSchema)
async def check_db_connection():
    """Endpoint para verificar si la base de datos está conectada."""
    try:
        health_status = await get_health_status()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
