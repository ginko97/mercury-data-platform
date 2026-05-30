# ingestors/postgres_ingestor.py
from __future__ import annotations

import os
import psycopg2
from psycopg2.extras import execute_values
import structlog
from typing import List, Tuple

log = structlog.get_logger()

class PostgresIngestor:
    """
    Manages robust connection handshakes and query executions against the PostgreSQL storage cluster.
    """
    def __init__(self) -> None:
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASS", "postgres")
        self.database = os.getenv("DB_NAME", "postgres")

    def _get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def test_connection(self) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            log.info("database_handshake_success", component="PostgresIngestor", layer="bronze")
            return True
        except Exception as e:
            log.error("database_handshake_failed", component="PostgresIngestor", error=str(e))
            return False

    def load_transaction_batch(self, batch_data: list[tuple]) -> int:
        """Pumps raw file data into the raw Bronze layer."""
        query = """
            INSERT INTO bronze_transactions (
                transaction_id, account_id, amount, currency, transaction_date, merchant, payload
            ) VALUES %s
            ON CONFLICT (transaction_id) DO NOTHING;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, query, batch_data)
                conn.commit()
            log.info("bronze_batch_load_successful", inserted_count=len(batch_data))
            return len(batch_data)
        except Exception as e:
            log.error("bronze_batch_load_failed", error=str(e))
            raise

    # 🆕 NEW METHOD 1: Read raw records from Bronze
    def fetch_bronze_records(self) -> List[Tuple]:
        """Extracts unparsed raw rows from the bronze layer to feed the transformation pipeline."""
        query = """
            SELECT transaction_id, account_id, amount, currency, transaction_date, merchant, payload 
            FROM bronze_transactions;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    records = cur.fetchall()
            log.info("bronze_records_fetched_successfully", count=len(records))
            return records
        except Exception as e:
            log.error("bronze_records_fetch_failed", error=str(e))
            raise

    # 🆕 NEW METHOD 2: Write flattened rows into Silver
    def load_silver_batch(self, silver_data: List[Tuple]) -> int:
        """Pumps cleaned, flattened data records into the structured Silver layer."""
        query = """
            INSERT INTO silver_transactions (
                transaction_id, account_id, amount, currency, transaction_date, merchant, 
                category, status, is_risk_flagged
            ) VALUES %s
            ON CONFLICT (transaction_id) DO UPDATE SET
                status = EXCLUDED.status,
                is_risk_flagged = EXCLUDED.is_risk_flagged,
                transformed_at = CURRENT_TIMESTAMP;
        """
        if not silver_data:
            return 0
            
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, query, silver_data)
                conn.commit()
            log.info("silver_batch_load_successful", inserted_count=len(silver_data))
            return len(silver_data)
        except Exception as e:
            log.error("silver_batch_load_failed", error=str(e))
            raise