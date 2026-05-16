# main.py

import os
from dotenv import load_dotenv
import structlog

from ingestors.postgres_ingestor import PostgresIngestor
from ingestors.file_ingestor import parse_transaction_csv

load_dotenv()
log = structlog.get_logger()

def main():
    log.info("starting_file_ingestion_pipeline", environment="local")
    
    # Define our raw source target file path
    csv_target = os.path.join("data", "raw", "transactions_v1.csv")
    
    # Initialize the ingestor engine
    ingestor = PostgresIngestor()
    
    # 1. Check if DB is healthy
    if not ingestor.test_connection():
        log.critical("pipeline_aborted", reason="infrastructure_unreachable")
        return

    # 2. Extract: Parse records out of our physical CSV file
    if not os.path.exists(csv_target):
        log.error("pipeline_failed", reason="source_file_not_found", path=csv_target)
        return
        
    extracted_batch = parse_transaction_csv(csv_target)

    # 3. Load: Pump the file contents straight into our Bronze layer table
    if extracted_batch:
        inserted_count = ingestor.load_transaction_batch(extracted_batch)
        log.info("pipeline_run_success", records_ingested=inserted_count)
    else:
        log.warn("pipeline_skipped", reason="no_records_to_process")

if __name__ == "__main__":
    main()