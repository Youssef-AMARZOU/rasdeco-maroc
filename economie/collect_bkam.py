"""
collect_bkam.py — Collecte des données de Bank Al-Maghrib (BAM)

Sources :
  1. API CKAN data.gov.ma (organisme "bank-al-maghrib")
     → statistiques monétaires, balance des paiements, change
  2. API REST officielle BAM (apihelpdesk.centralbankofmorocco.ma)
     → Taux directeur, cours de change, adjudications
     → Nécessite une clé API gratuite (à configurer si disponible)
  3. Scraping HTML bkam.ma (FRAGILE)
     → pages de statistiques monétaires si l'API n'est pas dispo

Usage :
    python collect_bkam.py
"""

import json
import os
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
SOURCE = "bkam"
CKAN_API = "https://www.data.gov.ma/data/api/3/action"

# Clé API BAM (optionnelle — obtenez-la sur apihelpdesk.centralbankofmorocco.ma)
BAM_API_KEY = os.environ.get("BAM_API_KEY", "")
BAM_API_BASE = "https://apihelpdesk.centralbankofmorocco.ma"

CKAN_QUERIES = [
    {"q": "monétaire", "desc": "Statistiques monétaires"},
    {"q": "taux directeur", "desc": "Taux directeur BAM"},
    {"q": "change", "desc": "Cours de change"},
    {"q": "balance paiements", "desc": "Balance des paiements"},
    {"q": "trésor", "desc": "Adjudications Trésor"},
]

logger = get_logger(SOURCE)


