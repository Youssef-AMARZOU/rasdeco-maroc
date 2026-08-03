"""
parsers/parse_finances.py -- Parser pour les fichiers du Ministere des Finances.

Gere les formats .xls (.xls legacy via xlrd/openpyxl) :
- Budget/depenses (2010-2012) : multi-feuilles ADM/REG/CE/CF, annees en colonnes
- Dette publique (2014) : annees en rangee 0, indicateurs en lignes
- Stats economiques (2013) : multi-feuilles, annees en rangee 1, indicateurs en lignes
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import polars as pl

from .base import (
    RAW_ROOT,
    ParsedFile,
    SourceParser,
    detect_code_indicateur,
    detect_version_serie,
    parse_date_label,
)
from .smart_xls import detect_format, read_all_sheets

# Mapping indicateurs Finances -> codes normalises
_FINANCE_INDICATOR_MAP = {
    # Dette publique
    "encours total (millions $ us)": "DETTE.PUBLIQUE.US",
    "encours total (millions dh)": "DETTE.PUBLIQUE.DH",
    "en % du pib": "DETTE.PUBLIQUE.PCT_PIB",
    "service de la dette (millions $ us)": "DETTE.SERVICE.US",
    "service de la dette (millions dh)": "DETTE.SERVICE.DH",
    "en % des recettes courantes": "DETTE.SERVICE.PCT_RECETTES",
    "charges en interets": "DETTE.CHARGES",
    "charges en int\u00e9r\u00eats": "DETTE.CHARGES",
    "encours de la dette ext\u00e9rieure du tr\u00e9sor": "DETTE.TRESOR_EXT",
    "encours de la dette int\u00e9rieure du tr\u00e9sor": "DETTE.TRESOR_INT",
    # Finances publiques
    "current revenues": "RECETTES.COURANTES",
    "recettes courantes": "RECETTES.COURANTES",
    "fiscal revenue": "RECETTES.FISCALES",
    "recettes fiscales": "RECETTES.FISCALES",
    "privatization": "RECETTES.PRIVATISATION",
    "privatisations": "RECETTES.PRIVATISATION",
    "current expenditure": "DEPENSES.COURANTES",
    "depenses courantes": "DEPENSES.COURANTES",
    "administrative expenses": "DEPENSES.ADMIN",
    "depenses administratives": "DEPENSES.ADMIN",
    "subsidization": "SUBVENTIONS",
    "subventions": "SUBVENTIONS",
    # Commerce exterieur
    "imports": "IMPORTATIONS",
    "importations": "IMPORTATIONS",
    "exports": "EXPORTATIONS",
    "exportations": "EXPORTATIONS",
    "overall trade balance": "BALANCE.COMMERCIALE",
    "balance commerciale": "BALANCE.COMMERCIALE",
    "energy and lubricants": "IMPORT.ENERGIE",
    "manufactures": "EXPORT.MANUFACTURES",
    # Budget
    "investissement": "INVESTISSEMENT.PUBLIC",
    "total": "DEPENSES.TOTAL",
    "mat\u00e9riel et d\u00e9penses diverses": "DEPENSES.FONCTIONNEMENT",
}


def _detect_indicator_code(row_label: str) -> str:
    """Detecte le code indicateur a partir du libelle."""
    lower = row_label.lower().strip()
    for kw, code in _FINANCE_INDICATOR_MAP.items():
        if kw in lower:
            return code
    # Fallback generique
    return detect_code_indicateur(lower) or "DEFICIT.BUDGET"


def _is_year(val) -> bool:
    """Verifie si une valeur est une annee (2000-2030)."""
    try:
        y = int(float(val))
        return 2000 <= y <= 2030
    except (ValueError, TypeError):
        return False


def _year_to_label(val) -> str:
    """Convertit une valeur en label d'annee."""
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return str(val)


