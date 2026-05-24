# dags/bronze_ingestion_dag.py

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'ginko',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'mercury_bronze_ingestion',
    default_args=default_args,
    description='Automated batch ingestion of banking transactions to Bronze layer',
    schedule_interval='@daily',  # Automates execution once every day at midnight
    start_date=datetime(2026, 5, 1),
    catchup=False,
    tags=['mercury', 'bronze'],
) as dag:

    # Task 1: Verify the file system can locate our raw source data target file
    check_source_file = BashOperator(
        task_id='check_source_file_exists',
        bash_command='ls -la /opt/airflow/data/raw/transactions_v1.csv',
    )

    # Task 2: Install client libraries inside the container pool, then execute orchestration
    run_ingestion = BashOperator(
        task_id='execute_postgres_ingestion',
        # This pipes a quick inline pip install before firing your main program entrypoint
        bash_command='pip install structlog python-dotenv psycopg2-binary && python /opt/airflow/main.py',
    )

    # Establish dependency chain (Task 1 must pass before Task 2 fires)
    check_source_file >> run_ingestion