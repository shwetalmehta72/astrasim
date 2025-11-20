from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.options.expected_move import (
    compute_expected_move,
    get_recent_expected_moves,
)

router = APIRouter(prefix="/options/expected-move", tags=["options"])


class ExpectedMoveRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    horizon: Optional[int] = Field(None, ge=1)
    use_latest: bool = False


@router.post("/compute", status_code=status.HTTP_202_ACCEPTED)
async def compute_expected_move_endpoint(payload: ExpectedMoveRequest, force: bool = Query(False)) -> dict[str, object]:
    result = await compute_expected_move(
        payload.symbol,
        payload.horizon,
        use_latest=payload.use_latest,
        force=force,
    )
    return {"status": "ok", **result}


@router.get("/{symbol}")
async def list_expected_moves(symbol: str, limit: int = Query(10, ge=1, le=50)) -> dict[str, object]:
    results = await get_recent_expected_moves(symbol, limit=limit)
    if not results:
        raise HTTPException(status_code=404, detail="No expected move records found")
    return {"symbol": symbol.upper(), "results": results}

