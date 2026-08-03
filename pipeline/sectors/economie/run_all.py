"""
run_all.py — Orchestrateur de collecte pour le module Économie RASD-Maroc

Exécute tous les scripts de collecte dans l'ordre :
  1. HCP (Haut-Commissariat au Plan)
  2. Bank Al-Maghrib (BAM)
  3. Ministère des Finances
  4. Office des Changes
  5. data.gov.ma (groupe Économie & Finance)

Features :
  - Reprise automatique : skip les sources déjà collectées (meta.json existant)
  - Rapport final avec statistiques
  - Gestion d'erreurs isolée par source (une erreur n'arrête pas les autres)

Usage :
    python run_all.py                  # collecte complète (skip si déjà fait)
    python run_all.py --force          # force la re-collecte de tout
    python run_all.py --sources hcp bkam  # collecte sélective
"""

import argparse
import importlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le répertoire courant au path pour les imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import get_logger, RAW_ROOT

# ---------------------------------------------------------------------------
# Configuration des sources
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "name": "hcp",
        "module": "collect_hcp",
        "label": "Haut-Commissariat au Plan (HCP)",
        "depends_on": None,
    },
    {
        "name": "bkam",
        "module": "collect_bkam",
        "label": "Bank Al-Maghrib (BAM)",
        "depends_on": None,
    },
    {
        "name": "finances",
        "module": "collect_finances",
        "label": "Ministère des Finances",
        "depends_on": None,
    },
    {
        "name": "office_des_changes",
        "module": "collect_office_des_changes",
        "label": "Office des Changes",
        "depends_on": None,
    },
    {
        "name": "datagov",
        "module": "collect_datagov",
        "label": "data.gov.ma (Économie & Finance)",
        "depends_on": ["hcp", "bkam", "finances", "office_des_changes"],
    },
]

logger = get_logger("run_all")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def is_already_collected(source_name: str) -> bool:
    """Vérifie si une source a déjà été collectée (meta.json existant)."""
    meta_path = RAW_ROOT / source_name / "meta.json"
    return meta_path.exists()


def load_meta_stats(source_name: str) -> dict:
    """Charge les stats depuis le meta.json existant."""
    meta_path = RAW_ROOT / source_name / "meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def run_source(source_cfg: dict, force: bool = False) -> dict:
    """
    Exécute un script de collecte.
    Retourne un dict avec le résultat (success, count, duration).
    """
    name = source_cfg["name"]
    module_name = source_cfg["module"]

    # Skip si déjà collecté (sauf --force)
    if not force and is_already_collected(name):
        meta = load_meta_stats(name)
        count = len(meta.get("jeux_telecharges", []))
        logger.info(
            "SKIP %s — déjà collecté (%d fichiers, meta.json existant)",
            source_cfg["label"],
            count,
        )
        return {"success": True, "skipped": True, "count": count}

    logger.info("> Lancement : %s", source_cfg["label"])
    start_time = time.time()

    try:
        mod = importlib.import_module(module_name)
        results = mod.main()
        duration = time.time() - start_time
        count = len(results) if results else 0
        logger.info(
            "OK Termine : %s - %d fichiers (%.1fs)",
            source_cfg["label"],
            count,
            duration,
        )
        return {
            "success": True,
            "skipped": False,
            "count": count,
            "duration_s": round(duration, 1),
        }
    except Exception as exc:
        duration = time.time() - start_time
        logger.error(
            "ERREUR : %s - %s (%.1fs)",
            source_cfg["label"],
            exc,
            duration,
        )
        return {
            "success": False,
            "skipped": False,
            "count": 0,
            "duration_s": round(duration, 1),
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de collecte — Module Économie RASD-Maroc"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force la re-collecte même si meta.json existe déjà.",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=[s["name"] for s in SOURCES],
        help="Collecte sélective (noms de sources séparés par des espaces).",
    )
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("PIPELINE ÉCONOMIE RASD-MAROC — DÉMARRAGE")
    logger.info("Date : %s", datetime.now(timezone.utc).isoformat())
    logger.info("Mode : %s", "FORCE" if args.force else "SKIP si déjà collecté")
    if args.sources:
        logger.info("Sources sélectionnées : %s", ", ".join(args.sources))
    else:
        logger.info("Toutes les sources")
    logger.info("=" * 70)

    # Filtrer les sources si --sources spécifié
    if args.sources:
        active_sources = [s for s in SOURCES if s["name"] in args.sources]
    else:
        active_sources = SOURCES

    # Exécuter dans l'ordre (respecter les dépendances)
    results = {}
    completed = set()

    for source_cfg in active_sources:
        # Vérifier les dépendances
        deps = source_cfg.get("depends_on") or []
        missing_deps = [d for d in deps if d in {s["name"] for s in active_sources} and d not in completed]
        if missing_deps:
            logger.warning(
                "SKIP %s — dépendances non satisfaites : %s",
                source_cfg["label"],
                missing_deps,
            )
            results[source_cfg["name"]] = {
                "success": False,
                "skipped": True,
                "error": f"Dépendances manquantes : {missing_deps}",
            }
            continue

        result = run_source(source_cfg, force=args.force)
        results[source_cfg["name"]] = result
        completed.add(source_cfg["name"])

    # -----------------------------------------------------------------------
    # Rapport final
    # -----------------------------------------------------------------------
    logger.info("")
    logger.info("=" * 70)
    logger.info("RAPPORT FINAL")
    logger.info("=" * 70)

    total_files = 0
    total_errors = 0
    total_skipped = 0

    for source_cfg in SOURCES:
        name = source_cfg["name"]
        if name not in results:
            continue
        r = results[name]
        status = "OK" if r["success"] else "ERR"
        if r.get("skipped"):
            status = "SKP"
            total_skipped += 1
        elif not r["success"]:
            total_errors += 1
        total_files += r.get("count", 0)

        duration_str = f" ({r['duration_s']}s)" if "duration_s" in r else ""
        count_str = f"{r['count']} fichiers" if not r.get("skipped") else "déjà collecté"
        error_str = f" - ERREUR: {r['error']}" if r.get("error") else ""

        logger.info(
            "  %s %-30s %s%s%s",
            status,
            source_cfg["label"],
            count_str,
            duration_str,
            error_str,
        )

    logger.info("")
    logger.info("Total fichiers : %d", total_files)
    logger.info("Erreurs : %d", total_errors)
    logger.info("Déjà collectés (skip) : %d", total_skipped)
    logger.info("=" * 70)

    # Écrire un rapport global
    report_path = RAW_ROOT / "pipeline_report.json"
    report = {
        "date_run": datetime.now(timezone.utc).isoformat(),
        "force": args.force,
        "sources": results,
        "totals": {
            "files": total_files,
            "errors": total_errors,
            "skipped": total_skipped,
        },
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Rapport écrit -> %s", report_path)

    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
