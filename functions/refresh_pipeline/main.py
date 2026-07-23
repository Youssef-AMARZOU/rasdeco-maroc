"""
Cloud Function : refresh_pipeline
Declenchee par Cloud Scheduler (hebdomadaire, lundi 06:00 UTC).

Execute : collecte -> nettoyage/transformation -> rechargement BigQuery.
Notification Slack en cas d'echec.
"""

from __future__ import annotations

import logging
import os
import sys
import traceback

import functions_framework
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "")


def _notifier_echec(etape: str, err: Exception):
    """Notification Slack + log ERROR pour Cloud Monitoring."""
    msg = f"[RASD-Maroc] Pipeline Economie en echec a l'etape << {etape} >> : {err}"
    logger.error(msg + "\n" + traceback.format_exc())
    if SLACK_WEBHOOK:
        try:
            requests.post(SLACK_WEBHOOK, json={"text": msg}, timeout=10)
        except Exception:
            logger.warning("Echec envoi Slack notification")


def _notifier_succes():
    """Notification Slack de succes (optionnel)."""
    if SLACK_WEBHOOK:
        try:
            requests.post(
                SLACK_WEBHOOK,
                json={"text": "[RASD-Maroc] Pipeline Economie termine avec succes."},
                timeout=10,
            )
        except Exception:
            pass


@functions_framework.http
def refresh(request):
    """
    Point d'entree HTTP de la Cloud Function.

    Etapes :
      1. Collecte (HCP, BAM, Finances, OC, data.gov.ma)
      2. Nettoyage / transformation (parsers, dedup, imputation, regions)
      3. Rechargement BigQuery (WRITE_TRUNCATE)
    """
    # Ajouter le repertoire racine au path pour que les imports economie.* fonctionnent
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)

    etapes = [
        ("collecte", _run_collect),
        ("nettoyage", _run_clean),
        ("chargement BigQuery", _run_load_bq),
        ("previsions", _run_forecast),
    ]

    for etape_name, fn in etapes:
        try:
            logger.info("Demarrage de l'etape : %s", etape_name)
            fn()
            logger.info("Etape terminee : %s", etape_name)
        except Exception as e:
            _notifier_echec(etape_name, e)
            return (f"Echec : {etape_name} — {e}", 500)

    _notifier_succes()
    return ("Pipeline OK — toutes les etapes terminees", 200)


def _run_collect():
    """Collecte depuis toutes les sources."""
    from economie.run_all import main as collect_main
    collect_main()


def _run_clean():
    """Transformation / nettoyage / parsing."""
    from economie.transform.pipeline import run_pipeline
    run_pipeline(selected_sources=None, do_load=False, dry_run=False)


def _run_load_bq():
    """Rechargement BigQuery (WRITE_TRUNCATE)."""
    from economie.transform.pipeline import run_pipeline
    run_pipeline(selected_sources=None, do_load=True, dry_run=False)


def _run_forecast():
    """Generation des previsions et chargement en BQ."""
    from economie.forecasting.forecast_to_bq import run_forecast_to_bq
    run_forecast_to_bq(horizon=8)
