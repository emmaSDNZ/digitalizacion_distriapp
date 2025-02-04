from db.connected_to_db import get_db_connection
from asyncpg import PostgresError

async def check_connection():
    try:
        """Ejecuta la consulta para verificar la conexión a la base de datos."""
        conn = await get_db_connection()
        result = await conn.fetch("SELECT 1 AS test")
        await conn.close()
        return result
    except PostgresError as e:
        raise PostgresError(f"Error de conexión a la base de datos: {str(e)}")
