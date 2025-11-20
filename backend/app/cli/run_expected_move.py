from __future__ import annotations

import argparse
import asyncio

from app.core.logging import get_logger
from app.services.options.expected_move import compute_expected_move

logger = get_logger("cli.options.expected_move")


async def _run(symbol: str, horizon: int | None, use_latest: bool, force: bool) -> None:
    result = await compute_expected_move(symbol, horizon, use_latest=use_latest, force=force)
    logger.info(
        "Expected move computed: horizon=%s abs=%.4f pct=%.4f",
        result["horizon"],
        result["expected_move_abs"],
        result["expected_move_pct"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute expected move diagnostics")
    parser.add_argument("symbol", help="Underlying ticker symbol (e.g., AAPL)")
    parser.add_argument(
        "horizon",
        nargs="?",
        type=int,
        help="Horizon in days (required unless --latest specified)",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the most recent ATM straddle horizon",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass cache and refresh guardrails",
    )
    args = parser.parse_args()
    if not args.latest and args.horizon is None:
        parser.error("horizon is required unless --latest is provided")
    asyncio.run(_run(args.symbol, args.horizon, args.latest, args.force))


if __name__ == "__main__":
    main()

