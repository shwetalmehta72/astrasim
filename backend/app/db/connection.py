from __future__ import annotations

from typing import Optional

import asyncpg

from app.core.config import get_settings

_pool: Optional[asyncpg.Pool] = None


async def connect_to_db() -> None:
    global _pool

    if _pool is not None:
        return

    settings = get_settings()
    _pool = await asyncpg.create_pool(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        command_timeout=60,
        min_size=1,
        max_size=10,
    )


async def close_db_connection() -> None:
    global _pool

    if _pool is None:
        return

    await _pool.close()
    _pool = None


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        await connect_to_db()

    assert _pool is not None  # for mypy
    return _pool

