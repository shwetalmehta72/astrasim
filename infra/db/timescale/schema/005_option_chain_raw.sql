CREATE TABLE IF NOT EXISTS option_chain_raw (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES securities(id),
    option_symbol TEXT NOT NULL,
    strike NUMERIC NOT NULL,
    expiration DATE NOT NULL,
    call_put TEXT NOT NULL,
    bid NUMERIC,
    ask NUMERIC,
    mid NUMERIC,
    volume BIGINT,
    open_interest BIGINT,
    underlying_price NUMERIC,
    raw_payload JSONB,
    snapshot_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chain_raw_sec_exp
    ON option_chain_raw (security_id, expiration);

