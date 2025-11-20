from __future__ import annotations

import argparse
import asyncio
from datetime import date

from app.core.logging import get_logger
from app.services.options import ingest_atm_straddle

logger = get_logger("cli.options")


async def _run(symbol: str, target_date: date | None) -> None:
    result = await ingest_atm_straddle(symbol, target_date)
    logger.info("ATM straddle ingested: %s", result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ATM straddle for a symbol")
    parser.add_argument("symbol", help="Underlying ticker symbol (e.g., AAPL)")
    parser.add_argument(
        "--target-date",
        dest="target_date",
        help="Target date (YYYY-MM-DD). Defaults to today.",
    )
    args = parser.parse_args()
    parsed_date = date.fromisoformat(args.target_date) if args.target_date else None
    asyncio.run(_run(args.symbol, parsed_date))


if __name__ == "__main__":
    main()

