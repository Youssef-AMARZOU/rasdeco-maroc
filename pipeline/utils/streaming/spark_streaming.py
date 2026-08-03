"""
PySpark Structured Streaming job:
- Reads from Kafka topics (raw.*)  
- Parses JSON
- Computes per-source, per-indicator stats
- Writes to Cassandra

Submit:
  spark-submit --master spark://localhost:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 \
    scripts/streaming/spark_streaming.py
"""
import json

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, schema_of_json, window, coalesce, to_timestamp, current_timestamp
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

KAFKA_BROKER = "kafka:9092"
CASSANDRA_HOST = "cassandra"
CASSANDRA_KEYSPACE = "rasd_maroc"

RAW_SCHEMA = StructType(
    [
        StructField("code", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("value", DoubleType(), True),
        StructField("source", StringType(), True),
        StructField("label", StringType(), True),
        StructField("source_detail", StringType(), True),
        StructField("qualite", StringType(), True),
        StructField("ingested_at", StringType(), True),
    ]
)


def main():
    spark = (
        SparkSession.builder.appName("RASD-Maroc Streaming")
        .config("spark.sql.streaming.schemaInference", "true")
        .config("spark.cassandra.connection.host", CASSANDRA_HOST)
        .config("spark.cassandra.connection.port", "9042")
        .config("spark.sql.catalog.cassandra", "com.datastax.spark.connector.datasource.CassandraCatalog")
        .getOrCreate()
    )

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER)
        .option("subscribe", "raw.economie,raw.imf_weo,raw.agriculture,raw.education,raw.sante")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
        .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "topic")
    )

    parsed = df.select(
        col("topic"),
        from_json(col("value"), RAW_SCHEMA).alias("data"),
    ).select("topic", "data.*")

    valid = parsed.filter(col("code").isNotNull() & col("value").isNotNull())
    valid = valid.withColumn("ingested_at", coalesce(to_timestamp(col("ingested_at")), current_timestamp()))

    writes = (
        valid.writeStream.outputMode("append")
        .foreachBatch(write_to_cassandra)
        .option("checkpointLocation", "/tmp/spark-checkpoints")
        .trigger(processingTime="60 seconds")
        .start()
    )

    writes.awaitTermination()


def write_to_cassandra(df, epoch_id):
    if df.count() == 0:
        return

    df.write.format("org.apache.spark.sql.cassandra").mode("append").options(
        table="indicators_raw", keyspace=CASSANDRA_KEYSPACE
    ).save()

    from pyspark.sql import functions as F
    from pyspark.sql import Window

    stats = (
        df.groupBy("source", "code")
        .agg(
            F.count("*").alias("count"),
            F.avg("value").alias("avg_value"),
            F.min("value").alias("min_value"),
            F.max("value").alias("max_value"),
        )
        .withColumn("last_updated", F.current_timestamp())
    )

    stats.write.format("org.apache.spark.sql.cassandra").mode("append").options(
        table="indicators_stats", keyspace=CASSANDRA_KEYSPACE
    ).save()

    latest = (
        df.withColumn("rn", F.row_number().over(
            Window.partitionBy("code").orderBy(F.col("year").desc())
        ))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )

    latest.write.format("org.apache.spark.sql.cassandra").mode("append").options(
        table="indicators_latest", keyspace=CASSANDRA_KEYSPACE
    ).save()


if __name__ == "__main__":
    main()
