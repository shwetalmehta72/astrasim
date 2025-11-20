from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from typing import List

from app.core.logging import get_logger
from app.services.validation.reconciliation import run_reconciliation

logger = get_logger("cli.reconciliation")


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


async def _run(symbols: List[str], start: str, end: str) -> int:
    return await run_reconciliation(symbols, _parse_date(start), _parse_date(end))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reconciliation across symbols")
    parser.add_argument("symbols", nargs="+", help="List of symbols (at least two)")
    parser.add_argument("--start", required=True, help="Start timestamp (YYYY-MM-DD or ISO8601)")
    parser.add_argument("--end", required=True, help="End timestamp (YYYY-MM-DD or ISO8601)")
    args = parser.parse_args()

    try:
        issues = asyncio.run(_run(args.symbols, args.start, args.end))
        logger.info("Reconciliation complete: %s issues logged", issues)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Reconciliation failed: %s", exc)
        raise SystemExit(1) from exc

    raise SystemExit(0)


if __name__ == "__main__":
    main()

