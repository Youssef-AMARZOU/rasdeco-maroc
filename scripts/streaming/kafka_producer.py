"""
Kafka producer: polls MongoDB collections and publishes new documents
to Kafka topics (one topic per collection).
"""
import json
import logging
import os
import time

from datetime import datetime

from kafka import KafkaProducer
from pymongo import MongoClient

logger = logging.getLogger(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rasd_maroc")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))

EXCLUDED_COLLECTIONS = {"system.views", "system.users", "system.keyspaces"}


def init_high_watermarks(db):
    hw = {}
    for name in db.list_collection_names():
        if name in EXCLUDED_COLLECTIONS:
            continue
        doc = db[name].find_one(sort=[("$natural", -1)])
        if doc:
            hw[name] = doc.get("_id")
        else:
            hw[name] = None
    return hw


def run():
    mongo = MongoClient(MONGODB_URI, tls=False)
    db = mongo.get_database()

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        acks="all",
        retries=3,
    )

    hw = init_high_watermarks(db)
    logger.info(
        f"Connected to {MONGODB_URI} | Kafka {KAFKA_BROKER} | "
        f"polling every {POLL_INTERVAL}s"
    )

    while True:
        for name in db.list_collection_names():
            if name in EXCLUDED_COLLECTIONS:
                continue
            query = {}
            last_id = hw.get(name)
            if last_id is not None:
                query = {"_id": {"$gt": last_id}}

            cursor = db[name].find(query).sort("$natural", 1)
            count = 0
            for doc in cursor:
                doc.pop("_id", None)
                future = producer.send(f"raw.{name}", value=doc)
                future.get(timeout=5)
                hw[name] = doc.get("_id", doc)
                count += 1

            if count:
                logger.info(f"Published {count} docs to raw.{name}")

        producer.flush()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
