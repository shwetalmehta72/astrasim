# TimescaleDB Schema — AstraSim Phase 1

This directory contains the authoritative SQL definitions for AstraSim’s Phase 1 data layer. The schema is applied automatically when the TimescaleDB container boots via `docker-entrypoint-initdb.d`.

## Folder Structure

```
infra/db/timescale/
├── README.md                 # This file
└── schema/
    ├── 001_base_schema.sql   # Core extension + securities + OHLCV + corp actions
    └── 002_ingestion_logging.sql # Ingestion runs + error tracking tables
```

Additional migrations should continue the numeric prefix convention (`003_options.sql`, etc.) to ensure deterministic execution order.

## Applying the Schema

1. Ensure Docker Desktop is running.
2. From the repo root: `cd infra && docker compose up timescaledb`.
3. The Timescale container automatically executes all `schema/*.sql` files on first boot.

You can inspect the database via:

```powershell
docker exec -it astrasim-timescaledb psql -U astrasim -d astrasim
```

## Extension & Hypertables

- `001_base_schema.sql`:
  - Enables the `timescaledb` extension.
  - Defines `securities`, `ohlcv_bars` (hypertable on `time` partitioned by `security_id`), and `corporate_actions`.
  - Adds constraints and indexes for symbol lookup, uniqueness, and time-series queries.
- `002_ingestion_logging.sql`:
  - Adds `ingestion_runs` and `ingestion_errors` for tracking ETL executions.

## Future Work

- Options & implied vol schema (`003_options_schema.sql`).
- Regime/event/factor storage.
- Migration/versioning strategy beyond init scripts (e.g., Sqitch or Alembic-managed SQL).

Track follow-up tasks in `docs/meta/TASK_BACKLOG.md` before adding new files.

