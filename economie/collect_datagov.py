"""
collect_datagov.py — Collecte du groupe « Économie et Finance » sur data.gov.ma

Source unique : API CKAN de data.gov.ma
  - Groupe : Économie et Finance (group_id : 5026f7a6-0fbd-40a3-8463-9f5a10348e68)
  - Tous les jeux de données du groupe, toutes organisations confondues
  - Téléchargement de TOUTES les ressources structurées (XLSX, CSV, JSON)

Ce script est le plus exhaustif : il récupère l'intégralité du portail
open data pour le domaine économique.

Usage :
    python collect_datagov.py
"""

import json
import sys
from pathlib import Path

from utils import (
    download_file,
    dest_for,
    filename_from_url,
    get_logger,
    make_session,
    write_meta,
    year_from_filename,
    RAW_ROOT,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SOURCE = "datagov"
CKAN_API = "https://www.data.gov.ma/data/api/3/action"
CKAN_BASE_DL = "https://www.data.gov.ma/data/fr/dataset"

# ID du groupe « Économie et Finance » sur data.gov.ma
GROUP_ID = "5026f7a6-0fbd-40a3-8463-9f5a10348e68"

# Mots-clés de recherche pour compléter la collecte groupée
KEYWORD_QUERIES = [
    "PIB",
    "IPC",
    "inflation",
    "chômage",
    "emploi",
    "budget",
    "dette",
    "monétaire",
    "taux directeur",
    "balance commerciale",
    "investissement étranger",
    "changes",
    "export",
    "import",
    "commerce extérieur",
    "fiscalité",
    "recettes budgétaires",
    "dépenses budgétaires",
    "industrie",
    "agriculture",
    "tourisme",
    "immobilier",
]

# Formats de fichiers à télécharger
TARGET_FORMATS = {"XLSX", "XLS", "CSV", "JSON", "XML", "ODS"}

logger = get_logger(SOURCE)


# ---------------------------------------------------------------------------
# 1. Collecte groupée par groupe CKAN
# ---------------------------------------------------------------------------
def collect_by_group() -> list[dict]:
    """
    Récupère TOUS les jeux du groupe Économie & Finance via CKAN.
    Utilise la pagination (rows + start) pour ne rien rater.
    """
    session = make_session(SOURCE)
    downloads_info = []
    seen_urls: set[str] = set()

    start = 0
    batch_size = 100
    total_count = None

    logger.info("Collecte groupée — groupe Économie & Finance (ID: %s)", GROUP_ID)

    while True:
        try:
            resp = session.get(
                f"{CKAN_API}/package_search",
                params={
                    "fq": f"groups:{GROUP_ID}",
                    "rows": batch_size,
                    "start": start,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("Erreur API CKAN (group, start=%d) : %s", start, exc)
            break

        if not data.get("success"):
            logger.warning("API CKAN success=false")
            break

        result = data.get("result", {})
        if total_count is None:
            total_count = result.get("count", 0)
            logger.info("Total jeux dans le groupe : %d", total_count)

        results = result.get("results", [])
        if not results:
            break

        logger.info("Batch %d–%d / %d jeux", start, start + len(results), total_count)

        for pkg in results:
            pkg_name = pkg.get("name", "unknown")
            pkg_title = pkg.get("title", "")
            org = pkg.get("organization", {})
            org_name = org.get("title", "inconnu") if org else "inconnu"

            for resource in pkg.get("resources", []):
                url = resource.get("url", "")
                fmt = (resource.get("format") or "").upper()
                res_name = resource.get("name") or resource.get("description") or ""

                if fmt not in TARGET_FORMATS:
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                fname = filename_from_url(url)
                year = year_from_filename(fname)
                # Sous-dossier par organisme pour garder de l'ordre
                org_slug = (
                    org_name.lower()
                    .replace(" ", "_")
                    .replace("'", "")
                    .replace("é", "e")
                    .replace("è", "e")
                    .replace("ô", "o")
                )
                dest = dest_for(f"{SOURCE}/{org_slug}", year, fname)

                success = download_file(session, url, dest, logger)
                if success and dest.exists() and dest.stat().st_size > 0:
                    downloads_info.append({
                        "url": url,
                        "format": fmt,
                        "description": f"{pkg_title} — {res_name}",
                        "ckan_package": pkg_name,
                        "organisme": org_name,
                        "fichier": str(dest.relative_to(RAW_ROOT)),
                    })

        start += batch_size
        if start >= total_count:
            break

    logger.info("Total fichiers téléchargés (groupe) : %d", len(downloads_info))
    return downloads_info


# ---------------------------------------------------------------------------
# 2. Recherche par mots-clés (complément)
# ---------------------------------------------------------------------------
def collect_by_keywords() -> list[dict]:
    """
    Recherche complémentaire par mots-clés pour catcher
    les jeux qui ne seraient pas dans le groupe mais restent
    dans le domaine économique.
    """
    session = make_session(SOURCE)
    downloads_info = []
    seen_urls: set[str] = set()

    for q in KEYWORD_QUERIES:
        logger.info("Requête CKAN (keyword) : '%s'", q)

        try:
            resp = session.get(
                f"{CKAN_API}/package_search",
                params={"q": q, "rows": 30},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("Erreur CKAN '%s' : %s", q, exc)
            continue

        if not data.get("success"):
            continue

        results = data.get("result", {}).get("results", [])

        for pkg in results:
            pkg_name = pkg.get("name", "unknown")
            pkg_title = pkg.get("title", "")

            for resource in pkg.get("resources", []):
                url = resource.get("url", "")
                fmt = (resource.get("format") or "").upper()
                res_name = resource.get("name") or resource.get("description") or ""

                if fmt not in TARGET_FORMATS:
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                fname = filename_from_url(url)
                year = year_from_filename(fname)
                dest = dest_for(SOURCE, year, fname)

                success = download_file(session, url, dest, logger)
                if success and dest.exists() and dest.stat().st_size > 0:
                    downloads_info.append({
                        "url": url,
                        "format": fmt,
                        "description": f"{pkg_title} — {res_name}",
                        "ckan_package": pkg_name,
                        "keyword_query": q,
                        "fichier": str(dest.relative_to(RAW_ROOT)),
                    })

    logger.info("Total fichiers téléchargés (keywords) : %d", len(downloads_info))
    return downloads_info


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("DÉBUT COLLECTE data.gov.ma — %s", SOURCE)
    logger.info("=" * 60)

    # 1. Collecte groupée (exhaustive)
    logger.info("--- Phase 1 : Groupe Économie & Finance ---")
    group_downloads = collect_by_group()

    # 2. Recherche par mots-clés (complément)
    logger.info("--- Phase 2 : Recherche par mots-clés ---")
    keyword_downloads = collect_by_keywords()

    # Dédoublonner
    all_downloads = group_downloads + keyword_downloads
    seen = set()
    unique_downloads = []
    for d in all_downloads:
        key = d["url"]
        if key not in seen:
            seen.add(key)
            unique_downloads.append(d)

    meta_path = write_meta(
        dest_dir=RAW_ROOT / SOURCE,
        source="data.gov.ma — Groupe Économie et Finance",
        urls=unique_downloads,
        periodicite="Variable (selon jeux)",
        granularite="Nationale, régionale, sectorielle",
        date_debut_reelle="1960",
        extra={
            "portail": "https://www.data.gov.ma/data/fr/group/finance",
            "group_id": GROUP_ID,
            "licence": "ODbL",
            "nb_keywords_searched": len(KEYWORD_QUERIES),
        },
    )
    logger.info("meta.json écrit → %s", meta_path)
    logger.info(
        "FIN COLLECTE data.gov.ma — %d fichiers uniques téléchargés",
        len(unique_downloads),
    )

    return unique_downloads


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results else 1)
