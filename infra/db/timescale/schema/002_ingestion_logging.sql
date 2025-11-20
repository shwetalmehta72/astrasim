-- 002_ingestion_logging.sql
-- ETL tracking tables for AstraSim Phase 1.

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    target_table TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('success', 'failed', 'partial', 'running')),
    rows_inserted BIGINT NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_source_started
    ON ingestion_runs (source, started_at DESC);

CREATE TABLE IF NOT EXISTS ingestion_errors (
    id BIGSERIAL PRIMARY KEY,
    ingestion_run_id BIGINT NOT NULL REFERENCES ingestion_runs (id) ON DELETE CASCADE,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    context TEXT,
    payload JSONB,
    message TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ingestion_errors_run
    ON ingestion_errors (ingestion_run_id, occurred_at DESC);

COMMENT ON TABLE ingestion_runs IS 'Tracks ETL executions for OHLCV, corporate actions, etc.';
COMMENT ON TABLE ingestion_errors IS 'Detailed error payloads linked to ingestion runs.';

