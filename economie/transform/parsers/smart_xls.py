"""Lecteur adaptatif pour fichiers Excel legacy (portails officiels marocains).

Gere les pieges classiques :
- .xls binaire (BIFF) -> xlrd
- .xlsx renomme en .xls -> openpyxl
- HTML/tableau web deguise en .xls (export datagov/HCP) -> pandas.read_html
- En-tetes multi-lignes et cellules fusionnees
- Nombres au format francais : "1 234,56", "n.d.", "-"

Dependances : pandas, xlrd, openpyxl.
"""

from __future__ import annotations

import io
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_MAGIC = {
    b"\xd0\xcf\x11\xe0": "xls",
    b"PK\x03\x04": "xlsx",
}
_NA_VALUES = ["n.d.", "n.d", "nd", "N.D.", "-", "\u2013", "\u2014", "..", "...", ""]


def detect_format(path: str | Path) -> str:
    """Detecte le format reel par les octets magiques."""
    head = Path(path).read_bytes()[:512]
    for magic, fmt in _MAGIC.items():
        if head.startswith(magic):
            return fmt
    if re.search(rb"<\s*(html|table)", head, re.IGNORECASE):
        return "html"
    raise ValueError(f"Format non reconnu pour {path} (premiers octets : {head[:8]!r})")


def _read_raw(path: Path, fmt: str, sheet: int | str = 0) -> pd.DataFrame:
    """Lit le fichier sans interpreter les en-tetes (header=None)."""
    if fmt == "xls":
        return pd.read_excel(path, sheet_name=sheet, header=None, engine="xlrd")
    if fmt == "xlsx":
        try:
            return pd.read_excel(path, sheet_name=sheet, header=None, engine="openpyxl")
        except Exception:
            return pd.read_excel(path, sheet_name=sheet, header=None, engine="calamine")
    if fmt == "html":
        tables = pd.read_html(
            io.StringIO(path.read_text(encoding="utf-8", errors="replace"))
        )
        return tables[sheet if isinstance(sheet, int) else 0]
    raise ValueError(fmt)


def _read_raw_all_sheets(path: Path, fmt: str) -> dict[str, pd.DataFrame]:
    """Lit toutes les feuilles et retourne {nom_feuille: DataFrame}."""
    if fmt == "xls":
        import xlrd

        wb = xlrd.open_workbook(str(path))
        out = {}
        for name in wb.sheet_names():
            sh = wb.sheet_by_name(name)
            rows = []
            for r in range(sh.nrows):
                rows.append([sh.cell_value(r, c) for c in range(sh.ncols)])
            out[name] = pd.DataFrame(rows)
        return out
    if fmt == "xlsx":
        xls = pd.ExcelFile(path, engine="openpyxl")
        return {s: xls.parse(s, header=None) for s in xls.sheet_names}
    if fmt == "html":
        tables = pd.read_html(
            io.StringIO(path.read_text(encoding="utf-8", errors="replace"))
        )
        return {f"table_{i}": t for i, t in enumerate(tables)}
    raise ValueError(fmt)


def detect_header_rows(df: pd.DataFrame, max_scan: int = 10) -> int:
    """Trouve la premiere ligne de donnees : celle ou la majorite
    des cellules non vides sont numeriques."""
    for i in range(min(max_scan, len(df))):
        cells = df.iloc[i].dropna().astype(str)
        if len(cells) == 0:
            continue
        numeric = cells.str.match(r"^-?[\d\s.,]+$").mean()
        if numeric > 0.5:
            return i
    return 1


def _flatten_headers(df: pd.DataFrame, n_header_rows: int) -> list[str]:
    """Aplati les en-tetes multi-lignes ; propage les cellules fusionnees."""
    headers = df.iloc[:n_header_rows].ffill(axis=1).ffill(axis=0)
    cols = []
    for col in headers.columns:
        parts = [str(v).strip() for v in headers[col] if pd.notna(v)]
        seen, uniq = set(), []
        for p in parts:
            if p not in seen:
                seen.add(p)
                uniq.append(p)
        cols.append(" / ".join(uniq) or f"col_{col}")
    return cols


def _deduplicate_columns(cols):
    """Ajoute _1, _2, _3... aux noms de colonnes dupliques."""
    seen = {}
    out = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            out.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            out.append(c)
    return out


def _clean_french_numbers(s) -> pd.Series:
    """'1 234,56' -> 1234.56 ; gere espaces insecables et n.d.
    Accepte Series ou DataFrame (retourne premiere colonne si DataFrame)."""
    if isinstance(s, pd.DataFrame):
        s = s.iloc[:, 0]
    cleaned = (
        s.astype(str)
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace(_NA_VALUES, pd.NA)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def read_legacy_excel(
    path: str | Path,
    sheet: int | str = 0,
    numeric_threshold: float = 0.6,
) -> tuple[pd.DataFrame, dict]:
    """Point d'entree : lit n'importe quel 'xls' et retourne
    (DataFrame nettoye, metadonnees de tracabilite)."""
    path = Path(path)
    fmt = detect_format(path)
    logger.info("Lecture %s — format reel : %s", path.name, fmt)

    raw = _read_raw(path, fmt, sheet)
    raw = raw.dropna(how="all").dropna(axis=1, how="all")

    n_headers = detect_header_rows(raw)
    df = raw.iloc[n_headers:].reset_index(drop=True)
    df.columns = _deduplicate_columns(_flatten_headers(raw, n_headers))

    converted = []
    for col in df.columns:
        as_num = _clean_french_numbers(df[col])
        if as_num.notna().mean() >= numeric_threshold:
            df[col] = as_num
            converted.append(col)

    meta = {
        "fichier": path.name,
        "format_reel": fmt,
        "lignes_entete": n_headers,
        "colonnes_numeriques": converted,
        "n_lignes": len(df),
        "taux_valeurs_manquantes": round(float(df.isna().mean().mean()), 4),
    }
    return df, meta


def read_all_sheets(
    path: str | Path,
    numeric_threshold: float = 0.6,
) -> list[tuple[str, pd.DataFrame, dict]]:
    """Lit toutes les feuilles et retourne une liste de
    (nom_feuille, DataFrame, metadonnees)."""
    path = Path(path)
    fmt = detect_format(path)
    sheets = _read_raw_all_sheets(path, fmt)

    results = []
    for name, raw in sheets.items():
        raw = raw.dropna(how="all").dropna(axis=1, how="all")
        if raw.empty:
            continue
        n_headers = detect_header_rows(raw)
        df = raw.iloc[n_headers:].reset_index(drop=True)
        df.columns = _deduplicate_columns(_flatten_headers(raw, n_headers))

        converted = []
        for col in df.columns:
            as_num = _clean_french_numbers(df[col])
            if as_num.notna().mean() >= numeric_threshold:
                df[col] = as_num
                converted.append(col)

        meta = {
            "fichier": path.name,
            "feuille": name,
            "format_reel": fmt,
            "lignes_entete": n_headers,
            "colonnes_numeriques": converted,
            "n_lignes": len(df),
        }
        results.append((name, df, meta))
    return results


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    for fp in sys.argv[1:]:
        sheets = read_all_sheets(fp)
        for name, df, meta in sheets:
            print(f"\n=== {name} ===")
            print(meta)
            print(df.head(5))
