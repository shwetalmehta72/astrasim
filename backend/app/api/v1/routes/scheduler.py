from __future__ import annotations

from datetime import date, datetime
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.scheduler import get_job_status, run_job_now, start_scheduler
from app.services.scheduler.backfill import run_backfill

router = APIRouter(prefix="/scheduler")


class BackfillRequest(BaseModel):
    ingestion_type: str = Field(..., pattern="^(ohlcv|corp_actions|indexes)$")
    symbols: List[str] = Field(..., min_items=1)
    start: date
    end: date


class RunJobResponse(BaseModel):
    status: str


@router.post("/backfill", status_code=status.HTTP_202_ACCEPTED)
async def trigger_backfill(payload: BackfillRequest) -> dict[str, int | List[int] | str]:
    summary = await run_backfill(payload.ingestion_type, payload.symbols, payload.start, payload.end)
    return {"status": "ok", **summary}


@router.post("/run/{job_id}", response_model=RunJobResponse)
async def run_scheduler_job(job_id: str) -> RunJobResponse:
    try:
        await run_job_now(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunJobResponse(status="ok")


@router.get("/status")
async def scheduler_status() -> dict[str, dict[str, str | None]]:
    await start_scheduler()
    return get_job_status()

