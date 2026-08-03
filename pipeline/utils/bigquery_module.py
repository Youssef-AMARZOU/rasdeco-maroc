"""
bigquery_module.py -- Chargement BigQuery pour les modules
Social, Education, Sante, Agriculture, Sport.

Lit le parquet produit par chaque module et le charge dans le dataset BQ correspondant.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Literal

import pandas as pd
import polars as pl
from google.cloud import bigquery

logger = logging.getLogger(__name__)

Module = Literal["social", "education", "sante", "agriculture", "sport"]

PROJECT = os.environ.get("RASD_BQ_PROJECT", "rasd-maroc")
LOCATION = os.environ.get("BQ_LOCATION", "EU")

PARQUET_PATHS: dict[Module, str] = {
    "social": "social/data/output/social_complet.parquet",
    "education": "education/data/output/education_complet.parquet",
    "sante": "sante/data/output/sante_complet.parquet",
    "agriculture": "agriculture/data/output/agriculture_complet.parquet",
    "sport": "sport/data/output/sport_complet.parquet",
}

DATASET_NAMES: dict[Module, str] = {
    "social": os.environ.get("RASD_BQ_DATASET_SOCIAL", "social"),
    "education": os.environ.get("RASD_BQ_DATASET_EDUCATION", "education"),
    "sante": os.environ.get("RASD_BQ_DATASET_SANTE", "sante"),
    "agriculture": os.environ.get("RASD_BQ_DATASET_AGRICULTURE", "agriculture"),
    "sport": os.environ.get("RASD_BQ_DATASET_SPORT", "sport"),
}


def _client() -> bigquery.Client:
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if creds and os.path.exists(creds):
        from google.oauth2 import service_account
        sa = service_account.Credentials.from_service_account_file(creds)
        return bigquery.Client(project=PROJECT, credentials=sa)
    return bigquery.Client(project=PROJECT)


def _ensure_dataset(client: bigquery.Client, dataset_id: str):
    ds_ref = bigquery.DatasetReference(PROJECT, dataset_id)
    try:
        client.get_dataset(ds_ref)
    except Exception:
        ds = bigquery.Dataset(ds_ref)
        ds.location = LOCATION
        client.create_dataset(ds)
        logger.info("Dataset cree : %s", dataset_id)


def load_module_to_bq(module: Module, parquet_path: str | None = None) -> None:
    """Charge le parquet d'un module dans BigQuery."""
    path = parquet_path or PARQUET_PATHS.get(module, "")
    dataset_id = DATASET_NAMES.get(module, module)

    parquet_file = Path(path)
    if not parquet_file.exists():
        logger.warning("Fichier parquet introuvable : %s", parquet_file)
        return

    logger.info("Chargement module=%s depuis %s vers %s.%s", module, path, PROJECT, dataset_id)

    # Lire le parquet avec Polars, convertir en Pandas
    pdf = pl.read_parquet(path).to_pandas()

    # Renommer les colonnes pour correspondre au schema BigQuery standard
    col_rename = {
        "year": "date",
        "value": "valeur",
        "indicator_code": "code_indicateur",
        "unite": "unite",
        "region_code": "region_code",
        "region": "region_nom",
        "level": "niveau",
        "category": "categorie",
        "location": "localite",
    }
    pdf.rename(columns={v: k for k, v in col_rename.items() if v in pdf.columns}, inplace=True)
    pdf.rename(columns=col_rename, inplace=True)

    # S'assurer que date est bien formatee
    if "date" in pdf.columns:
        pdf["date"] = pd.to_datetime(pdf["date"], errors="coerce")

    client = _client()
    _ensure_dataset(client, dataset_id)

    table_ref = f"{PROJECT}.{dataset_id}.fact_indicateurs"

    # WRITE_TRUNCATE pour remplacer completement
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
        time_partitioning=bigquery.TimePartitioning(
            field="date",
            type_="DAY",
        ),
        clustering={"fields": ["code_indicateur"]} if "code_indicateur" in pdf.columns else None,
    )

    job = client.load_table_from_dataframe(pdf, table_ref, job_config=job_config)
    job.result()
    logger.info("Charge %d lignes vers %s", len(pdf), table_ref)

    # Creer des previsions simples (tendance lineaire par indicateur)
    _generate_simple_forecast(client, dataset_id, pdf)


def _generate_simple_forecast(client: bigquery.Client, dataset_id: str, pdf: pd.DataFrame):
    """Genere des previsions simples par tendance lineaire."""
    if "date" not in pdf.columns or "valeur" not in pdf.columns or "code_indicateur" not in pdf.columns:
        return

    from sklearn.linear_model import LinearRegression
    import numpy as np

    rows = []
    for code, grp in pdf.groupby("code_indicateur"):
        grp = grp.dropna(subset=["date", "valeur"]).copy()
        grp["annee"] = grp["date"].dt.year
        grp = grp.groupby("annee", as_index=False)["valeur"].mean()
        if len(grp) < 3:
            continue
        X = grp["annee"].values.reshape(-1, 1)
        y = grp["valeur"].values
        model = LinearRegression()
        model.fit(X, y)
        derniere_annee = int(grp["annee"].max())
        for h in range(1, 9):
            annee = derniere_annee + h
            pred = model.predict([[annee]])[0]
            resid = np.std(y - model.predict(X))
            rows.append({
                "date": pd.Timestamp(f"{annee}-01-01"),
                "code_indicateur": code,
                "yhat": pred,
                "yhat_lower": pred - 1.28 * resid,
                "yhat_upper": pred + 1.28 * resid,
            })

    if not rows:
        return

    prev_df = pd.DataFrame(rows)
    prev_table = f"{PROJECT}.{dataset_id}.previsions"
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )
    job = client.load_table_from_dataframe(prev_df, prev_table, job_config=job_config)
    job.result()
    logger.info("Previsions chargees : %d lignes vers %s", len(prev_df), prev_table)


if __name__ == "__main__":
    for mod in ["social", "education", "sante", "agriculture", "sport"]:
        load_module_to_bq(mod)
