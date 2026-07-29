"""
Enregistre le connecteur Debezium PostgreSQL aupres de Kafka Connect.
Usage: python scripts/debezium/register_connector.py
"""
import json
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

CONNECT_URL = os.getenv("KAFKA_CONNECT_URL", "http://localhost:8083")

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
        "key.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "key.converter.schemas.enable": "false",
        "value.converter.schemas.enable": "false",
        "snapshot.mode": "initial",
        "heartbeat.interval.ms": "5000",
        "provide.transaction.metadata": "true",
    },
}


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
    # Supprimer si existe deja
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

    # Verifier statut
    time.sleep(3)
    r = requests.get(
        f"{CONNECT_URL}/connectors/rasd-postgres-connector/status", timeout=5
    )
    logger.info(f"Connector status: {json.dumps(r.json(), indent=2)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wait_for_connect()
    register()
