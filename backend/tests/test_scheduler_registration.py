from app.core.config import Settings
from app.services.scheduler import scheduler


class FakeScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, func, trigger, id, replace_existing, timezone, **schedule):
        self.jobs.append((id, trigger, schedule))


def test_register_jobs_adds_expected_jobs():
    fake = FakeScheduler()
    settings = Settings(SCHEDULER_ENABLED=True, SCHEDULER_TIMEZONE="UTC")
    scheduler.register_jobs(fake, settings=settings)

    job_ids = {job_id for job_id, _, _ in fake.jobs}
    assert {"update_ohlcv", "update_corp_actions", "update_indexes", "validation_sweep"} <= job_ids

