CREATE TABLE IF NOT EXISTS backfill_manifest (
    id BIGSERIAL PRIMARY KEY,
    ingestion_type TEXT NOT NULL,
    symbol TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_backfill_manifest_symbol
    ON backfill_manifest (symbol, created_at DESC);

