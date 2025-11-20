from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.ingestion import backfill_ohlcv, update_ohlcv

router = APIRouter(prefix="/ingestion/ohlcv")


class BackfillRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    start: date
    end: date


class UpdateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)


@router.post("/backfill", status_code=status.HTTP_202_ACCEPTED)
async def trigger_backfill(payload: BackfillRequest) -> dict[str, int | str]:
    rows = await backfill_ohlcv(payload.symbol, payload.start, payload.end)
    return {"status": "ok", "rows": rows}


@router.post("/update", status_code=status.HTTP_202_ACCEPTED)
async def trigger_update(payload: UpdateRequest) -> dict[str, int | str]:
    rows = await update_ohlcv(payload.symbol)
    return {"status": "ok", "rows": rows}

