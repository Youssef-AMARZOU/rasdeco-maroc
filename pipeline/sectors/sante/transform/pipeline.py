"""SANTE transformation pipeline."""
from __future__ import annotations

from pathlib import Path
import polars as pl
from sante.parse.hcp_bds_parser import parse_all_indicators
from sante.base import COVID_YEARS, REGIONS_12

OUTPUT_DIR = Path("sante/data/output")
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


def add_covid_flag(df: pl.DataFrame) -> pl.DataFrame:
    """Add COVID-19 rupture variable."""
    if "year" not in df.columns:
        return df
    covid_strs = [str(y) for y in COVID_YEARS]
    return df.with_columns(
        pl.col("year").str.contains_any(covid_strs).alias("is_covid")
    )


def quality_checks(df: pl.DataFrame) -> pl.DataFrame:
    n_rows = len(df)
    n_nulls = df.select(pl.col("value").null_count()).item() if "value" in df.columns else 0
    n_regions = df.select(pl.col("region").n_unique()).item() if "region" in df.columns else 0
    n_years = df.select(pl.col("year").n_unique()).item() if "year" in df.columns else 0
    print(f"  Quality: {n_rows} rows, {n_nulls} nulls, {n_regions} regions, {n_years} years")
    return df


def export(df: pl.DataFrame, name: str = "sante_complet") -> Path:
    out = OUTPUT_DIR / f"{name}.parquet"
    df.write_parquet(out)
    print(f"  Exported: {out} ({len(df)} rows, {df.width} cols)")
    return out


def run_pipeline() -> pl.DataFrame:
    print("=" * 60)
    print("SANTE TRANSFORMATION PIPELINE")
    print("=" * 60)

    print("\n[1/6] Parsing HCP BDS indicators...")
    df = parse_all_indicators()
    print(f"  HCP data: {len(df)} rows")

    if len(df) == 0:
        print("  No data to process!")
        return pl.DataFrame()

    print("\n[2/6] Deduplication...")
    df = dedup(df)
    print(f"  After dedup: {len(df)} rows")

    print("\n[3/6] Type enforcement...")
    df = enforce_types(df)

    print("\n[4/6] Region harmonization...")
    df = harmonize_regions(df)

    print("\n[5/6] Adding COVID-19 rupture variable...")
    df = add_covid_flag(df)

    print("\n[6/6] Quality checks...")
    df = quality_checks(df)

    print("\nExporting...")
    export(df)
    return df


if __name__ == "__main__":
    run_pipeline()
