from __future__ import annotations

import argparse
import asyncio
from datetime import date

from app.core.logging import get_logger
from app.services.scheduler.backfill import run_backfill

logger = get_logger("cli.backfill")


async def _run(ingestion_type: str, symbols: str, start: str, end: str) -> None:
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    summary = await run_backfill(ingestion_type, symbol_list, date.fromisoformat(start), date.fromisoformat(end))
    logger.info("Backfill completed: %s", summary)
    if summary["failed"]:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run orchestrated backfill job")
    parser.add_argument("ingestion_type", choices=["ohlcv", "corp_actions", "indexes"])
    parser.add_argument("symbols", help="Comma-separated list of symbols")
    parser.add_argument("start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("end", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    try:
        asyncio.run(_run(args.ingestion_type, args.symbols, args.start, args.end))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Backfill failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

