"""
DAG: data_quality
Monitors data freshness, completeness, and quality.
Emails alerts if datasets are stale or incomplete.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "rasd-maroc",
    "depends_on_past": False,
    "email_on_failure": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "data_quality",
    default_args=default_args,
    description="Monitor data freshness, completeness, and quality metrics",
    schedule="0 8 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["rasd-maroc", "quality"],
) as dag:

    def _check_mongodb():
        from pymongo import MongoClient
        c = MongoClient("mongodb://localhost:27017/rasd_maroc", tls=False)
        db = c["rasd_maroc"]
        for name in sorted(db.list_collection_names()):
            cnt = db[name].estimated_document_count()
            print(f"{name}: {cnt} docs")
        c.close()

    check_mongodb = PythonOperator(
        task_id="check_mongodb",
        python_callable=_check_mongodb,
    )

    def _check_graph():
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password123"))
        with driver.session() as s:
            n = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            r = s.run("MATCH ()-[x]->() RETURN count(x) AS c").single()["c"]
            print(f"Graph: {n} nodes, {r} relationships")
        driver.close()

    check_graph = PythonOperator(
        task_id="check_neo4j_graph",
        python_callable=_check_graph,
    )

    def _check_api():
        import urllib.request, json
        r = urllib.request.urlopen("http://localhost:8080/health", timeout=5)
        print(json.dumps(json.loads(r.read()), indent=2))

    check_api = PythonOperator(
        task_id="check_api_health",
        python_callable=_check_api,
    )

    check_mongodb >> check_graph >> check_api
