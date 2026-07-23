"""
pipeline.py -- Orchestrateur principal du pipeline de transformation.

Enchaine :
  1. Parsing de toutes les sources brutes
  2. Consolidation dans fact_indicateurs
  3. Dedoublonnage
  4. Imputation conditionnelle
  5. Mapping regions 16->12
  6. Score de fiabilite cross-source
  7. Generation du rapport de controle qualite
  8. Generation du data_dictionary.md
  9. Chargement BigQuery (optionnel via --load)

Usage :
    python -m economie.transform.pipeline
    python -m economie.transform.pipeline --load
    python -m economie.transform.pipeline --dry-run
    python -m economie.transform.pipeline --sources hcp bkam
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from .parsers import (
    HCParser,
    BKAMParser,
    FinancesParser,
    OfficeChangesParser,
    DatagovParser,
)
from .regions import build_dim_regions, aggregate_ancien_region
from .imputation import impute_missing
from .reliability import ReliabilityScorer
from .quality_report import generate_report, save_report
from .data_dictionary import generate_data_dictionary

# ---------------------------------------------------------------------------
# Dimensions statiques
# ---------------------------------------------------------------------------
CURATED_ROOT = Path(__file__).resolve().parents[3] / "data" / "curated" / "economie"


def _build_dim_domaines() -> pl.DataFrame:
    return pl.DataFrame([
        {"domaine_code": "CN", "domaine_label": "Comptes nationaux", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "PRIX", "domaine_label": "Prix et inflation", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "EMPLOI", "domaine_label": "Emploi et chomage", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "MONETAIRE", "domaine_label": "Statistiques monetaires", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "BUDGET", "domaine_label": "Finances publiques et budget", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "COMMERCE", "domaine_label": "Commerce exterieur", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "EXT", "domaine_label": "Secteur exterieur", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "CHANGE", "domaine_label": "Taux de change", "domaine_parent": "", "niveau": 1},
        {"domaine_code": "?", "domaine_label": "Indetermine", "domaine_parent": "", "niveau": 9},
    ])


def _build_dim_sources() -> pl.DataFrame:
    return pl.DataFrame([
        {"source_code": "HCP", "source_nom": "Haut-Commissariat au Plan",
         "periodicite": "Trimestrielle/Annuelle", "url_principale": "https://www.hcp.ma",
         "niveau_fiabilite_base": 2},
        {"source_code": "BAM", "source_nom": "Bank Al-Maghrib",
         "periodicite": "Mensuelle/Hebdomadaire", "url_principale": "https://www.bkam.ma",
         "niveau_fiabilite_base": 2},
        {"source_code": "FIN", "source_nom": "Ministere de l'economie et des Finances",
         "periodicite": "Annuelle", "url_principale": "https://www.finances.gov.ma",
         "niveau_fiabilite_base": 2},
        {"source_code": "OC", "source_nom": "Office des Changes",
         "periodicite": "Mensuelle/Annuelle", "url_principale": "https://www.oc.gov.ma",
         "niveau_fiabilite_base": 2},
        {"source_code": "DATAGOV", "source_nom": "data.gov.ma (portail open data)",
         "periodicite": "Variable", "url_principale": "https://www.data.gov.ma",
         "niveau_fiabilite_base": 1},
    ])


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def run_pipeline(
    selected_sources: list[str] | None = None,
    do_load: bool = False,
    dry_run: bool = False,
    force_recompute: bool = False,
) -> dict:
    """
    Execute le pipeline complet.

    Parametres
    ----------
    selected_sources : liste de noms de sources (None = toutes)
    do_load : charger dans BigQuery apres transformation
    dry_run : ne pas ecrire, seulement rapporter
    force_recompute : ignorer le cache et tout retraiter
    """
    t0 = time.time()
    print("=" * 70)
    print("  PIPELINE TRANSFORMATION ECONOMIE - RASD-Maroc")
    print(f"  Debut : {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # -- Parseurs disponibles
    all_parsers: dict[str, object] = {
        "hcp": HCParser(),
        "bkam": BKAMParser(),
        "finances": FinancesParser(),
        "office_des_changes": OfficeChangesParser(),
        "datagov": DatagovParser(),
    }

    if selected_sources:
        parsers = {k: v for k, v in all_parsers.items() if k in selected_sources}
    else:
        parsers = dict(all_parsers)

    print(f"\nSources a traiter : {', '.join(parsers.keys())}")

    # -- Phase 1 : Parsing
    print("\n-- Phase 1 : Parsing des fichiers bruts --")
    chunks: list[pl.DataFrame] = []
    for name, parser in parsers.items():
        print(f"  [{name}] Parsing...")
        df = parser.parse_all()
        if len(df) > 0:
            chunks.append(df)
            print(f"  [{name}] -> {len(df)} lignes extraites")
        else:
            print(f"  [{name}] -> 0 lignes (aucun fichier parse)")

    if not chunks:
        print("\n!  Aucune donnee parsee. Executez d'abord les scripts de collecte.")
        return {"status": "no_data", "n_rows": 0}

    fact = pl.concat(chunks, how="vertical")
    print(f"\n  Total brut consolide : {len(fact)} lignes")

    # -- Phase 2 : Dedoublonnage
    print("\n-- Phase 2 : Dedoublonnage --")
    before = len(fact)
    fact = fact.unique(
        subset=["date", "region_code", "code_indicateur", "source_code", "version_serie"],
        keep="first",
    )
    dup_removed = before - len(fact)
    print(f"  Doublons supprimes : {dup_removed}")
    print(f"  Lignes apres dedoublonnage : {len(fact)}")

    # -- Phase 3 : Correction des types
    print("\n-- Phase 3 : Typage et normalisation --")
    fact = fact.with_columns(
        pl.col("date").str.to_date().alias("date"),
        pl.col("code_indicateur").fill_null("?"),
        pl.col("source_code").fill_null("?"),
        pl.col("region_code").fill_null("MA00"),
    )
    print("  OK Types normalises")

    # -- Phase 4 : Imputation conditionnelle
    print("\n-- Phase 4 : Imputation conditionnelle --")
    fact = impute_missing(fact)
    nan_count = fact["valeur"].null_count()
    total = len(fact)
    print(f"  NaN restants : {nan_count}/{total} ({nan_count/total*100:.1f}%)")

    # -- Phase 5 : Mapping regions 16 -> 12
    print("\n-- Phase 5 : Mapping regions 16->12 --")
    # Les anciennes regions (MA01-MA16 non actives) sont mappees
    fact = aggregate_ancien_region(fact)
    # Les regions 12 sont gardees, MA00 est la nationale
    print(f"  Regions actives dans les donnees : {fact['region_code'].n_unique()}")
    print(f"  Codes region presents : {sorted(fact['region_code'].unique().to_list())}")

    # -- Phase 6 : Score de fiabilite cross-source
    print("\n-- Phase 6 : Score de fiabilite cross-source --")
    scorer = ReliabilityScorer()
    fact = scorer.score(fact)
    fiab_dist = fact.group_by("fiabilite").len().sort("fiabilite")
    for row in fiab_dist.iter_rows(named=True):
        print(f"  Fiabilite {row['fiabilite']} : {row['len']} lignes")

    # -- Phase 7 : Rapport de controle
    print("\n-- Phase 7 : Rapport de controle qualite --")
    report = generate_report(fact)
    print(report)
    report_path = save_report(report)
    print(f"  Rapport sauvegarde : {report_path}")

    # -- Phase 8 : Data dictionary
    print("\n-- Phase 8 : Dictionnaire des donnees --")
    dd_path = generate_data_dictionary(fact)
    print(f"  Dictionnaire : {dd_path}")

    # -- Phase 9 : Export Parquet (intermediaire)
    if not dry_run:
        CURATED_ROOT.mkdir(parents=True, exist_ok=True)
        parquet_path = CURATED_ROOT / "fact_indicateurs.parquet"
        fact.write_parquet(parquet_path, compression="zstd")
        size_mb = fact.estimated_size("mb")
        print(f"\n  Export Parquet : {parquet_path} ({size_mb:.1f} MB)")

        # Dimensions
        dim_regions = build_dim_regions()
        dim_regions.write_parquet(CURATED_ROOT / "dim_regions.parquet")
        dim_domaines = _build_dim_domaines()
        dim_domaines.write_parquet(CURATED_ROOT / "dim_domaines.parquet")
        dim_sources = _build_dim_sources()
        dim_sources.write_parquet(CURATED_ROOT / "dim_sources.parquet")
        print("  Dimensions exportees en Parquet")
    else:
        print("\n  [dry-run] Export Parquet desactive")

    # -- Phase 10 : Chargement BigQuery
    if do_load:
        print("\n-- Phase 9 : Chargement BigQuery --")
        try:
            from .bigquery_loader import load_fact_table

            results = load_fact_table(
                fact_df=fact,
                dim_regions=build_dim_regions(),
                dim_domaines=_build_dim_domaines(),
                dim_sources=_build_dim_sources(),
                write_disposition="WRITE_TRUNCATE",
                dry_run=dry_run,
            )
            print(f"  Tables chargees : {results}")
        except ImportError as e:
            print(f"  ! Google Cloud BigQuery non dispo : {e}")
        except Exception as e:
            print(f"  ! Erreur chargement BigQuery : {e}")
    else:
        print("\n  [skip] Chargement BigQuery (--load pour activer)")

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"  PIPELINE TERMINe -- {elapsed:.1f}s -- {len(fact)} lignes dans fact_indicateurs")
    print(f"{'=' * 70}")

    return {"status": "ok", "n_rows": len(fact), "elapsed_s": round(elapsed, 1)}


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline transformation -- Module eCONOMIE RASD-Maroc"
    )
    parser.add_argument("--load", action="store_true", help="Charger dans BigQuery apres transformation")
    parser.add_argument("--dry-run", action="store_true", help="Ne pas ecrire, seulement rapporter")
    parser.add_argument("--sources", nargs="+", choices=["hcp", "bkam", "finances", "office_des_changes", "datagov"],
                        help="Sources a traiter (toutes par defaut)")
    parser.add_argument("--force", action="store_true", help="Forcer le retraitement complet")
    args = parser.parse_args()

    result = run_pipeline(
        selected_sources=args.sources,
        do_load=args.load,
        dry_run=args.dry_run,
        force_recompute=args.force,
    )
    sys.exit(0 if result["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
