from __future__ import annotations

import argparse
import asyncio
from datetime import date

from app.core.logging import get_logger
from app.services.ingestion import backfill_ohlcv, update_ohlcv

logger = get_logger("cli.ingestion")


async def _run_backfill(symbol: str, start: str, end: str) -> int:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    return await backfill_ohlcv(symbol, start_date, end_date)


async def _run_update(symbol: str) -> int:
    return await update_ohlcv(symbol)


def main() -> None:
    parser = argparse.ArgumentParser(description="AstraSim OHLCV ingestion runner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backfill_parser = subparsers.add_parser("backfill", help="Run historical backfill")
    backfill_parser.add_argument("symbol", type=str)
    backfill_parser.add_argument("start", type=str, help="Start date (YYYY-MM-DD)")
    backfill_parser.add_argument("end", type=str, help="End date (YYYY-MM-DD)")

    update_parser = subparsers.add_parser("update", help="Run daily incremental ingestion")
    update_parser.add_argument("symbol", type=str)

    args = parser.parse_args()

    try:
        if args.command == "backfill":
            rows = asyncio.run(_run_backfill(args.symbol, args.start, args.end))
        else:
            rows = asyncio.run(_run_update(args.symbol))
        logger.info("Ingestion finished: %s rows", rows)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ingestion failed: %s", exc)
        raise SystemExit(1) from exc
    raise SystemExit(0)


if __name__ == "__main__":
    main()

