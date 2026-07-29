"""
DAG: export_datasets
Exports MongoDB collections to JSON, Parquet, and Kaggle formats.
Runs daily.
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
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "export_datasets",
    default_args=default_args,
    description="Export MongoDB collections to JSON, Parquet, and Kaggle",
    schedule="0 4 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["rasd-maroc", "export"],
) as dag:

    def export_to_json():
        import json
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/rasd_maroc", tls=False)
        db = client["rasd_maroc"]
        export_dir = ROOT / "data" / "export"
        export_dir.mkdir(parents=True, exist_ok=True)
        for name in db.list_collection_names():
            docs = list(db[name].find({}, {"_id": 0}).limit(50000))
            fp = export_dir / f"{name}.json"
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=2, default=str, ensure_ascii=False)
            print(f"Exported {len(docs)} docs to {fp.name}")
        client.close()

    export_json = PythonOperator(
        task_id="export_mongodb_to_json",
        python_callable=export_to_json,
    )

    def export_dashboard_data():
        import json
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/rasd_maroc", tls=False)
        db = client["rasd_maroc"]
        indicators = list(db.economie.find({}, {"_id": 0}).limit(10000))
        imf = list(db.imf_weo.find({}, {"_id": 0}))
        dashboard = {
            "indicators": indicators,
            "imf": imf,
            "exported_at": datetime.utcnow().isoformat(),
        }
        for fp in [ROOT / "public" / "data.json", ROOT / "out" / "data.json"]:
            fp.parent.mkdir(parents=True, exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(dashboard, f, default=str, ensure_ascii=False)
            print(f"Dashboard data exported to {fp}")
        client.close()

    export_dashboard = PythonOperator(
        task_id="export_dashboard_data",
        python_callable=export_dashboard_data,
    )

    export_json >> export_dashboard
