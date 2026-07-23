"""
parsers/base.py -- Classe abstraite et helpers pour tous les parsers source.

Chaque parser source :
  1. Scanne son dossier data/raw/economie/<source>/
  2. Detecte les formats (XLSX, CSV, JSON, PDF)
  3. Extrait les series et les mappe vers le schema pivot fact_indicateurs
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Optional

import polars as pl
import polars.selectors as cs

from ..schema import empty_fact

RAW_ROOT = Path(__file__).resolve().parents[3] / "data" / "raw" / "economie"


# ---------------------------------------------------------------------------
# Logging helper silencieux (evite dependance circulaire)
# ---------------------------------------------------------------------------
def _log(source: str, msg: str, level: str = "INFO"):
    print(f"[{level}] [{source}] {msg}")


# ---------------------------------------------------------------------------
# Structure de sortie d'un parser
# ---------------------------------------------------------------------------
class ParsedFile:
    """Resultat du parsing d'un fichier brut."""

    def __init__(
        self,
        fichier_relatif: str,
        lignes: pl.DataFrame | None = None,
        erreur: str | None = None,
    ):
        self.fichier_relatif = fichier_relatif
        self.lignes = lignes if lignes is not None else empty_fact()
        self.erreur = erreur

    def __bool__(self) -> bool:
        return self.erreur is None and len(self.lignes) > 0


# ---------------------------------------------------------------------------
# Codes indicateurs normalises
# ---------------------------------------------------------------------------
INDICATOR_CODES: dict[str, dict] = {
    # PIB & croissance
    "PIB.TRIM.VOL": {"label": "PIB trimestriel (volume)", "domaine": "CN", "unite": "MAD"},
    "PIB.ANNUEL.VOL": {"label": "PIB annuel (volume)", "domaine": "CN", "unite": "MAD"},
    "PIB.CROISSANCE": {"label": "Croissance PIB (%)", "domaine": "CN", "unite": "%"},
    "PIB.TETE": {"label": "PIB par tete", "domaine": "CN", "unite": "MAD"},
    "VAB.AGRICULTURE": {"label": "Valeur ajoutee agriculture", "domaine": "CN", "unite": "MAD"},
    "VAB.INDUSTRIE": {"label": "Valeur ajoutee industrie", "domaine": "CN", "unite": "MAD"},
    "VAB.SERVICES": {"label": "Valeur ajoutee services", "domaine": "CN", "unite": "MAD"},
    # IPC / inflation
    "IPC.INDICE": {"label": "Indice des prix a la consommation", "domaine": "PRIX", "unite": "Base100"},
    "IPC.GLISSEMENT": {"label": "Inflation glissement annuel (%)", "domaine": "PRIX", "unite": "%"},
    "IPC.MENSUEL": {"label": "Inflation mensuelle (%)", "domaine": "PRIX", "unite": "%"},
    # Chomage / emploi
    "CHOMAGE.TAUX": {"label": "Taux de chomage", "domaine": "EMPLOI", "unite": "%"},
    "CHOMAGE.TAUX.URBAIN": {"label": "Taux de chomage urbain", "domaine": "EMPLOI", "unite": "%"},
    "CHOMAGE.TAUX.RURAL": {"label": "Taux de chomage rural", "domaine": "EMPLOI", "unite": "%"},
    "EMPLOI.VOLUME": {"label": "Volume d'emploi", "domaine": "EMPLOI", "unite": "Milliers"},
    # Monetaire
    "TAUX.DIRECTEUR": {"label": "Taux directeur BAM", "domaine": "MONETAIRE", "unite": "%"},
    "M3": {"label": "Agregat M3", "domaine": "MONETAIRE", "unite": "MAD"},
    "CREDIT.ECONOMIE": {"label": "Credit a l'economie", "domaine": "MONETAIRE", "unite": "MAD"},
    # Finances publiques
    "DETTE.PUBLIQUE": {"label": "Dette publique", "domaine": "BUDGET", "unite": "%PIB"},
    "DEFICIT.BUDGET": {"label": "Deficit budgetaire", "domaine": "BUDGET", "unite": "%PIB"},
    "RECETTES": {"label": "Recettes budgetaires", "domaine": "BUDGET", "unite": "MAD"},
    "DEPENSES": {"label": "Depenses budgetaires", "domaine": "BUDGET", "unite": "MAD"},
    "INVESTISSEMENT.PUBLIC": {"label": "Investissement public", "domaine": "BUDGET", "unite": "MAD"},
    # Commerce exterieur
    "EXPORTATIONS": {"label": "Exportations", "domaine": "COMMERCE", "unite": "MAD"},
    "IMPORTATIONS": {"label": "Importations", "domaine": "COMMERCE", "unite": "MAD"},
    "BALANCE.COMMERCIALE": {"label": "Balance commerciale", "domaine": "COMMERCE", "unite": "MAD"},
    # Reserves / IDE
    "RESERVES.CHANGE": {"label": "Reserves de change", "domaine": "EXT", "unite": "Mois_import"},
    "IDE.FLUX": {"label": "Investissements directs etrangers (flux)", "domaine": "EXT", "unite": "MAD"},
    "IDE.STOCK": {"label": "Investissements directs etrangers (stock)", "domaine": "EXT", "unite": "MAD"},
    # Change
    "CHANGE.USD": {"label": "Taux de change USD/MAD", "domaine": "CHANGE", "unite": "MAD"},
    "CHANGE.EUR": {"label": "Taux de change EUR/MAD", "domaine": "CHANGE", "unite": "MAD"},
}


