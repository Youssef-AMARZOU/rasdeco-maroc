"""
parsers/parse_bkam.py -- Parser pour les fichiers Bank Al-Maghrib.

Sources :
  - CKAN data.gov.ma (org bank-al-maghrib)
  - API REST BAM (JSON)
  - Scraping bkam.ma
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl

from .base import (
    INDICATOR_CODES,
    ParsedFile,
    SourceParser,
    detect_code_indicateur,
    detect_version_serie,
)


class BKAMParser(SourceParser):
    def __init__(self):
        super().__init__("bkam")

    @property
    def source_code(self) -> str:
        return "BAM"

    def parse_file(self, fpath: Path) -> ParsedFile:
        rel = str(fpath.relative_to(
            Path(__file__).resolve().parents[3] / "data" / "raw" / "economie"
        ))
        ext = fpath.suffix.lower()
        try:
            if ext in (".xlsx", ".xls"):
                return self._parse_xlsx(fpath, rel)
            elif ext == ".csv":
                return self._parse_csv(fpath, rel)
            elif ext == ".json":
                return self._parse_json(fpath, rel)
            else:
                return ParsedFile(rel, erreur=f"Format non supporte : {ext}")
        except Exception as e:
            return ParsedFile(rel, erreur=str(e))

    def _parse_xlsx(self, fpath: Path, rel: str) -> ParsedFile:
        df = pl.read_excel(fpath)
        return self._extract(df, rel)

    def _parse_csv(self, fpath: Path, rel: str) -> ParsedFile:
        df = pl.read_csv(fpath, infer_schema_length=1000, null_values=["", "NA", ".."])
        return self._extract(df, rel)

    def _parse_json(self, fpath: Path, rel: str) -> ParsedFile:
        """
        Parse les fichiers JSON de l'API REST BAM.
        Format attendu : liste d'objets avec date + valeur,
        ou un objet avec cles = dates, valeurs = series.
        """
        with open(fpath) as f:
            data = json.load(f)

        code = detect_code_indicateur(rel)
        version = detect_version_serie(rel)
        rows = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    date_val = item.get("date") or item.get("annee") or item.get("periode") or item.get("period")
                    value = item.get("valeur") or item.get("value") or item.get("montant")
                    if date_val and value is not None:
                        try:
                            rows.append(self._make_row(
                                date_label=str(date_val),
                                valeur=float(value),
                                code_indicateur=code or "TAUX.DIRECTEUR",
                                fichier=rel,
                                version_serie=version,
                            ))
                        except (ValueError, TypeError):
                            pass

        elif isinstance(data, dict):
            # Format { "serie": [...], "values": [...], "dates": [...] }
            dates = data.get("dates") or data.get("date") or []
            values = data.get("values") or data.get("valeurs") or data.get("valeur") or []
            if isinstance(dates, dict):
                dates = list(dates.keys())
                values = list(dates.values())
            if dates and values and len(dates) == len(values):
                for d, v in zip(dates, values):
                    if v is not None:
                        try:
                            rows.append(self._make_row(
                                date_label=str(d),
                                valeur=float(v),
                                code_indicateur=code or "TAUX.DIRECTEUR",
                                fichier=rel,
                                version_serie=version,
                            ))
                        except (ValueError, TypeError):
                            pass

        if not rows:
            return ParsedFile(rel, erreur="Aucune serie extraite du JSON")

        return ParsedFile(rel, lignes=pl.DataFrame(rows))

    def _extract(self, df: pl.DataFrame, rel: str) -> ParsedFile:
        """Extraction generique pour DataFrame tabulaire BAM."""
        if df.is_empty():
            return ParsedFile(rel, erreur="DataFrame vide")

        df = self._normalize_columns(df)
        code = detect_code_indicateur(rel) or "TAUX.DIRECTEUR"
        version = detect_version_serie(rel)
        cols = df.columns

        date_col = None
        for c in cols:
            cl = c.lower()
            if any(kw in cl for kw in ["date", "annee", "annee", "mois", "trimestre", "periode", "periode"]):
                date_col = c
                break

        if date_col is None:
            # Fallback : premiere colonne
            date_col = cols[0]

        value_cols = [c for c in cols if c != date_col and df[c].dtype in (pl.Float64, pl.Int64, pl.Float32)]
        if not value_cols:
            return ParsedFile(rel, erreur="Aucune colonne numerique")

        rows = []
        for vcol in value_cols:
            for row in df.iter_rows(named=True):
                raw_date = row[date_col]
                raw_val = row[vcol]
                if raw_val is None or (isinstance(raw_val, float) and raw_val != raw_val):
                    continue
                try:
                    val = float(raw_val)
                except (ValueError, TypeError):
                    continue
                rows.append(self._make_row(
                    date_label=str(raw_date),
                    valeur=val,
                    code_indicateur=code,
                    fichier=rel,
                    version_serie=version,
                ))

        if not rows:
            return ParsedFile(rel, erreur="Aucune ligne extraite")

        return ParsedFile(rel, lignes=pl.DataFrame(rows))
