"""
forecast_to_bq.py -- Lance les previsions pour chaque indicateur et charge en BigQuery.

Genere la table previsions avec colonnes :
  date, code_indicateur, yhat, yhat_lower, yhat_upper, modele, date_insertion

Usage :
  python -m economie.forecasting.forecast_to_bq
  python -m economie.forecasting.forecast_to_bq --indicators PIB.TRIM.VOL CHOMAGE.TAUX
  python -m economie.forecasting.forecast_to_bq --dry-run
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

# Ajouter la racine du projet au path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from economie.transform.bigquery_loader import load_table

logger = logging.getLogger(__name__)


def _load_historical(code: str) -> pd.DataFrame | None:
    """Charge l'historique depuis fact_indicateurs pour un indicateur."""
    try:
        from economie.transform.bigquery_loader import (
            BQ_PROJECT,
            BQ_DATASET,
            _ensure_bq_client,
        )
        client = _ensure_bq_client()
        sql = f"""
            SELECT date, valeur
            FROM `{BQ_PROJECT}.{BQ_DATASET}.fact_indicateurs`
            WHERE code_indicateur = @code
              AND region_code = 'MA00'
            ORDER BY date
        """
        from google.cloud import bigquery
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("code", "STRING", code)
            ]
        )
        df = client.query(sql, job_config=job_config).to_dataframe()
        if df.empty:
            return None
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()
        return df
    except Exception as e:
        logger.warning("Impossible de charger l'historique pour %s : %s", code, e)
        return None


def _forecast_single(
    code: str, h: int = 8, alpha: float = 0.2
) -> pd.DataFrame | None:
    """Genere les previsions pour un indicateur unique."""
    df = _load_historical(code)
    if df is None or len(df) < 12:
        logger.info("Pas assez de donnees pour %s (%s points)", code, len(df) if df is not None else 0)
        return None

    serie = df["valeur"].astype(float)
    preds, lower, upper = None, None, None
    model_name = None

    # Essayer SARIMA d'abord
    try:
        from economie.forecasting.sarima_model import SARIMAModel
        model = SARIMAModel()
        model.fit(serie.values, freq="QS")
        preds, lower, upper = model.predict(h=h, alpha=alpha)
        model_name = "SARIMA"
    except Exception as e:
        logger.debug("SARIMA echoue pour %s : %s", code, e)

    # Fallback Prophet
    if preds is None:
        try:
            from economie.forecasting.prophet_model import ProphetModel
            model = ProphetModel()
            model.fit(serie.reset_index().rename(columns={"date": "ds", "valeur": "y"}))
            preds, lower, upper = model.predict(h=h, alpha=alpha)
            model_name = "Prophet"
        except Exception as e:
            logger.debug("Prophet echoue pour %s : %s", code, e)

    # Fallback naive saisonnier
    if preds is None:
        try:
            from economie.forecasting.baselines import naive_seasonal_forecast
            last_values = serie.values
            season = min(4, len(last_values) // 2)
            preds = np.array([last_values[-season + i % season] for i in range(h)])
            std_resid = np.std(last_values[-20:]) if len(last_values) >= 20 else np.std(last_values)
            lower = preds - 1.28 * std_resid
            upper = preds + 1.28 * std_resid
            model_name = "Naive Saisonnier"
        except Exception as e:
            logger.warning("Tous les modeles ont echoue pour %s : %s", code, e)
            return None

    # Construire les dates de prevision (frequence trimestrielle ou mensuelle)
    last_date = serie.index[-1]
    try:
        freq = pd.infer_freq(serie.index[-8:]) if len(serie) >= 8 else "QS"
    except Exception:
        freq = "QS"
    future_dates = pd.date_range(start=last_date, periods=h + 1, freq=freq)[1:]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for i in range(h):
        rows.append({
            "date": future_dates[i].strftime("%Y-%m-%d"),
            "code_indicateur": code,
            "yhat": round(float(preds[i]), 4),
            "yhat_lower": round(float(lower[i]), 4),
            "yhat_upper": round(float(upper[i]), 4),
            "modele": model_name,
            "date_insertion": now,
        })

    return pd.DataFrame(rows)


def run_forecast_to_bq(
    indicators: list[str] | None = None,
    horizon: int = 8,
    dry_run: bool = False,
) -> int:
    """
    Lance les previsions pour tous les indicateurs et charge en BQ.

    Retourne le nombre total de lignes chargees.
    """
    # Si pas d'indicateurs specifies, les recuperer depuis BQ
    if indicators is None:
        try:
            from economie.transform.bigquery_loader import (
                BQ_PROJECT,
                BQ_DATASET,
                _ensure_bq_client,
            )
            client = _ensure_bq_client()
            sql = f"""
                SELECT DISTINCT code_indicateur
                FROM `{BQ_PROJECT}.{BQ_DATASET}.fact_indicateurs`
            """
            df_ind = client.query(sql).to_dataframe()
            indicators = df_ind["code_indicateur"].tolist()
        except Exception as e:
            logger.error("Impossible de recuperer les indicateurs depuis BQ : %s", e)
            return 0

    logger.info("Previsions pour %d indicateurs (horizon=%d)", len(indicators), horizon)

    all_dfs = []
    for code in indicators:
        logger.info("Prevision : %s", code)
        prev = _forecast_single(code, h=horizon)
        if prev is not None:
            all_dfs.append(prev)
            logger.info("  -> %d lignes generees", len(prev))

    if not all_dfs:
        logger.warning("Aucune prevision generee")
        return 0

    combined = pd.concat(all_dfs, ignore_index=True)
    logger.info("Total : %d lignes de previsions", len(combined))

    if dry_run:
        print(combined.to_string(index=False))
        return len(combined)

    # Convertir en Polars et charger
    pf = pl.from_pandas(combined)
    n = load_table("previsions", pf, write_disposition="WRITE_TRUNCATE")
    logger.info("Charge dans BQ : %d lignes", n)
    return n


def main():
    parser = argparse.ArgumentParser(description="Generer et charger les previsions en BQ")
    parser.add_argument("--indicators", nargs="*", help="Codes indicateurs a prevoir")
    parser.add_argument("--horizon", type=int, default=8, help="Nombre de periodes a prevoir")
    parser.add_argument("--dry-run", action="store_true", help="Afficher sans charger")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    n = run_forecast_to_bq(
        indicators=args.indicators,
        horizon=args.horizon,
        dry_run=args.dry_run,
    )
    print(f"Termine : {n} lignes chargees dans BigQuery")


if __name__ == "__main__":
    main()
