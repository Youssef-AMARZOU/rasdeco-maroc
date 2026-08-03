"""
CDC Consumer avec Dead Letter Queue et commit manuel.
Consomme les evenements Debezium (Avro) depuis Kafka.
Les messages non-parsables sont routes vers rasd-dlq.
Le commit n'est fait qu'apres ecriture reussie dans MongoDB.
"""
import json
import logging
import os
import signal
import sys
import time

from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from pymongo import MongoClient, UpdateOne

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rasd_maroc")
GROUP_ID = os.getenv("CDC_GROUP_ID", "cdc-consumer-group")
SR_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")

TOPICS = ["rasd.public.indicators", "rasd.public.sources"]

running = True


def signal_handler(sig, frame):
    global running
    logger.info("Shutting down...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def extract_payload(msg_value):
    try:
        data = json.loads(msg_value.decode("utf-8"))
    except (json.JSONDecodeError, TypeError, AttributeError):
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
    if after is None:
        return None
    doc = {k: v for k, v in after.items() if v is not None}
    doc.pop("id", None)
    doc.pop("raw_json", None)
    return doc


class CDCErrorHandler:
    def __init__(self, dlq_topic="rasd-dlq"):
        self.producer = Producer({"bootstrap.servers": KAFKA_BROKER})
        self.dlq_topic = dlq_topic

    def send_to_dlq(self, msg, error_reason):
        self.producer.produce(
            topic=self.dlq_topic,
            key=msg.key(),
            value=msg.value(),
            headers=[
                ("error_reason", str(error_reason).encode("utf-8")),
                ("original_topic", (msg.topic() or "").encode("utf-8")),
                ("original_partition", str(msg.partition()).encode("utf-8")),
                ("original_offset", str(msg.offset()).encode("utf-8")),
            ],
        )
        self.producer.poll(0)
        logger.warning(f"DLQ: sent offset {msg.offset()} reason={error_reason}")

    def flush(self):
        self.producer.flush()


def process_batch(mongo_collection, batch):
    ops = []
    for after in batch:
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
        logger.info(
            f"MongoDB: {len(ops)} ops "
            f"(matched={result.matched_count}, upserted={result.upserted_count})"
        )
    return len(ops)


def run():
    mongo = MongoClient(MONGODB_URI, tls=False)
    db = mongo.get_database()

    dlq_handler = CDCErrorHandler()

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BROKER,
            "group.id": GROUP_ID,
            "enable.auto.commit": False,
            "auto.offset.reset": "earliest",
            "session.timeout.ms": 45000,
            "heartbeat.interval.ms": 15000,
            "max.poll.interval.ms": 300000,
        }
    )

    consumer.subscribe(TOPICS)
    logger.info(
        f"Connected to Kafka {KAFKA_BROKER}, group={GROUP_ID}, "
        f"consuming: {TOPICS} | DLQ: rasd-dlq"
    )

    buffer = []
    last_commit = time.time()
    BATCH_SIZE = 100
    BATCH_TIMEOUT = 5.0

    while running:
        msg = consumer.poll(1.0)

        # Check for timeout or size threshold to commit
        now = time.time()
        should_commit = len(buffer) >= BATCH_SIZE or (len(buffer) > 0 and now - last_commit >= BATCH_TIMEOUT)

        if should_commit:
            try:
                count = process_batch(db.indicators, buffer)
                dlq_handler.flush()
                consumer.commit()
                logger.info(f"Committed {count} docs due to size or timeout")
                buffer.clear()
                last_commit = now
            except Exception as e:
                logger.error(f"Batch write failed: {e}")
                for doc in buffer:
                    dlq_handler.send_to_dlq(
                        type("Msg", (), {"key": lambda: None, "value": lambda: json.dumps(doc).encode(), "topic": lambda: "unknown", "partition": lambda: -1, "offset": lambda: -1})(),
                        f"mongo_write_failed: {e}",
                    )
                consumer.commit()
                buffer.clear()
                last_commit = now

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            logger.error(f"Kafka error: {msg.error()}")
            continue

        try:
            op, after = extract_payload(msg.value())
        except Exception as e:
            dlq_handler.send_to_dlq(msg, f"extract_payload failed: {e}")
            consumer.commit(msg)
            continue

        if after is None:
            consumer.commit(msg)
            continue

        if op == "delete":
            consumer.commit(msg)
            continue

        buffer.append(after)

    if buffer:
        try:
            process_batch(db.indicators, buffer)
            consumer.commit()
        except Exception as e:
            logger.error(f"Final batch failed: {e}")

    dlq_handler.flush()
    consumer.close()
    mongo.close()
    logger.info("CDC Consumer stopped cleanly")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    run()
