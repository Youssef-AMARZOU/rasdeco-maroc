"""
quality_report.py -- Rapport de controle qualite avant chargement.

Genere un texte structure contenant :
  - Nombre total de lignes
  - % de valeurs manquantes par indicateur
  - Plage de dates couvertes
  - Doublons detectes
  - Statistiques par source et domaine

Le rapport est affiche en console ET sauvegarde dans
data/curated/economie/quality_report_{timestamp}.txt
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

CURATED_ROOT = Path(__file__).resolve().parents[3] / "data" / "curated" / "economie"


def _safe_pct(part: int, total: int) -> str:
    if total == 0:
        return "0.0"
    return f"{part / total * 100:.1f}"


def generate_report(df: pl.DataFrame, title: str = "Rapport de controle") -> str:
    """Genere le rapport texte complet."""
    now = datetime.now(timezone.utc).isoformat()
    total = len(df)

    if total == 0:
        msg = (
            "+==============================================+\n"
            "|   RAPPORT DE CONTRoLE -- TABLE VIDE           |\n"
            "+==============================================+\n"
        )
        return msg

    lines = []
    lines.append("=" * 70)
    lines.append(f"  {title}")
    lines.append(f"  Genere le : {now}")
    lines.append("=" * 70)
    lines.append("")

    # -- Statistiques generales
    lines.append("-- 1. VUE D'ENSEMBLE --")
    lines.append(f"  Total lignes              : {total:,}")
    lines.append(f"  Indicateurs uniques       : {df['code_indicateur'].n_unique()}")
    lines.append(f"  Sources                   : {df['source_code'].n_unique()}")
    lines.append(f"  Regions                   : {df['region_code'].n_unique()}")
    lines.append(f"  Domaines                  : {df['domaine_code'].n_unique()}")
    lines.append(f"  Versions de serie         : {df['version_serie'].n_unique()}")
    lines.append("")

    # -- Plage de dates
    dates = df.filter(pl.col("date").is_not_null())["date"]
    if len(dates) > 0:
        try:
            dates_parsed = pl.Series(dates).str.to_date()
            d_min = dates_parsed.min()
            d_max = dates_parsed.max()
            lines.append(f"  Plage de dates            : {d_min} -> {d_max}")
        except Exception:
            lines.append(f"  Plage de dates            : {dates.min()} -> {dates.max()}")
    lines.append("")

    # -- 2. VALEURS MANQUANTES PAR INDICATEUR
    lines.append("-- 2. VALEURS MANQUANTES PAR INDICATEUR --")
    missing_by_indicator = (
        df
        .group_by("code_indicateur")
        .agg([
            pl.len().alias("total"),
            pl.col("valeur").null_count().alias("n_nan"),
            pl.col("qualite_flag").eq(pl.lit("manquant")).sum().alias("n_manquant"),
        ])
        .with_columns([
            (pl.col("n_nan") / pl.col("total") * 100).round(1).alias("pct_nan"),
            (pl.col("n_manquant") / pl.col("total") * 100).round(1).alias("pct_manquant"),
        ])
        .sort("pct_nan", descending=True)
    )

    for row in missing_by_indicator.iter_rows(named=True):
        lines.append(
            f"  {row['code_indicateur']:<25s}  "
            f"total={row['total']:>5d}  "
            f"NaN={row['n_nan']:>4d} ({row['pct_nan']:>5.1f}%)  "
            f"manquant={row['n_manquant']:>4d} ({row['pct_manquant']:>5.1f}%)"
        )
    lines.append("")

    # -- 3. DOUBLONS
    lines.append("-- 3. DOUBLONS DeTECTeS --")
    dups = df.group_by(["date", "region_code", "code_indicateur", "source_code", "version_serie"]).len()
    dups = dups.filter(pl.col("len") > 1)
    if len(dups) > 0:
        lines.append(f"  {len(dups)} doublons detectes (meme date/region/indicateur/source/version)")
        for row in dups.head(10).iter_rows(named=True):
            lines.append(
                f"    × {row['date']}  {row['region_code']}  "
                f"{row['code_indicateur']}  {row['source_code']}  "
                f"{row['version_serie']}  -> {row['len']} occurrences"
            )
        if len(dups) > 10:
            lines.append(f"    ... et {len(dups) - 10} autres doublons")
    else:
        lines.append("  Aucun doublon detecte.")
    lines.append("")

    # -- 4. SCORES DE FIABILITe
    lines.append("-- 4. SCORES DE FIABILITe --")
    fiab_stats = (
        df
        .group_by("fiabilite")
        .len()
        .sort("fiabilite")
    )
    for row in fiab_stats.iter_rows(named=True):
        f = row["fiabilite"]
        label = {3: "elevee (cross-checke)", 2: "Moyenne (defaut)", 1: "Faible"}.get(f, str(f))
        lines.append(f"  Score {f} ({label:<25s}) : {row['len']:>6d} lignes  ({_safe_pct(row['len'], total)}%)")
    lines.append("")

    # -- 5. STATISTIQUES PAR SOURCE
    lines.append("-- 5. LIGNES PAR SOURCE --")
    src_stats = df.group_by("source_code").len().sort("len", descending=True)
    for row in src_stats.iter_rows(named=True):
        lines.append(f"  {row['source_code']:<10s}  : {row['len']:>6d} lignes  ({_safe_pct(row['len'], total)}%)")
    lines.append("")

    # -- 6. STATISTIQUES PAR DOMAINE
    lines.append("-- 6. LIGNES PAR DOMAINE --")
    dom_stats = df.group_by("domaine_code").len().sort("len", descending=True)
    for row in dom_stats.iter_rows(named=True):
        lines.append(f"  {row['domaine_code']:<12s}  : {row['len']:>6d} lignes  ({_safe_pct(row['len'], total)}%)")
    lines.append("")

    # -- 7. QUALITe : FLAGS
    lines.append("-- 7. QUALITe : RePARTITION DES FLAGS --")
    qf_stats = df.group_by("qualite_flag").len().sort("len", descending=True)
    for row in qf_stats.iter_rows(named=True):
        qf = row["qualite_flag"] or "(None)"
        lines.append(f"  {qf:<30s}  : {row['len']:>6d} lignes  ({_safe_pct(row['len'], total)}%)")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def save_report(report_text: str) -> Path:
    """Sauvegarde le rapport dans data/curated/economie/."""
    CURATED_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = CURATED_ROOT / f"quality_report_{timestamp}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(report_text)
    return path
