"""EDUCATION transformation pipeline."""
from __future__ import annotations

from pathlib import Path
import polars as pl
from education.parse.hcp_bds_parser import parse_all_indicators
from education.base import REGIONS_12

OUTPUT_DIR = Path("education/data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def dedup(df: pl.DataFrame) -> pl.DataFrame:
    possible_keys = ["indicator_code", "year", "region", "location", "category"]
    key_cols = [c for c in possible_keys if c in df.columns]
    return df.unique(subset=key_cols, keep="first")


def enforce_types(df: pl.DataFrame) -> pl.DataFrame:
    if "year" in df.columns:
        df = df.with_columns(
            pl.col("year").cast(pl.Utf8).str.slice(0, 4).cast(pl.Int32, strict=False).alias("year_numeric")
        )
    if "value" in df.columns:
        df = df.with_columns(pl.col("value").cast(pl.Float64, strict=False))
    return df


def harmonize_regions(df: pl.DataFrame) -> pl.DataFrame:
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


def quality_checks(df: pl.DataFrame) -> pl.DataFrame:
    n_rows = len(df)
    n_nulls = df.select(pl.col("value").null_count()).item() if "value" in df.columns else 0
    n_regions = df.select(pl.col("region").n_unique()).item() if "region" in df.columns else 0
    n_years = df.select(pl.col("year").n_unique()).item() if "year" in df.columns else 0
    print(f"  Quality: {n_rows} rows, {n_nulls} nulls, {n_regions} regions, {n_years} years")
    return df


def export(df: pl.DataFrame, name: str = "education_complet") -> Path:
    out = OUTPUT_DIR / f"{name}.parquet"
    df.write_parquet(out)
    print(f"  Exported: {out} ({len(df)} rows, {df.width} cols)")
    return out


def run_pipeline() -> pl.DataFrame:
    print("=" * 60)
    print("EDUCATION TRANSFORMATION PIPELINE")
    print("=" * 60)

    print("\n[1/5] Parsing HCP BDS indicators...")
    df = parse_all_indicators()
    print(f"  HCP data: {len(df)} rows")

    if len(df) == 0:
        print("  No data to process!")
        return pl.DataFrame()

    print("\n[2/5] Deduplication...")
    df = dedup(df)
    print(f"  After dedup: {len(df)} rows")

    print("\n[3/5] Type enforcement...")
    df = enforce_types(df)

    print("\n[4/5] Region harmonization...")
    df = harmonize_regions(df)

    print("\n[5/5] Quality checks...")
    df = quality_checks(df)

    print("\nExporting...")
    export(df)
    return df


if __name__ == "__main__":
    run_pipeline()