# ---------------------------------------------------------------------------
# Detection des versions de serie (rebasages HCP)
# ---------------------------------------------------------------------------
_VERSION_PATTERNS = [
    (r"base[\s_-]*(20[0-2][0-9])", lambda m: f"base_{m.group(1)}"),
    (r"base[\s_-]*100[\s_-]*(20[0-2][0-9])", lambda m: f"base_{m.group(1)}"),
    (r"ann[ee]e[\s_-]*de[\s_-]*base[\s_-]*(20[0-2][0-9])", lambda m: f"base_{m.group(1)}"),
    (r"20([0-2][0-9])[\s_-]*=[\s_-]*100", lambda m: f"base_20{m.group(1)}"),
]


def detect_version_serie(filename: str, text_sample: str = "") -> str:
    """Detecte la version de serie a partir du nom de fichier et d'un echantillon."""
    combined = f"{filename} {text_sample}".lower()
    for pattern, formatter in _VERSION_PATTERNS:
        match = re.search(pattern, combined)
        if match:
            return formatter(match)
    return "recente"


def detect_code_indicateur(filename: str, text_sample: str = "") -> str | None:
    """Detecte le code indicateur le plus probable."""
    combined = f"{filename} {text_sample}".lower()

    keywords = {
        "pib": "PIB.TRIM.VOL",
        "croissance": "PIB.CROISSANCE",
        "ipc": "IPC.INDICE",
        "inflation": "IPC.GLISSEMENT",
        "chomage": "CHOMAGE.TAUX",
        "chomage": "CHOMAGE.TAUX",
        "emploi": "EMPLOI.VOLUME",
        "taux directeur": "TAUX.DIRECTEUR",
        "m3": "M3",
        "monetaire": "M3",
        "monetaire": "M3",
        "dette": "DETTE.PUBLIQUE",
        "budget": "DEFICIT.BUDGET",
        "recette": "RECETTES",
        "depense": "DEPENSES",
        "depense": "DEPENSES",
        "reserves": "RESERVES.CHANGE",
        "reserves": "RESERVES.CHANGE",
        "ide": "IDE.FLUX",
        "investissement etranger": "IDE.FLUX",
        "change": "CHANGE.USD",
        "export": "EXPORTATIONS",
        "import": "IMPORTATIONS",
        "balance commerciale": "BALANCE.COMMERCIALE",
    }
    for kw, code in keywords.items():
        if kw in combined:
            return code
    return None


