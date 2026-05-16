-- scripts/init_bronze.sql

CREATE TABLE IF NOT EXISTS bronze_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    account_id VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    merchant VARCHAR(100) NOT NULL,
    payload JSONB, -- Storing the raw JSON payload for flexibility
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Creating an index on transaction_date as we will query/filter by time slices later.
CREATE INDEX IF NOT EXISTS idx_bronze_tx_date ON bronze_transactions(transaction_date);