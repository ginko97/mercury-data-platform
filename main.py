# main.py

import os
from dotenv import load_dotenv
import structlog

from ingestors.postgres_ingestor import PostgresIngestor
from ingestors.file_ingestor import parse_transaction_csv
from transformers.transaction_transformer import TransactionTransformer  # 🆕 Import our new transformer

load_dotenv()
log = structlog.get_logger()

def main():
    log.info("starting_data_platform_pipeline_run", environment="local")
    
    # Initialize our infrastructure engines
    ingestor = PostgresIngestor()
    transformer = TransactionTransformer()
    
    # Test database connectivity boundary
    if not ingestor.test_connection():
        log.critical("pipeline_aborted", reason="infrastructure_unreachable")
        return

    # ==============================================================================
    # PHASE 1: BRONZE LAYER (Extract from CSV -> Load raw to DB)
    # ==============================================================================
    platform_home = os.getenv("PLATFORM_HOME", "")
    csv_target = os.path.join(platform_home, "data", "raw", "transactions_v1.csv")
    
    if os.path.exists(csv_target):
        log.info("executing_bronze_ingestion_phase")
        extracted_batch = parse_transaction_csv(csv_target)
        if extracted_batch:
            ingestor.load_transaction_batch(extracted_batch)
    else:
        log.warn("bronze_source_skipped", reason="file_not_found", path=csv_target)

    # ==============================================================================
    # 🆕 PHASE 2: SILVER LAYER (Read raw DB -> Clean & Flatten -> Load silver to DB)
    # ==============================================================================
    log.info("executing_silver_transformation_phase")
    
    # 1. Read raw rows directly out of the database Bronze table
    raw_bronze_data = ingestor.fetch_bronze_records()
    
    if raw_bronze_data:
        # 2. Run data through our cleaning and unpacking rule-engine
        cleaned_silver_data = transformer.clean_and_flatten(raw_bronze_data)
        
        # 3. Load structured rows into the target Silver table
        inserted_silver_count = ingestor.load_silver_batch(cleaned_silver_data)
        log.info("silver_pipeline_run_success", records_processed=inserted_silver_count)
    else:
        log.warn("silver_pipeline_skipped", reason="no_bronze_records_found")

if __name__ == "__main__":
    main()