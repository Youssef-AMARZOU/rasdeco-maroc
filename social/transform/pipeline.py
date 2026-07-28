"""SOCIAL transformation pipeline.

Steps: parse → dedup → type → impute → regions → quality → export
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

from social.base import INDICATOR_CODES, REGIONS_12
from social.parse.hcp_bds_parser import parse_all_indicators

OUTPUT_DIR = Path("social/data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Step 1: Parse (already done by parser modules)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Step 2: Deduplication
# ---------------------------------------------------------------------------
def dedup(df: pl.DataFrame) -> pl.DataFrame:
    """Remove duplicate rows based on key columns."""
    possible_keys = ["indicator_code", "year", "region", "location", "category", "milieu"]
    key_cols = [c for c in possible_keys if c in df.columns]
    return df.unique(subset=key_cols, keep="first")


# ---------------------------------------------------------------------------
# Step 3: Type enforcement
# ---------------------------------------------------------------------------
def enforce_types(df: pl.DataFrame) -> pl.DataFrame:
    """Ensure correct data types."""
    if "year" in df.columns:
        df = df.with_columns(
            pl.col("year").cast(pl.Utf8).str.slice(0, 4).cast(pl.Int32, strict=False).alias("year_numeric")
        )
    if "value" in df.columns:
        df = df.with_columns(pl.col("value").cast(pl.Float64, strict=False))
    return df


# ---------------------------------------------------------------------------
# Step 4: Imputation (linear interpolation for missing years)
# ---------------------------------------------------------------------------
def impute_missing(df: pl.DataFrame) -> pl.DataFrame:
    """Linear interpolation for small gaps in time series."""
    if "year_numeric" not in df.columns or "value" not in df.columns:
        return df

    indicator_col = "indicator_code"
    region_col = "region" if "region" in df.columns else None
    category_col = "category" if "category" in df.columns else None

    group_cols = [indicator_col]
    if region_col:
        group_cols.append(region_col)
    if category_col:
        group_cols.append(category_col)

    result_frames = []
    for group_vals in df.select(group_cols).unique().iter_rows():
        mask = pl.lit(True)
        for col, val in zip(group_cols, group_vals):
            mask = mask & (pl.col(col) == val)

        group_df = df.filter(mask).sort("year_numeric")

        group_df = group_df.with_columns(
            pl.col("value").interpolate(method="linear").alias("value_imputed")
        )

        group_df = group_df.with_columns(
            pl.when(pl.col("value").is_null())
            .then(pl.col("value_imputed"))
            .otherwise(pl.col("value"))
            .alias("value")
        ).drop("value_imputed")

        result_frames.append(group_df)

    if not result_frames:
        return df

    return pl.concat(result_frames, how="diagonal")


# ---------------------------------------------------------------------------
# Step 5: Region harmonization
# ---------------------------------------------------------------------------
def harmonize_regions(df: pl.DataFrame) -> pl.DataFrame:
    """Map region names to standard codes and add region_code column."""
    if "region" not in df.columns:
        return df

    name_to_code = {v: k for k, v in REGIONS_12.items()}

    df = df.with_columns(
        pl.col("region").map_elements(
            lambda x: name_to_code.get(x, None) if x else None,
            return_dtype=pl.Int32,
        ).alias("region_code")
    )

    return df


# ---------------------------------------------------------------------------
# Step 6: Quality checks
# ---------------------------------------------------------------------------
def quality_checks(df: pl.DataFrame) -> pl.DataFrame:
    """Run quality checks and add quality metadata."""
    n_rows = len(df)
    n_nulls = df.select(pl.col("value").null_count()).item() if "value" in df.columns else 0
    n_regions = df.select(pl.col("region").n_unique()).item() if "region" in df.columns else 0
    n_years = df.select(pl.col("year").n_unique()).item() if "year" in df.columns else 0

    print(f"  Quality: {n_rows} rows, {n_nulls} nulls, {n_regions} regions, {n_years} years")

    if "value" in df.columns and n_rows > 0:
        null_ratio = n_nulls / n_rows
        if null_ratio > 0.5:
            print(f"  WARNING: {null_ratio:.1%} null ratio — indicator may need external data")

    return df


# ---------------------------------------------------------------------------
# Step 7: Export
# ---------------------------------------------------------------------------
def export(df: pl.DataFrame, name: str = "social_complet") -> Path:
    """Export to parquet."""
    out = OUTPUT_DIR / f"{name}.parquet"
    df.write_parquet(out)
    print(f"  Exported: {out} ({len(df)} rows, {df.width} cols)")
    return out


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_pipeline() -> pl.DataFrame:
    """Run the full SOCIAL transformation pipeline."""
    print("=" * 60)
    print("SOCIAL TRANSFORMATION PIPELINE")
    print("=" * 60)

    # Step 1: Parse
    print("\n[1/6] Parsing HCP BDS indicators...")
    df = parse_all_indicators()
    print(f"  HCP data: {len(df)} rows")

    if len(df) == 0:
        print("  No data to process!")
        return pl.DataFrame()

    # Step 2: Dedup
    print("\n[2/6] Deduplication...")
    df = dedup(df)
    print(f"  After dedup: {len(df)} rows")

    # Step 3: Types
    print("\n[3/6] Type enforcement...")
    df = enforce_types(df)

    # Step 4: Impute
    print("\n[4/6] Imputation...")
    df = impute_missing(df)

    # Step 5: Regions
    print("\n[5/6] Region harmonization...")
    df = harmonize_regions(df)

    # Step 6: Quality
    print("\n[6/6] Quality checks...")
    df = quality_checks(df)

    # Export
    print("\nExporting...")
    export(df)

    return df


if __name__ == "__main__":
    run_pipeline()
