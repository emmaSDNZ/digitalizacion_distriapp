# Configuración de la conexión a la DB
import asyncpg
from contextlib import asynccontextmanager
import logging

DATABASE_URL = "postgresql://postgres:distridb1234@localhost:5432/distridb"


# Configurar logging
logger = logging.getLogger(__name__)

#Manejo de eventos con lifespan
@asynccontextmanager
async def lifespan(app):
    try:
        # Establecer la conexión a la base de datos
        app.state.db_connection = await asyncpg.connect(DATABASE_URL)
        logger.info("✅ Conexión a la base de datos exitosa.")
        yield
    finally:
        await app.state.db_connection.close()
        logger.info("🔴 Conexión a la base de datos cerrada.")