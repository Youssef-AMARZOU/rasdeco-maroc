"""
generate_pptx.py – Genere une presentation PowerPoint pro pour le Maroc
avec graphiques matplotlib importes et mise en page soignee.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.chart import XL_CHART_TYPE

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_parser import IMF_INDICATORS, IMF_MOROCCO_VALUES

# Couleurs Maroc
MAROC_GREEN = RGBColor(0x00, 0x66, 0x33)
MAROC_RED = RGBColor(0xC0, 0x00, 0x00)
DARK_BLUE = RGBColor(0x00, 0x33, 0x66)
GOLD = RGBColor(0xFF, 0xC0, 0x00)
GRAY = RGBColor(0x99, 0x99, 0x99)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Couleurs matplotlib
MPL_GREEN = "#006633"
MPL_RED = "#C00000"
MPL_BLUE = "#003366"
MPL_GOLD = "#FFC000"


def _save_chart(fig: plt.Figure, name: str) -> str:
    dest = Path(__file__).parent / f"_{name}.png"
    fig.savefig(str(dest), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(dest)


def chart_gdp_growth() -> str:
    """GDP growth line chart with recession shading."""
    vals = IMF_MOROCCO_VALUES.get("NGDP_RPCH", {})
    years = sorted(vals.keys())
    values = [vals[y] for y in years]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.fill_between(years, values, 0, where=[v >= 0 for v in values],
                    color=MPL_GREEN, alpha=0.15, label="Croissance positive")
    ax.fill_between(years, values, 0, where=[v < 0 for v in values],
                    color=MPL_RED, alpha=0.25, label="Recession")
    ax.plot(years, values, color=MPL_BLUE, linewidth=2, marker="o", markersize=3)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_title("Croissance du PIB reel (1980-2029)", fontsize=14, fontweight="bold", color=MPL_BLUE)
    ax.set_ylabel("Variation annuelle (%)")
    ax.set_xlabel("Annee")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig, "gdp_growth")


def chart_inflation() -> str:
    vals = IMF_MOROCCO_VALUES.get("PCPIEPCH", {})
    years = sorted(vals.keys())
    values = [vals[y] for y in years]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.fill_between(years, values, color=MPL_RED, alpha=0.2)
    ax.plot(years, values, color=MPL_RED, linewidth=2, marker="s", markersize=2)
    ax.axhline(2, color=MPL_GREEN, linestyle="--", linewidth=1, label="Cible BAM 2%")
    ax.set_title("Inflation IPC (1980-2029)", fontsize=14, fontweight="bold", color=MPL_RED)
    ax.set_ylabel("Variation annuelle (%)")
    ax.set_xlabel("Annee")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig, "inflation")


def chart_debt_deficit() -> str:
    debt = IMF_MOROCCO_VALUES.get("GGXWDG", {})
    deficit = IMF_MOROCCO_VALUES.get("GGXCNL", {})
    years = sorted(debt.keys())

    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.bar(years, [deficit.get(y, 0) for y in years], color=MPL_RED, alpha=0.6, label="Deficit (% PIB)")
    ax1.axhline(0, color="black", linewidth=0.5)
    ax1.set_ylabel("Deficit (% PIB)", color=MPL_RED)
    ax1.tick_params(axis="y", labelcolor=MPL_RED)

    ax2 = ax1.twinx()
    ax2.plot(years, [debt.get(y, 0) for y in years], color=MPL_BLUE, linewidth=2.5,
             marker="o", markersize=3, label="Dette (% PIB)")
    ax2.set_ylabel("Dette publique (% PIB)", color=MPL_BLUE)
    ax2.tick_params(axis="y", labelcolor=MPL_BLUE)

    ax1.set_title("Dette publique et deficit budgetaire (1990-2029)", fontsize=14, fontweight="bold", color=MPL_BLUE)
    ax1.set_xlabel("Annee")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig, "debt_deficit")


def chart_current_account() -> str:
    vals = IMF_MOROCCO_VALUES.get("BCA_NGDPD", {})
    years = sorted(vals.keys())
    values = [vals[y] for y in years]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    colors = [MPL_GREEN if v >= 0 else MPL_RED for v in values]
    ax.bar(years, values, color=colors, alpha=0.7, width=0.8)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_title("Balance courante (% PIB) — 1980-2029", fontsize=14, fontweight="bold", color=MPL_BLUE)
    ax.set_ylabel("% PIB")
    ax.set_xlabel("Annee")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig, "current_account")


def chart_gdp_per_capita() -> str:
    vals = IMF_MOROCCO_VALUES.get("NGDPDPC", {})
    years = sorted(vals.keys())
    values = [vals[y] for y in years]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.fill_between(years, values, alpha=0.3, color=MPL_GOLD)
    ax.plot(years, values, color="#CC8800", linewidth=2.5, marker="o", markersize=2)
    ax.set_title("PIB par habitant (USD courants) — 1980-2029", fontsize=14, fontweight="bold", color=MPL_BLUE)
    ax.set_ylabel("USD")
    ax.set_xlabel("Annee")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig, "gdp_per_capita")


def chart_unemployment() -> str:
    vals = IMF_MOROCCO_VALUES.get("LUR", {})
    years = sorted(vals.keys())
    values = [vals[y] for y in years]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.fill_between(years, values, color=MPL_RED, alpha=0.15)
    ax.plot(years, values, color=MPL_RED, linewidth=2, marker="^", markersize=2)
    ax.set_title("Taux de chomage (normes BIT) — 1980-2029", fontsize=14, fontweight="bold", color=MPL_RED)
    ax.set_ylabel("% population active")
    ax.set_xlabel("Annee")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig, "unemployment")


def add_slide_title(prs: Presentation, text: str, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    h, w = prs.slide_height, prs.slide_width
    # Background rectangle
    from pptx.util import Emu
    shape = slide.shapes.add_shape(
        1, Emu(0), Emu(0), w, h  # 1 = rectangle
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = DARK_BLUE
    shape.line.fill.background()

    txBox = slide.shapes.add_textbox(Emu(w // 2 - Inches(4)), Emu(h // 2 - Inches(1.5)), Inches(8), Inches(1.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(18)
        p2.font.color.rgb = RGBColor(0xFF, 0xD7, 0x00)
        p2.alignment = PP_ALIGN.CENTER
    return slide


def add_slide_chart(prs: Presentation, title: str, chart_path: str, note: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    h, w = prs.slide_height, prs.slide_width

    # Title
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # Chart image
    slide.shapes.add_picture(chart_path, Inches(0.5), Inches(0.9), Inches(8.5), Inches(4.5))

    # Note
    if note:
        txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(9), Inches(0.4))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = note
        p2.font.size = Pt(10)
        p2.font.italic = True
        p2.font.color.rgb = GRAY

    return slide


def add_summary_slide(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    h, w = prs.slide_height, prs.slide_width

    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "Tableau recapitulatif — Maroc"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = DARK_BLUE

    # Build table
    rows = 12
    cols = 5
    table_shape = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.0), Inches(9), Inches(4.5))
    table = table_shape.table

    headers = ["Indicateur", "2023", "2024", "2025", "2026"]
    data_rows = [
        ["Croissance PIB (%)", "3.36", "3.30", "3.90", "4.00"],
        ["Inflation IPC (%)", "6.09", "1.16", "2.09", "2.00"],
        ["Chomage (%)", "12.40", "12.20", "12.00", "12.20"],
        ["Dette/PIB (%)", "69.57", "68.22", "67.14", "65.84"],
        ["Deficit/PIB (%)", "-3.45", "-3.30", "-3.48", "-3.47"],
        ["PIB/hab (USD)", "4,525", "4,763", "5,198", "5,107"],
        ["Balance courante (%PIB)", "-2.12", "-2.72", "-3.01", "-3.24"],
        ["Investissement (%PIB)", "28.72", "29.05", "29.39", "29.79"],
        ["Population (M)", "31.83", "32.00", "32.17", "32.33"],
        ["Exportations (var%)", "5.52", "7.36", "4.71", "3.90"],
        ["Importations (var%)", "1.92", "4.61", "3.52", "3.50"],
    ]

    for ci, hdr in enumerate(headers):
        cell = table.cell(0, ci)
        cell.text = hdr
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BLUE

    for ri, row_data in enumerate(data_rows, 1):
        for ci, val in enumerate(row_data):
            cell = table.cell(ri, ci)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(10)
                p.alignment = PP_ALIGN.CENTER
                if ci == 0:
                    p.font.bold = True
                    p.alignment = PP_ALIGN.LEFT
            if ri % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xE8, 0xF0, 0xFE)

    # Source
    txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(5.6), Inches(9), Inches(0.3))
    tf2 = txBox2.text_frame
    p2 = tf2.paragraphs[0]
    p2.text = "Source: FMI World Economic Outlook (WEO) — Avril 2026"
    p2.font.size = Pt(9)
    p2.font.italic = True
    p2.font.color.rgb = GRAY

    return slide


def main():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Slide 1: Title
    add_slide_title(prs, "MAROC", "Indicateurs macroeconomiques 1980-2029\nFMI World Economic Outlook (WEO) — Avril 2026")

    # Slide 2: GDP Growth
    add_slide_chart(prs, "Croissance du PIB reel",
                    chart_gdp_growth(),
                    "Source: FMI WEO (NGDP_RPCH). Periodes de recession (barres rouges) correspondant aux annees de croissance negative.")

    # Slide 3: Inflation
    add_slide_chart(prs, "Inflation IPC",
                    chart_inflation(),
                    "Source: FMI WEO (PCPIEPCH). La ligne pointillee verte represente la cible de 2% de Bank Al-Maghrib.")

    # Slide 4: Unemployment
    add_slide_chart(prs, "Taux de chomage",
                    chart_unemployment(),
                    "Source: FMI WEO (LUR). Taux selon les normes du Bureau International du Travail (BIT).")

    # Slide 5: Debt & Deficit
    add_slide_chart(prs, "Dette publique et deficit budgetaire",
                    chart_debt_deficit(),
                    "Source: FMI WEO (GGXWDG, GGXCNL). Deficit = net lending/borrowing de l'administration publique.")

    # Slide 6: Current Account
    add_slide_chart(prs, "Balance courante",
                    chart_current_account(),
                    "Source: FMI WEO (BCA_NGDPD). Barres vertes = excedent, barres rouges = deficit.")

    # Slide 7: GDP per capita
    add_slide_chart(prs, "PIB par habitant",
                    chart_gdp_per_capita(),
                    "Source: FMI WEO (NGDPDPC). PIB en USD courants divise par la population totale.")

    # Slide 8: Summary table
    add_summary_slide(prs)

    # Slide 9: End
    add_slide_title(prs, "Merci", "Donnees FMI WEO — Avril 2026\nGeneration automatisee avec Python + python-pptx")

    path = Path(__file__).parent / "Maroc_Macro_Indicateurs.pptx"
    prs.save(str(path))
    print(f"[OK] Presentation generee: {path}")

    # Cleanup temp charts
    for f in Path(__file__).parent.glob("_*.png"):
        f.unlink()


if __name__ == "__main__":
    main()