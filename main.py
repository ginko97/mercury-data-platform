import structlog
import psycopg2

# Global Configuration
CONNECTION_PARAMS = {
    "host": "localhost",
    "port": 5434, # Mapped in docker-compose
    "database": "banking_db",
    "user": "ginko",
    "password": "password123"
}

log = structlog.get_logger()

def test_db_connection():
    try:
        # Unpacking the global dict
        conn = psycopg2.connect(**CONNECTION_PARAMS) 
        log.info("database_connection_success", status="handshake_complete")
        conn.close()
    except Exception as e:
        log.error("database_connection_failed", error=str(e))

def main():
    test_db_connection()

if __name__ == "__main__":
    main()