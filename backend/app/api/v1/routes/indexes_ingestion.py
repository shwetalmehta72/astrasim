from __future__ import annotations

from datetime import date

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.services.ingestion import backfill_index_series, update_index_series

router = APIRouter(prefix="/ingestion/indexes")


class IndexBackfillRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    start: date
    end: date


class IndexUpdateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)


@router.post("/backfill", status_code=status.HTTP_202_ACCEPTED)
async def trigger_index_backfill(payload: IndexBackfillRequest) -> dict[str, str | int]:
    rows = await backfill_index_series(payload.symbol, payload.start, payload.end)
    return {"status": "ok", "rows": rows}


@router.post("/update", status_code=status.HTTP_202_ACCEPTED)
async def trigger_index_update(payload: IndexUpdateRequest) -> dict[str, str | int]:
    rows = await update_index_series(payload.symbol)
    return {"status": "ok", "rows": rows}

