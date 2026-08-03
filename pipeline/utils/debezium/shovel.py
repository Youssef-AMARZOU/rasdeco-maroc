"""
Shovel: Rejoue les messages de la Dead Letter Queue vers le topic principal.
Usage: python scripts/debezium/shovel.py [--topic rasd-dlq] [--target rasd.public.indicators]

Lit la DLQ, reinjecte dans le topic original, commit seulement apres succes.
"""
import json
import logging
import os
import sys

from confluent_kafka import Consumer, Producer, KafkaError

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
DLQ_TOPIC = os.getenv("DLQ_TOPIC", "rasd-dlq")
TARGET_TOPIC = os.getenv("TARGET_TOPIC", "rasd.public.indicators")


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Rejoue les messages DLQ vers le topic principal")
    p.add_argument("--dlq", default=DLQ_TOPIC, help="Topic DLQ source")
    p.add_argument("--target", default=TARGET_TOPIC, help="Topic cible")
    p.add_argument("--dry-run", action="store_true", help="Simule sans reinjecter")
    p.add_argument("--max-messages", type=int, default=1000, help="Limite de messages a rejouer")
    return p.parse_args()


def main():
    args = parse_args()

    consumer = Consumer({
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "shovel-replay-group",
        "enable.auto.commit": False,
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([args.dlq])

    producer = Producer({"bootstrap.servers": KAFKA_BROKER})

    logger.info(f"Shovel starting: {args.dlq} -> {args.target} (dry_run={args.dry_run})")

    count = 0
    errors = 0

    try:
        while count < args.max_messages:
            msg = consumer.poll(1.0)
            if msg is None:
                break
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error(f"Consumer error: {msg.error()}")
                errors += 1
                continue

            key = msg.key()
            value = msg.value()

            if args.dry_run:
                logger.info(f"[DRY-RUN] Would replay: offset={msg.offset()} key={key}")
                consumer.commit(msg)
                count += 1
                continue

            try:
                producer.produce(
                    topic=args.target,
                    key=key,
                    value=value,
                    headers=[("shovel_replayed_at", str(__import__("time").time()).encode("utf-8"))],
                )
                producer.flush()
                consumer.commit(msg)
                count += 1
                if count % 100 == 0:
                    logger.info(f"Replayed {count} messages")
            except Exception as e:
                logger.error(f"Failed to replay offset {msg.offset()}: {e}")
                errors += 1
                if errors > 10:
                    logger.critical("Too many errors, aborting")
                    break

    except KeyboardInterrupt:
        logger.info("Shovel interrupted")

    finally:
        consumer.close()
        producer.flush()

    logger.info(f"Shovel complete: {count} replayed, {errors} errors")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    main()
