"""
collect_hcp.py — Collecte des données du Haut-Commissariat au Plan (HCP)

Sources :
  1. API CKAN data.gov.ma (organisme "haut-commissariat-au-plan")
     → PIB, IPC, chômage, comptes nationaux
  2. BDS hcp.ma (Base de Données Statistiques)
     → scraping HTML (sélecteurs CSS, fragile)

Usage :
    python collect_hcp.py
"""

import json
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
SOURCE = "hcp"
CKAN_API = "https://www.data.gov.ma/data/api/3/action"
CKAN_BASE_DL = "https://www.data.gov.ma/data/fr/dataset"

# Requêtes CKAN ciblant les jeux HCP pertinents pour l'économie
CKAN_QUERIES = [
    # PIB & comptes nationaux
    {"q": "PIB", "desc": "PIB et comptes nationaux"},
    {"q": "valeur ajoutée", "desc": "Valeurs ajoutées sectorielles"},
    # IPC / inflation
    {"q": "IPC", "desc": "Indice des Prix à la Consommation"},
    {"q": "inflation", "desc": "Inflation"},
    # Emploi / chômage
    {"q": "chômage", "desc": "Taux de chômage"},
    {"q": "emploi", "desc": "Enquête emploi"},
]

logger = get_logger(SOURCE)


# ---------------------------------------------------------------------------
# 1. Collecte via CKAN API (propre, fiable)
# ---------------------------------------------------------------------------
def collect_ckan() -> list[dict]:
    """
    Interroge l'API CKAN de data.gov.ma pour chaque requête,
    télécharge toutes les ressources XLSX/CSV trouvées.
    Retourne la liste des métadonnées de téléchargement.
    """
    session = make_session(SOURCE)
    downloads_info = []
    seen_urls: set[str] = set()

    for query_cfg in CKAN_QUERIES:
        q = query_cfg["q"]
        logger.info("Requête CKAN : '%s'", q)

        try:
            resp = session.get(
                f"{CKAN_API}/package_search",
                params={"q": q, "rows": 50, "fq": "organization:haut-commissariat-au-plan"},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("Erreur API CKAN pour '%s' : %s", q, exc)
            continue

        if not data.get("success"):
            logger.warning("API CKAN a retourné success=false pour '%s'", q)
            continue

        results = data.get("result", {}).get("results", [])
        logger.info("  → %d jeux trouvés pour '%s'", len(results), q)

        for pkg in results:
            pkg_name = pkg.get("name", "unknown")
            for resource in pkg.get("resources", []):
                url = resource.get("url", "")
                fmt = (resource.get("format") or "").upper()
                res_name = resource.get("name") or resource.get("description") or ""

                # Ne télécharger que les fichiers structurés
                if fmt not in ("XLSX", "XLS", "CSV", "JSON", "XML"):
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
# 2. Scraping BDS hcp.ma (FRAGILE — sélecteurs CSS)
# ---------------------------------------------------------------------------
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#  SECTION FRAGILE : Scraping HTML du portail BDS du HCP
#
#  Ces sélecteurs CSS dépendent du rendu du site bds.hcp.ma.
#  Toute refonte du site cassera ce code.
#  À surveiller / adapter régulièrement.
#
#  Le BDS propose des téléchargements directs de tableaux XLSX.
#  Les URL de téléchargement suivent un pattern REST-like.
#  On tente ici de récupérer la page d'accueil pour extraire
#  les liens de téléchargement.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

BDS_BASE = "https://bds.hcp.ma"

# Pages ciblées du BDS (mots-clés → URLs relatives)
BDS_PAGES = {
    "pib": "/bds/Theme/Tableau.aspx?theme=614",
    "ipc": "/bds/Theme/Tableau.aspx?theme=212",
    "chomage": "/bds/Theme/Tableau.aspx?theme=672",
}


def scraping_bds_fragile() -> list[dict]:
    """
    [FRAGILE] Tente de récupérer des fichiers depuis le BDS du HCP.
    Utilise requests pour récupérer les pages et BeautifulSoup pour
    extraire les liens de téléchargement.

    NOTE : Ce scraping est susceptible de casser si le site est refondu.
    Les sélecteurs CSS ci-dessous sont à adapter en cas de changement.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning(
            "BeautifulSoup non installé (pip install beautifulsoup4). "
            "Skipping scraping BDS."
        )
        return []

    session = make_session(SOURCE)
    downloads_info = []

    for key, relative_url in BDS_PAGES.items():
        full_url = f"{BDS_BASE}{relative_url}"
        logger.info("[SCRAPING FRAGILE] BDS page '%s' : %s", key, full_url)

        try:
            resp = session.get(full_url, timeout=60)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Échec accès BDS page '%s' : %s", key, exc)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # -----------------------------------------------------------------
        # SÉLECTEURS CSS FRAGILS — adapter si le site change
        # -----------------------------------------------------------------
        # Le BDS utilise des liens <a> avec des classes spécifiques
        # pour les téléchargements XLSX. On cherche tous les liens
        # contenant ".xlsx" ou des classes liées au téléchargement.
        download_links = set()

        # Stratégie 1 : liens <a> dont href contient .xlsx
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if ".xlsx" in href.lower() or "download" in href.lower():
                if href.startswith("http"):
                    download_links.add(href)
                elif href.startswith("/"):
                    download_links.add(f"{BDS_BASE}{href}")

        # Stratégie 2 : boutons/éléments avec attribut data-url ou data-href
        for tag in soup.find_all(attrs={"data-url": True}):
            download_links.add(tag["data-url"])
        for tag in soup.find_all(attrs={"data-href": True}):
            download_links.add(tag["data-href"])

        logger.info("  → %d liens de téléchargement trouvés pour '%s'", len(download_links), key)

        for url in download_links:
            fname = filename_from_url(url)
            year = year_from_filename(fname)
            dest = dest_for(SOURCE, year, fname)

            success = download_file(session, url, dest, logger)
            if success and dest.exists() and dest.stat().st_size > 0:
                downloads_info.append({
                    "url": url,
                    "format": "XLSX",
                    "description": f"BDS HCP — {key}",
                    "fichier": str(dest.relative_to(RAW_ROOT)),
                    "fragile": True,
                })

    return downloads_info


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("DÉBUT COLLECTE HCP — %s", SOURCE)
    logger.info("=" * 60)

    # 1. CKAN (propre)
    logger.info("--- Phase 1 : API CKAN data.gov.ma ---")
    ckan_downloads = collect_ckan()

    # 2. BDS (fragile)
    logger.info("--- Phase 2 : Scraping BDS hcp.ma [FRAGILE] ---")
    bds_downloads = scraping_bds_fragile()

    all_downloads = ckan_downloads + bds_downloads

    # meta.json
    meta_path = write_meta(
        dest_dir=RAW_ROOT / SOURCE,
        source="Haut-Commissariat au Plan (HCP)",
        urls=all_downloads,
        periodicite="Trimestrielle / Annuelle",
        granularite="Nationale, régionale",
        date_debut_reelle="1955",
        extra={
            "source_primaire": "https://www.hcp.ma",
            "portail_bds": "https://bds.hcp.ma",
            "portail_ckan": "https://www.data.gov.ma/data/fr/organization/haut-commissariat-au-plan",
        },
    )
    logger.info("meta.json écrit → %s", meta_path)
    logger.info("FIN COLLECTE HCP — %d fichiers téléchargés", len(all_downloads))

    return all_downloads


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results else 1)