def _extract_year_rows(df: pd.DataFrame, rel: str, parser: "FinancesParser") -> list[dict]:
    """Extrait les series depuis un format 'annees en colonnes, indicateurs en lignes'.
    Gere aussi le format budget-d-etat ou les annees sont dans les noms de colonnes."""
    if df.empty or len(df) < 2:
        return []

    rows_out = []

    # --- Essai 1 : annees dans les cellules d'en-tete (format standard) ---
    header_row = None
    for i in range(min(8, len(df))):
        row_vals = df.iloc[i].dropna()
        year_count = sum(1 for v in row_vals if _is_year(v))
        if year_count >= 2:
            header_row = i
            break

    year_cols = {}
    if header_row is not None:
        header_vals = df.iloc[header_row]
        for ci in range(len(header_vals)):
            v = header_vals.iloc[ci]
            if _is_year(v):
                year_cols[ci] = _year_to_label(v)

    # --- Essai 2 : annees dans les noms de colonnes (format budget-d-etat) ---
    if not year_cols:
        year_re = re.compile(r"(20\d{2})")
        for ci, col_name in enumerate(df.columns):
            m = year_re.search(str(col_name))
            if m:
                year_cols[ci] = m.group(1)
        if not year_cols:
            return []

    # Extraire les donnees
    for ri in range(header_row + 1 if header_row is not None else 0, len(df)):
        # Trouver le label dans la premiere colonne non-numeric
        label = None
        for offset in range(min(3, df.shape[1])):
            cell = df.iloc[ri, offset]
            if pd.notna(cell) and not _is_year(cell):
                label = str(cell).strip()
                break
        if not label or label.lower() in ("nan", "total", "source", "note", ""):
            continue

        # Verifier si c'est une ligne de donnees (au moins 1 valeur numerique)
        has_data = False
        for ci in year_cols:
            if ci < df.iloc[ri].shape[0]:
                v = df.iloc[ri, ci]
                if pd.notna(v):
                    try:
                        float(str(v).replace(",", ".").replace(" ", ""))
                        has_data = True
                        break
                    except (ValueError, TypeError):
                        pass

        if not has_data:
            continue

        code = _detect_indicator_code(label)

        for ci, year_label in year_cols.items():
            if ci >= df.iloc[ri].shape[0]:
                continue
            raw_val = df.iloc[ri, ci]
            if pd.isna(raw_val):
                continue
            try:
                val = float(str(raw_val).replace(",", ".").replace(" ", ""))
            except (ValueError, TypeError):
                continue

            rows_out.append(
                parser._make_row(
                    date_label=year_label,
                    valeur=val,
                    code_indicateur=code,
                    fichier=rel,
                )
            )

    return rows_out


def _extract_budget_regions(df: pd.DataFrame, rel: str, parser: "FinancesParser") -> list[dict]:
    """Extrait les donnees budgetaires par region (format REG)."""
    if df.empty:
        return []

    rows_out = []
    # Meme logique que year_rows mais avec noms de regions en colonne 1
    header_row = None
    for i in range(min(8, len(df))):
        row_vals = df.iloc[i].dropna()
        year_count = sum(1 for v in row_vals if _is_year(v))
        if year_count >= 2:
            header_row = i
            break

    if header_row is None:
        return []

    header_vals = df.iloc[header_row]
    year_cols = {}
    for ci in range(len(header_vals)):
        v = header_vals.iloc[ci]
        if _is_year(v):
            year_cols[ci] = _year_to_label(v)

    for ri in range(header_row + 1, len(df)):
        if df.iloc[ri].shape[0] < 2:
            continue
        region = str(df.iloc[ri, 1]).strip() if pd.notna(df.iloc[ri, 1]) else ""
        if not region or region.lower() in ("nan", "total"):
            continue

        code = "INVESTISSEMENT.PUBLIC"
        if "total" in region.lower():
            code = "DEPENSES.TOTAL"

        for ci, year_label in year_cols.items():
            if ci >= df.iloc[ri].shape[0]:
                continue
            raw_val = df.iloc[ri, ci]
            if pd.isna(raw_val):
                continue
            try:
                val = float(str(raw_val).replace(",", ".").replace(" ", ""))
            except (ValueError, TypeError):
                continue

            rows_out.append(
                parser._make_row(
                    date_label=year_label,
                    valeur=val,
                    code_indicateur=code,
                    fichier=rel,
                )
            )

    return rows_out


