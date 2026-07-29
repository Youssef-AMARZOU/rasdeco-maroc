"""
CDC Consumer: lit les evenements Debezium depuis Kafka et les insere dans MongoDB.
Suit le format CDC Debezium pour PostgreSQL.

Topics consommes:
  - rasd.public.indicators  (create/update/delete)
  - rasd.public.sources
"""
import json
import logging
import os
import signal
import sys

from kafka import KafkaConsumer
from pymongo import MongoClient, UpdateOne

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rasd_maroc")
TOPICS = [
    "rasd.public.indicators",
    "rasd.public.sources",
]

running = True


def signal_handler(sig, frame):
    global running
    logger.info("Shutting down...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def extract_payload(msg_value):
    """Extrait le payload CDC Debezium et retourne (op, after)."""
    try:
        data = json.loads(msg_value)
    except (json.JSONDecodeError, TypeError):
        return None, None

    payload = data.get("payload", {})
    op = payload.get("op")

    if op == "c":
        op = "create"
    elif op == "u":
        op = "update"
    elif op == "d":
        op = "delete"
    elif op == "r":
        op = "read"

    after = payload.get("after")
    return op, after


def doc_from_pg(after):
    """Convertit un enregistrement PostgreSQL en document MongoDB."""
    if after is None:
        return None
    doc = {k: v for k, v in after.items() if v is not None}
    # Supprimer les champs internes
    doc.pop("id", None)
    doc.pop("raw_json", None)
    doc["ingested_at"] = after.get("ingested_at")
    return doc


def process_indicators(mongo_collection, after_batch):
    """Insere ou met a jour les indicateurs dans MongoDB."""
    ops = []
    for after in after_batch:
        doc = doc_from_pg(after)
        if doc and doc.get("code") and doc.get("year") is not None:
            ops.append(
                UpdateOne(
                    {"code": doc["code"], "year": doc["year"]},
                    {"$set": doc},
                    upsert=True,
                )
            )
    if ops:
        result = mongo_collection.bulk_write(ops)
        logger.info(f"MongoDB: {len(ops)} ops (matched={result.matched_count}, "
                    f"upserted={result.upserted_count})")


def run():
    mongo = MongoClient(MONGODB_URI, tls=False)
    db = mongo.get_database()

    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda v: v.decode("utf-8") if v else None,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="cdc-consumer",
    )

    logger.info(f"Connected to Kafka {KAFKA_BROKER}, consuming: {TOPICS}")

    buffer = []

    for msg in consumer:
        if not running:
            break

        op, after = extract_payload(msg.value)
        if op is None or after is None:
            continue

        topic_short = msg.topic.split(".")[-1]

        if op == "delete":
            logger.info(f"DELETE on {topic_short}: skipping sync (CDC only)")
            continue

        buffer.append(after)

        if len(buffer) >= 100:
            process_indicators(db.indicators, buffer)
            buffer.clear()

    if buffer:
        process_indicators(db.indicators, buffer)

    mongo.close()
    consumer.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
