"""
utils_xls.py -- Utilitaires pour parser les fichiers Excel HCP en format cross-table.

Les fichiers HCP sur data.gov.ma sont des tableaux croises :
  - Ligne 1-2 : titre fusionne (A1:AR2)
  - Ligne 4+  : colonne A = libelle, colonnes B..N = trimestres/annees

Ce module convertit ce format "large" en format "tidy" (Melt/Unpivot).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import polars as pl


def parse_cross_table_xlsx(
    fpath: Path,
    date_pattern: str = r"(20\d{2})[TQ](\d)",
    skip_rows: int = 3,
) -> Optional[pl.DataFrame]:
    """
    Ouvre un fichier XLSX HCP en format cross-table et le convertit en tidy.

    Detection automatique :
      1. Charge via openpyxl pour lire les cellules fusionnees
      2. Detecte la ligne d'en-tete (contient des dates 2014T1, 2020Q3, etc.)
      3. Convertit en format long : date, indicateur, valeur

    Retourne None si le format n'est pas reconnu.
    """
    import openpyxl

    wb = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    if "Data" not in wb.sheetnames:
        return None
    ws = wb["Data"]

    rows = list(ws.iter_rows(values_only=True))

    # Trouver la ligne d'en-tete (contient des motifs de date)
    header_row_idx = None
    header_values = None
    for i, row in enumerate(rows):
        vals = [str(v).strip() if v is not None else "" for v in row]
        date_count = sum(1 for v in vals if re.search(date_pattern, v))
        if date_count >= 3:
            header_row_idx = i
            header_values = vals
            break

    if header_row_idx is None:
        return None

    # Extraire les dates de l'en-tete
    dates = []
    date_cols = []
    for j, v in enumerate(header_values):
        m = re.search(date_pattern, v)
        if m:
            year = int(m.group(1))
            quarter = int(m.group(2))
            date_str = f"{year}-{quarter * 3 - 2:02d}-01"
            dates.append(date_str)
            date_cols.append(j)

    if not dates:
        return None

    # Lire les lignes de donnees
    records = []
    for row in rows[header_row_idx + 1:]:
        if not row or all(v is None for v in row):
            continue
        label = str(row[0]).strip() if row[0] is not None else ""
        if not label or len(label) > 80:
            continue
        for ci, dj in enumerate(date_cols):
            if dj < len(row) and row[dj] is not None:
                try:
                    val = float(row[dj])
                    records.append({
                        "indicateur": label,
                        "date": dates[ci],
                        "valeur": val,
                    })
                except (ValueError, TypeError):
                    pass

    if not records:
        return None

    return pl.DataFrame(records)


def parse_oecd_xls(fpath: Path, skip_rows: int = 3) -> Optional[pl.DataFrame]:
    """
    Parse les fichiers .xls ancien format de l'OCDE / finances.
    """
    try:
        import xlrd
    except ImportError:
        return None

    wb = xlrd.open_workbook(str(fpath))
    sheet = wb.sheet_by_index(0)

    rows = []
    for r in range(sheet.nrows):
        rows.append([sheet.cell_value(r, c) for c in range(sheet.ncols)])

    # Detection de l'en-tete
    header_idx = None
    for i, row in enumerate(rows):
        date_count = sum(1 for v in row if isinstance(v, str) and re.search(r"20\d{2}", v))
        if date_count >= 3:
            header_idx = i
            break

    if header_idx is None:
        return None

    header = rows[header_idx]
    date_cols = []
    dates = []
    for j, v in enumerate(header):
        v_str = str(v).strip()
        m = re.search(r"(20\d{2})", v_str)
        if m:
            year = int(m.group(1))
            date_str = f"{year}-01-01"
            dates.append(date_str)
            date_cols.append(j)

    records = []
    for row in rows[header_idx + 1:]:
        label = str(row[0]).strip() if row[0] else ""
        if not label or len(label) > 100:
            continue
        for ci, dj in enumerate(date_cols):
            if dj < len(row):
                val = row[dj]
                if isinstance(val, (int, float)):
                    records.append({
                        "indicateur": label,
                        "date": dates[ci] if ci < len(dates) else "2000-01-01",
                        "valeur": float(val),
                    })

    if not records:
        return None
    return pl.DataFrame(records)
