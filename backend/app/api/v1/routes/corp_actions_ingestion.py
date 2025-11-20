from __future__ import annotations

from datetime import date

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.services.ingestion import backfill_corp_actions, update_corp_actions

router = APIRouter(prefix="/ingestion/corp-actions")


class CorpActionsBackfillRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    start: date
    end: date


class CorpActionsUpdateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)


@router.post("/backfill", status_code=status.HTTP_202_ACCEPTED)
async def trigger_corp_actions_backfill(payload: CorpActionsBackfillRequest) -> dict[str, str | int]:
    rows = await backfill_corp_actions(payload.symbol, payload.start, payload.end)
    return {"status": "ok", "rows": rows}


@router.post("/update", status_code=status.HTTP_202_ACCEPTED)
async def trigger_corp_actions_update(payload: CorpActionsUpdateRequest) -> dict[str, str | int]:
    rows = await update_corp_actions(payload.symbol)
    return {"status": "ok", "rows": rows}

