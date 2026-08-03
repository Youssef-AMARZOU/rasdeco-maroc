"""
generate_tables.py – Genere des fichiers Excel organises par theme
avec mise en forme pro et code VBA pour la recherche dans les tables.

Structure :
  tables/
    01-Croissance_PIB.xlsx
    02-Inflation_Prix.xlsx
    03-Emploi.xlsx
    04-Finances_Publiques.xlsx
    05- Commerce_Exterieur.xlsx
    06-Investissement.xlsx
    07-Demographie.xlsx
    08-Recherche_Macro.bas       # Module VBA a importer
    09-Tableau_de_Bord.xlsx       # Tableau recapitulatif
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

try:
    from openpyxl import Workbook
    from openpyxl.styles import (
        Alignment, Border, Font, PatternFill, Side
    )
    from openpyxl.utils import get_column_letter
    from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
except ImportError:
    print("Install openpyxl: pip install openpyxl")
    raise

# ── Config ─────────────────────────────────────────────────────────────
BASE = Path(__file__).parent / "tables"
BASE.mkdir(parents=True, exist_ok=True)

# ── Styles ─────────────────────────────────────────────────────────────
HEADER_FILL = PatternFill("solid", fgColor="003366")
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
SUBHEADER_FILL = PatternFill("solid", fgColor="4472C4")
SUBHEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
DATA_FONT = Font(name="Consolas", size=9)
BAND_1 = PatternFill("solid", fgColor="FFFFFF")
BAND_2 = PatternFill("solid", fgColor="E8F0FE")
BORDER = Border(
    left=Side("thin", "BFBFBF"), right=Side("thin", "BFBFBF"),
    top=Side("thin", "BFBFBF"), bottom=Side("thin", "BFBFBF"),
)
CENTER = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(wrap_text=True, vertical="center")

# Palettes par theme
THEME_COLORS = {
    "croissance": "4472C4",
    "inflation": "ED7D31",
    "emploi": "70AD47",
    "finances": "C00000",
    "commerce": "5B9BD5",
    "investissement": "FFC000",
    "demographie": "7030A0",
}

# ── Donnees ────────────────────────────────────────────────────────────
# Les donnees proviennent de data_parser.py
import sys
sys.path.insert(0, str(Path(__file__).parent))
from data_parser import IMF_INDICATORS, IMF_MOROCCO_VALUES

THEMES = {
    "01-Croissance_PIB": {
        "title": "Croissance et PIB",
        "fill": "4472C4",
        "indicators": ["NGDP_RPCH", "NGDP", "NGDPD", "NGDPDPC", "NGDP_D"],
    },
    "02-Inflation_Prix": {
        "title": "Inflation et Prix",
        "fill": "ED7D31",
        "indicators": ["PCPIEPCH"],
    },
    "03-Emploi": {
        "title": "Emploi et Chomage",
        "fill": "70AD47",
        "indicators": ["LUR"],
    },
    "04-Finances_Publiques": {
        "title": "Finances Publiques",
        "fill": "C00000",
        "indicators": ["GGR", "GGX", "GGXCNL", "GGXWDG"],
    },
    "05-Commerce_Exterieur": {
        "title": "Commerce Exterieur et Balance Courante",
        "fill": "5B9BD5",
        "indicators": ["BCA", "BCA_NGDPD", "TM_RPCH", "TX_RPCH"],
    },
    "06-Investissement": {
        "title": "Investissement",
        "fill": "FFC000",
        "indicators": ["NID_NGDP"],
    },
    "07-Demographie": {
        "title": "Demographie",
        "fill": "7030A0",
        "indicators": ["LP"],
    },
}


def build_table_data(indicators: List[str]) -> tuple[List[str], List[str], Dict]:
    """
    Retourne (headers, years, rows_dict) pour les indicateurs donnes.
    rows_dict[code] = {annee: valeur}
    """
    all_years: set = set()
    rows = {}
    for code in indicators:
        if code not in IMF_MOROCCO_VALUES:
            continue
        vals = IMF_MOROCCO_VALUES[code]
        rows[code] = vals
        all_years.update(vals.keys())
    sorted_years = sorted(all_years)
    return sorted_years, rows


def write_theme_excel(filename: str, theme: Dict) -> str:
    """Cree un fichier Excel colore pour un theme."""
    indicators = theme["indicators"]
    sorted_years, rows = build_table_data(indicators)
    title = theme["title"]
    accent = theme["fill"]

    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]

    # Titre
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(sorted_years) + 2)
    title_cell = ws.cell(row=1, column=1, value=f"MAROC — {title.upper()} — FMI WEO 1980-2029")
    title_cell.font = Font(name="Calibri", bold=True, size=14, color=accent)
    title_cell.alignment = Alignment(horizontal="center")

    # Sous-titre source
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(sorted_years) + 2)
    sub = ws.cell(row=2, column=1, value="Source: IMF World Economic Outlook (WEO) — Avril 2026")
    sub.font = Font(name="Calibri", italic=True, size=9, color="666666")
    sub.alignment = Alignment(horizontal="center")

    # Headers: ID | Name | annees...
    headers = ["Code", "Indicateur"] + [str(y) for y in sorted_years]
    ws.append(headers)
    _style_row(ws, 3, len(headers), HEADER_FILL, HEADER_FONT)

    # Data rows
    for i, code in enumerate(indicators):
        if code not in rows:
            continue
        meta = IMF_INDICATORS.get(code, {})
        row_data = [code, meta.get("name", "")]
        vals = rows[code]
        for y in sorted_years:
            v = vals.get(y, None)
            row_data.append(v)
        r = ws.max_row + 1
        ws.append(row_data)
        fill = BAND_1 if i % 2 == 0 else BAND_2
        _style_row(ws, r, len(headers), fill, DATA_FONT, is_data=True)

    # Color scale sur les colonnes de donnees (colonnes 3+)
    if len(indicators) > 0 and len(sorted_years) > 2:
        first_data_row = 4
        last_data_row = ws.max_row
        if last_data_row >= first_data_row:
            col_start = 3
            col_end = len(headers)
            cell_range = f"{get_column_letter(col_start)}{first_data_row}:{get_column_letter(col_end)}{last_data_row}"
            ws.conditional_formatting.add(
                cell_range,
                ColorScaleRule(
                    start_type="min", start_color="F8696B",
                    mid_type="percentile", mid_value=50, mid_color="FCFCFF",
                    end_type="max", end_color="63BE7B",
                ),
            )

    # Freeze panes
    ws.freeze_panes = "C4"

    # Largeurs
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 55
    for c in range(3, len(headers) + 1):
        ws.column_dimensions[get_column_letter(c)].width = 9

    path = BASE / f"{filename}.xlsx"
    wb.save(str(path))
    return str(path)


def _style_row(ws, row: int, ncols: int, fill, font, is_data=False):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = fill
        cell.font = font
        cell.border = BORDER
        if c == 2 and is_data:
            cell.alignment = WRAP
        else:
            cell.alignment = CENTER
    if is_data:
        ws.cell(row=row, column=1).font = Font(name="Consolas", bold=True, size=9, color="003366")


# ── Tableau de bord recapitulatif ────────────────────────────────────
def write_dashboard():
    """Cree un tableau de bord combine avec les KPIs 2026."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Tableau de Bord"

    # Titre
    ws.merge_cells("A1:H1")
    ws.cell(row=1, column=1, value="MAROC — TABLEAU DE BORD MACROECONOMIQUE — FMI WEO 2026").font = Font(
        name="Calibri", bold=True, size=16, color="003366"
    )

    ws.merge_cells("A2:H2")
    ws.cell(row=2, column=1, value="Indicateurs cles pour 2024 (reel), 2025 (estimation), 2026-2029 (projections)").font = Font(
        name="Calibri", italic=True, size=10, color="666666"
    )

    # Headers
    headers = ["Theme", "Indicateur", "Code", "Unite", "2024", "2025", "2026", "2029"]
    ws.append([])  # blank row
    ws.append(headers)
    _style_row(ws, 4, len(headers), HEADER_FILL, HEADER_FONT)

    # Theme mapping
    theme_map = {
        "NGDP_RPCH": "Croissance", "NGDPD": "Croissance", "NGDPDPC": "Croissance",
        "PCPIEPCH": "Inflation",
        "LUR": "Emploi",
        "GGR": "Finances", "GGX": "Finances", "GGXCNL": "Finances", "GGXWDG": "Finances",
        "BCA_NGDPD": "Commerce Exterieur", "TX_RPCH": "Commerce Exterieur", "TM_RPCH": "Commerce Exterieur",
        "NID_NGDP": "Investissement",
        "LP": "Demographie",
    }

    row = 5
    for code, meta in sorted(IMF_INDICATORS.items()):
        vals = IMF_MOROCCO_VALUES.get(code, {})
        v2024 = vals.get(2024, "")
        v2025 = vals.get(2025, "")
        v2026 = vals.get(2026, "")
        v2029 = vals.get(2029, "")
        theme = theme_map.get(code, "Autre")

        ws.cell(row=row, column=1, value=theme).font = Font(name="Calibri", bold=True, size=10)
        ws.cell(row=row, column=2, value=meta["name"]).font = Font(name="Calibri", size=9)
        ws.cell(row=row, column=3, value=code).font = Font(name="Consolas", size=9, color="003366")
        ws.cell(row=row, column=4, value=meta["unit"]).font = Font(name="Calibri", size=9)

        for ci, v in [(5, v2024), (6, v2025), (7, v2026), (8, v2029)]:
            cell = ws.cell(row=row, column=ci)
            if isinstance(v, float):
                cell.value = round(v, 3)
                cell.font = Font(name="Consolas", size=10, bold=True)
                cell.number_format = '#,##0.000'
            cell.alignment = CENTER
            cell.border = BORDER

        fill = BAND_1 if (row - 4) % 2 == 0 else BAND_2
        for c in range(1, len(headers) + 1):
            ws.cell(row=row, column=c).fill = fill
            ws.cell(row=row, column=c).border = BORDER

        row += 1

    # Color scale on 2024-2029 columns
    ws.conditional_formatting.add(
        f"E5:H{row - 1}",
        ColorScaleRule(
            start_type="min", start_color="F8696B",
            mid_type="percentile", mid_value=50, mid_color="FCFCFF",
            end_type="max", end_color="63BE7B",
        ),
    )

    ws.freeze_panes = "E5"
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 55
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 30
    for c in "EFGH":
        ws.column_dimensions[c].width = 14

    path = BASE / "09-Tableau_de_Bord.xlsx"
    wb.save(str(path))
    return str(path)


