# Manejamos la lógica antes de hacer consultas. 
import pandas as pd
import re
import sys
import os 


from models.product import HealthCheckModel
from db.queries.queries import check_connection

async def get_health_status():
    """Llama a la base de datos y devuelve el estado de la conexión."""
    result = await check_connection()
    return HealthCheckModel(status="connected", result=result)