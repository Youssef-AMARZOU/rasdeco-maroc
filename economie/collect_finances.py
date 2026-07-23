"""
collect_finances.py — Collecte des données du Ministère des Finances

Sources :
  1. API CKAN data.gov.ma (organisme "ministere-de-l-economie-et-des-finances")
     -> dette publique, budget, exécution budgétaire
  2. Téléchargements directs finances.gov.ma
     -> rapports budgétaires annuels (PDF)
  3. Scraping HTML finances.gov.ma (FRAGILE)
     -> pages de publications / documents

Usage :
    python collect_finances.py
"""

import re
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
SOURCE = "finances"
CKAN_API = "https://www.data.gov.ma/data/api/3/action"

CKAN_QUERIES = [
    {"q": "budget", "desc": "Budget de l'État"},
    {"q": "dette publique", "desc": "Dette publique"},
    {"q": "exécution budgétaire", "desc": "Exécution budgétaire"},
    {"q": "finances publiques", "desc": "Finances publiques"},
    {"q": "loi finances", "desc": "Loi de finances"},
]

# URLs directes pour les rapports budgétaires annuels (PDF)
# Pattern : finances.gov.ma/Publication/db/{year}/BC LF {year} VFr.pdf
CURRENT_YEAR = 2026
BUDGET_YEARS = list(range(CURRENT_YEAR - 5, CURRENT_YEAR + 1))  # 5 dernières années
DIRECT_BUDGET_URLS = [
    {
        "url": f"https://www.finances.gov.ma/Publication/db/{y}/BC%20LF%20{y}%20VFr.pdf",
        "desc": f"Budget consolidated LF {y}",
        "year": str(y),
    }
    for y in BUDGET_YEARS
]

logger = get_logger(SOURCE)


# ---------------------------------------------------------------------------
# 1. Collecte via CKAN API (propre)
# ---------------------------------------------------------------------------
def collect_ckan() -> list[dict]:
    """Interroge CKAN pour les jeux de données du Ministère des Finances."""
    session = make_session(SOURCE)
    downloads_info = []
    seen_urls: set[str] = set()

    for query_cfg in CKAN_QUERIES:
        q = query_cfg["q"]
        logger.info("Requête CKAN : '%s' (Finances)", q)

        try:
            resp = session.get(
                f"{CKAN_API}/package_search",
                params={
                    "q": q,
                    "rows": 50,
                    "fq": "organization:ministere-de-l-economie-et-des-finances",
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("Erreur API CKAN pour '%s' : %s", q, exc)
            continue

        if not data.get("success"):
            continue

        results = data.get("result", {}).get("results", [])
        logger.info("  -> %d jeux trouvés", len(results))

        for pkg in results:
            pkg_name = pkg.get("name", "unknown")
            for resource in pkg.get("resources", []):
                url = resource.get("url", "")
                fmt = (resource.get("format") or "").upper()
                res_name = resource.get("name") or resource.get("description") or ""

                if fmt not in ("XLSX", "XLS", "CSV", "JSON", "XML", "PDF"):
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
                        "description": f"{query_cfg['desc']} — {res_name}",
                        "ckan_package": pkg_name,
                        "fichier": str(dest.relative_to(RAW_ROOT)),
                    })

    return downloads_info


# ---------------------------------------------------------------------------
# 2. Téléchargements directs (propre — URL prédictibles)
# ---------------------------------------------------------------------------
def collect_direct_downloads() -> list[dict]:
    """
    Télécharge les rapports budgétaires annuels depuis finances.gov.ma.
    Les URL suivent un pattern prédictible par année.
    """
    session = make_session(SOURCE)
    downloads_info = []

    for entry in DIRECT_BUDGET_URLS:
        url = entry["url"]
        year = entry["year"]
        fname = filename_from_url(url)
        dest = dest_for(SOURCE, year, fname)

        logger.info("Téléchargement direct : %s", entry["desc"])
        success = download_file(session, url, dest, logger)
        if success and dest.exists() and dest.stat().st_size > 0:
            downloads_info.append({
                "url": url,
                "format": "PDF",
                "description": entry["desc"],
                "fichier": str(dest.relative_to(RAW_ROOT)),
            })

    return downloads_info


