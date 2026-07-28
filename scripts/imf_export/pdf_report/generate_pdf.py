"""
generate_pdf.py – Rapport PDF complet Maroc (17 indicateurs FMI)
=================================================================
Genere un rapport professionnel A4 avec tous les indicateurs macro,
graphiques matplotlib, tableaux de donnees, et analyse regionale.
"""

from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_parser import IMF_INDICATORS, IMF_MOROCCO_VALUES

OUT = Path(__file__).parent
MPL_BLUE = "#003366"
MPL_RED = "#C00000"
MPL_GREEN = "#006633"
MPL_GOLD = "#FFC000"
MPL_PURPLE = "#7030A0"

def _fig(fig, name):
    dest = OUT / f"_{name}.png"
    fig.savefig(str(dest), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(dest)

def _ts(code):
    vals = IMF_MOROCCO_VALUES.get(code, {})
    y, v = zip(*sorted(vals.items()))
    return list(y), list(v)

# ── CHARTS ──────────────────────────────────────────────────────────

def chart_gdp_growth():
    y, v = _ts("NGDP_RPCH")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, 0, where=[x >= 0 for x in v], color=MPL_GREEN, alpha=0.15)
    ax.fill_between(y, v, 0, where=[x < 0 for x in v], color=MPL_RED, alpha=0.25)
    ax.plot(y, v, color=MPL_BLUE, lw=2.5, marker="o", markersize=2.5)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_title("Croissance du PIB reel (%)", fontsize=13, fontweight="bold", color=MPL_BLUE)
    ax.set_ylabel("Variation annuelle (%)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "gdp")

def chart_gdp_level():
    y, v = _ts("NGDPD")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, alpha=0.3, color=MPL_BLUE)
    ax.plot(y, v, color=MPL_BLUE, lw=2.5)
    ax.set_title("PIB nominal (millions USD)", fontsize=13, fontweight="bold", color=MPL_BLUE)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "gdp_level")

def chart_gdp_per_capita():
    y, v = _ts("NGDPDPC")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, alpha=0.3, color=MPL_GOLD)
    ax.plot(y, v, color="#CC8800", lw=2.5, marker="o", markersize=2)
    ax.set_title("PIB par habitant (USD courants)", fontsize=13, fontweight="bold", color=MPL_BLUE)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "gdppc")

def chart_inflation():
    y, v = _ts("PCPIEPCH")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, color=MPL_RED, alpha=0.2)
    ax.plot(y, v, color=MPL_RED, lw=2, marker="s", markersize=2)
    ax.axhline(2, color=MPL_GREEN, ls="--", lw=1, label="Cible BAM 2%")
    ax.set_title("Inflation IPC (%)", fontsize=13, fontweight="bold", color=MPL_RED)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "inf")

def chart_gdp_deflator():
    y, v = _ts("NGDP_D")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, alpha=0.25, color=MPL_PURPLE)
    ax.plot(y, v, color=MPL_PURPLE, lw=2)
    ax.set_title("Deflateur du PIB (Index)", fontsize=13, fontweight="bold", color=MPL_PURPLE)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "deflator")

def chart_unemployment():
    y, v = _ts("LUR")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, color=MPL_RED, alpha=0.15)
    ax.plot(y, v, color=MPL_RED, lw=2.5, marker="^", markersize=2.5)
    ax.set_title("Taux de chomage (% population active)", fontsize=13, fontweight="bold", color=MPL_RED)
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "unemp")

def chart_gov_finance():
    debt_y, debt_v = _ts("GGXWDG")
    rev = {k: v for k, v in IMF_MOROCCO_VALUES.get("GGR", {}).items()}
    exp = {k: v for k, v in IMF_MOROCCO_VALUES.get("GGX", {}).items()}
    deficit = IMF_MOROCCO_VALUES.get("GGXCNL", {})
    y = sorted(debt_y)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.8))

    ax1.bar(y, [deficit.get(yy, 0) for yy in y], color=MPL_RED, alpha=0.6, width=0.8)
    ax1.axhline(0, color="black", lw=0.5)
    ax1.set_title("Deficit (% PIB)", fontsize=11, fontweight="bold", color=MPL_RED)
    ax1.grid(True, alpha=0.3)

    ax2.plot(y, [debt_v[i] for i in range(len(y))], color=MPL_BLUE, lw=2.5, marker="o", markersize=2)
    ax2.fill_between(y, [debt_v[i] for i in range(len(y))], alpha=0.2, color=MPL_BLUE)
    ax2.set_title("Dette publique (% PIB)", fontsize=11, fontweight="bold", color=MPL_BLUE)
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "govfin")

