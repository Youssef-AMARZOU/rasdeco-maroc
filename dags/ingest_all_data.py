"""
DAG: ingest_all_data
Orchestrates full data ingestion pipeline: files -> MongoDB -> Neo4j graph -> exports.
Runs every 6 hours, or on demand.
"""
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

ROOT = Path(__file__).resolve().parent.parent

default_args = {
    "owner": "rasd-maroc",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "ingest_all_data",
    default_args=default_args,
    description="Full data ingestion: files -> MongoDB -> Neo4j -> exports",
    schedule="0 */6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["rasd-maroc", "ingestion"],
) as dag:

    scan_files = BashOperator(
        task_id="scan_data_files",
        bash_command="python scripts/ingest_all.py",
        cwd=str(ROOT),
    )

    def rebuild_graph():
        import sys
        sys.path.insert(0, str(ROOT))
        from scripts.graph_api import build_graph
        build_graph()
        print("Graph rebuild complete")

    rebuild_graph = PythonOperator(
        task_id="rebuild_neo4j_graph",
        python_callable=rebuild_graph,
    )

    def export_summary():
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/rasd_maroc", tls=False)
        db = client["rasd_maroc"]
        summary = {}
        for name in db.list_collection_names():
            summary[name] = db[name].estimated_document_count()
        client.close()
        import json
        with open(ROOT / "data" / "export" / "mongo_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Exported summary: {summary}")

    export_summary = PythonOperator(
        task_id="export_summary",
        python_callable=export_summary,
    )

    scan_files >> rebuild_graph >> export_summary
