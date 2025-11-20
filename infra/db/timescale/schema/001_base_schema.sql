-- 001_base_schema.sql
-- Core AstraSim Phase 1 schema: instruments, OHLCV hypertable, corporate actions.

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS securities (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT,
    type TEXT NOT NULL CHECK (type IN ('stock', 'etf', 'index')),
    exchange TEXT,
    currency TEXT NOT NULL DEFAULT 'USD',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (symbol, type)
);

CREATE INDEX IF NOT EXISTS idx_securities_symbol ON securities (symbol);

CREATE TABLE IF NOT EXISTS ohlcv_bars (
    time TIMESTAMPTZ NOT NULL,
    security_id BIGINT NOT NULL REFERENCES securities (id) ON DELETE CASCADE,
    interval TEXT NOT NULL,
    open NUMERIC(20, 8) NOT NULL,
    high NUMERIC(20, 8) NOT NULL,
    low NUMERIC(20, 8) NOT NULL,
    close NUMERIC(20, 8) NOT NULL,
    volume NUMERIC(28, 4) NOT NULL,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (security_id, time, interval)
);

SELECT create_hypertable('ohlcv_bars', 'time', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_ohlcv_bars_security_time ON ohlcv_bars (security_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_bars_interval_time ON ohlcv_bars (interval, time DESC);

CREATE TABLE IF NOT EXISTS corporate_actions (
    id BIGSERIAL PRIMARY KEY,
    security_id BIGINT NOT NULL REFERENCES securities (id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    ex_date DATE NOT NULL,
    record_date DATE,
    pay_date DATE,
    amount NUMERIC(20, 8),
    split_ratio NUMERIC(12, 6),
    raw_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_corporate_actions_security_exdate
    ON corporate_actions (security_id, ex_date);

COMMENT ON TABLE securities IS 'Universe of tradable instruments used throughout AstraSim.';
COMMENT ON TABLE ohlcv_bars IS 'Timescale hypertable storing OHLCV data for stocks and indices.';
COMMENT ON TABLE corporate_actions IS 'Corporate action records (splits, dividends, mergers).';

