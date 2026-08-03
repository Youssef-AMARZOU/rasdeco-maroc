"""
Cloud Function : refresh_pipeline_multimodule
Declenchee par Cloud Scheduler pour chaque module (economie, social, education, sante, agriculture, sport).

Execute : collecte -> nettoyage/transformation -> rechargement BigQuery -> previsions.
Notification Slack en cas d'echec.
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from typing import Literal

import functions_framework
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "")
Module = Literal["economie", "social", "education", "sante", "agriculture", "sport"]

# Frequences (pour le Scheduler):
#   economie:    hebdomadaire (lundi 06:00)
#   social:      annuelle (01/01 08:00)
#   education:   annuelle (01/09 08:00)
#   sante:       annuelle (01/04 08:00)
#   agriculture: saisonniere (01/03, 01/10) + toutes les 2 semaines NDVI
#   sport:       quotidienne pendant competitions


def _notifier_echec(etape: str, err: Exception, module: str = "general"):
    """Notification Slack + log ERROR."""
    msg = f"[RASD-Maroc] Pipeline {module.upper()} en echec a l'etape << {etape} >> : {err}"
    logger.error(msg + "\n" + traceback.format_exc())
    if SLACK_WEBHOOK:
        try:
            requests.post(SLACK_WEBHOOK, json={"text": msg}, timeout=10)
        except Exception:
            logger.warning("Echec envoi Slack notification")


def _notifier_succes(module: str = "general"):
    if SLACK_WEBHOOK:
        try:
            requests.post(
                SLACK_WEBHOOK,
                json={"text": f"[RASD-Maroc] Pipeline {module.upper()} termine avec succes."},
                timeout=10,
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Modulaire : chaque module a ses propres etapes
# ---------------------------------------------------------------------------

def _module_import(module: Module):
    """Ajoute le repertoire racine au sys.path si necessaire."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)


def _run_collect(module: Module):
    """Collecte module-specifique."""
    if module == "economie":
        from economie.run_all import main as collect_main
        collect_main()
    elif module == "social":
        from social.collect.hcp_bds import fetch_all_social_indicators
        fetch_all_social_indicators()
    elif module == "education":
        from education.collect.hcp_bds import fetch_all_education_indicators
        fetch_all_education_indicators()
    elif module == "sante":
        from sante.collect.hcp_bds import fetch_all_sante_indicators
        fetch_all_sante_indicators()
    elif module == "agriculture":
        from agriculture.collect.hcp_bds import fetch_all_agriculture_indicators
        fetch_all_agriculture_indicators()
    elif module == "sport":
        from sport.collect.fifa_scraper import fetch_all_sport_data
        fetch_all_sport_data()


def _run_clean(module: Module):
    """Parsing / transformation."""
    if module == "economie":
        from economie.transform.pipeline import run_pipeline
        run_pipeline(selected_sources=None, do_load=False, dry_run=False)
    elif module == "social":
        from social.transform.pipeline import run_pipeline
        run_pipeline()
    elif module == "education":
        from education.transform.pipeline import run_pipeline
        run_pipeline()
    elif module == "sante":
        from sante.transform.pipeline import run_pipeline
        run_pipeline()
    elif module == "agriculture":
        from agriculture.transform.pipeline import run_pipeline
        run_pipeline()
    elif module == "sport":
        from sport.transform.pipeline import run_pipeline
        run_pipeline()


def _run_load_bq(module: Module):
    """Chargement BigQuery."""
    if module == "economie":
        from economie.transform.pipeline import run_pipeline
        run_pipeline(selected_sources=None, do_load=True, dry_run=False)
    else:
        from bigquery_module import load_module_to_bq
        load_module_to_bq(module)


def _run_forecast(module: Module):
    """Generation previsions."""
    if module == "economie":
        from economie.forecasting.forecast_to_bq import run_forecast_to_bq
        run_forecast_to_bq(horizon=8)
    # Les autres modules : predictions lineaires simples via bigquery_module


# ---------------------------------------------------------------------------
# Point d'entree HTTP : refresh multi-module
# ---------------------------------------------------------------------------

@functions_framework.http
def refresh(request):
    """
    Declencheur Cloud Scheduler pour un module specifique.

    Parametres requete (JSON ou query string) :
      - module (obligatoire) : economie, social, education, sante, agriculture, sport
      - etapes (optionnel)   : "all" (defaut) ou liste separee par virgule
    """
    data = request.get_json(silent=True) or {}
    module_str = data.get("module") or request.args.get("module", "").lower()
    if module_str not in ("economie", "social", "education", "sante", "agriculture", "sport"):
        return ("Parametre 'module' invalide. Choisir parmi: economie, social, education, sante, agriculture, sport", 400)

    module: Module = module_str
    _module_import(module)

    etapes = [
        ("collecte", lambda: _run_collect(module)),
        ("nettoyage", lambda: _run_clean(module)),
        ("chargement BigQuery", lambda: _run_load_bq(module)),
        ("previsions", lambda: _run_forecast(module)),
    ]

    for etape_name, fn in etapes:
        try:
            logger.info("[%s] Demarrage : %s", module, etape_name)
            fn()
            logger.info("[%s] Terminee : %s", module, etape_name)
        except Exception as e:
            _notifier_echec(etape_name, e, module)
            return (f"Echec {module}/{etape_name} : {e}", 500)

    _notifier_succes(module)
    return (f"Pipeline {module} OK — toutes les etapes terminees", 200)
