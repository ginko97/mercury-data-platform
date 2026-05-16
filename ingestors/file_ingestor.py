# ingestors/file_ingestor.py

import csv
import structlog
from datetime import datetime

log = structlog.get_logger()

def parse_transaction_csv(file_path: str) -> list[tuple]:
    """
    Reads a raw transaction CSV file and parses rows into typed tuples 
    compatible with the PostgresIngestor bulk insertion layout.
    """
    parsed_records = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert the transaction_date string back into a proper python datetime object
                dt = datetime.fromisoformat(row['transaction_date'].replace('Z', '+00:00'))
                
                record = (
                    row['transaction_id'],
                    row['account_id'],
                    float(row['amount']),
                    row['currency'],
                    dt,
                    row['merchant'],
                    row['payload']  # Already a valid JSON string from the CSV
                )
                parsed_records.append(record)
                
        log.info("csv_file_parsed_successfully", file_path=file_path, records_found=len(parsed_records))
        return parsed_records
    except Exception as e:
        log.error("csv_file_parsing_failed", file_path=file_path, error=str(e))
        raise e