def chart_gov_rev_exp():
    rev = IMF_MOROCCO_VALUES.get("GGR", {})
    exp = IMF_MOROCCO_VALUES.get("GGX", {})
    y = sorted(set(list(rev.keys()) + list(exp.keys())))
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.plot(y, [rev.get(yy, 0) for yy in y], color=MPL_GREEN, lw=2, label="Recettes")
    ax.plot(y, [exp.get(yy, 0) for yy in y], color=MPL_RED, lw=2, label="Depenses")
    ax.fill_between(y, [rev.get(yy, 0) for yy in y], [exp.get(yy, 0) for yy in y],
                     where=[rev.get(yy, 0) <= exp.get(yy, 0) for yy in y],
                     color=MPL_RED, alpha=0.1)
    ax.set_title("Recettes et depenses publiques (% PIB)", fontsize=13, fontweight="bold", color=MPL_BLUE)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "govexp")

def chart_current_account():
    y, v = _ts("BCA_NGDPD")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    colors_bar = [MPL_GREEN if x >= 0 else MPL_RED for x in v]
    ax.bar(y, v, color=colors_bar, alpha=0.7, width=0.8)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_title("Balance courante (% PIB)", fontsize=13, fontweight="bold", color=MPL_BLUE)
    ax.set_ylabel("% PIB")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "bca")

def chart_trade_volumes():
    y_exp, v_exp = _ts("TX_RPCH")
    y_imp, v_imp = _ts("TM_RPCH")
    y = sorted(set(y_exp + y_imp))
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.plot(y_exp, v_exp, color=MPL_GREEN, lw=2, marker="o", markersize=2, label="Exportations")
    ax.plot(y_imp, v_imp, color=MPL_RED, lw=2, marker="s", markersize=2, label="Importations")
    ax.axhline(0, color="black", lw=0.5)
    ax.set_title("Volume du commerce exterieur (var. annuelle %)", fontsize=12, fontweight="bold", color=MPL_BLUE)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "trade")

def chart_investment():
    y, v = _ts("NID_NGDP")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, alpha=0.3, color=MPL_GOLD)
    ax.plot(y, v, color="#CC8800", lw=2.5, marker="o", markersize=2)
    ax.axhline(30, color=MPL_BLUE, ls="--", lw=1, label="Seuil 30%")
    ax.set_title("Investissement total (% PIB)", fontsize=13, fontweight="bold", color=MPL_BLUE)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "invest")

def chart_population():
    y, v = _ts("LP")
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.fill_between(y, v, alpha=0.3, color=MPL_PURPLE)
    ax.plot(y, v, color=MPL_PURPLE, lw=2.5, marker="o", markersize=2)
    ax.set_title("Population (millions)", fontsize=13, fontweight="bold", color=MPL_PURPLE)
    ax.set_ylabel("Millions")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _fig(fig, "pop")

# ── STYLES ──────────────────────────────────────────────────────────
B3 = HexColor("#003366")
B4 = HexColor("#4472C4")
GRAY_FILL = HexColor("#F2F2F2")
WHITE_FILL = white
GRAY_TXT = HexColor("#666666")

def _make_table(data, col_widths, repeat=1):
    t = Table(data, colWidths=col_widths, repeatRows=repeat)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), B3),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GRAY_FILL]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (0, -1), 7.5),
    ]))
    return t

# ── BUILD ───────────────────────────────────────────────────────────

