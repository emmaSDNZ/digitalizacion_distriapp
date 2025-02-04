import asyncpg
from fastapi import HTTPException

DATABASE_URL = "postgresql://postgres:distridb1234@localhost:5432/distridb"

async def get_db_connection():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {str(e)}")
