"""
utils.py — Fonctions partagées pour le pipeline Économie RASD-Maroc.

Fournit :
  - Session HTTP avec retry/backoff exponentiel
  - Logger structuré par source
  - Écriture du meta.json par jeu téléchargé
  - Utilitaires de gestion de fichiers et doublons
"""

import json
import logging
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Hotes a ignorer (ne resolvent pas le DNS)
HOSTS_IGNORES = frozenset({"datagovma.webhi.net"})

# ---------------------------------------------------------------------------
# Racine du projet (un niveau au-dessus de economie/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "economie"


# ---------------------------------------------------------------------------
# Session HTTP avec retry / backoff exponentiel
# ---------------------------------------------------------------------------
def make_session(
    source_name: str,
    max_retries: int = 5,
    backoff_factor: float = 1.5,
    status_forcelist: tuple = (429, 500, 502, 503, 504),
    timeout: int = 120,
) -> requests.Session:
    """
    Crée une requests.Session avec :
      - retry automatique (backoff exponentiel)
      - User-Agent identifiant le projet
      - timeout configurable
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "User-Agent": "RASD-Maroc-Pipeline/1.0 (collecte economie; contact: rasd-maroc@example.com)",
        "Accept": "*/*",
    })
    session.timeout = timeout  # type: ignore[attr-defined]

    return session


def download_file(
    session: requests.Session,
    url: str,
    dest_path: Path,
    logger: logging.Logger,
) -> bool:
    """
    Télécharge un fichier avec streaming. Retourne True si succès.
    Gère les fichiers existants (skip si déjà présent).
    """
    if dest_path.exists() and dest_path.stat().st_size > 0:
        logger.info("SKIP (deja present) : %s", dest_path.name)
        return True

    # Verification rapide DNS pour les hotes connus comme morts
    host = urlparse(url).hostname
    if host in HOSTS_IGNORES:
        logger.warning("HOTE ignore (ne repond pas) : %s", host)
        return False

    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with session.get(url, stream=True, timeout=session.timeout) as resp:  # type: ignore[attr-defined]
            resp.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
        size_kb = dest_path.stat().st_size / 1024
        logger.info("OK (%.1f KB) : %s", size_kb, dest_path.name)
        return True
    except requests.RequestException as exc:
        logger.error("ECHEC telechargement %s -> %s", url, exc)
        if dest_path.exists():
            dest_path.unlink()
        return False


# ---------------------------------------------------------------------------
# Logger par source
# ---------------------------------------------------------------------------
def get_logger(source_name: str) -> logging.Logger:
    """
    Logger avec sortie console + fichier data/raw/economie/<source>/collect.log
    """
    logger = logging.getLogger(f"rasd.{source_name}")
    if logger.handlers:
        return logger  # déjà initialisé

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-7s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Fichier
    log_dir = RAW_ROOT / source_name
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "collect.log", mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


# ---------------------------------------------------------------------------
# meta.json
# ---------------------------------------------------------------------------
def write_meta(
    dest_dir: Path,
    source: str,
    urls: list[dict[str, Any]],
    periodicite: str,
    granularite: str = "Nationale",
    date_debut_reelle: Optional[str] = None,
    extra: Optional[dict] = None,
) -> Path:
    """
    Écrit meta.json dans dest_dir.

    Paramètres
    ----------
    urls : liste de {"url": ..., "description": ..., "format": ...}
    periodicite : ex. "Trimestrielle", "Mensuelle", "Annuelle"
    """
    now = datetime.now(timezone.utc).isoformat()
    meta = {
        "source": source,
        "date_recuperation": now,
        "organisme": source,
        "periodicite": periodicite,
        "granularite_geographique": granularite,
        "date_debut_reelle_donnees": date_debut_reelle or "Non déterminé",
        "jeux_telecharges": urls,
    }
    if extra:
        meta.update(extra)

    meta_path = dest_dir / "meta.json"
    dest_dir.mkdir(parents=True, exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def filename_from_url(url: str) -> str:
    """Extrait le nom de fichier propre depuis une URL."""
    parsed = urlparse(url)
    name = Path(unquote(parsed.path)).name
    return name or "download"


def year_from_filename(name: str) -> str:
    """Tire l'année d'un nom de fichier, fallback 'undated'."""
    import re
    match = re.search(r"(20[0-2]\d|19\d\d)", name)
    return match.group(0) if match else "undated"


def dest_for(source: str, year: str, filename: str) -> Path:
    """Construit le chemin data/raw/economie/<source>/<year>/<filename>."""
    path = RAW_ROOT / source / year
    path.mkdir(parents=True, exist_ok=True)
    return path / filename