def build_pdf():
    path = OUT / "Maroc_Rapport_Macro.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm,
                            topMargin=1.8*cm, bottomMargin=1.8*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitleBlue", parent=styles["Title"],
                               textColor=B3, fontSize=24, spaceAfter=4))
    styles.add(ParagraphStyle("SubTitle", parent=styles["Normal"],
                               textColor=GRAY_TXT, fontSize=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle("SectionHead", parent=styles["Heading2"],
                               textColor=B3, fontSize=14, spaceBefore=16, spaceAfter=6))
    styles.add(ParagraphStyle("SubSection", parent=styles["Heading3"],
                               textColor=B4, fontSize=11, spaceBefore=10, spaceAfter=4))
    styles.add(ParagraphStyle("BodyText2", parent=styles["Normal"], fontSize=8.5, leading=11))
    styles.add(ParagraphStyle("SmallNote", parent=styles["Normal"], fontSize=6.5,
                               textColor=HexColor("#999999"), alignment=TA_CENTER))
    styles.add(ParagraphStyle("TableHeader", parent=styles["Normal"], fontSize=6.5,
                               textColor=white, alignment=TA_CENTER))

    E = []

    # ════════════════════════════════════════════════════════════════
    # PAGE DE GARDE
    # ════════════════════════════════════════════════════════════════
    E.append(Spacer(1, 4*cm))
    E.append(Paragraph("RAPPORT MACROECONOMIQUE", styles["TitleBlue"]))
    E.append(Paragraph("MAROC 1980-2029", styles["TitleBlue"]))
    E.append(Spacer(1, 0.5*cm))
    E.append(Paragraph("by AMARZOU Youssef", styles["SubTitle"]))
    E.append(Spacer(1, 0.3*cm))
    E.append(Paragraph("Donnees issues du FMI World Economic Outlook (WEO) — Avril 2026", styles["SubTitle"]))
    E.append(Spacer(1, 0.3*cm))
    E.append(Paragraph("17 indicateurs macroeconomiques | 50 annees de donnees (1980-2029)", styles["SubTitle"]))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # TABLEAU RECAPITULATIF COMPLET (tous les 17 indicateurs)
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("Synthese generale — Tous les indicateurs", styles["SectionHead"]))
    E.append(Paragraph("Valeurs pour les annees clefs : historique (1980, 1990, 2000, 2010, 2020) et recentes (2023-2029)",
                       styles["SmallNote"]))

    all_indicators = [
        ("NGDP_RPCH", "Croissance du PIB (%)"),
        ("NGDP", "PIB constant (Mds NCU)"),
        ("NGDPD", "PIB courant (M USD)"),
        ("NGDPDPC", "PIB par habitant (USD)"),
        ("NGDP_D", "Deflateur PIB (Index)"),
        ("PCPIEPCH", "Inflation IPC (%)"),
        ("LUR", "Taux de chomage (%)"),
        ("NID_NGDP", "Investissement (% PIB)"),
        ("TX_RPCH", "Exportations (var. %)"),
        ("TM_RPCH", "Importations (var. %)"),
        ("GGR", "Recettes publiques (% PIB)"),
        ("GGX", "Depenses publiques (% PIB)"),
        ("GGXCNL", "Deficit (% PIB)"),
        ("GGXWDG", "Dette publique (% PIB)"),
        ("BCA", "Balance courante (M USD)"),
        ("BCA_NGDPD", "Balance courante (% PIB)"),
        ("LP", "Population (millions)"),
    ]
    summary_years = [1980, 1990, 2000, 2010, 2020, 2023, 2024, 2025, 2026, 2029]
    header = ["Indicateur"] + [str(y) for y in summary_years]
    table_data = [header]
    for code, label in all_indicators:
        vals = IMF_MOROCCO_VALUES.get(code, {})
        row = [label]
        for y in summary_years:
            v = vals.get(y)
            if v is None:
                row.append("-")
            elif abs(v) >= 1000 or code in ("NGDPD", "BCA"):
                row.append(f"{v:,.1f}")
            elif abs(v) >= 100:
                row.append(f"{v:,.2f}")
            else:
                row.append(f"{v:,.3f}")
        table_data.append(row)

    col_w = [4.5*cm] + [1.1*cm]*len(summary_years)
    E.append(_make_table(table_data, col_w))
    E.append(Paragraph("Source: FMI World Economic Outlook (WEO) Database — Avril 2026", styles["SmallNote"]))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 1 : CROISSANCE ET PIB
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("1. Croissance economique et PIB", styles["SectionHead"]))
    E.append(Image(chart_gdp_growth(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Le PIB du Maroc a connu une forte volatilite historique avec des recessions en 1981 (-2.8%), 1987 (-2.5%), "
        "1992-93, 1995 (-6.6%) et 2020 (-7.2%, COVID-19). Les periodes de forte expansion incluent 1996 (+12.0%), "
        "1988 (+10.4%) et 1994 (+10.7%). Les projections du FMI tablent sur une croissance stabilisee autour de 4% pour 2026-2028.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.3*cm))

    E.append(Image(chart_gdp_level(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Le PIB nominal en USD est passe de 21 milliards en 1980 a 152 milliards en 2024. Les projections 2029 atteignent "
        "258 milliards USD, soit un quasi-doublement en 5 ans. La croissance du PIB en volume et l'appreciation du taux de change effectif expliquent cette progression.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.3*cm))

    E.append(Image(chart_gdp_per_capita(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Le PIB par habitant est passe de ~1,079 USD en 1980 a 4,763 USD en 2024 et devrait atteindre 6,493 USD en 2029. "
        "La progression est constante malgre la croissance demographique. Le Maroc se rapproche du seuil des 6,000 USD qui caracterise les pays a revenu intermediaire superieur.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))

    # Mini-tableau PIB
    E.append(Paragraph("Tableau : Evolution du PIB", styles["SubSection"]))
    gdp_codes = [("NGDP_RPCH", "Croissance PIB (%)"), ("NGDPD", "PIB nominal (M USD)"),
                 ("NGDPDPC", "PIB/hab (USD)"), ("NGDP_D", "Deflateur")]
    tdata = [["Indicateur", "2010", "2015", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "2029"]]
    for code, label in gdp_codes:
        vals = IMF_MOROCCO_VALUES.get(code, {})
        row = [label]
        for y in [2010, 2015, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2029]:
            v = vals.get(y)
            if v is None: row.append("-")
            elif code == "NGDPD": row.append(f"{v:,.0f}")
            else: row.append(f"{v:,.3f}")
        tdata.append(row)
    E.append(_make_table(tdata, [3.5*cm] + [1.25*cm]*10))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 2 : INFLATION ET PRIX
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("2. Inflation et prix", styles["SectionHead"]))
    E.append(Image(chart_inflation(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "L'inflation a connu un pic a 12.0% en 1981, puis une tendance baissiere structurelle grace a la discipline monetaire. "
        "Le choc de 2022 (6.6%) etait lie aux prix internationaux des matieres premieres et de l'energie. "
        "Bank Al-Maghrib cible 2% depuis 2016 et les projections 2026-2029 sont stables a 2%.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.3*cm))
    E.append(Image(chart_gdp_deflator(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Le deflateur du PIB suit une progression reguliere, passant de 0.12 en 1980 a 0.49 en 2029 (projection). "
        "Il reflete l'inflation sous-jacente de l'ensemble de l'economie, incluant les biens et services non-consommes directement par les menages.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 3 : EMPLOI
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("3. Marche du travail", styles["SectionHead"]))
    E.append(Image(chart_unemployment(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Le taux de chomage (normes BIT) a culmine dans les annees 1990 (15.9% en 1996) avant de baisser progressivement "
        "jusqu'a 8.9% en 2011. La crise COVID a fait remonter le taux a 12.3% en 2021. Les projections 2026-2029 le "
        "situent autour de 12.2%, refletant un chomage structurel persistant malgre la croissance economique.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))

    E.append(Paragraph("Tableau : Chomage par periode", styles["SubSection"]))
    tdata = [["Annee", "1990", "1995", "2000", "2005", "2010", "2015", "2020", "2023", "2024", "2025", "2029"]]
    vals = IMF_MOROCCO_VALUES.get("LUR", {})
    row = ["Taux (%)"]
    for y in [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023, 2024, 2025, 2029]:
        v = vals.get(y)
        row.append(f"{v:.1f}%" if v else "-")
    tdata.append(row)
    E.append(_make_table(tdata, [3*cm] + [1.2*cm]*11))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 4 : FINANCES PUBLIQUES
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("4. Finances publiques", styles["SectionHead"]))
    E.append(Image(chart_gov_finance(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "La dette publique a culmine a 82.6% du PIB en 1995, puis a entame un repli jusqu'a 48% en 2009-2010. "
        "Le choc COVID a fait remonter la dette a 71.9% en 2020. La trajectoire est descendante jusqu'a 62.3% en 2029. "
        "Le deficit budgetaire est stable autour de -3.5% du PIB sur la periode de projection.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.3*cm))

    E.append(Image(chart_gov_rev_exp(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Les recettes publiques oscillent autour de 28-30% du PIB, tandis que les depenses se situent entre 30-35%. "
        "L'ecart structurel creuse un deficit persistant. Les recettes ont atteint un pic a 31.6% en 2008 et les "
        "depenses un maximum a 34.9% en 2020 (mesures COVID). Le redressement budgetaire est progressif.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))

    E.append(Paragraph("Tableau : Finances publiques (% PIB)", styles["SubSection"]))
    fin_codes = [("GGR", "Recettes"), ("GGX", "Depenses"), ("GGXCNL", "Deficit"), ("GGXWDG", "Dette")]
    tdata = [["Indicateur", "2000", "2005", "2010", "2015", "2020", "2023", "2024", "2025", "2026", "2029"]]
    for code, label in fin_codes:
        vals = IMF_MOROCCO_VALUES.get(code, {})
        row = [label]
        for y in [2000, 2005, 2010, 2015, 2020, 2023, 2024, 2025, 2026, 2029]:
            v = vals.get(y)
            row.append(f"{v:.2f}%" if v is not None else "-")
        tdata.append(row)
    E.append(_make_table(tdata, [3*cm] + [1.3*cm]*10))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 5 : SECTEUR EXTERIEUR
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("5. Secteur exterieur", styles["SectionHead"]))
    E.append(Image(chart_current_account(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Le Maroc presente un deficit courant chronique, compense par les investissements directs etrangers et "
        "les transferts des MRE. Seules quelques annees (1988, 1992-93, 1996, 2001-2002, 2005-2006) ont connu un excedent. "
        "Le deficit se creuse progressivement dans les projections 2026-2029, passant de -3.2% a -4.3% du PIB.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.3*cm))

    E.append(Image(chart_trade_volumes(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "Les exportations et importations montrent une forte volatilite, avec des chocs majeurs en 2009 (-12% exports) "
        "et 2020 (-20% exports). Le rebond post-COVID a ete vigoureux (+25% exports en 2021). Les projections montrent "
        "une stabilisation autour de 3.5-4% pour les exports et 3.5% pour les imports.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))

    E.append(Paragraph("Tableau : Balance courante et commerce", styles["SubSection"]))
    ext_codes = [("BCA_NGDPD", "Balance courante (% PIB)"), ("BCA", "Balance courante (M USD)"),
                 ("TX_RPCH", "Exports (var. %)"), ("TM_RPCH", "Imports (var. %)")]
    tdata = [["Indicateur", "2000", "2005", "2010", "2015", "2020", "2023", "2024", "2025", "2026", "2029"]]
    for code, label in ext_codes:
        vals = IMF_MOROCCO_VALUES.get(code, {})
        row = [label]
        for y in [2000, 2005, 2010, 2015, 2020, 2023, 2024, 2025, 2026, 2029]:
            v = vals.get(y)
            if v is None: row.append("-")
            elif code == "BCA": row.append(f"{v:,.0f}")
            else: row.append(f"{v:.2f}%")
        tdata.append(row)
    E.append(_make_table(tdata, [3.5*cm] + [1.25*cm]*10))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 6 : INVESTISSEMENT
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("6. Investissement", styles["SectionHead"]))
    E.append(Image(chart_investment(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "L'investissement total (FBCF) oscille autour de 30% du PIB, un niveau correct pour un pays emergent. "
        "Le taux d'investissement a atteint un pic de 31.4% en 2018 et un minimum de 22.1% en 1997. "
        "Les projections 2026-2029 le maintiennent autour de 29-30% du PIB.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # SECTION 7 : DEMOGRAPHIE
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("7. Demographie", styles["SectionHead"]))
    E.append(Image(chart_population(), width=16*cm, height=7*cm))
    E.append(Paragraph(
        "La population marocaine est passee de 19.7 millions en 1980 a 32.0 millions en 2024, soit une croissance "
        "de +62% en 44 ans. Le rythme de croissance ralentit progressivement : +2.5% par an dans les annees 1980 "
        "contre +0.5% actuellement. Les projections 2029 atteignent 32.8 millions.",
        styles["BodyText2"]))
    E.append(Spacer(1, 0.5*cm))

    E.append(Paragraph("Tableau : Population 1980-2029", styles["SubSection"]))
    vals = IMF_MOROCCO_VALUES.get("LP", {})
    pop_years = list(range(1980, 2030, 5))
    tdata = [["Annee"] + [str(y) for y in pop_years]]
    row = ["Population (M)"]
    for y in pop_years:
        v = vals.get(y)
        row.append(f"{v:.3f}" if v else "-")
    tdata.append(row)
    # Croissance decennale
    row2 = ["Croiss. (%)"]
    prev = vals.get(pop_years[0])
    for y in pop_years[1:]:
        v = vals.get(y)
        if prev and v:
            row2.append(f"{(v/prev - 1)*100:.1f}%")
        else:
            row2.append("-")
        prev = v
    # Growing rate per 5-year period
    taux_list = []
    for i in range(2, len(pop_years)):
        y_prev = vals.get(pop_years[i-1])
        y_cur = vals.get(pop_years[i])
        if y_prev and y_cur:
            ann = ((y_cur / y_prev) ** 0.2 - 1) * 100
            taux_list.append(f"{ann:.2f}%")
        else:
            taux_list.append("-")
    tdata.append(["Taux annuel"] + [""] + taux_list)
    E.append(_make_table(tdata, [3*cm] + [1.4*cm]*len(pop_years)))
    E.append(PageBreak())

    # ════════════════════════════════════════════════════════════════
    # ANNEXE : TABLEAUX COMPLETS
    # ════════════════════════════════════════════════════════════════
    E.append(Paragraph("Annexe — Series temporelles completes", styles["SectionHead"]))
    E.append(Paragraph("Tous les indicateurs avec donnees annees par annees. Source: FMI WEO Avril 2026.",
                       styles["BodyText2"]))
    E.append(Spacer(1, 0.3*cm))

    # Pour chaque indicateur, un mini tableau
    display_years = list(range(1980, 2030, 5))
    for code, meta in sorted(IMF_INDICATORS.items()):
        vals = IMF_MOROCCO_VALUES.get(code, {})
        if not vals:
            continue
        E.append(Paragraph(f"{meta['name']} ({meta['unit']}) — Code: {code}", styles["SubSection"]))
        tdata = [["Annee"] + [str(y) for y in display_years]]
        row = ["Valeur"]
        for y in display_years:
            v = vals.get(y)
            if v is None:
                row.append("-")
            elif abs(v) >= 10000 or code in ("NGDPD", "BCA", "NGDP"):
                row.append(f"{v:,.1f}")
            else:
                row.append(f"{v:.3f}")
        tdata.append(row)
        col_w2 = [2*cm] + [1.4*cm]*len(display_years)
        E.append(_make_table(tdata, col_w2))
        E.append(Spacer(1, 0.2*cm))

    E.append(Spacer(1, 1*cm))
    E.append(Paragraph("Fin du rapport. Generation automatisee — by AMARZOU Youssef", styles["SmallNote"]))

    doc.build(E)
    print(f"[OK] Rapport PDF genere: {path}")

if __name__ == "__main__":
    build_pdf()