# Mercury Data Platform

A production-grade data engineering platform for banking transaction ingestion, built with Python 3.13, Docker, and Airflow.

## ## 1. Prerequisites
* **Python**: 3.13+
* **Package Manager**: [uv](https://docs.astral.sh/uv/)
* **Containerization**: Docker and Docker Compose

## ## 2. Setup

### Step 1: Environment Configuration
Create a `.env` file in the root directory and add the following (matching your `.gitignore` rules):
```env
DB_HOST=localhost
DB_PORT=5434
DB_NAME=banking_db
DB_USER=your_user
DB_PASS=your_password
```

## Data Platform Architecture

The following diagram illustrates our automated multi-service batch ingestion architecture running across container and host filesystem boundaries:

```mermaid
graph TD
    subgraph Host_Machine [Host System]
        Local_CSV[data/raw/transactions_v1.csv]
        Local_Env[.env Configuration]
    end

    subgraph Docker_Compose_Network [Docker Bridge Network]
        subgraph Airflow_Services [Orchestration Layer]
            Scheduler[mercury-airflow-scheduler]
            Webserver[mercury-airflow-webserver]
        end

        subgraph Core_Execution [Pipeline Runtime Context]
            DAG_Workflow[mercury_bronze_ingestion DAG]
            Main_Script[main.py Entrypoint]
            File_Ingestor[ingestors/file_ingestor.py]
            Postgres_Ingestor[ingestors/postgres_ingestor.py]
        end

        subgraph Database_Layer [Storage Infrastructure]
            Metadata_DB[(Airflow Metadata)]
            Target_DB[(PostgreSQL: banking_db)]
            Bronze_Table[(Table: bronze_transactions)]
        end
    end

    %% Volume Mount Linkages
    Local_CSV -.->|Mounted Volume Link| Main_Script
    Local_Env -.->|Injected Variables| Airflow_Services
    Local_Env -.->|Injected Variables| Database_Layer

    %% Workflow Control Loops
    Webserver -->|UI Monitor| DAG_Workflow
    Scheduler -->|Trigger Window| DAG_Workflow
    DAG_Workflow -->|1. Task: Bash Check| Local_CSV
    DAG_Workflow -->|2. Task: Run Script| Main_Script

    %% Execution Dataflow
    Main_Script -->|Invoke| File_Ingestor
    Main_Script -->|Invoke| Postgres_Ingestor
    File_Ingestor -->|Extract & Parse Streaming Data| Local_CSV
    Postgres_Ingestor -->|Establish Handshake: postgres:5432| Target_DB
    Postgres_Ingestor -->|Execute High-Throughput Batch Insert| Bronze_Table

    %% Airflow Backend Connectivity
    Airflow_Services ===|SQLAlchemy Connection| Metadata_DB

    %% Styling Elements
    style Local_CSV fill:#f9f,stroke:#333,stroke-width:2px
    style DAG_Workflow fill:#bbf,stroke:#333,stroke-width:2px
    style Bronze_Table fill:#bfb,stroke:#333,stroke-width:2px
```