"""
data_dictionary.py -- Generation automatique du dictionnaire des donnees.

Produit un fichier data_dictionary.md dans data/curated/economie/
documentant chaque serie (code_indicateur, label, domaine, unite,
source, periode, fiabilite, version_serie).

Le dictionnaire se met a jour automatiquement a chaque execution du pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from .parsers.base import INDICATOR_CODES
from .reliability import ReliabilityScorer

CURATED_ROOT = Path(__file__).resolve().parents[3] / "data" / "curated" / "economie"


def _describe_qualite_flag(flag: str | None) -> str:
    if flag is None:
        return "Donnee originale"
    return {
        "manquant": "Donnee manquante (non collectee)",
        "interpole": "Valeur interpolee (trou ≤ 2 dans serie longue)",
        "ambig_ancien_vers_nouveau": "Ambiguïte lors du mapping 16->12 regions",
        "alerte_rupture": "Rupture de serie detectee (rebasage)",
    }.get(flag, flag)


def _build_domain_tree() -> dict[str, dict]:
    return {
        "CN": {"label": "Comptes nationaux", "parent": "", "niveau": 1},
        "PRIX": {"label": "Prix et inflation", "parent": "", "niveau": 1},
        "EMPLOI": {"label": "Emploi et chomage", "parent": "", "niveau": 1},
        "MONETAIRE": {"label": "Statistiques monetaires", "parent": "", "niveau": 1},
        "BUDGET": {"label": "Finances publiques et budget", "parent": "", "niveau": 1},
        "COMMERCE": {"label": "Commerce exterieur", "parent": "", "niveau": 1},
        "EXT": {"label": "Secteur exterieur", "parent": "", "niveau": 1},
        "CHANGE": {"label": "Taux de change", "parent": "", "niveau": 1},
    }


def generate_data_dictionary(
    fact_df: pl.DataFrame,
    output_path: Path | None = None,
) -> str:
    """Genere le dictionnaire des donnees au format Markdown."""
    if output_path is None:
        output_path = CURATED_ROOT / "data_dictionary.md"
    CURATED_ROOT.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    domains = _build_domain_tree()

    lines = []
    lines.append(f"# Dictionnaire des donnees -- Module eCONOMIE")
    lines.append(f"")
    lines.append(f"Genere automatiquement le {now}")
    lines.append(f"")
    lines.append(f"## Schema cible : `fact_indicateurs`")
    lines.append(f"")
    lines.append("| Colonne | Type | Description |")
    lines.append("|---------|------|-------------|")
    lines.append("| `date` | DATE | Date de l'observation (partition cle) |")
    lines.append("| `date_label` | STRING | Libelle brut de la periode |")
    lines.append("| `region_code` | STRING | Code region (FK -> dim_regions) |")
    lines.append("| `domaine_code` | STRING | Code domaine (FK -> dim_domaines) |")
    lines.append("| `code_indicateur` | STRING | Code indicateur normalise |")
    lines.append("| `valeur` | FLOAT64 | Valeur observee |")
    lines.append("| `unite` | STRING | Unite de mesure |")
    lines.append("| `source_code` | STRING | Code source (FK -> dim_sources) |")
    lines.append("| `version_serie` | STRING | Version de serie (ex: base_2014) |")
    lines.append("| `fiabilite` | INT8 | Score de fiabilite (1-3) |")
    lines.append("| `qualite_flag` | STRING | Flag qualite |")
    lines.append("| `fichier_source` | STRING | Fichier brut d'origine |")
    lines.append("| `date_insertion` | DATETIME | Horodatage ingestion |")
    lines.append("")

    lines.append("## Indicateurs")
    lines.append("")
    lines.append("| Code | Libelle | Domaine | Unite | Source(s) | Fiabilite | Periode couverte | Versions de serie |")
    lines.append("|------|---------|---------|-------|-----------|-----------|-----------------|-------------------|")

    if len(fact_df) > 0:
        info_by_code = (
            fact_df
            .group_by("code_indicateur")
            .agg([
                pl.col("domaine_code").first(),
                pl.col("unite").first(),
                pl.col("source_code").unique().implode(),
                pl.col("fiabilite").mean().round(1),
                pl.col("date").min().alias("date_debut"),
                pl.col("date").max().alias("date_fin"),
                pl.col("version_serie").unique().implode(),
            ])
            .sort("code_indicateur")
        )

        for row in info_by_code.iter_rows(named=True):
            code = row["code_indicateur"]
            meta = INDICATOR_CODES.get(code, {})
            label = meta.get("label", code)
            domaine = row["domaine_code"]
            domaine_label = domains.get(domaine, {}).get("label", domaine)
            unite = row["unite"]
            sources = ", ".join(row["source_code"])
            fiabilite = row["fiabilite"]
            debut = row["date_debut"]
            fin = row["date_fin"]
            versions = ", ".join(sorted(set(v for v in row["version_serie"] if v)))

            lines.append(
                f"| `{code}` | {label} | {domaine_label} | "
                f"{unite} | {sources} | {fiabilite} | "
                f"{debut} -> {fin} | {versions} |"
            )
    else:
        lines.append("| *(Aucune donnee -- pipeline a executer)* | | | | | | |")

    lines.append("")
    lines.append("## Domaines")
    lines.append("")
    lines.append("| Code | Libelle | Niveau |")
    lines.append("|------|---------|-------|")
    for code, info in domains.items():
        lines.append(f"| `{code}` | {info['label']} | Niveau {info['niveau']} |")
    lines.append("")

    lines.append("## Sources")
    lines.append("")
    if len(fact_df) > 0:
        src_info = fact_df.group_by("source_code").agg([
            pl.col("code_indicateur").unique().implode(),
            pl.col("fiabilite").mean().round(1),
        ]).sort("source_code")

        for row in src_info.iter_rows(named=True):
            lines.append(f"- **{row['source_code']}** : {len(row['code_indicateur'])} indicateurs, fiabilite moyenne {row['fiabilite']}")
    lines.append("")

    lines.append("## Notes sur les versions de serie (rebasages HCP)")
    lines.append("")
    lines.append("| Version | Periode | Description |")
    lines.append("|---------|---------|-------------|")
    lines.append("| `base_2007` | ~1998–2014 | IPC/PIB base 2007 |")
    lines.append("| `base_2014` | ~2014–2020 | IPC/PIB base 2014 |")
    lines.append("| `base_2017` | ~2020–present | IPC base 2017 |")
    lines.append("| `recente` | Variable | Version non detectee (post-2017 par defaut) |")
    lines.append("")
    lines.append("**Ces versions ne doivent JAMAIS etre fusionnees sans traitement explicite.**")
    lines.append("")

    lines.append("## Qualite des donnees")
    lines.append("")
    lines.append("| Flag | Signification |")
    lines.append("|------|---------------|")
    lines.append("| `(null)` | Donnee originale verifiee |")
    lines.append("| `manquant` | Valeur absente dans la source |")
    lines.append("| `interpole` | Interpolation lineaire (trou ≤ 2 periodes) |")
    lines.append("| `ambig_ancien_vers_nouveau` | Mapping approximatif 16->12 regions |")
    lines.append("| `cross_checked` | Coherence verifiee avec Banque Mondiale/FMI |")
    lines.append("| `alerte_rupture` | Rupture de serie a surveiller |")
    lines.append("")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path)
