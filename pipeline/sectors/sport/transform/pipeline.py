"""SPORT transformation pipeline."""
from __future__ import annotations

from pathlib import Path
import polars as pl
from pipeline.sectors.sport.parse.parsers import parse_all_sport

OUTPUT_DIR = Path("pipeline/sectors/sport/data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def dedup(df: pl.DataFrame) -> pl.DataFrame:
    possible_keys = ["indicator_code", "year", "region"]
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


def quality_checks(df: pl.DataFrame) -> pl.DataFrame:
    n_rows = len(df)
    n_nulls = df.select(pl.col("value").null_count()).item() if "value" in df.columns else 0
    print(f"  Quality: {n_rows} rows, {n_nulls} nulls")
    return df


def export(df: pl.DataFrame, name: str = "sport_complet") -> Path:
    out = OUTPUT_DIR / f"{name}.parquet"
    df.write_parquet(out)
    print(f"  Exported: {out} ({len(df)} rows, {df.width} cols)")
    return out


def run_pipeline() -> pl.DataFrame:
    print("=" * 60)
    print("SPORT TRANSFORMATION PIPELINE")
    print("=" * 60)

    print("\n[1/4] Parsing sport data...")
    df = parse_all_sport()
    print(f"  Sport data: {len(df)} rows")

    if len(df) == 0:
        print("  No data to process!")
        return pl.DataFrame()

    print("\n[2/4] Deduplication...")
    df = dedup(df)
    print(f"  After dedup: {len(df)} rows")

    print("\n[3/4] Type enforcement...")
    df = enforce_types(df)

    print("\n[4/4] Quality checks...")
    df = quality_checks(df)

    print("\nExporting...")
    export(df)
    return df


if __name__ == "__main__":
    run_pipeline()
