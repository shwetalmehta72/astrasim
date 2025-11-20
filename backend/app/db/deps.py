from __future__ import annotations

from collections.abc import AsyncGenerator

import asyncpg

from app.db.connection import get_pool


async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection

