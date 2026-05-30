# dags/silver_processing_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'ginko',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'mercury_silver_transformation',
    default_args=default_args,
    description='Extracts records from Bronze database tables, flattens payload attributes, and builds Silver models.',
    schedule_interval='@daily',
    catchup=False,
    tags=['mercury', 'silver', 'transformation'],
) as dag:

    # Task 1: Execute our unified pipeline entrypoint focusing on the Silver phase
    # We pass the required library installations inline just like our Bronze setup
    run_silver_transformation = BashOperator(
        task_id='execute_silver_transformation',
        bash_command='pip install structlog python-dotenv psycopg2-binary && python main.py',
        cwd='/opt/airflow',
    )

    run_silver_transformation