from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.insert(0, '/opt/airflow/src')
from fetch_f1_data import main as fetch_main
from transform_f1_data import main as transform_main
from aggregate_f1_data import main as aggregate_main

with DAG(
    dag_id='f1ow_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule='@weekly',
    catchup=False
) as dag:
    task1 = PythonOperator(
        task_id='fetch_and_store_f1_data',
        python_callable=fetch_main
    )
    task2 = PythonOperator(
        task_id='transform_to_silver',
        python_callable=transform_main
    )
    task3 = PythonOperator(
        task_id='aggregate_to_gold',
        python_callable=aggregate_main
    )

    task1 >> task2 >> task3