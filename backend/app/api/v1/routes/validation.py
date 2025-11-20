from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.services.validation.reconciliation import run_reconciliation, run_validation

router = APIRouter(prefix="/validation")


class ValidationRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=16)
    start: datetime
    end: datetime


class ReconciliationRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=2)
    start: datetime
    end: datetime


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_symbol_validation(payload: ValidationRequest) -> dict[str, int | str]:
    issues = await run_validation(payload.symbol, payload.start, payload.end)
    return {"status": "ok", "issues_logged": issues}


@router.post("/reconcile", status_code=status.HTTP_202_ACCEPTED)
async def run_symbols_reconciliation(payload: ReconciliationRequest) -> dict[str, int | str]:
    issues = await run_reconciliation(payload.symbols, payload.start, payload.end)
    return {"status": "ok", "issues_logged": issues}

