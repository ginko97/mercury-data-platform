-- scripts/init_silver.sql

CREATE TABLE IF NOT EXISTS silver_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    transaction_date TIMESTAMPTZ NOT NULL,
    merchant VARCHAR(100) NOT NULL,
    
    -- Flattened Fields (Extracted from the raw text payload string)
    category VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    is_risk_flagged BOOLEAN DEFAULT FALSE,
    
    -- Audit Metadata Tracking Window
    transformed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Optimize downstream filtering performance for our analysts
CREATE INDEX IF NOT EXISTS idx_silver_account_id ON silver_transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_silver_transaction_date ON silver_transactions(transaction_date);