def parse_date_label(raw: str) -> tuple[str, str]:
    """
    Convertit une etiquette de date brute en (date_label, date_standard).
    date_standard = 'AAAA-MM-JJ' pour tri, 'AAAA' pour annee seule.
    """
    raw = raw.strip()

    # Annee seule : "2023"
    m = re.match(r"^(\d{4})$", raw)
    if m:
        return raw, f"{m.group(1)}-01-01"

    # Trimestre : "2023-T1", "T1-2023", "2023Q1"
    m = re.match(r"(\d{4})[-\s]?[TQ](\d)", raw)
    if not m:
        m = re.match(r"[TQ](\d)[-\s]?(\d{4})", raw)
    if m:
        y, q = m.groups() if len(m.groups()) == 2 else (m.group(2), m.group(1))
        month_map = {"1": "01", "2": "04", "3": "07", "4": "10"}
        return raw, f"{y}-{month_map.get(q, '01')}-01"

    # Mois : "2023-01", "2023M01", "janvier 2023"
    m = re.match(r"(\d{4})[-\s]?M?(0[1-9]|1[0-2])", raw)
    if m:
        return raw, f"{m.group(1)}-{m.group(2)}-01"

    return raw, f"{raw}-01-01"


def date_from_label(date_label: str) -> str:
    """Retourne une date ISO YYYY-MM-DD depuis n'importe quel format connu."""
    _, std = parse_date_label(date_label)
    return std


# ---------------------------------------------------------------------------
# Classe de base abstraite
# ---------------------------------------------------------------------------
class SourceParser(ABC):
    """Parser source. Scanne un dossier raw, parse chaque fichier."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.source_dir = RAW_ROOT / source_name
        self.now = datetime.now(timezone.utc)

    @property
    @abstractmethod
    def source_code(self) -> str:
        """Code court identifiant la source (HCP, BAM, FIN...)."""

    def list_files(self) -> list[Path]:
        """Liste les fichiers dans data/raw/economie/<source>/, recursivement."""
        if not self.source_dir.exists():
            _log(self.source_name, f"Dossier introuvable : {self.source_dir}", "WARN")
            return []
        files = []
        for ext in ("*.xlsx", "*.xls", "*.csv", "*.json", "*.xml"):
            files.extend(self.source_dir.rglob(ext))
        return sorted(files)

    def parse_all(self) -> pl.DataFrame:
        """Parse tous les fichiers trouves, retourne un DataFrame concatene."""
        chunks: list[pl.DataFrame] = []

        for fpath in self.list_files():
            result = self.parse_file(fpath)
            if result:
                _log(self.source_name, f"OK {result.fichier_relatif} -> {len(result.lignes)} lignes")
                chunks.append(result.lignes)
            else:
                _log(self.source_name, f"X {fpath.relative_to(RAW_ROOT)} -> {result.erreur}", "WARN")

        if not chunks:
            _log(self.source_name, "Aucune donnee parsee", "WARN")
            return empty_fact()

        return pl.concat(chunks, how="vertical")

    @abstractmethod
    def parse_file(self, fpath: Path) -> ParsedFile:
        """Parse un fichier individuel. Retourne ParsedFile."""

    def _make_row(
        self,
        date_label: str,
        valeur: float,
        code_indicateur: str,
        fichier: str,
        region_code: str = "MA00",
        unite: str | None = None,
        qualite_flag: str | None = None,
        version_serie: str | None = None,
    ) -> dict[str, Any]:
        """Construit une ligne normalisee pour le schema fact_indicateurs."""
        _, date_std = parse_date_label(str(date_label))
        indicator_meta = INDICATOR_CODES.get(code_indicateur, {})
        return {
            "date": date_std,
            "date_label": str(date_label),
            "region_code": region_code,
            "domaine_code": indicator_meta.get("domaine", "?"),
            "code_indicateur": code_indicateur,
            "valeur": float(valeur),
            "unite": unite or indicator_meta.get("unite", "?"),
            "source_code": self.source_code,
            "version_serie": version_serie or detect_version_serie(fichier),
            "fiabilite": 2,
            "qualite_flag": qualite_flag,
            "fichier_source": fichier,
            "date_insertion": self.now,
        }

    def _normalize_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """Tente de normaliser les noms de colonnes d'un fichier inconnu."""
        lower_map: dict[str, str] = {}
        for col in df.columns:
            c = col.strip().lower()
            c = re.sub(r"[\s\-_\.]+", "_", c)
            lower_map[col] = c
        return df.rename(lower_map)
