import structlog
import psycopg2
import os

from dotenv import load_dotenv

load_dotenv()

# Access them using os.getenv
CONNECTION_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)), # Convert port to int
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
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