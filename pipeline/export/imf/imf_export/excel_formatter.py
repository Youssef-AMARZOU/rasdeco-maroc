"""
excel_formatter.py – Export Excel multi-sheet pour le Maroc
=============================================================
Génère un fichier .xlsx professionnel avec :
  • Sheet 1 – Macro FMI (Time Series) : matrice indicateurs × années
  • Sheet 2 – World Bank (2024-2025)
  • Sheet 3 – Définitions & Sources
  • Sheet 4 – PIB Historique (Worldometers)

Avec : headers figés, bandes alternées, échelles de couleurs conditionnelles,
largeurs automatiques, et mise en forme soignée.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from openpyxl import Workbook
    from openpyxl.styles import (
        Alignment,
        Border,
        Font,
        NamedStyle,
        PatternFill,
        Side,
    )
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, Reference
    from openpyxl.formatting.rule import ColorScaleRule
except ImportError:
    msg = (
        "openpyxl is required. Install with: pip install openpyxl"
    )
    raise ImportError(msg)

# ── Palette ───────────────────────────────────────────────────────────
DARK_BLUE = "003366"
WHITE = "FFFFFF"
LIGHT_BLUE = "D6E4F0"
LIGHT_GRAY = "F2F2F2"
ACCENT_GOLD = "FFC000"

HEADER_FILL = PatternFill(start_color=DARK_BLUE, end_color=DARK_BLUE, fill_type="solid")
HEADER_FONT = Font(name="Calibri", bold=True, color=WHITE, size=11)
ROW_EVEN = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")
ROW_ODD = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")
THIN_BORDER = Border(
    left=Side(style="thin", color="BFBFBF"),
    right=Side(style="thin", color="BFBFBF"),
    top=Side(style="thin", color="BFBFBF"),
    bottom=Side(style="thin", color="BFBFBF"),
)
WRAP = Alignment(wrap_text=True, vertical="center")
CENTER = Alignment(horizontal="center", vertical="center")


def _auto_width(ws, min_width: int = 8, max_width: int = 45) -> None:
    """Ajuste la largeur des colonnes au contenu."""
    for col_cells in ws.columns:
        col_letter = get_column_letter(col_cells[0].column)
        lengths = []
        for cell in col_cells:
            if cell.value is not None:
                # Tentative de calcul de largeur
                val = str(cell.value)
                lengths.append(len(val))
        best = max(lengths) if lengths else min_width
        ws.column_dimensions[col_letter].width = min(max(best + 3, min_width), max_width)


def _style_header_row(ws, ncols: int) -> None:
    """Applique le style header bleu foncé sur la ligne 1."""
    for col in range(1, ncols + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = THIN_BORDER


def _band_rows(ws, start_row: int, end_row: int, ncols: int) -> None:
    """Bandes alternées gris clair / blanc."""
    for r in range(start_row, end_row + 1):
        fill = ROW_EVEN if (r - start_row) % 2 == 1 else ROW_ODD
        for c in range(1, ncols + 1):
            cell = ws.cell(row=r, column=c)
            cell.fill = fill
            cell.border = THIN_BORDER
            if c == 1:
                cell.font = Font(name="Calibri", bold=True, size=10)
            else:
                cell.font = Font(name="Calibri", size=10)


def _freeze(ws, cell: str = "B2") -> None:
    ws.freeze_panes = cell


# ── Sheet 1 : Macro FMI ──────────────────────────────────────────────

def write_fmi_sheet(
    wb: Workbook,
    rows: List[Dict[str, Any]],
    years: List[int],
) -> None:
    ws = wb.active
    ws.title = "Macro FMI"

    # En-têtes : ID / Name / Unit / 1980 / 1981 / …
    headers = ["ID", "Indicateur", "Unité"] + [str(y) for y in years]
    ws.append(headers)

    for row in rows:
        values = [row["indicator_id"], row["indicator_name"], row["unit"]]
        for y in years:
            values.append(row.get(str(y), None))
        ws.append(values)

    ncols = len(headers)
    nrows = len(rows) + 1

    _style_header_row(ws, ncols)
    _band_rows(ws, 2, nrows, ncols)
    _freeze(ws, "D2")
    _auto_width(ws)

    # ── Color scale conditionnelle sur colonnes années ───────────────
    # Appliquée à la colonne "GDP growth" (NGDP_RPCH)
    gdp_growth_col = None
    for idx, h in enumerate(headers):
        if h == "ID":
            for r_idx in range(2, nrows + 1):
                if ws.cell(row=r_idx, column=idx + 1).value == "NGDP_RPCH":
                    gdp_growth_col = idx + 1
                    break
            break

    if gdp_growth_col:
        # Color scale 3 couleurs (rouge → blanc → vert)
        ws.conditional_formatting.add(
            f"{get_column_letter(gdp_growth_col)}2:{get_column_letter(ncols)}{nrows}",
            ColorScaleRule(
                start_type="min",
                start_color="FF4444",
                mid_type="percentile",
                mid_value=50,
                mid_color="FFFFFF",
                end_type="max",
                end_color="44AA44",
            ),
        )

    # Color scale pour current account balance (% GDP)
    bca_col = None
    for idx, h in enumerate(headers):
        if h == "ID":
            for r_idx in range(2, nrows + 1):
                if ws.cell(row=r_idx, column=idx + 1).value == "BCA_NGDPD":
                    bca_col = idx + 1
                    break
            break

    if bca_col:
        ws.conditional_formatting.add(
            f"{get_column_letter(bca_col)}2:{get_column_letter(ncols)}{nrows}",
            ColorScaleRule(
                start_type="min",
                start_color="FF4444",
                mid_type="percentile",
                mid_value=50,
                mid_color="FFFFFF",
                end_type="max",
                end_color="44AA44",
            ),
        )


# ── Sheet 2 : Banque Mondiale ───────────────────────────────────────

def write_world_bank_sheet(wb: Workbook, wb_rows: List[Dict]) -> None:
    ws = wb.create_sheet("Banque Mondiale")
    if not wb_rows:
        ws.append(["Aucune donnée"])
        return

    # Rassembler toutes les années présentes
    all_years = set()
    for r in wb_rows:
        for k in r:
            if k not in ("indicator", "description", "unit", "source") and k.isdigit():
                all_years.add(int(k))
    sorted_years = sorted(all_years)

    headers = ["Indicateur", "Description", "Unité", "Source"] + [str(y) for y in sorted_years]
    ws.append(headers)

    for row in wb_rows:
        values = [row["indicator"], row["description"], row["unit"], row["source"]]
        for y in sorted_years:
            values.append(row.get(str(y), None))
        ws.append(values)

    ncols = len(headers)
    nrows = len(wb_rows) + 1

    _style_header_row(ws, ncols)
    _band_rows(ws, 2, nrows, ncols)
    _freeze(ws, "E2")
    _auto_width(ws)


# ── Sheet 3 : Définitions & Sources ─────────────────────────────────

def write_definitions_sheet(wb: Workbook, def_rows: List[Dict]) -> None:
    ws = wb.create_sheet("Définitions & Sources")
    headers = ["ID", "Indicateur", "Unité", "Définition / Notes"]
    ws.append(headers)

    for r in def_rows:
        ws.append([r["indicator_id"], r["indicator_name"], r["unit"], r["notes"]])

    ncols = len(headers)
    nrows = len(def_rows) + 1

    _style_header_row(ws, ncols)
    _band_rows(ws, 2, nrows, ncols)
    _freeze(ws, "B2")
    _auto_width(ws)

    # La colonne Définition mérite plus de largeur
    ws.column_dimensions["D"].width = 80
    for r in range(2, nrows + 1):
        ws.cell(row=r, column=4).alignment = WRAP
        ws.cell(row=r, column=4).font = Font(name="Calibri", size=9)


# ── Sheet 4 : PIB Historique (Worldometers) ─────────────────────────
# Source : https://www.worldometers.info/gdp/morocco-gdp/

HISTORICAL_GDP = [
    # Année, PIB (M$), Croissance
    (1960, 2037, None),
    (1961, 2027, None),
    (1962, 2158, None),
    (1963, 2328, None),
    (1964, 2479, None),
    (1965, 2698, None),
    (1966, 2902, None),
    (1967, 3023, None),
    (1968, 3298, None),
    (1969, 3602, None),
    (1970, 3956, None),
    (1971, 4286, None),
    (1972, 5027, None),
    (1973, 6165, None),
    (1974, 7971, None),
    (1975, 9060, None),
    (1976, 10235, None),
    (1977, 11989, None),
    (1978, 13435, None),
    (1979, 14989, None),
    (1980, 21729, None),
    (1981, 17792, None),
    (1982, 18414, None),
    (1983, 16768, None),
    (1984, 16732, None),
    (1985, 17675, None),
    (1986, 21074, None),
    (1987, 22859, None),
    (1988, 25277, None),
    (1989, 26105, None),
    (1990, 28591, None),
    (1991, 31084, None),
    (1992, 32158, None),
    (1993, 31854, None),
    (1994, 35023, None),
    (1995, 36839, None),
    (1996, 39842, None),
    (1997, 38713, None),
    (1998, 42593, None),
    (1999, 43107, None),
    (2000, 42563, None),
    (2001, 43955, None),
    (2002, 47637, None),
    (2003, 55850, None),
    (2004, 63969, None),
    (2005, 68055, None),
    (2006, 74053, None),
    (2007, 81584, None),
    (2008, 92952, None),
    (2009, 92867, None),
    (2010, 93217, None),
    (2011, 101379, None),
    (2012, 98778, None),
    (2013, 107243, None),
    (2014, 110018, None),
    (2015, 110196, None),
    (2016, 111258, None),
    (2017, 115370, None),
    (2018, 123353, None),
    (2019, 125280, None),
    (2020, 114671, None),
    (2021, 141690, None),
    (2022, 134260, None),
    (2023, 143983, None),
]

HISTORICAL_GDP_HEADERS = ["Année", "PIB (millions US$)", "Croissance (%)"]


def write_historical_gdp_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("PIB Historique")
    ws.append(HISTORICAL_GDP_HEADERS)
    for year, gdp, growth in HISTORICAL_GDP:
        ws.append([year, gdp, growth])

    ncols = len(HISTORICAL_GDP_HEADERS)
    nrows = len(HISTORICAL_GDP) + 1

    _style_header_row(ws, ncols)
    _band_rows(ws, 2, nrows, ncols)
    _freeze(ws, "B2")
    _auto_width(ws)

    # Format monétaire pour la colonne PIB
    for r in range(2, nrows + 1):
        cell = ws.cell(row=r, column=2)
        cell.number_format = '#,##0'

    # Color scale sur PIB
    ws.conditional_formatting.add(
        f"B2:B{nrows}",
        ColorScaleRule(
            start_type="min", start_color="FF4444",
            mid_type="percentile", mid_value=50, mid_color="FFFFFF",
            end_type="max", end_color="44AA44",
        ),
    )

    # Graphique barres
    chart = BarChart()
    chart.type = "col"
    chart.title = "PIB du Maroc (millions US$)"
    chart.y_axis.title = "PIB (millions US$)"
    chart.x_axis.title = "Année"
    chart.style = 10
    chart.width = 30
    chart.height = 15

    data_ref = Reference(ws, min_col=2, min_row=1, max_row=nrows)
    cats_ref = Reference(ws, min_col=1, min_row=2, max_row=nrows)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    chart.shape = 4
    ws.add_chart(chart, "D2")


# ── Orchestrateur principal ──────────────────────────────────────────

def generate_excel(
    fmi_rows: List[Dict[str, Any]],
    years: List[int],
    wb_rows: List[Dict],
    def_rows: List[Dict],
    output_path: str | Path = "morocco_data.xlsx",
) -> str:
    wb = Workbook()
    write_fmi_sheet(wb, fmi_rows, years)
    write_world_bank_sheet(wb, wb_rows)
    write_definitions_sheet(wb, def_rows)
    write_historical_gdp_sheet(wb)

    path = Path(output_path)
    wb.save(str(path))
    return str(path)