# ---------------------------------------------------------------------------
# 3. Scraping HTML finances.gov.ma (FRAGILE)
# ---------------------------------------------------------------------------
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#  SECTION FRAGILE : Scraping du site finances.gov.ma
#
#  Le site publie des listes de documents (PDF, XLSX) sur des pages
#  de publications. Les sélecteurs CSS ci-dessous ciblent ces liens.
#
#  Ces sélecteurs sont SUJETS À CHANGEMENT.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

FINANCES_PUB_URLS = [
    "https://www.finances.gov.ma/fr/publications",
    "https://www.finances.gov.ma/fr/etudes-et-rapports",
]


def scraping_finances_fragile() -> list[dict]:
    """
    [FRAGILE] Scrape les pages de publications de finances.gov.ma
    pour récupérer les liens vers les documents officiels.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("BeautifulSoup non installé. Skipping scraping finances.gov.ma.")
        return []

    session = make_session(SOURCE)
    downloads_info = []

    for page_url in FINANCES_PUB_URLS:
        logger.info("[SCRAPING FRAGILE] %s", page_url)

        try:
            resp = session.get(page_url, timeout=60)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Échec accès %s : %s", page_url, exc)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # -----------------------------------------------------------------
        # SÉLECTEURS CSS FRAGILS — adapter si le site change
        # -----------------------------------------------------------------
        download_links = set()

        # Tous les liens <a> vers des fichiers documents
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            lower_href = href.lower()

            # Fichiers documents
            if any(ext in lower_href for ext in (".pdf", ".xlsx", ".xls", ".csv")):
                if href.startswith("http"):
                    download_links.add(href)
                elif href.startswith("/"):
                    download_links.add(f"https://www.finances.gov.ma{href}")

            # Liens contenant "download" ou "télécharger"
            if "download" in lower_href or "telecharg" in lower_href:
                if href.startswith("http"):
                    download_links.add(href)
                elif href.startswith("/"):
                    download_links.add(f"https://www.finances.gov.ma{href}")

        # Éléments avec data-href ou data-url
        for tag in soup.find_all(attrs={"data-href": True}):
            download_links.add(tag["data-href"])
        for tag in soup.find_all(attrs={"data-url": True}):
            download_links.add(tag["data-url"])

        logger.info("  -> %d liens trouvés", len(download_links))

        for url in download_links:
            fname = filename_from_url(url)
            year = year_from_filename(fname)
            dest = dest_for(SOURCE, year, fname)

            success = download_file(session, url, dest, logger)
            if success and dest.exists() and dest.stat().st_size > 0:
                ext = fname.rsplit(".", 1)[-1].upper() if "." in fname else "UNKNOWN"
                downloads_info.append({
                    "url": url,
                    "format": ext,
                    "description": f"Publication MEF — {fname}",
                    "fichier": str(dest.relative_to(RAW_ROOT)),
                    "fragile": True,
                })

    return downloads_info


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("DÉBUT COLLECTE FINANCES — %s", SOURCE)
    logger.info("=" * 60)

    # 1. CKAN (propre)
    logger.info("--- Phase 1 : API CKAN data.gov.ma ---")
    ckan_downloads = collect_ckan()

    # 2. Téléchargements directs (propre)
    logger.info("--- Phase 2 : Téléchargements directs finances.gov.ma ---")
    direct_downloads = collect_direct_downloads()

    # 3. Scraping (fragile)
    logger.info("--- Phase 3 : Scraping finances.gov.ma [FRAGILE] ---")
    scraping_downloads = scraping_finances_fragile()

    all_downloads = ckan_downloads + direct_downloads + scraping_downloads

    meta_path = write_meta(
        dest_dir=RAW_ROOT / SOURCE,
        source="Ministère de l'Économie et des Finances",
        urls=all_downloads,
        periodicite="Annuelle",
        granularite="Nationale",
        date_debut_reelle="2000",
        extra={
            "source_primaire": "https://www.finances.gov.ma",
            "portail_ckan": "https://www.data.gov.ma/data/fr/organization/ministere-de-l-economie-et-des-finances",
        },
    )
    logger.info("meta.json écrit -> %s", meta_path)
    logger.info("FIN COLLECTE FINANCES — %d fichiers téléchargés", len(all_downloads))

    return all_downloads


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results else 1)
