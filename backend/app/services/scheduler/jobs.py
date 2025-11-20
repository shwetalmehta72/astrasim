from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.core.logging import get_logger
from app.services.ingestion import update_corp_actions, update_index_series, update_ohlcv
from app.services.options.atm_straddle import ingest_atm_straddle
from app.services.options.vol_surface import compute_surface
from app.services.validation.reconciliation import run_validation

logger = get_logger("scheduler.jobs")

OPTIONS_UNIVERSE = ("AAPL", "MSFT", "GOOGL")

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


async def job_refresh_options_atm() -> None:
    logger.info("Refreshing ATM straddles for options universe")
    for symbol in OPTIONS_UNIVERSE:
        try:
            await ingest_atm_straddle(symbol)
        except Exception as exc:  # noqa: BLE001
            logger.exception("ATM refresh failed for %s: %s", symbol, exc)
    logger.info("ATM refresh job complete")


async def job_refresh_options_surface() -> None:
    logger.info("Refreshing vol surfaces for options universe")
    for symbol in OPTIONS_UNIVERSE:
        try:
            await compute_surface(symbol)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Surface refresh failed for %s: %s", symbol, exc)
    logger.info("Surface refresh job complete")

