from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.options import get_recent_atm_straddles, ingest_atm_straddle

router = APIRouter(prefix="/options/straddles", tags=["options"])


class IngestRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    target_date: Optional[date] = None


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_straddle(payload: IngestRequest) -> dict[str, object]:
    straddle = await ingest_atm_straddle(payload.symbol, payload.target_date)
    return {"status": "ok", "straddle": straddle}


@router.get("/{symbol}")
async def list_straddles(symbol: str, limit: int = Query(10, ge=1, le=100)) -> dict[str, object]:
    straddles = await get_recent_atm_straddles(symbol, limit=limit)
    if not straddles:
        raise HTTPException(status_code=404, detail="No straddles found")
    return {"symbol": symbol.upper(), "results": straddles}

