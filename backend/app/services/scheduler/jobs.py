from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.core.logging import get_logger
from app.services.ingestion import update_corp_actions, update_index_series, update_ohlcv
from app.services.validation.reconciliation import run_validation

logger = get_logger("scheduler.jobs")


async def job_update_ohlcv() -> None:
    logger.info("Starting OHLCV daily update")
    for symbol in ("AAPL", "MSFT", "GOOGL"):
        await update_ohlcv(symbol)
    logger.info("Completed OHLCV daily update")


async def job_update_corp_actions() -> None:
    logger.info("Starting corporate actions daily update")
    for symbol in ("AAPL", "MSFT", "GOOGL"):
        await update_corp_actions(symbol)
    logger.info("Completed corporate actions daily update")


async def job_update_indexes() -> None:
    logger.info("Starting index/macro daily update")
    for symbol in ("SPX", "NDX", "VIX", "TNX", "SPY", "QQQ"):
        await update_index_series(symbol)
    logger.info("Completed index/macro daily update")


async def job_validation_sweep() -> None:
    logger.info("Starting validation sweep")
    today = date.today()
    await run_validation("SPY", datetime.combine(today - timedelta(days=30), datetime.min.time(), tzinfo=timezone.utc), datetime.now(tz=timezone.utc))
    logger.info("Completed validation sweep")