# ---------------------------------------------------------------------------
# 1. Collecte via CKAN API (propre)
# ---------------------------------------------------------------------------
def collect_ckan() -> list[dict]:
    """Interroge CKAN pour les jeux de données BAM."""
    session = make_session(SOURCE)
    downloads_info = []
    seen_urls: set[str] = set()

    for query_cfg in CKAN_QUERIES:
        q = query_cfg["q"]
        logger.info("Requête CKAN : '%s' (BAM)", q)

        try:
            resp = session.get(
                f"{CKAN_API}/package_search",
                params={"q": q, "rows": 50, "fq": "organization:bank-al-maghrib"},
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
        logger.info("  → %d jeux trouvés", len(results))

        for pkg in results:
            pkg_name = pkg.get("name", "unknown")
            for resource in pkg.get("resources", []):
                url = resource.get("url", "")
                fmt = (resource.get("format") or "").upper()
                res_name = resource.get("name") or resource.get("description") or ""

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
# 2. API REST officielle BAM (propre, nécessite clé API)
# ---------------------------------------------------------------------------
# Endpoints documentés de l'API BAM :
#   - /api/v1/taux-directeurs    → taux directeur
#   - /api/v1/cours-change       → cours de change
#   - /api/v1/adjudications      → adjudications du Trésor
#   - /api/v1/statistiques-monetaires → agrégats monétaires
#
# La clé API se obtient gratuitement sur :
#   https://apihelpdesk.centralbankofmorocco.ma/

BAM_ENDPOINTS = {
    "taux_directeur": {
        "path": "/api/v1/taux-directeurs",
        "desc": "Taux directeur BAM",
    },
    "cours_change": {
        "path": "/api/v1/cours-change",
        "desc": "Cours de change officiels",
    },
    "adjudications": {
        "path": "/api/v1/adjudications",
        "desc": "Marché des adjudications Trésor",
    },
    "stats_monetaires": {
        "path": "/api/v1/statistiques-monetaires",
        "desc": "Agrégats et statistiques monétaires",
    },
}


def collect_bam_api() -> list[dict]:
    """
    Appelle l'API REST officielle de Bank Al-Maghrib.
    Nécessite la variable d'environnement BAM_API_KEY.
    """
    if not BAM_API_KEY:
        logger.warning(
            "Clé API BAM non configurée. "
            "Inscrivez-vous sur %s et définissez BAM_API_KEY.",
            BAM_API_BASE,
        )
        logger.info("Skipping API BAM — utilisation de CKAN uniquement.")
        return []

    session = make_session(SOURCE)
    session.headers["X-API-KEY"] = BAM_API_KEY  # type: ignore[attr-defined]
    downloads_info = []

    for key, endpoint in BAM_ENDPOINTS.items():
        url = f"{BAM_API_BASE}{endpoint['path']}"
        logger.info("API BAM : %s", endpoint["desc"])

        try:
            resp = session.get(url, timeout=60)
            resp.raise_for_status()
        except Exception as exc:
            logger.error("Erreur API BAM '%s' : %s", key, exc)
            continue

        # L'API retourne du JSON ; on le sauvegarde tel quel
        content_type = resp.headers.get("Content-Type", "")

        if "json" in content_type:
            fname = f"{key}.json"
            year = "latest"
            dest = dest_for(SOURCE, year, fname)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(resp.text)
            logger.info("OK (JSON) : %s", fname)
            downloads_info.append({
                "url": url,
                "format": "JSON",
                "description": endpoint["desc"],
                "fichier": str(dest.relative_to(RAW_ROOT)),
            })
        else:
            # Si l'API renvoie un fichier (xlsx, csv...)
            fname_raw = filename_from_url(url)
            year = "latest"
            dest = dest_for(SOURCE, year, fname_raw)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                f.write(resp.content)
            logger.info("OK (%s) : %s", content_type, fname_raw)
            downloads_info.append({
                "url": url,
                "format": content_type.split("/")[-1].upper(),
                "description": endpoint["desc"],
                "fichier": str(dest.relative_to(RAW_ROOT)),
            })

    return downloads_info


# ---------------------------------------------------------------------------
# 3. Scraping HTML bkam.ma (FRAGILE)
# ---------------------------------------------------------------------------
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#  SECTION FRAGILE : Scraping du site bkam.ma
#
#  Le site BAM propose des tableaux de statistiques monétaires
#  et des séries temporelles en HTML. Les sélecteurs ci-dessous
#  ciblent ces tableaux pour extraire les données ou les liens
#  de téléchargement.
#
#  Ces sélecteurs sont SUJETS À CHANGEMENT lors de refonte du site.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

BKAM_STATS_URL = "https://www.bkam.ma/Statistiques/Calendrier/Statistiques-monetaires"


def scraping_bkam_fragile() -> list[dict]:
    """
    [FRAGILE] Tente de récupérer les liens de téléchargement
    depuis la page des statistiques monétaires de bkam.ma.

    Le site propose parfois des liens XLSX/PDF en bas de tableaux.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.warning("BeautifulSoup non installé. Skipping scraping bkam.ma.")
        return []

    session = make_session(SOURCE)
    downloads_info = []

    logger.info("[SCRAPING FRAGILE] Page stats monétaires BKAM : %s", BKAM_STATS_URL)

    try:
        resp = session.get(BKAM_STATS_URL, timeout=60)
        resp.raise_for_status()
    except Exception as exc:
        logger.error("Échec accès bkam.ma : %s", exc)
        return downloads_info

    soup = BeautifulSoup(resp.text, "html.parser")

    # -----------------------------------------------------------------
    # SÉLECTEURS CSS FRAGILS — adapter si le site change
    # -----------------------------------------------------------------
    download_links = set()

    # Stratégie 1 : liens directs vers fichiers
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        lower_href = href.lower()
        if any(ext in lower_href for ext in (".xlsx", ".xls", ".csv", ".pdf")):
            if href.startswith("http"):
                download_links.add(href)
            elif href.startswith("/"):
                download_links.add(f"https://www.bkam.ma{href}")

    # Stratégie 2 : boutons de téléchargement (class="download" ou id="download")
    for tag in soup.find_all(["a", "button"], class_=lambda c: c and "download" in str(c).lower()):
        href = tag.get("href") or tag.get("data-url") or ""
        if href:
            if href.startswith("http"):
                download_links.add(href)
            elif href.startswith("/"):
                download_links.add(f"https://www.bkam.ma{href}")

    logger.info("  → %d liens de téléchargement trouvés", len(download_links))

    for url in download_links:
        fname = filename_from_url(url)
        year = year_from_filename(fname)
        dest = dest_for(SOURCE, year, fname)

        success = download_file(session, url, dest, logger)
        if success and dest.exists() and dest.stat().st_size > 0:
            downloads_info.append({
                "url": url,
                "format": fname.rsplit(".", 1)[-1].upper() if "." in fname else "UNKNOWN",
                "description": f"Stats monétaires BKAM — {fname}",
                "fichier": str(dest.relative_to(RAW_ROOT)),
                "fragile": True,
            })

    return downloads_info


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    logger.info("=" * 60)
    logger.info("DÉBUT COLLECTE BKAM — %s", SOURCE)
    logger.info("=" * 60)

    # 1. CKAN (propre)
    logger.info("--- Phase 1 : API CKAN data.gov.ma ---")
    ckan_downloads = collect_ckan()

    # 2. API REST BAM (propre, si clé dispo)
    logger.info("--- Phase 2 : API REST Bank Al-Maghrib ---")
    api_downloads = collect_bam_api()

    # 3. Scraping bkam.ma (fragile)
    logger.info("--- Phase 3 : Scraping bkam.ma [FRAGILE] ---")
    scraping_downloads = scraping_bkam_fragile()

    all_downloads = ckan_downloads + api_downloads + scraping_downloads

    meta_path = write_meta(
        dest_dir=RAW_ROOT / SOURCE,
        source="Bank Al-Maghrib (BAM)",
        urls=all_downloads,
        periodicite="Mensuelle / Hebdomadaire",
        granularite="Nationale",
        date_debut_reelle="1959",
        extra={
            "source_primaire": "https://www.bkam.ma",
            "api_officielle": BAM_API_BASE,
            "portail_ckan": "https://www.data.gov.ma/data/fr/organization/bank-al-maghrib",
            "note_api": "Clé API requise (BAM_API_KEY). Inscription gratuite sur apihelpdesk.centralbankofmorocco.ma",
        },
    )
    logger.info("meta.json écrit → %s", meta_path)
    logger.info("FIN COLLECTE BKAM — %d fichiers téléchargés", len(all_downloads))

    return all_downloads


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results else 1)
