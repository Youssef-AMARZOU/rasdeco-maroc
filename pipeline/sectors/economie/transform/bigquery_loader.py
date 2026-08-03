"""
bigquery_loader.py -- Chargement de la table finalisee dans BigQuery.

Partitionnement : par date (colonnes DATE ou TIMESTAMP).

Fonctionnalites :
  - Creation automatique du dataset et des tables si absents
  - Schema deduit du DataFrame Polars
  - Partition par date + clustering par region_code
  - ecriture en mode WRITE_TRUNCATE ou WRITE_APPEND
  - Tables : fact_indicateurs, dim_regions, dim_domaines, dim_sources
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import polars as pl

# ---------------------------------------------------------------------------
# Configuration BigQuery (via variables d'environnement)
# ---------------------------------------------------------------------------
BQ_PROJECT = os.environ.get("RASD_BQ_PROJECT", "rasd-maroc")
BQ_DATASET = os.environ.get("RASD_BQ_DATASET", "economie")
BQ_LOCATION = os.environ.get("RASD_BQ_LOCATION", "EU")
BQ_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

# Tables cibles
BQ_TABLES = {
    "fact_indicateurs": {
        "partition_field": "date",
        "partition_type": "DATE",  # MONTH, YEAR, DATE
        "cluster_fields": ["region_code", "code_indicateur"],
    },
    "dim_regions": {},
    "dim_domaines": {},
    "dim_sources": {},
    "previsions": {
        "partition_field": "date",
        "partition_type": "DATE",
        "cluster_fields": ["code_indicateur"],
    },
}


def _polars_to_bq_schema(df: pl.DataFrame) -> list[dict]:
    """Convertit les types Polars en types BigQuery."""
    type_map = {
        pl.Float64: "FLOAT64",
        pl.Float32: "FLOAT64",
        pl.Int64: "INT64",
        pl.Int32: "INT64",
        pl.Int8: "INT64",
        pl.Boolean: "BOOL",
        pl.Utf8: "STRING",
        pl.Date: "DATE",
        pl.Datetime: "DATETIME",
        pl.Duration: "INT64",
    }
    schema = []
    for col, dtype in df.schema.items():
        bq_type = type_map.get(dtype, "STRING")
        mode = "NULLABLE"
        schema.append({"name": col, "type": bq_type, "mode": mode})
    return schema


def _ensure_bq_client():
    """Retourne un client BigQuery, avec ou sans credentials."""
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
    except ImportError:
        raise ImportError(
            "google-cloud-bigquery n'est pas installe. "
            "Installez-le avec : pip install google-cloud-bigquery"
        )

    if BQ_CREDENTIALS and Path(BQ_CREDENTIALS).exists():
        credentials = service_account.Credentials.from_service_account_file(BQ_CREDENTIALS)
        return bigquery.Client(project=BQ_PROJECT, credentials=credentials)
    return bigquery.Client(project=BQ_PROJECT)


def _ensure_dataset(client) -> None:
    """Cree le dataset s'il n'existe pas."""
    from google.cloud import bigquery
    dataset_ref = bigquery.DatasetReference(BQ_PROJECT, BQ_DATASET)
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = BQ_LOCATION
        client.create_dataset(dataset)
        print(f"[BQ] Dataset cree : {BQ_PROJECT}.{BQ_DATASET}")


def _prepare_table_schema(client, table_name: str, df: pl.DataFrame) -> None:
    """Cree ou met a jour le schema de la table BigQuery."""
    from google.cloud import bigquery

    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{table_name}"
    bq_schema = _polars_to_bq_schema(df)
    schema = [bigquery.SchemaField(f["name"], f["type"], mode=f["mode"]) for f in bq_schema]

    table_config = BQ_TABLES.get(table_name, {})
    partition_field = table_config.get("partition_field")
    cluster_fields = table_config.get("cluster_fields")

    try:
        existing = client.get_table(table_id)
        # Mise a jour du schema si necessaire
        if existing.schema != schema:
            existing.schema = schema
            client.update_table(existing, ["schema"])
            print(f"[BQ] Schema mis a jour : {table_id}")
    except Exception:
        # Creation de la table
        from google.cloud.bigquery import (
            RangePartitioning,
            TimePartitioning,
            ClusteringFields,
        )

        table = bigquery.Table(table_id, schema=schema)

        if partition_field:
            table.time_partitioning = TimePartitioning(
                type_=table_config.get("partition_type", "DATE"),
                field=partition_field,
            )
        if cluster_fields:
            table.clustering_fields = cluster_fields

        client.create_table(table)
        print(f"[BQ] Table creee : {table_id}")


def load_table(
    table_name: str,
    df: pl.DataFrame,
    write_disposition: str = "WRITE_TRUNCATE",
    dry_run: bool = False,
) -> int:
    """
    Charge un DataFrame Polars dans une table BigQuery.

    Parametres
    ----------
    table_name : nom de la table (fact_indicateurs, dim_regions, ...)
    df : DataFrame Polars a charger
    write_disposition : WRITE_TRUNCATE | WRITE_APPEND | WRITE_EMPTY
    dry_run : si True, n'execute pas le chargement

    Retourne le nombre de lignes chargees.
    """
    if df.is_empty():
        print(f"[BQ] Table {table_name} vide -- rien a charger")
        return 0

    if dry_run:
        n = len(df)
        print(f"[BQ][DRY-RUN] Pret a charger {n} lignes dans {BQ_PROJECT}.{BQ_DATASET}.{table_name}")
        return n

    client = _ensure_bq_client()
    _ensure_dataset(client)
    _prepare_table_schema(client, table_name, df)

    table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{table_name}"

    # Conversion Polars -> Pandas -> BQ (methode fiable)
    pandas_df = df.to_pandas()

    job_config = {
        "write_disposition": write_disposition,
        "autodetect": False,
    }

    from google.cloud import bigquery
    job = client.load_table_from_dataframe(
        pandas_df,
        table_id,
        job_config=bigquery.LoadJobConfig(**job_config),
    )
    job.result()

    print(f"[BQ] OK {job.output_rows} lignes chargees dans {table_id}")
    return job.output_rows


def load_fact_table(
    fact_df: pl.DataFrame,
    dim_regions: pl.DataFrame | None = None,
    dim_domaines: pl.DataFrame | None = None,
    dim_sources: pl.DataFrame | None = None,
    write_disposition: str = "WRITE_TRUNCATE",
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Charge toutes les tables du pipeline dans BigQuery.

    Retourne un dict {nom_table: nb_lignes_chargees}.
    """
    results = {}

    results["fact_indicateurs"] = load_table(
        "fact_indicateurs", fact_df,
        write_disposition=write_disposition,
        dry_run=dry_run,
    )

    dims = {
        "dim_regions": dim_regions,
        "dim_domaines": dim_domaines,
        "dim_sources": dim_sources,
    }
    for name, dim_df in dims.items():
        if dim_df is not None and not dim_df.is_empty():
            results[name] = load_table(name, dim_df, write_disposition=write_disposition, dry_run=dry_run)
        else:
            print(f"[BQ] Dimension {name} non fournie -- ignoree")

    return results
