"""
collect_office_des_changes.py — Collecte de l'Office des Changes (OC)

Sources :
  1. Publications officielles oc.gov.ma
     -> rapports annuels, bulletins mensuels (PDF/XLSX)
  2. Scraper la page des séries statistiques
     -> réserves de change, IDE, balance commerciale
  3. API CKAN data.gov.ma (recherche "office changes" / "changes")

Usage :
    python collect_office_des_changes.py
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
SOURCE = "office_des_changes"
CKAN_API = "https://www.data.gov.ma/data/api/3/action"
OC_BASE = "https://www.oc.gov.ma"

CKAN_QUERIES = [
    {"q": "office changes", "desc": "Office des Changes"},
    {"q": "investissements étrangers", "desc": "IDE"},
    {"q": "réserves change", "desc": "Réserves de change"},
    {"q": "balance commerciale", "desc": "Balance commerciale"},
]

# URLs de publications connues (pattern prévisible)
CURRENT_YEAR = 2026
OC_PUBLICATIONS = [
    # Bulletins mensuels (pattern annuel)
    {
        "url": f"{OC_BASE}/wp-content/uploads/{y}/bulletin-{y}.pdf",
        "desc": f"Bulletin mensuel OC {y}",
        "year": str(y),
    }
    for y in range(CURRENT_YEAR - 5, CURRENT_YEAR + 1)
]

logger = get_logger(SOURCE)


# ---------------------------------------------------------------------------
# 1. Collecte via CKAN API (propre)
# ---------------------------------------------------------------------------
def collect_ckan() -> list[dict]:
    """Interroge CKAN pour les jeux liés à l'Office des Changes."""
    session = make_session(SOURCE)
    downloads_info = []
    seen_urls: set[str] = set()

    for query_cfg in CKAN_QUERIES:
        q = query_cfg["q"]
        logger.info("Requête CKAN : '%s' (OC)", q)

        try:
            resp = session.get(
                f"{CKAN_API}/package_search",
                params={"q": q, "rows": 50},
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
# 2. Téléchargements directs OC (propre)
# ---------------------------------------------------------------------------
def collect_direct_publications() -> list[dict]:
    """Tente de récupérer les publications officielles OC par URL pattern."""
    session = make_session(SOURCE)
    downloads_info = []

    for entry in OC_PUBLICATIONS:
        url = entry["url"]
        year = entry["year"]
        fname = filename_from_url(url)
        dest = dest_for(SOURCE, year, fname)

        logger.info("Publication OC directe : %s", entry["desc"])
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
# 3. Scraping OC (FRAGILE)
# ---------------------------------------------------------------------------
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#  SECTION FRAGILE : Scraping de oc.gov.ma
#
#  L'Office des Changes publie des séries statistiques et des
#  bulletins sur son portail. Les sélecteurs ci-dessous extraient
#  les liens de téléchargement depuis les pages publications.
#
#  SUJET À CHANGEMENT lors de refonte du site.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

OC_SCRAPE_PAGES = [
    f"{OC_BASE}/fr/publications",
    f"{OC_BASE}/fr/etudes-et-statistiques",
    f"{OC_BASE}/fr/series-statistiques",
]


def scraping_oc_fragile() -> list[dict]:
    """
    [FRAGILE] Scrape les pages de publications/études de oc.gov.ma.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("BeautifulSoup non installé. Skipping scraping OC.")
        return []

    session = make_session(SOURCE)
    downloads_info = []

    for page_url in OC_SCRAPE_PAGES:
        logger.info("[SCRAPING FRAGILE] %s", page_url)

        try:
            resp = session.get(page_url, timeout=60)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Échec accès %s : %s", page_url, exc)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # -----------------------------------------------------------------
        # SÉLECTEURS CSS FRAGILS
        # -----------------------------------------------------------------
        download_links = set()

        # Liens <a> vers fichiers
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            lower_href = href.lower()
            if any(ext in lower_href for ext in (".pdf", ".xlsx", ".xls", ".csv")):
                if href.startswith("http"):
                    download_links.add(href)
                elif href.startswith("/"):
                    download_links.add(f"{OC_BASE}{href}")

        # Boutons de téléchargement (class contain "download")
        for tag in soup.find_all(["a", "button"], class_=lambda c: c and "download" in str(c).lower()):
            href = tag.get("href") or tag.get("data-url") or ""
            if href:
                if href.startswith("http"):
                    download_links.add(href)
                elif href.startswith("/"):
                    download_links.add(f"{OC_BASE}{href}")

        # data-href / data-url
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
                    "description": f"Publication OC — {fname}",
                    "fichier": str(dest.relative_to(RAW_ROOT)),
                    "fragile": True,
                })

    return downloads_info


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("DÉBUT COLLECTE OFFICE DES CHANGES — %s", SOURCE)
    logger.info("=" * 60)

    # 1. CKAN (propre)
    logger.info("--- Phase 1 : API CKAN data.gov.ma ---")
    ckan_downloads = collect_ckan()

    # 2. Téléchargements directs (propre)
    logger.info("--- Phase 2 : Publications directes OC ---")
    direct_downloads = collect_direct_publications()

    # 3. Scraping (fragile)
    logger.info("--- Phase 3 : Scraping oc.gov.ma [FRAGILE] ---")
    scraping_downloads = scraping_oc_fragile()

    all_downloads = ckan_downloads + direct_downloads + scraping_downloads

    meta_path = write_meta(
        dest_dir=RAW_ROOT / SOURCE,
        source="Office des Changes (OC)",
        urls=all_downloads,
        periodicite="Mensuelle / Annuelle",
        granularite="Nationale",
        date_debut_reelle="1970",
        extra={
            "source_primaire": "https://www.oc.gov.ma",
            "portail_ckan": "https://www.data.gov.ma/data/fr/organization/office-des-changes",
        },
    )
    logger.info("meta.json écrit -> %s", meta_path)
    logger.info("FIN COLLECTE OC — %d fichiers téléchargés", len(all_downloads))

    return all_downloads


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results else 1)
