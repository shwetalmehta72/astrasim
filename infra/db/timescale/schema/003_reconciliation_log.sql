CREATE TABLE IF NOT EXISTS reconciliation_log (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES securities(id),
    issue_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    details JSONB,
    issue_timestamp TIMESTAMPTZ NOT NULL,
    ingestion_run_id BIGINT REFERENCES ingestion_runs(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recon_security_time
    ON reconciliation_log (security_id, issue_timestamp DESC);

