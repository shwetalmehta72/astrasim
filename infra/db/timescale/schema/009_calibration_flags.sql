CREATE TABLE IF NOT EXISTS calibration_flags (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES securities(id),
    horizon_days INTEGER NOT NULL,
    flag_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    details JSONB,
    snapshot_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingestion_run_id BIGINT REFERENCES ingestion_runs(id)
);

SELECT create_hypertable('calibration_flags', 'snapshot_timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_calibration_flags_symbol_time
    ON calibration_flags (security_id, snapshot_timestamp DESC);

