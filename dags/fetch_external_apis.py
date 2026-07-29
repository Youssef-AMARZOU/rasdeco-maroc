"""
DAG: fetch_external_apis
Recupere automatiquement les donnees depuis des API externes
(World Bank, HCP, BAM, ONU, FMI) et les stocke dans MongoDB.

Planification: quotidienne (6h du matin)

Etapes:
  1. fetch_world_bank -> nettoie -> insert dans MongoDB
  2. fetch_hcp -> nettoie -> insert dans MongoDB
  3. fetch_bam -> nettoie -> insert dans MongoDB
  4. fetch_fmi_weo -> nettoie -> insert dans MongoDB
"""
from datetime import datetime, timedelta
from pathlib import Path

import json
import logging
import time

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

default_args = {
    "owner": "rasd-maroc",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# ---- INDICATEURS MAROC ----
WORLD_BANK_INDICATORS = {
    "NY.GDP.MKTP.CD": "PIB (USD courants)",
    "NY.GDP.MKTP.KD.ZG": "Croissance PIB (%)",
    "FP.CPI.TOTL.ZG": "Inflation IPC (%)",
    "SL.UEM.TOTL.ZS": "Chomage (% pop active)",
    "NY.GNP.PCAP.CD": "RNB par habitant (USD)",
    "BX.KLT.DINV.WD.GD.ZS": "IDE entrants (% PIB)",
    "NE.EXP.GNFS.ZS": "Exportations (% PIB)",
    "NE.IMP.GNFS.ZS": "Importations (% PIB)",
    "SE.XPD.TOTL.GD.ZS": "Depenses education (% PIB)",
    "SH.XPD.CHEX.GD.ZS": "Depenses sante (% PIB)",
    "EG.USE.ELEC.KH.PC": "Consommation electricite (kWh/hab)",
    "IT.NET.USER.ZS": "Internet (% population)",
    "SP.DYN.LE00.IN": "Esperance de vie (ans)",
    "SP.POP.TOTL": "Population totale",
    "EN.ATM.CO2E.PC": "Emissions CO2 (tonnes/hab)",
}

HCP = "Haut-Commissariat au Plan"
BAM = "Bank Al-Maghrib"
FMI = "Fonds Monetaire International"


def fetch_world_bank(**context):
    """
    Recupere les indicateurs Maroc depuis l'API World Bank v2.
    Format: https://api.worldbank.org/v2/country/MA/indicator/{code}?format=json
    Nettoie et retourne une liste de documents propres.
    """
    import requests as req

    base = "https://api.worldbank.org/v2/country/MA/indicator"
    results = []

    for code, label in WORLD_BANK_INDICATORS.items():
        url = f"{base}/{code}?format=json&per_page=100&date=2000:2026"
        try:
            resp = req.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"World Bank {code}: {e}")
            continue

        if not isinstance(data, list) or len(data) < 2:
            continue

        for entry in data[1]:
            if entry is None:
                continue
            value = entry.get("value")
            year = entry.get("year")
            if value is None or year is None:
                continue

            results.append({
                "code": code,
                "label": label,
                "value": float(value) if value is not None else None,
                "year": int(year),
                "source": "World Bank",
                "source_detail": "World Bank API v2",
                "qualite": "officielle",
                "ingested_at": datetime.utcnow().isoformat(),
            })

        time.sleep(0.3)

    logger.info(f"World Bank: {len(results)} valeurs recuperees")
    return results


def fetch_hcp(**context):
    """
    Recupere les donnees depuis l'API HCP (emploi, chomage, IPC).
    HCP met a disposition des donnees via leur portail data.hcp.ma
    """
    import requests as req
    results = []

    endpoints = [
        ("IPC", "https://www.hcp.ma/indicateurs/ipc.json"),
        ("CHOMAGE", "https://www.hcp.ma/indicateurs/chomage.json"),
        ("EMPLOI", "https://www.hcp.ma/indicateurs/emploi.json"),
    ]

    for code, url in endpoints:
        try:
            resp = req.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"HCP {code}: {e}")
            continue

        rows = data if isinstance(data, list) else [data]
        for row in rows:
            results.append({
                "code": f"HCP_{code}",
                "label": row.get("label", code),
                "value": row.get("value"),
                "year": row.get("annee"),
                "source": HCP,
                "source_detail": "data.hcp.ma",
                "qualite": "officielle",
                "ingested_at": datetime.utcnow().isoformat(),
            })

    logger.info(f"HCP: {len(results)} valeurs recuperees")
    return results


