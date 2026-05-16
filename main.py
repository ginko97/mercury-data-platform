# main.py

import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import structlog

# Import our brand new class module
from ingestors.postgres_ingestor import PostgresIngestor

load_dotenv()
log = structlog.get_logger()

def generate_mock_transactions() -> list[tuple]:
    """Generates mock banking transaction tuples matching our DDL requirements."""
    now = datetime.now(timezone.utc)
    
    # Each tuple: (transaction_id, account_id, amount, currency, transaction_date, merchant, payload)
    return [
        (
            "TXN-2026-001", "ACC-7742", 125.50, "USD", now, "Starbucks Coffee",
            json.dumps({"category": "food_beverage", "device": "pos_terminal_04"})
        ),
        (
            "TXN-2026-002", "ACC-1109", 1450.00, "USD", now, "Delta Air Lines",
            json.dumps({"category": "travel", "upgrade_purchased": True})
        ),
        (
            "TXN-2026-003", "ACC-9981", 12.99, "USD", now, "Netflix Digital",
            json.dumps({"category": "entertainment", "billing_cycle": "monthly"})
        )
    ]

def main():
    log.info("starting_pipeline_run", environment="local")
    
    # Initialize the ingestor engine
    ingestor = PostgresIngestor()
    
    # 1. Execute infrastructure connection test
    if not ingestor.test_connection():
        log.critical("pipeline_aborted", reason="infrastructure_unreachable")
        return

    # 2. Extract / Generate raw source data
    mock_batch = generate_mock_transactions()
    log.info("source_records_extracted", count=len(mock_batch))

    # 3. Load records into our Bronze database layer
    inserted_count = ingestor.load_transaction_batch(mock_batch)
    log.info("pipeline_run_success", records_ingested=inserted_count)

    # 4. Read back and verify metrics (New Verification Step)
    metrics = ingestor.get_bronze_metrics()
    log.info("bronze_layer_state", **metrics)    

if __name__ == "__main__":
    main()