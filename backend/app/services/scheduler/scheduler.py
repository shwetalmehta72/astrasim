from __future__ import annotations

from typing import Dict, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.services.scheduler import jobs

logger = get_logger("scheduler")

_scheduler: Optional[AsyncIOScheduler] = None

JOB_DEFINITIONS = {
    "update_ohlcv": jobs.job_update_ohlcv,
    "update_corp_actions": jobs.job_update_corp_actions,
    "update_indexes": jobs.job_update_indexes,
    "validation_sweep": jobs.job_validation_sweep,
    "refresh_options_atm": jobs.job_refresh_options_atm,
    "refresh_options_surface": jobs.job_refresh_options_surface,
}

JOB_SCHEDULES = {
    "update_ohlcv": {"hour": 1, "minute": 0},
    "update_corp_actions": {"hour": 2, "minute": 0},
    "update_indexes": {"hour": 3, "minute": 0},
    "validation_sweep": {"hour": 4, "minute": 0},
    "refresh_options_atm": {"hour": 5, "minute": 0},
    "refresh_options_surface": {"hour": 5, "minute": 30},
}


def register_jobs(scheduler: AsyncIOScheduler, settings: Optional[Settings] = None) -> None:
    settings = settings or get_settings()
    for job_id, func in JOB_DEFINITIONS.items():
        schedule = JOB_SCHEDULES.get(job_id)
        if schedule is None:
            interval = max(settings.JOB_INTERVAL_MINUTES, 1)
            schedule = {"minute": f"*/{interval}"}
        scheduler.add_job(
            func,
            trigger="cron",
            id=job_id,
            replace_existing=True,
            timezone=settings.SCHEDULER_TIMEZONE,
            **schedule,
        )
        logger.info("Registered scheduler job %s", job_id)


async def start_scheduler(settings: Optional[Settings] = None) -> bool:
    settings = settings or get_settings()
    if not settings.SCHEDULER_ENABLED:
        logger.info("Scheduler disabled via settings")
        return False

    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        register_jobs(_scheduler, settings=settings)

    if not _scheduler.running:
        _scheduler.start()
        logger.info("Scheduler started")
    return True


async def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    _scheduler = None


async def run_job_now(job_id: str) -> None:
    func = JOB_DEFINITIONS.get(job_id)
    if not func:
        raise ValueError(f"Unknown job {job_id}")
    logger.info("Manually running job %s", job_id)
    await func()


def get_job_status() -> Dict[str, Dict[str, str]]:
    if _scheduler is None:
        return {}
    status = {}
    for job in _scheduler.get_jobs():
        status[job.id] = {
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
        }
    return status