# ── VBA Search Macro ─────────────────────────────────────────────────
SEARCH_MACRO = """Attribute VB_Name = "SearchTables"
'=====================================================
' SearchTables - Macro de recherche pour tables Excel
' Utilisation: Ctrl+Shift+F ou via le ruban Developpeur
'=====================================================

Sub SearchAllTables()
    ' Recherche dans toutes les feuilles du classeur
    Dim searchTerm As String
    Dim ws As Worksheet
    Dim rng As Range
    Dim found As Range
    Dim firstAddress As String
    Dim results As String
    Dim count As Integer
    
    searchTerm = InputBox("Entrez le texte ou la valeur a rechercher dans toutes les tables:", "Recherche dans les tables")
    
    If searchTerm = "" Then Exit Sub
    
    count = 0
    results = "Resultats de la recherche pour: " & searchTerm & vbCrLf & vbCrLf
    
    For Each ws In ThisWorkbook.Worksheets
        Set rng = ws.UsedRange
        Set found = rng.Find(What:=searchTerm, LookIn:=xlValues, LookAt:=xlPart)
        
        If Not found Is Nothing Then
            firstAddress = found.Address
            Do
                count = count + 1
                results = results & "Feuille: " & ws.Name & " | Cellule: " & found.Address & _
                          " | Valeur: " & found.Value & vbCrLf
                Set found = rng.FindNext(found)
            Loop While Not found Is Nothing And found.Address <> firstAddress
        End If
    Next ws
    
    If count > 0 Then
        results = results & vbCrLf & "Total: " & count & " occurrence(s) trouvee(s)."
        MsgBox results, vbInformation, "Recherche terminee"
    Else
        MsgBox "Aucun resultat trouve pour: " & searchTerm, vbExclamation, "Recherche"
    End If
End Sub

Sub SearchCurrentSheet()
    ' Recherche uniquement dans la feuille active
    Dim searchTerm As String
    Dim rng As Range
    Dim found As Range
    Dim firstAddress As String
    Dim results As String
    Dim count As Integer
    
    searchTerm = InputBox("Entrez la valeur a rechercher dans la feuille active:", "Recherche dans la feuille")
    
    If searchTerm = "" Then Exit Sub
    
    count = 0
    results = "Resultats dans la feuille [" & ActiveSheet.Name & "] pour: " & searchTerm & vbCrLf & vbCrLf
    
    Set rng = ActiveSheet.UsedRange
    Set found = rng.Find(What:=searchTerm, LookIn:=xlValues, LookAt:=xlPart)
    
    If Not found Is Nothing Then
        firstAddress = found.Address
        Do
            count = count + 1
            results = results & "Cellule: " & found.Address & " | Valeur: " & found.Value & vbCrLf
            Set found = rng.FindNext(found)
        Loop While Not found Is Nothing And found.Address <> firstAddress
    End If
    
    If count > 0 Then
        results = results & vbCrLf & "Total: " & count & " occurrence(s) dans la feuille active."
        MsgBox results, vbInformation, "Recherche terminee"
    Else
        MsgBox "Aucun resultat trouve pour: " & searchTerm, vbExclamation, "Recherche"
    End If
End Sub

Sub HighlightSearchTerm()
    ' Recherche et surligne en jaune toutes les occurrences
    Dim searchTerm As String
    Dim rng As Range
    Dim found As Range
    Dim firstAddress As String
    
    searchTerm = InputBox("Entrez la valeur a surligner dans la feuille active:", "Surligner")
    
    If searchTerm = "" Then Exit Sub
    
    ' Effacer les couleurs precedentes
    Cells.Interior.ColorIndex = xlNone
    
    Set rng = ActiveSheet.UsedRange
    Set found = rng.Find(What:=searchTerm, LookIn:=xlValues, LookAt:=xlPart)
    
    If Not found Is Nothing Then
        firstAddress = found.Address
        Do
            found.Interior.Color = RGB(255, 255, 0)  ' Jaune
            Set found = rng.FindNext(found)
        Loop While Not found Is Nothing And found.Address <> firstAddress
        
        MsgBox "Recherche terminee. Toutes les occurrences sont surlignees en jaune.", vbInformation, "Surlignage"
    Else
        MsgBox "Aucun resultat trouve.", vbExclamation, "Recherche"
    End If
End Sub

Sub ClearHighlights()
    ' Efface tous les surlignages
    Cells.Interior.ColorIndex = xlNone
    MsgBox "Surlignages effaces.", vbInformation
End Sub
"""


# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Generation des tables Excel organisees")
    print("=" * 60)

    generated = []
    for filename, theme in THEMES.items():
        path = write_theme_excel(filename, theme)
        generated.append(path)
        print(f"  [OK] {Path(path).name}")

    path = write_dashboard()
    generated.append(path)
    print(f"  [OK] {Path(path).name}")

    # VBA macro
    macro_path = BASE / "08-Recherche_Macro.bas"
    macro_path.write_text(SEARCH_MACRO, encoding="utf-8")
    generated.append(str(macro_path))
    print(f"  [OK] {macro_path.name}")

    # Readme
    readme = """=== TABLES MACROECONOMIQUES MAROC - FMI WEO ===

Contenu:
"""
    for g in generated:
        readme += f"  - {Path(g).name}\n"
    readme += """
Utilisation:
  1. Ouvrez un fichier .xlsx
  2. Importez la macro VBA: Developpeur > Visual Basic > Fichier > Importer
     (ou双击 le fichier 08-Recherche_Macro.bas)
  3. Executez les macros via Developpeur > Macros ou les raccourcis:
     - SearchAllTables : Ctrl+Shift+F (recherche dans toutes les feuilles)
     - SearchCurrentSheet : Ctrl+Shift+S (recherche feuille active)
     - HighlightSearchTerm : Ctrl+Shift+H (surligner)
     - ClearHighlights : Ctrl+Shift+C (effacer surlignage)

Donnees:
  Source : FMI World Economic Outlook (WEO) - Avril 2026
  Periode : 1980-2029 (50 ans)
  Pays : Maroc (MAR)
"""
    readme_path = BASE / "README.txt"
    readme_path.write_text(readme, encoding="utf-8")
    print(f"  [OK] README.txt")

    print("-" * 60)
    print(f"Dossier genere : {BASE}")
    print(f"  {len(generated)} fichiers crees")
    print("=" * 60)


if __name__ == "__main__":
    main()
