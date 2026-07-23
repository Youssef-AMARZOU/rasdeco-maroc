"""
schema.py -- Schemas Polars cibles pour le pipeline eCONOMIE.

Definit les colonnes, types et contraintes pour :
  - fact_indicateurs (table de faits pivot)
  - dim_regions, dim_domaines, dim_sources (dimensions)
"""

import polars as pl

# ---------------------------------------------------------------------------
# fact_indicateurs
# ---------------------------------------------------------------------------
# Partitionne par date (mois/trimestre/annee selon la serie).
# Une ligne = une observation d'un indicateur pour une date × region donnee.

FACT_INDICATEURS_SCHEMA = {
    "date": pl.Date,
    "date_label": pl.Utf8,
    "region_code": pl.Utf8,
    "domaine_code": pl.Utf8,
    "code_indicateur": pl.Utf8,
    "valeur": pl.Float64,
    "unite": pl.Utf8,
    "source_code": pl.Utf8,
    "version_serie": pl.Utf8,
    "fiabilite": pl.Int8,
    "qualite_flag": pl.Utf8,
    "fichier_source": pl.Utf8,
    "date_insertion": pl.Datetime,
}

FACT_INDICATEURS_DTYPE = pl.Struct([pl.Field(k, v) for k, v in FACT_INDICATEURS_SCHEMA.items()])

# ---------------------------------------------------------------------------
# dim_regions
# ---------------------------------------------------------------------------
DIM_REGIONS_SCHEMA = {
    "region_code": pl.Utf8,
    "region_nom_fr": pl.Utf8,
    "region_nom_ar": pl.Utf8,
    "niveau": pl.Utf8,
    "ancien_code": pl.Utf8,
    "actif": pl.Boolean,
}

# ---------------------------------------------------------------------------
# dim_domaines
# ---------------------------------------------------------------------------
DIM_DOMAINES_SCHEMA = {
    "domaine_code": pl.Utf8,
    "domaine_label": pl.Utf8,
    "domaine_parent": pl.Utf8,
    "niveau": pl.Int8,
}

# ---------------------------------------------------------------------------
# dim_sources
# ---------------------------------------------------------------------------
DIM_SOURCES_SCHEMA = {
    "source_code": pl.Utf8,
    "source_nom": pl.Utf8,
    "periodicite": pl.Utf8,
    "url_principale": pl.Utf8,
    "niveau_fiabilite_base": pl.Int8,
}


def fact_schema() -> dict[str, type]:
    return dict(FACT_INDICATEURS_SCHEMA)


def empty_fact() -> pl.DataFrame:
    return pl.DataFrame({col: pl.Series(col, [], dtype=typ) for col, typ in FACT_INDICATEURS_SCHEMA.items()})


def empty_dim_regions() -> pl.DataFrame:
    return pl.DataFrame({col: pl.Series(col, [], dtype=typ) for col, typ in DIM_REGIONS_SCHEMA.items()})


def empty_dim_domaines() -> pl.DataFrame:
    return pl.DataFrame({col: pl.Series(col, [], dtype=typ) for col, typ in DIM_DOMAINES_SCHEMA.items()})


def empty_dim_sources() -> pl.DataFrame:
    return pl.DataFrame({col: pl.Series(col, [], dtype=typ) for col, typ in DIM_SOURCES_SCHEMA.items()})