class FinancesParser(SourceParser):
    def __init__(self):
        super().__init__("finances")

    @property
    def source_code(self) -> str:
        return "FIN"

    def parse_file(self, fpath: Path) -> ParsedFile:
        rel = str(fpath.relative_to(RAW_ROOT))
        ext = fpath.suffix.lower()

        if ext == ".pdf":
            return ParsedFile(rel, erreur="PDF ignore (non structure)")

        if ext not in (".xlsx", ".xls", ".csv", ".json"):
            return ParsedFile(rel, erreur=f"Format non supporte : {ext}")

        try:
            if ext in (".xlsx", ".xls"):
                return self._parse_excel(fpath, rel)
            elif ext == ".csv":
                return self._parse_csv(fpath, rel)
            elif ext == ".json":
                return self._parse_json(fpath, rel)
        except Exception as e:
            return ParsedFile(rel, erreur=str(e))

        return ParsedFile(rel, erreur="Format non gere")

    def _parse_excel(self, fpath: Path, rel: str) -> ParsedFile:
        """Parse un fichier Excel via smart_xls."""
        sheets = read_all_sheets(fpath)
        all_rows = []

        for sheet_name, df, meta in sheets:
            if df.empty:
                continue

            # Detecter le format:
            # Format budget (ADM/REG/CE/CF) -> annees en colonnes
            # Format dette/stats -> annees en rangee d'en-tete
            # Les deux utilisent la meme logique year_rows
            rows = _extract_year_rows(df, rel, self)
            if rows:
                all_rows.extend(rows)

            # Aussi essayer le format budget par region (REG sheet)
            rows_reg = _extract_budget_regions(df, rel, self)
            if rows_reg:
                all_rows.extend(rows_reg)

        if not all_rows:
            return ParsedFile(rel, erreur="Aucune serie extraite du fichier Excel")

        return ParsedFile(rel, lignes=pl.DataFrame(all_rows))

    def _parse_csv(self, fpath: Path, rel: str) -> ParsedFile:
        df = pd.read_csv(fpath, na_values=["", "NA", "..", "n.d."])
        code = detect_code_indicateur(rel) or "DEFICIT.BUDGET"
        version = detect_version_serie(rel)

        rows = []
        if not df.empty:
            cols = list(df.columns)
            date_col = None
            for c in cols:
                cl = str(c).lower()
                if any(kw in cl for kw in ["annee", "date", "trimestre", "mois"]):
                    date_col = c
                    break
            if date_col is None:
                date_col = cols[0]

            value_cols = [
                c for c in cols if c != date_col and pd.api.types.is_numeric_dtype(df[c])
            ]

            for vcol in value_cols:
                for _, row in df.iterrows():
                    raw_val = row[vcol]
                    if pd.isna(raw_val):
                        continue
                    try:
                        val = float(raw_val)
                    except (ValueError, TypeError):
                        continue
                    rows.append(
                        self._make_row(
                            date_label=str(row[date_col]),
                            valeur=val,
                            code_indicateur=code,
                            fichier=rel,
                            version_serie=version,
                        )
                    )

        if not rows:
            return ParsedFile(rel, erreur="Aucune serie CSV extraite")
        return ParsedFile(rel, lignes=pl.DataFrame(rows))

    def _parse_json(self, fpath: Path, rel: str) -> ParsedFile:
        df = pd.read_json(fpath)
        code = detect_code_indicateur(rel) or "DEFICIT.BUDGET"
        version = detect_version_serie(rel)

        rows = []
        if not df.empty:
            cols = list(df.columns)
            date_col = cols[0]
            value_cols = [
                c for c in cols if c != date_col and pd.api.types.is_numeric_dtype(df[c])
            ]
            for vcol in value_cols:
                for _, row in df.iterrows():
                    raw_val = row[vcol]
                    if pd.isna(raw_val):
                        continue
                    try:
                        val = float(raw_val)
                    except (ValueError, TypeError):
                        continue
                    rows.append(
                        self._make_row(
                            date_label=str(row[date_col]),
                            valeur=val,
                            code_indicateur=code,
                            fichier=rel,
                            version_serie=version,
                        )
                    )

        if not rows:
            return ParsedFile(rel, erreur="Aucune serie JSON extraite")
        return ParsedFile(rel, lignes=pl.DataFrame(rows))
