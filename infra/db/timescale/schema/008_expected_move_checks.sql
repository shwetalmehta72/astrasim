CREATE TABLE IF NOT EXISTS expected_move_checks (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES securities(id),
    horizon_days INTEGER NOT NULL,
    expected_move_abs NUMERIC NOT NULL,
    expected_move_pct NUMERIC NOT NULL,
    surface_expected_move NUMERIC,
    realized_expected_move NUMERIC,
    pct_diff_surface NUMERIC,
    pct_diff_realized NUMERIC,
    severity_surface TEXT,
    severity_realized TEXT,
    snapshot_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingestion_run_id BIGINT REFERENCES ingestion_runs(id),
    raw_payload JSONB
);

SELECT create_hypertable('expected_move_checks', 'snapshot_timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_expected_move_checks_symbol_time
    ON expected_move_checks (security_id, snapshot_timestamp DESC);

