# transformers/transaction_transformer.py
from __future__ import annotations
import json
import structlog
from typing import List, Tuple, Dict, Any

log = structlog.get_logger()

class TransactionTransformer:
    """
    Applies transformation logic to migrate records from Bronze (Raw) to Silver (Cleaned).
    Parses string-encoded payloads and applies data risk classification metrics.
    """
    def __init__(self) -> None:
        pass

    def clean_and_flatten(self, raw_bronze_records: List[Tuple]) -> List[Tuple]:
        """
        Processes raw records and returns flattened, conformed tuples ready for Silver storage.
        """
        transformed_collection = []

        for record in raw_bronze_records:
            try:
                tx_id, account_id, amount, currency, tx_date, merchant, raw_payload = record
                
                if not raw_payload:
                    log.warn("empty_payload_skipping_record", transaction_id=tx_id)
                    continue

                # FIX: Handle case where database engine has already unpacked the object into a dict
                if isinstance(raw_payload, dict):
                    payload_dict = raw_payload
                else:
                    # Fallback to string loader if it arrived as a raw string block
                    payload_dict = json.loads(raw_payload)
                
                # Extract and conform attributes with explicit fallback defaults
                category = payload_dict.get("category", "Unassigned").strip()
                status = payload_dict.get("status", "PENDING").upper()
                
                # Apply automated risk rule engine logic
                is_risk_flagged = False
                if float(amount) > 800.00 or status == "SUSPICIOUS":
                    is_risk_flagged = True
                    log.warn("risk_threshold_breached", transaction_id=tx_id, amount=amount)

                # Map attributes directly into the conformed Silver DDL layout
                silver_record = (
                    tx_id,
                    account_id,
                    float(amount),
                    currency,
                    tx_date,
                    merchant,
                    category,
                    status,
                    is_risk_flagged
                )
                transformed_collection.append(silver_record)

            except Exception as e:
                log.error("record_transformation_failed", transaction_id=record[0], error=str(e))
                continue

        log.info("batch_transformation_completed", output_count=len(transformed_collection))
        return transformed_collection