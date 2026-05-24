# ingestors/file_ingestor.py
from __future__ import annotations

import csv
from datetime import datetime
import os
import structlog
# Import explicit collection structures for complete Python 3.8 backward safety
from typing import List, Tuple, Dict, Any

log = structlog.get_logger()

# FIX: Modified type hint signatures to use List and Tuple wrappers
def parse_transaction_csv(file_path: str) -> List[Tuple]:
    """
    Extracts raw banking transactions from a local CSV text stream.
    Applies baseline timestamp parsing and returns structured records.
    """
    if not os.path.exists(file_path):
        log.error("source_file_missing", path=file_path)
        raise FileNotFoundError(f"Target ingestion file not found: {file_path}")

    parsed_records = []
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map and serialize raw text data fields into formatted database rows
                record = (
                    row['transaction_id'],
                    row['account_id'],
                    float(row['amount']),
                    row['currency'],
                    datetime.fromisoformat(row['transaction_date'].replace('Z', '+00:00')),
                    row['merchant'],
                    row['payload']  # Kept as raw string for JSON/Text storage
                )
                parsed_records.append(record)
                
        log.info("csv_parsing_successful", record_count=len(parsed_records), path=file_path)
        return parsed_records
        
    except Exception as e:
        log.error("csv_parsing_failed", error=str(e), path=file_path)
        raise