def fetch_bam(**context):
    """
    Recupere les indicateurs monétaires depuis BAM (Bank Al-Maghrib).
    API: https://www.bkam.ma/api/...
    """
    import requests as req
    results = []

    endpoints = [
        ("RESERVES", "https://www.bkam.ma/api/reserves"),
        ("TAUX_DIRECTEUR", "https://www.bkam.ma/api/taux-directeur"),
        ("M3", "https://www.bkam.ma/api/masse-monetaire"),
    ]

    for code, url in endpoints:
        try:
            resp = req.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning(f"BAM {code}: {e}")
            continue

        rows = data if isinstance(data, list) else [data]
        for row in rows:
            results.append({
                "code": f"BAM_{code}",
                "label": row.get("label", code),
                "value": row.get("value"),
                "year": row.get("annee", row.get("year")),
                "source": BAM,
                "source_detail": "bkam.ma",
                "qualite": "officielle",
                "ingested_at": datetime.utcnow().isoformat(),
            })

    logger.info(f"BAM: {len(results)} valeurs recuperees")
    return results


def fetch_all(**context):
    """
    Execute tous les fetchs et insere dans PostgreSQL.
    Debezium detecte les INSERT/UPDATE et les diffuse vers Kafka,
    puis le CDC consumer synchronise vers MongoDB.
    """
    import psycopg2
    from psycopg2.extras import execute_values

    pg_dsn = (
        context["var"]["value"]
        .get("PG_DSN", "postgresql://rasd:rasd123@postgres-data:5432/rasd_maroc_data")
    )

    tasks = {
        "world_bank": fetch_world_bank(**context),
        "hcp": fetch_hcp(**context),
        "bam": fetch_bam(**context),
    }

    conn = psycopg2.connect(pg_dsn)
    conn.autocommit = False
    cur = conn.cursor()
    total = 0

    try:
        for source, documents in tasks.items():
            if not documents:
                logger.warning(f"Aucune donnee pour {source}")
                continue

            rows = [
                (
                    doc["code"],
                    doc.get("label"),
                    doc.get("value"),
                    doc.get("year"),
                    doc.get("source"),
                    doc.get("source_detail"),
                    doc.get("qualite", "officielle"),
                )
                for doc in documents
            ]

            execute_values(
                cur,
                """
                INSERT INTO indicators (code, label, value, year, source, source_detail, qualite)
                VALUES %s
                ON CONFLICT (code, year, source)
                DO UPDATE SET
                    label = EXCLUDED.label,
                    value = EXCLUDED.value,
                    source_detail = EXCLUDED.source_detail,
                    qualite = EXCLUDED.qualite,
                    ingested_at = NOW()
                """,
                rows,
            )

            total += len(documents)
            logger.info(f"{source}: {len(documents)} lignes inserees")

        # Log de l'execution
        cur.execute(
            "INSERT INTO fetch_log (source, status, records_count) "
            "VALUES ('fetch_all', 'success', %s)",
            (total,),
        )

        conn.commit()
        logger.info(f"Total: {total} enregistrements inseres dans PostgreSQL")

    except Exception as e:
        conn.rollback()
        logger.error(f"Echec insertion PostgreSQL: {e}")
        cur.execute(
            "INSERT INTO fetch_log (source, status, records_count, error_message) "
            "VALUES ('fetch_all', 'failed', %s, %s)",
            (total, str(e)),
        )
        conn.commit()
        raise
    finally:
        cur.close()
        conn.close()

    return total


with DAG(
    "fetch_external_apis",
    default_args=default_args,
    description="Recuperation automatique depuis World Bank, HCP, BAM, FMI",
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["rasd-maroc", "api", "ingestion"],
) as dag:

    fetch_all_task = PythonOperator(
        task_id="fetch_all_external_apis",
        python_callable=fetch_all,
        provide_context=True,
    )

    fetch_all_task
