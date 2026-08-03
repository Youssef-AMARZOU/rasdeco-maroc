"""Split monolithic data.json into per-module lightweight files for fast loading."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
PUBLIC_DIR = ROOT / "public"
DATA_DIR = PUBLIC_DIR / "data"

DATA_JSON = PUBLIC_DIR / "data.json"


def split():
    with open(DATA_JSON, encoding="utf-8") as f:
        full = json.load(f)

    timeseries = full.get("timeseries", {})
    imf = full.get("imf", {})
    sources = full.get("sources", [])
    summary = full.get("summary", {})

    # Group timeseries by prefix
    groups = {}
    for key, value in timeseries.items():
        prefix = key.split(".")[0] if "." in key else "OTHER"
        # Normalize messy prefixes
        if prefix.startswith("col_") or prefix.startswith("_unnamed"):
            prefix = "OTHER"
        groups.setdefault(prefix, {})[key] = value

    # Create data directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Write per-prefix timeseries files
    for prefix, data in groups.items():
        path = DATA_DIR / f"ts_{prefix.lower()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        size_kb = path.stat().st_size / 1024
        print(f"  ts_{prefix.lower()}.json: {len(data)} series, {size_kb:.0f} KB")

    # Write IMF data
    imf_path = DATA_DIR / "imf.json"
    with open(imf_path, "w", encoding="utf-8") as f:
        json.dump(imf, f, ensure_ascii=False)
    print(f"  imf.json: {len(imf)} indicators, {imf_path.stat().st_size / 1024:.0f} KB")

    # Write sources
    src_path = DATA_DIR / "sources.json"
    with open(src_path, "w", encoding="utf-8") as f:
        json.dump(sources, f, ensure_ascii=False)
    print(f"  sources.json: {len(sources)} sources")

    # Write summary separately
    sum_path = DATA_DIR / "summary.json"
    with open(sum_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False)
    print(f"  summary.json: {sum_path.stat().st_size / 1024:.0f} KB")

    # Copy housing parquet (already exists)
    housing_parquet = ROOT / "data" / "export" / "housing_2024.parquet"
    if housing_parquet.exists():
        dest = DATA_DIR / "housing_2024.parquet"
        shutil.copy2(housing_parquet, dest)
        print(f"  housing_2024.parquet: {dest.stat().st_size / 1024:.0f} KB")

    # Compute total size
    total_kb = sum(f.stat().st_size for f in DATA_DIR.rglob("*") if f.is_file()) / 1024
    print(f"\nTotal data directory: {total_kb:.0f} KB ({total_kb / 1024:.1f} MB)")
    print(f"Original data.json: {DATA_JSON.stat().st_size / 1024 / 1024:.1f} MB")

    # Write a registry so the client knows what files are available
    registry = {
        "timeseries_groups": list(groups.keys()),
        "imf": True,
        "sources": True,
        "housing": housing_parquet.exists(),
    }
    reg_path = DATA_DIR / "registry.json"
    with open(reg_path, "w", encoding="utf-8") as f:
        json.dump(registry, f)
    print(f"  registry.json written")


if __name__ == "__main__":
    split()
