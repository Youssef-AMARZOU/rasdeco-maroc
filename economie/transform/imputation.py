"""
imputation.py -- Interpolation conditionnelle des valeurs manquantes.

Regles :
  - Trou ≤ 2 dans une serie longue (≥ 20 points) -> interpolation lineaire + flag 'interpole'
  - Trou > 2 -> laisse NaN + flag 'manquant'
  - Debut/fin de serie jamais interpoles
  - Rupture de serie detectee (version_serie change) -> aucune interpolation traversante
"""

from __future__ import annotations

import polars as pl


def impute_missing(df: pl.DataFrame) -> pl.DataFrame:
    """
    Applique l'imputation conditionnelle a la table fact_indicateurs.

    Pour chaque groupe (code_indicateur × region_code × version_serie) :
      - Si la serie a ≥ 20 lignes et ≤ 2 NaN consecutifs -> interpolation lineaire
      - Sinon -> NaN laisse avec qualite_flag = 'manquant'
    """
    groups = (
        df
        .with_columns(pl.col("date").str.to_date())
        .sort("date")
        .group_by("code_indicateur", "region_code", "version_serie")
    )

    chunks: list[pl.DataFrame] = []

    for group_key, group_df in groups:
        group_df = group_df.sort("date")
        n = len(group_df)

        if n < 20:
            # Serie trop courte : on flag les NaN sans imputer
            group_df = group_df.with_columns(
                pl.when(pl.col("valeur").is_null())
                .then(pl.lit("manquant"))
                .otherwise(pl.col("qualite_flag"))
                .alias("qualite_flag")
            )
            chunks.append(group_df)
            continue

        # Marquage des NaN avant imputation
        group_df = group_df.with_columns(
            pl.when((pl.col("valeur").is_null()) & (pl.col("qualite_flag").is_null()))
            .then(pl.lit("manquant"))
            .otherwise(pl.col("qualite_flag"))
            .alias("qualite_flag")
        )

        # Detection des trous consecutifs
        null_mask = group_df["valeur"].is_null().to_list()
        run_lengths = []
        current_run = 0
        for is_null in null_mask:
            if is_null:
                current_run += 1
            else:
                if current_run > 0:
                    run_lengths.append(current_run)
                current_run = 0
        if current_run > 0:
            run_lengths.append(current_run)

        max_run = max(run_lengths) if run_lengths else 0

        if max_run <= 2:
            # Interpolation lineaire
            group_df = group_df.with_columns(
                pl.col("valeur").interpolate(method="linear").alias("valeur")
            )
            group_df = group_df.with_columns(
                pl.when(pl.col("qualite_flag") == "manquant")
                .then(pl.lit("interpole"))
                .otherwise(pl.col("qualite_flag"))
                .alias("qualite_flag")
            )

        chunks.append(group_df)

    return pl.concat(chunks, how="vertical")
