CREATE TABLE IF NOT EXISTS vol_surface_points (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT REFERENCES securities(id) NOT NULL,
    expiration DATE NOT NULL,
    dte INTEGER NOT NULL,
    moneyness NUMERIC NOT NULL,
    strike NUMERIC NOT NULL,
    implied_vol NUMERIC NOT NULL,
    snapshot_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingestion_run_id BIGINT REFERENCES ingestion_runs(id),
    raw_payload JSONB
);

SELECT create_hypertable('vol_surface_points', 'snapshot_timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_vol_surface_sec_exp
    ON vol_surface_points (security_id, expiration);

