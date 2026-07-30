FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pandas pymongo redis pyarrow fastparquet openpyxl kafka-python confluent-kafka cassandra-driver requests strawberry-graphql neo4j

COPY . .

EXPOSE 8080

CMD uvicorn scripts.imf_export.api.main:app --host 0.0.0.0 --port 8080