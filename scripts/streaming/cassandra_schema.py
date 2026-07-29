"""
Initialize Cassandra keyspace and tables for RASD-Maroc.
Run once: python scripts/streaming/cassandra_schema.py
"""
import logging
import time

from cassandra.cluster import Cluster, NoHostAvailable

logger = logging.getLogger(__name__)

KEYSPACE = "rasd_maroc"

SCHEMA = f"""
CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}};

USE {KEYSPACE};

-- Raw indicators from Kafka stream
CREATE TABLE IF NOT EXISTS indicators_raw (
    code text,
    year int,
    value double,
    source text,
    label text,
    ingested_at timestamp,
    PRIMARY KEY ((code), year, ingested_at)
) WITH CLUSTERING ORDER BY (year DESC, ingested_at DESC);

-- Aggregated statistics per source
CREATE TABLE IF NOT EXISTS indicators_stats (
    source text,
    code text,
    count int,
    avg_value double,
    min_value double,
    max_value double,
    last_updated timestamp,
    PRIMARY KEY ((source), code)
);

-- Latest values per indicator (for dashboards)
CREATE TABLE IF NOT EXISTS indicators_latest (
    code text,
    value double,
    year int,
    source text,
    label text,
    ingested_at timestamp,
    PRIMARY KEY (code)
);
"""


def init_cassandra(host="cassandra", port=9042, retries=10, delay=5):
    for attempt in range(1, retries + 1):
        try:
            cluster = Cluster([host], port=port)
            session = cluster.connect()
            for stmt in SCHEMA.split(";"):
                stmt = stmt.strip()
                if stmt:
                    session.execute(stmt)
            logger.info("Cassandra schema initialized successfully")
            cluster.shutdown()
            return True
        except NoHostAvailable:
            if attempt < retries:
                logger.warning(
                    f"Cassandra not ready (attempt {attempt}/{retries}), "
                    f"retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error("Could not connect to Cassandra after all retries")
                raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_cassandra()
