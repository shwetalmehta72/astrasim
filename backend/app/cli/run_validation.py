from __future__ import annotations

import argparse
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.services.validation.reconciliation import run_validation

logger = get_logger("cli.validation")


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


async def _run(symbol: str, start: str, end: str) -> int:
    return await run_validation(symbol, _parse_date(start), _parse_date(end))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run validation for a single symbol")
    parser.add_argument("symbol", type=str)
    parser.add_argument("start", type=str, help="Start timestamp (YYYY-MM-DD or ISO8601)")
    parser.add_argument("end", type=str, help="End timestamp (YYYY-MM-DD or ISO8601)")
    args = parser.parse_args()

    try:
        issues = asyncio.run(_run(args.symbol, args.start, args.end))
        logger.info("Validation complete: %s issues logged", issues)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Validation failed: %s", exc)
        raise SystemExit(1) from exc

    raise SystemExit(0)


if __name__ == "__main__":
    main()

