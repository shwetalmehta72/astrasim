from __future__ import annotations

import argparse
import asyncio
from datetime import date

from app.core.logging import get_logger
from app.services.options.vol_surface import compute_surface

logger = get_logger("cli.options.surface")


async def _run(symbol: str, target_date: date | None) -> None:
    surface = await compute_surface(symbol, target_date)
    logger.info(
        "Vol surface computed: dte=%s moneyness=%s",
        surface.get("dte"),
        surface.get("moneyness"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute options vol surface for a symbol")
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

