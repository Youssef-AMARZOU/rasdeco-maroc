#!/usr/bin/env python3
"""
main.py – Orchestrateur Data Engineering Maroc
================================================
1. Parse les données FMI (inline ou fichier brut) → JSON propre
2. Génère le fichier Excel multi-sheet
3. Affiche un résumé dans la console

Usage :
    python main.py                          # données inline
    python main.py --input weo.json         # depuis fichier brut
    python main.py --input weo.json --output-dir ./out
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from data_parser import (
    MoroccoDataParser,
    build_definitions_rows,
    build_time_series_matrix,
    build_wb_rows,
)
from excel_formatter import generate_excel


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extraction Maroc (FMI + BM) → JSON propre + Excel"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Chemin vers le fichier JSON brut du FMI (WEO). Si omis, utilise les données inline.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=".",
        help="Répertoire de sortie (défaut: courant)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Extraction ────────────────────────────────────────────────
    print("=" * 60)
    print("MAR  Morocco Data Engineering Pipeline")
    print("=" * 60)

    if args.input:
        print(f"\n>>  Lecture du fichier brut : {args.input}")
        parser_inst = MoroccoDataParser.from_file(args.input)
        records = parser_inst.extract_morocco()
        print(f"   OK {len(records)} indicateurs extraits depuis MAR")
    else:
        print("\n>>  Utilisation des donnees inline (Maroc uniquement)")
        records = MoroccoDataParser.build_inline_records()
        print(f"   OK {len(records)} indicateurs charges depuis les donnees inline")

    # ── 2. Export JSON propre ────────────────────────────────────────
    json_path = out_dir / "morocco_imf_data.json"
    payload = {
        "country": "Morocco",
        "country_code": "MAR",
        "source": "IMF World Economic Outlook (WEO)",
        "indicators": records,
    }
    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\n>>  JSON propre : {json_path} ({json_path.stat().st_size / 1024:.1f} KB)")

    # ── 3. Matrices pour Excel ──────────────────────────────────────
    fmi_rows, years = build_time_series_matrix(records)
    wb_rows = build_wb_rows()
    def_rows = build_definitions_rows(records)

    print(
        f"   Matrice FMI    : {len(fmi_rows)} indicateurs x {len(years)} annees"
    )
    print(f"   Banque Mondiale : {len(wb_rows)} series")
    print(f"   Definitions     : {len(def_rows)} entrees")

    # ── 4. Génération Excel ─────────────────────────────────────────
    xlsx_path = generate_excel(
        fmi_rows=fmi_rows,
        years=years,
        wb_rows=wb_rows,
        def_rows=def_rows,
        output_path=str(out_dir / "morocco_data.xlsx"),
    )
    xlsx_file = Path(xlsx_path)
    print(f"\n>>  Excel genere : {xlsx_path} ({xlsx_file.stat().st_size / 1024:.1f} KB)")

    # ── 5. Résumé console ────────────────────────────────────────────
    print("\n" + "-" * 60)
    print("RESUME — MAROC")
    print("-" * 60)

    # Dernière année réelle (non-estimation)
    real_year = 2024  # la dernière année avec valeurs réelles
    proj_year = 2029

    for rec in records:
        y_map = {y["year"]: y["value"] for y in rec["years"]}
        latest = y_map.get(real_year, "N/A")
        proj = y_map.get(proj_year, "N/A")
        if isinstance(latest, float):
            print(f"   {rec['indicator_id']:12s} ({real_year}) : {latest:>12.3f}  |  ({proj_year}) : {proj}")
        else:
            print(f"   {rec['indicator_id']:12s} ({real_year}) : {latest!r:>12}  |  ({proj_year}) : {proj!r}")

    print("-" * 60)
    print("OK  Pipeline termine avec succes.")
    print(f"   JSON -> {json_path}")
    print(f"   XLSX -> {xlsx_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
