"""
Enregistre le connecteur Debezium PostgreSQL aupres de Kafka Connect.
Configure en Avro avec Schema Registry + Dead Letter Queue.
Usage: python scripts/debezium/register_connector.py
"""
import json
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://localhost:8083")
SR_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")

CONNECTOR_CONFIG = {
    "name": "rasd-postgres-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": os.getenv("PG_HOST", "postgres-data"),
        "database.port": os.getenv("PG_PORT", "5432"),
        "database.user": os.getenv("PG_USER", "rasd"),
        "database.password": os.getenv("PG_PASSWORD", "rasd123"),
        "database.dbname": os.getenv("PG_DATABASE", "rasd_maroc_data"),
        "topic.prefix": os.getenv("TOPIC_PREFIX", "rasd"),
        "table.include.list": "public.indicators,public.sources",
        "plugin.name": "pgoutput",
        "publication.name": "rasd_publication",
        "publication.autocreate.mode": "filtered",
        "slot.name": "rasd_slot",
        "slot.drop.on.stop": "false",
        "tombstones.on.delete": "false",
        "snapshot.mode": "initial",
        "heartbeat.interval.ms": "5000",
        "provide.transaction.metadata": "true",
        # JSON Converter
        "key.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "key.converter.schemas.enable": "true",
        "value.converter.schemas.enable": "true",
        # Dead Letter Queue
        "errors.tolerance": "all",
        "errors.deadletterqueue.topic.name": "rasd-dlq",
        "errors.deadletterqueue.context.headers.enable": "true",
        "errors.retry.timeout.ms": "30000",
        "errors.retry.delay.max.ms": "1000",
        # Schema evolution
        "schema.whitelist": "rasd_maroc_data.public.indicators",
        "column.include.list": "public.indicators.id,public.indicators.code,public.indicators.label,public.indicators.value,public.indicators.year,public.indicators.source,public.indicators.source_detail,public.indicators.qualite,public.indicators.ingested_at",
    },
}


def wait_for_schema_registry(retries=20, delay=5):
    for i in range(1, retries + 1):
        try:
            r = requests.get(f"{SR_URL}/subjects", timeout=5)
            if r.status_code == 200:
                logger.info(f"Schema Registry ready (attempt {i})")
                return True
        except requests.ConnectionError:
            pass
        logger.info(f"Waiting for Schema Registry... ({i}/{retries})")
        time.sleep(delay)
    raise RuntimeError("Schema Registry not ready after all retries")


def wait_for_connect(retries=30, delay=5):
    for i in range(1, retries + 1):
        try:
            r = requests.get(f"{CONNECT_URL}/", timeout=5)
            if r.status_code == 200:
                logger.info(f"Kafka Connect ready (attempt {i})")
                return True
        except requests.ConnectionError:
            pass
        logger.info(f"Waiting for Kafka Connect... ({i}/{retries})")
        time.sleep(delay)
    raise RuntimeError("Kafka Connect not ready after all retries")


def register():
    r = requests.get(f"{CONNECT_URL}/connectors/rasd-postgres-connector", timeout=5)
    if r.status_code == 200:
        logger.info("Connector exists, deleting...")
        requests.delete(f"{CONNECT_URL}/connectors/rasd-postgres-connector", timeout=5)
        time.sleep(2)

    r = requests.post(
        f"{CONNECT_URL}/connectors/",
        json=CONNECTOR_CONFIG,
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    if r.status_code in (200, 201):
        logger.info(f"Connector created: {r.json()}")
    else:
        logger.error(f"Failed: {r.status_code} {r.text}")
        raise RuntimeError(f"Connector registration failed: {r.text}")

    time.sleep(3)
    r = requests.get(
        f"{CONNECT_URL}/connectors/rasd-postgres-connector/status", timeout=5
    )
    logger.info(f"Connector status: {json.dumps(r.json(), indent=2)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    wait_for_schema_registry()
    wait_for_connect()
    register()
