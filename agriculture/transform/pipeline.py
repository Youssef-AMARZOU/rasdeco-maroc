"""AGRICULTURE transformation pipeline.

Steps: parse → dedup → type → impute → regions → quality → export
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

from agriculture.base import DROUGHT_CAMPAIGNS, INDICATOR_CODES, REGIONS_12
from agriculture.parse.hcp_bds_parser import parse_all_indicators, parse_barrage_files

OUTPUT_DIR = Path("agriculture/data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Step 1: Parse (already done by parser modules)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Step 2: Deduplication
# ---------------------------------------------------------------------------
def dedup(df: pl.DataFrame) -> pl.DataFrame:
    """Remove duplicate rows based on key columns."""
    # Key columns depend on what's available
    possible_keys = ["indicator_code", "year", "region", "location", "category", "milieu"]
    key_cols = [c for c in possible_keys if c in df.columns]
    return df.unique(subset=key_cols, keep="first")


# ---------------------------------------------------------------------------
# Step 3: Type enforcement
# ---------------------------------------------------------------------------
def enforce_types(df: pl.DataFrame) -> pl.DataFrame:
    """Ensure correct data types."""
    if "year" in df.columns:
        # Try to extract year from period strings like "2023-2024"
        df = df.with_columns(
            pl.col("year").cast(pl.Utf8).str.slice(0, 4).cast(pl.Int32, strict=False).alias("year_int")
        )
        # Keep original year for reference, use year_int for numeric operations
        if "year_int" in df.columns:
            df = df.with_columns(pl.col("year_int").alias("year_numeric"))
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

        # Linear interpolation for gaps <= 3 years
        group_df = group_df.with_columns(
            pl.col("value").interpolate(method="linear").alias("value_imputed")
        )

        # Only fill nulls, keep original values
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

    # Create mapping from name to code
    name_to_code = {v: k for k, v in REGIONS_12.items()}

    # Add region_code column
    df = df.with_columns(
        pl.col("region").map_elements(
            lambda x: name_to_code.get(x, None) if x else None,
            return_dtype=pl.Int32,
        ).alias("region_code")
    )

    return df


# ---------------------------------------------------------------------------
# Step 6: Add drought rupture variable
# ---------------------------------------------------------------------------
def add_drought_flag(df: pl.DataFrame) -> pl.DataFrame:
    """Add binary drought indicator for known drought campaigns."""
    if "year" not in df.columns:
        return df

    drought_strs = [str(y) for y in DROUGHT_CAMPAIGNS]
    return df.with_columns(
        pl.col("year").str.contains_any(drought_strs).alias("is_drought")
    )


# ---------------------------------------------------------------------------
# Step 7: Quality checks
# ---------------------------------------------------------------------------
def quality_checks(df: pl.DataFrame) -> pl.DataFrame:
    """Run quality checks and add quality metadata."""
    n_rows = len(df)
    n_nulls = df.select(pl.col("value").null_count()).item() if "value" in df.columns else 0
    n_regions = df.select(pl.col("region").n_unique()).item() if "region" in df.columns else 0
    n_years = df.select(pl.col("year").n_unique()).item() if "year" in df.columns else 0

    print(f"  Quality: {n_rows} rows, {n_nulls} nulls, {n_regions} regions, {n_years} years")

    # Flag low-quality indicators (too many nulls)
    if "value" in df.columns and n_rows > 0:
        null_ratio = n_nulls / n_rows
        if null_ratio > 0.5:
            print(f"  WARNING: {null_ratio:.1%} null ratio — indicator may need external data")

    return df


# ---------------------------------------------------------------------------
# Step 8: Export
# ---------------------------------------------------------------------------
def export(df: pl.DataFrame, name: str = "agriculture_complet") -> Path:
    """Export to parquet."""
    out = OUTPUT_DIR / f"{name}.parquet"
    df.write_parquet(out)
    print(f"  Exported: {out} ({len(df)} rows, {df.width} cols)")
    return out


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run_pipeline() -> pl.DataFrame:
    """Run the full AGRICULTURE transformation pipeline."""
    print("=" * 60)
    print("AGRICULTURE TRANSFORMATION PIPELINE")
    print("=" * 60)

    # Step 1: Parse
    print("\n[1/7] Parsing HCP BDS indicators...")
    hcp_df = parse_all_indicators()
    print(f"  HCP data: {len(hcp_df)} rows")

    print("\n[1b] Parsing barrage files...")
    barrage_df = parse_barrage_files()
    print(f"  Barrage data: {len(barrage_df)} rows")

    # Combine
    if len(hcp_df) > 0 and len(barrage_df) > 0:
        # Barrage data may have different columns — keep separate for now
        df = hcp_df
    elif len(hcp_df) > 0:
        df = hcp_df
    elif len(barrage_df) > 0:
        df = barrage_df
    else:
        print("  No data to process!")
        return pl.DataFrame()

    # Step 2: Dedup
    print("\n[2/7] Deduplication...")
    df = dedup(df)
    print(f"  After dedup: {len(df)} rows")

    # Step 3: Types
    print("\n[3/7] Type enforcement...")
    df = enforce_types(df)

    # Step 4: Impute
    print("\n[4/7] Imputation...")
    df = impute_missing(df)

    # Step 5: Regions
    print("\n[5/7] Region harmonization...")
    df = harmonize_regions(df)

    # Step 6: Drought flag
    print("\n[6/7] Adding drought rupture variable...")
    df = add_drought_flag(df)

    # Step 7: Quality
    print("\n[7/7] Quality checks...")
    df = quality_checks(df)

    # Export
    print("\nExporting...")
    export(df)

    return df


if __name__ == "__main__":
    run_pipeline()
