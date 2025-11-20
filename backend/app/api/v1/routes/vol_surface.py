from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.options.vol_surface import compute_surface, get_recent_surfaces

router = APIRouter(prefix="/options/surface", tags=["options"])


class SurfaceRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    target_date: Optional[date] = None


@router.post("/compute", status_code=status.HTTP_202_ACCEPTED)
async def compute_surface_endpoint(payload: SurfaceRequest) -> dict[str, object]:
    surface = await compute_surface(payload.symbol, payload.target_date)
    return {"status": "ok", "surface": surface}


@router.get("/{symbol}")
async def get_recent_surface(symbol: str, limit: int = Query(5, ge=1, le=20)) -> dict[str, object]:
    surfaces = await get_recent_surfaces(symbol, limit)
    if not surfaces:
        raise HTTPException(status_code=404, detail="No surfaces found")
    return {"symbol": symbol.upper(), "results": surfaces}

