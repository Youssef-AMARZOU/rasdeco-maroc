"""DAG: dbt_transforms - Medallion architecture transforms via dbt-trino"""
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

ROOT = Path(__file__).resolve().parent.parent
DBT_DIR = str(ROOT / "dbt")

default_args = {
    "owner": "rasd-maroc",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "dbt_transforms",
    default_args=default_args,
    description="Run dbt medallion transforms: bronze -> silver -> gold",
    schedule="0 4 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["dbt", "transforms", "lakehouse"],
) as dag:

    dbt_bronze = BashOperator(
        task_id="dbt_run_bronze",
        bash_command=f"cd {DBT_DIR} && dbt run --models bronze --profiles-dir .",
    )

    dbt_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"cd {DBT_DIR} && dbt run --models silver --profiles-dir .",
    )

    dbt_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"cd {DBT_DIR} && dbt run --models gold --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test --profiles-dir .",
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"cd {DBT_DIR} && dbt docs generate --profiles-dir .",
    )

    dbt_bronze >> dbt_silver >> dbt_gold >> dbt_test >> dbt_docs
