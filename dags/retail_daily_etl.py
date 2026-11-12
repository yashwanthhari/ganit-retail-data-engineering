from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="retail_daily_medallion_etl",
    description="Generate sample retail drops and run the local PySpark medallion pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["retail", "pyspark", "medallion"],
) as dag:
    generate = BashOperator(
        task_id="generate_daily_source_data",
        bash_command="cd /opt/airflow/project && python -m src.generate_data --date {{ ds }}",
    )
    transform = BashOperator(
        task_id="bronze_silver_gold",
        bash_command="cd /opt/airflow/project && python -m src.pipeline --date {{ ds }}",
    )
    generate >> transform
