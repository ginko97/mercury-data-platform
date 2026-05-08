import structlog
import os

# Configure Production-Grade Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer() 
    ]
)
logger = structlog.get_logger()

def main():
    # Use the port from your docker-compose.yml
    db_port = os.getenv("DB_PORT", "5434")
    
    logger.info("platform_startup", 
                version="0.1.0", 
                db_port=db_port,
                env="local")
    
    print("Hello from mercury-data-platform!")

if __name__ == "__main__":
    main()