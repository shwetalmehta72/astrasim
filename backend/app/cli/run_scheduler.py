from __future__ import annotations

import asyncio

from app.core.logging import get_logger
from app.services.scheduler import start_scheduler, stop_scheduler

logger = get_logger("cli.scheduler")


async def _run() -> None:
    started = await start_scheduler()
    if not started:
        logger.info("Scheduler is disabled; exiting")
        return
    logger.info("Scheduler running. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Stopping scheduler...")
        await stop_scheduler()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()

