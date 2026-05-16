# ingestors/postgres_ingestor.py

import os
import psycopg2
from psycopg2.extras import execute_values
import structlog

log = structlog.get_logger()

class PostgresIngestor:
    def __init__(self):
        """Initialize connection parameters using environment variables."""
        self.connection_params = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS")
        }

    def _get_connection(self):
        """Private helper to establish a fresh database connection handle."""
        return psycopg2.connect(**self.connection_params)

    def test_connection(self) -> bool:
        """Verifies if the platform can successfully execute a handshake."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            log.info("database_handshake_success", layer="bronze", component="PostgresIngestor")
            return True
        except Exception as e:
            log.error("database_handshake_failed", error=str(e), component="PostgresIngestor")
            return False

    def load_transaction_batch(self, batch_data: list[tuple]) -> int:
        """
        Executes a high-throughput batch insert into the bronze_transactions table.
        Uses execute_values for performance optimization.
        """
        query = """
            INSERT INTO bronze_transactions (
                transaction_id, account_id, amount, currency, transaction_date, merchant, payload
            ) VALUES %s
            ON CONFLICT (transaction_id) DO NOTHING;
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # execute_values is significantly faster than looping over execute()
                    execute_values(cur, query, batch_data)
                conn.commit()
            
            log.info("batch_load_completed", record_count=len(batch_data), layer="bronze")
            return len(batch_data)
        except Exception as e:
            log.error("batch_load_failed", error=str(e), layer="bronze")
            raise

    def get_bronze_metrics(self) -> dict:
            """Retrieves high-level metrics from the bronze layer to verify ingestion state."""
            query = """
                SELECT 
                    COUNT(*) as total_count, 
                    SUM(amount) as total_volume 
                FROM bronze_transactions;
            """
            try:
                with self._get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query)
                        result = cur.fetchone()
                return {
                    "total_records": result[0],
                    "total_volume": float(result[1]) if result[1] else 0.0
                }
            except Exception as e:
                log.error("metrics_retrieval_failed", error=str(e), layer="bronze")
                return {}