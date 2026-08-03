"""Migrate existing parquet/csv exports to Iceberg tables via Trino SQL"""
import json
import urllib.request
import urllib.error
import time
import sys
from pathlib import Path

TRINO_HOST = "localhost"
TRINO_PORT = 8088
TRINO_URL = f"http://{TRINO_HOST}:{TRINO_PORT}"

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "export"
IMF_DIR = ROOT / "scripts" / "imf_export" / "exports"


def trino_query(sql, catalog="iceberg"):
    """Execute SQL on Trino via REST API, return rows."""
    body = json.dumps({"query": sql}).encode()
    req = urllib.request.Request(
        f"{TRINO_URL}/v1/statement",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Trino-User": "rasd",
            "X-Trino-Catalog": catalog,
            "X-Trino-Schema": "rasd",
        },
    )
    rows = []
    next_uri = None
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read())
        next_uri = data.get("nextUri")
        if "data" in data:
            rows.extend(data["data"])
        while next_uri:
            resp = urllib.request.urlopen(next_uri, timeout=60)
            data = json.loads(resp.read())
            next_uri = data.get("nextUri")
            if "data" in data:
                rows.extend(data["data"])
        return rows
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR {e.code}: {body[:500]}")
        raise


def wait_trino(timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            trino_query("SELECT 1")
            print("Trino ready")
            return True
        except Exception as e:
            print(f"  Waiting for Trino... {e}")
            time.sleep(5)
    print("Trino not ready after timeout")
    return False


def create_schema():
    print("\n=== Creating Iceberg schema ===")
    trino_query("CREATE SCHEMA IF NOT EXISTS iceberg.rasd")
    print("Schema iceberg.rasd ready")


def create_economie_table():
    print("\n=== Creating iceberg.rasd.economie_maroc ===")
    sql = """
    CREATE TABLE IF NOT EXISTS iceberg.rasd.economie_maroc (
        date VARCHAR,
        date_label VARCHAR,
        region_code VARCHAR,
        domaine_code VARCHAR,
        code_indicateur VARCHAR,
        valeur DOUBLE,
        unite VARCHAR,
        source_code VARCHAR,
        version_serie VARCHAR,
        fiabilite INTEGER,
        qualite_flag VARCHAR,
        fichier_source VARCHAR,
        date_insertion TIMESTAMP
    ) WITH (
        format = 'PARQUET',
        partitioning = ARRAY['source_code', 'domaine_code']
    )
    """
    trino_query(sql)
    print("Table economie_maroc ready")


def create_imf_table():
    print("\n=== Creating iceberg.rasd.imf_weo ===")
    sql = """
    CREATE TABLE IF NOT EXISTS iceberg.rasd.imf_weo (
        indicator_id VARCHAR,
        indicator_name VARCHAR,
        unit VARCHAR,
        year INTEGER,
        value DOUBLE
    ) WITH (
        format = 'PARQUET',
        partitioning = ARRAY['indicator_id']
    )
    """
    trino_query(sql)
    print("Table imf_weo ready")


def create_dim_source():
    print("\n=== Creating iceberg.rasd.dim_source ===")
    sql = """
    CREATE TABLE IF NOT EXISTS iceberg.rasd.dim_source (
        source_code VARCHAR PRIMARY KEY,
        source_name VARCHAR,
        description VARCHAR
    ) WITH (format = 'PARQUET')
    """
    trino_query(sql)
    print("Table dim_source ready")


def populate_sources():
    print("\n=== Populating dim_source ===")
    sources = [
        ("BAM", "Bank Al-Maghrib", "Central bank of Morocco"),
        ("DATAGOV", "Data.gov.ma", "Open data portal of Morocco"),
        ("FIN", "Ministere des Finances", "Ministry of Finance"),
        ("HCP", "Haut-Commissariat au Plan", "High Commission for Planning"),
        ("OC", "Office des Changes", "Exchange Office"),
        ("IMF", "International Monetary Fund", "IMF World Economic Outlook"),
    ]
    for code, name, desc in sources:
        try:
            trino_query(
                f"INSERT INTO iceberg.rasd.dim_source VALUES "
                f"('{code}', '{name}', '{desc}')"
            )
        except Exception:
            pass  # likely already exists
    print("Sources inserted")


def migrate_economie():
    print("\n=== Migrating economie_maroc.parquet to Iceberg ===")
    import pandas as pd

    parquet_file = DATA_DIR / "economie_maroc.parquet"
    if not parquet_file.exists():
        print(f"  {parquet_file} not found, skipping")
        return

    df = pd.read_parquet(parquet_file)
    # Trino's Iceberg connector doesn't support bulk INSERT from files easily.
    # Use batch INSERT via VALUES with chunks.
    chunk_size = 500
    total = len(df)
    print(f"  Total rows: {total}")

    for start in range(0, total, chunk_size):
        chunk = df.iloc[start : start + chunk_size]
        values = []
        for _, row in chunk.iterrows():
            val = row.get("valeur")
            if pd.isna(val):
                val = "NULL"
            else:
                val = str(float(val))
            flag = row.get("qualite_flag")
            if pd.isna(flag) or flag is None:
                flag = "NULL"
            else:
                flag = f"'{str(flag)}'"
            ts = row.get("date_insertion")
            if pd.isna(ts) or ts is None:
                ts = "NULL"
            else:
                ts = f"TIMESTAMP '{pd.Timestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}'"
            values.append(
                f"('{row.get('date', '')}', "
                f"'{row.get('date_label', '')}', "
                f"'{row.get('region_code', '')}', "
                f"'{row.get('domaine_code', '')}', "
                f"'{row.get('code_indicateur', '')}', "
                f"{val}, "
                f"'{row.get('unite', '')}', "
                f"'{row.get('source_code', '')}', "
                f"'{row.get('version_serie', '')}', "
                f"{int(row.get('fiabilite', 0))}, "
                f"{flag}, "
                f"'{row.get('fichier_source', '')}', "
                f"{ts})"
            )
        sql = f"INSERT INTO iceberg.rasd.economie_maroc VALUES {', '.join(values)}"
        try:
            trino_query(sql)
            print(f"  Inserted rows {start}-{start + len(chunk)}/{total}")
        except Exception as e:
            print(f"  FAILED at row {start}: {e}")

    print("  Economie migration done")


def migrate_imf():
    print("\n=== Migrating IMF data to Iceberg ===")
    import pandas as pd

    imf_file = IMF_DIR / "morocco_imf_long.parquet"
    if not imf_file.exists():
        print(f"  {imf_file} not found, skipping")
        return

    df = pd.read_parquet(imf_file)
    chunk_size = 200
    total = len(df)
    print(f"  Total rows: {total}")

    for start in range(0, total, chunk_size):
        chunk = df.iloc[start : start + chunk_size]
        values = []
        for _, row in chunk.iterrows():
            val = row.get("value")
            if pd.isna(val):
                val = "NULL"
            else:
                val = str(float(val))
            iname = row.get("indicator_name", "").replace("'", "''")
            iunit = row.get("unit", "").replace("'", "''")
            values.append(
                f"('{row.get('indicator_id', '')}', "
                f"'{iname}', "
                f"'{iunit}', "
                f"{int(row.get('year', 0))}, "
                f"{val})"
            )
        sql = f"INSERT INTO iceberg.rasd.imf_weo VALUES {', '.join(values)}"
        try:
            trino_query(sql)
            print(f"  Inserted rows {start}-{start + len(chunk)}/{total}")
        except Exception as e:
            print(f"  FAILED at row {start}: {e}")

    print("  IMF migration done")


def create_aggregated_views():
    print("\n=== Creating aggregated views (Silver layer) ===")
    views = {
        "kpi_latest": """
            CREATE OR REPLACE VIEW iceberg.rasd.kpi_latest AS
            SELECT
                code_indicateur,
                date,
                valeur,
                unite,
                source_code
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY code_indicateur
                        ORDER BY date DESC
                    ) AS rn
                FROM iceberg.rasd.economie_maroc
            )
            WHERE rn = 1
        """,
        "annual_aggregates": """
            CREATE OR REPLACE VIEW iceberg.rasd.annual_aggregates AS
            SELECT
                source_code,
                domaine_code,
                extract(YEAR FROM date_insertion) AS year,
                COUNT(*) AS obs_count,
                ROUND(AVG(valeur), 4) AS avg_value,
                ROUND(SUM(valeur), 4) AS total_value
            FROM iceberg.rasd.economie_maroc
            GROUP BY source_code, domaine_code, year
        """,
        "imf_latest": """
            CREATE OR REPLACE VIEW iceberg.rasd.imf_latest AS
            SELECT *
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY indicator_id
                        ORDER BY year DESC
                    ) AS rn
                FROM iceberg.rasd.imf_weo
            )
            WHERE rn = 1
        """,
    }
    for name, sql in views.items():
        try:
            trino_query(sql)
            print(f"  View {name} created")
        except Exception as e:
            print(f"  FAILED view {name}: {e}")


def main():
    print("=" * 50)
    print("  Migrate existing data to Iceberg (Nessie catalog)")
    print("=" * 50)

    if not wait_trino():
        sys.exit(1)

    create_schema()
    create_economie_table()
    create_imf_table()
    create_dim_source()
    populate_sources()
    migrate_economie()
    migrate_imf()
    create_aggregated_views()

    print("\n=== Migration complete ===")
    print("Tables in iceberg.rasd schema:")
    for row in trino_query("SHOW TABLES FROM iceberg.rasd"):
        print(f"  - {row[0]}")


if __name__ == "__main__":
    main()
