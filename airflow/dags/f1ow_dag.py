from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.insert(0, '/opt/airflow/src')
from fetch_f1_data import main

with DAG(
    dag_id='f1ow_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@weekly',
    catchup=False
) as dag:
    task1 = PythonOperator(
        task_id='fetch_and_store_f1_data',
        python_callable=main
    )