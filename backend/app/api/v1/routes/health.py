import asyncpg
from fastapi import APIRouter, Depends, status

from app.db.deps import get_db_connection

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/db", status_code=status.HTTP_200_OK)
async def database_health(connection: asyncpg.Connection = Depends(get_db_connection)) -> dict[str, str]:
    await connection.execute("SELECT 1;")
    return {"status": "ok"}

