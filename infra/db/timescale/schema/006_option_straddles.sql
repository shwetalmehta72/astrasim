CREATE TABLE IF NOT EXISTS option_straddles (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES securities(id),
    expiration DATE NOT NULL,
    strike NUMERIC NOT NULL,
    call_mid NUMERIC,
    put_mid NUMERIC,
    straddle_mid NUMERIC,
    implied_vol NUMERIC,
    dte INTEGER NOT NULL,
    snapshot_timestamp TIMESTAMPTZ NOT NULL,
    ingestion_run_id BIGINT REFERENCES ingestion_runs(id),
    raw_call JSONB,
    raw_put JSONB
);

SELECT create_hypertable('option_straddles', 'snapshot_timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_straddles_sec_exp
    ON option_straddles (security_id, expiration);

