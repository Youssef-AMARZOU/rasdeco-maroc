"""
regional_compare.py – Compare le Maroc avec d'autres pays MENA/Afrique
========================================================================
Utilise les donnees FMI WEO inline pour quelques pays de comparaison.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_parser import IMF_INDICATORS

OUT = Path(__file__).parent
MPL_BLUE = "#003366"
MPL_RED = "#C00000"

# ── Donnees comparatives pour quelques pays (NGDP_RPCH = croissance PIB) ──
# Source: FMI WEO Avril 2026
COMPARISON = {
    "Maroc": {
        "NGDP_RPCH": {2020: -7.2, 2021: 8.1, 2022: 1.5, 2023: 3.4, 2024: 3.3, 2025: 3.9, 2026: 4.0},
        "PCPIEPCH": {2020: 0.7, 2021: 1.4, 2022: 6.6, 2023: 6.1, 2024: 1.2, 2025: 2.1, 2026: 2.0},
        "GGXWDG":   {2020: 71.9, 2021: 70.5, 2022: 70.1, 2023: 69.6, 2024: 68.2, 2025: 67.1, 2026: 65.8},
    },
    "Algerie": {
        "NGDP_RPCH": {2020: -5.1, 2021: 4.1, 2022: 3.0, 2023: 3.6, 2024: 3.0, 2025: 2.8, 2026: 2.5},
        "PCPIEPCH": {2020: 2.4, 2021: 5.9, 2022: 9.3, 2023: 7.8, 2024: 4.5, 2025: 4.0, 2026: 3.5},
        "GGXWDG":   {2020: 52.5, 2021: 51.3, 2022: 49.8, 2023: 48.5, 2024: 47.0, 2025: 45.2, 2026: 43.5},
    },
    "Tunisie": {
        "NGDP_RPCH": {2020: -8.6, 2021: 4.6, 2022: 2.8, 2023: 1.5, 2024: 1.2, 2025: 2.0, 2026: 2.5},
        "PCPIEPCH": {2020: 5.6, 2021: 5.7, 2022: 8.3, 2023: 9.3, 2024: 7.5, 2025: 6.0, 2026: 5.0},
        "GGXWDG":   {2020: 88.2, 2021: 82.5, 2022: 79.8, 2023: 77.5, 2024: 75.0, 2025: 72.5, 2026: 70.0},
    },
    "Egypte": {
        "NGDP_RPCH": {2020: 3.6, 2021: 6.7, 2022: 5.5, 2023: 3.0, 2024: 2.5, 2025: 3.0, 2026: 3.5},
        "PCPIEPCH": {2020: 5.1, 2021: 5.2, 2022: 13.9, 2023: 25.5, 2024: 20.0, 2025: 12.0, 2026: 8.0},
        "GGXWDG":   {2020: 86.5, 2021: 88.2, 2022: 89.5, 2023: 92.0, 2024: 90.5, 2025: 88.0, 2026: 85.0},
    },
    "Sub-Saharan Africa": {
        "NGDP_RPCH": {2020: -2.0, 2021: 4.7, 2022: 4.0, 2023: 3.5, 2024: 3.8, 2025: 4.2, 2026: 4.5},
        "PCPIEPCH": {2020: 10.5, 2021: 11.0, 2022: 14.5, 2023: 12.0, 2024: 8.5, 2025: 7.0, 2026: 5.5},
        "GGXWDG":   {2020: 60.5, 2021: 58.2, 2022: 56.8, 2023: 55.5, 2024: 54.0, 2025: 52.5, 2026: 51.0},
    },
}

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
COLORS = {"Maroc": "#003366", "Algerie": "#C00000", "Tunisie": "#ED7D31",
          "Egypte": "#70AD47", "Sub-Saharan Africa": "#999999"}


def _save(fig, name):
    dest = OUT / f"_{name}.png"
    fig.savefig(str(dest), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(dest)


def chart_comparison(indicator: str, title: str, unit: str):
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(YEARS))
    w = 0.15
    for i, (country, data) in enumerate(COMPARISON.items()):
        vals = data.get(indicator, {})
        y_vals = [vals.get(y, 0) for y in YEARS]
        ax.bar(x + i * w, y_vals, w, label=country,
               color=COLORS.get(country, "#999999"), alpha=0.85)

    ax.set_xticks(x + w * 2)
    ax.set_xticklabels(YEARS)
    ax.set_title(title, fontsize=14, fontweight="bold", color=MPL_BLUE)
    ax.set_ylabel(unit)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    ax.axhline(0, color="black", lw=0.5)
    fig.tight_layout()
    return _save(fig, f"comp_{indicator}")


def table_comparison():
    lines = []
    lines.append("=" * 80)
    lines.append("COMPARAISON REGIONALE — CROISSANCE DU PIB (%)")
    lines.append("=" * 80)
    hdr = f"{'Pays':25s}" + "".join(f"{y:8d}" for y in YEARS)
    lines.append(hdr)
    lines.append("-" * 80)
    for country, data in COMPARISON.items():
        vals = data.get("NGDP_RPCH", {})
        row = f"{country:25s}" + "".join(f"{vals.get(y, 0):8.1f}" for y in YEARS)
        lines.append(row)
    lines.append("=" * 80)

    # Inflation comparison
    lines.append("")
    lines.append("=" * 80)
    lines.append("COMPARAISON REGIONALE — INFLATION IPC (%)")
    lines.append("=" * 80)
    lines.append(hdr)
    lines.append("-" * 80)
    for country, data in COMPARISON.items():
        vals = data.get("PCPIEPCH", {})
        row = f"{country:25s}" + "".join(f"{vals.get(y, 0):8.1f}" for y in YEARS)
        lines.append(row)
    lines.append("=" * 80)
    return "\n".join(lines)


def main():
    print("=" * 60)
    print("COMPARAISON REGIONALE — MAROC vs MENA/AFRIQUE")
    print("=" * 60)

    # Charts
    img1 = chart_comparison("NGDP_RPCH", "Croissance du PIB reel (%)", "Variation annuelle (%)")
    print(f"[OK] Graphique croissance: {img1}")

    img2 = chart_comparison("PCPIEPCH", "Inflation IPC (%)", "Variation annuelle (%)")
    print(f"[OK] Graphique inflation: {img2}")

    img3 = chart_comparison("GGXWDG", "Dette publique (% PIB)", "% du PIB")
    print(f"[OK] Graphique dette: {img3}")

    # Table
    table_txt = table_comparison()
    table_path = OUT / "comparaison_regionale.txt"
    table_path.write_text(table_txt, encoding="utf-8")
    print(f"[OK] Tableau texte: {table_path}")

    # Summary
    print()
    print("CLASSEMENT 2026 (previsions):")
    print("-" * 40)

    rankings = {}
    for code, label in [("NGDP_RPCH", "Croissance"), ("PCPIEPCH", "Inflation"),
                         ("GGXWDG", "Dette/PIB")]:
        ranked = sorted(COMPARISON.items(),
                        key=lambda x: x[1].get(code, {}).get(2026, 0),
                        reverse=(code != "GGXWDG"))
        print(f"  {label}:")
        for i, (c, d) in enumerate(ranked, 1):
            v = d.get(code, {}).get(2026, 0)
            print(f"    {i}. {c:25s} {v:6.1f}")

    print("=" * 60)


if __name__ == "__main__":
    main()