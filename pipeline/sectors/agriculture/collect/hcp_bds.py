"""Collector for HCP BDS agriculture indicators."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx
import polars as pl

from agriculture.base import HCP_BDS_INDICATORS, INDICATOR_CODES

RAW_DIR = Path("agriculture/data/raw/hcp_bds")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Only fetch indicators with regional data (most valuable)
REGIONAL_INDICATORS = [k for k, v in INDICATOR_CODES.items() if v["granularite"] in ("region_province", "region") and not k.startswith("BARRAGE")]

# Also fetch key national indicators for context
NATIONAL_INDICATORS = [
    k for k, v in INDICATOR_CODES.items()
    if v["granularite"] == "national" and not k.startswith("BARRAGE")
]


def fetch_indicator(client: httpx.Client, code: str) -> dict[str, Any] | None:
    """Fetch a single indicator from the HCP BDS API."""
    url = f"{HCP_BDS_INDICATORS}/{code}"
    try:
        resp = client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] Failed to fetch {code}: {e}")
        return None


def fetch_all_agriculture_indicators(delay: float = 0.3) -> None:
    """Fetch all agriculture-related indicators and save raw JSON."""
    codes_to_fetch = REGIONAL_INDICATORS + NATIONAL_INDICATORS
    print(f"Fetching {len(codes_to_fetch)} agriculture indicators from HCP BDS...")

    with httpx.Client() as client:
        for i, code in enumerate(codes_to_fetch, 1):
            out = RAW_DIR / f"{code}.json"
            if out.exists():
                print(f"  [{i}/{len(codes_to_fetch)}] {code} — cached")
                continue

            print(f"  [{i}/{len(codes_to_fetch)}] {code} ...", end=" ")
            data = fetch_indicator(client, code)
            if data:
                out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                print("OK")
            else:
                print("SKIP")
            time.sleep(delay)

    print("Done fetching HCP BDS agriculture indicators.")


def fetch_barrage_data(barrage_dir: Path = Path("data/raw/economie/datagov")) -> None:
    """Collect barrage pluviometry data from local raw files."""
    barrage_out = RAW_DIR / "barrage"
    barrage_out.mkdir(exist_ok=True)

    # Find all barrage files
    barrage_files = list(barrage_dir.rglob("*.xlsx"))
    barrage_files = [f for f in barrage_files if "youssef" in f.name.lower() or "barrage" in f.name.lower()]

    print(f"Found {len(barrage_files)} barrage files")

    # Copy/symlink to raw directory
    for bf in barrage_files:
        dest = barrage_out / bf.name
        if not dest.exists():
            import shutil
            shutil.copy2(bf, dest)
            print(f"  Copied: {bf.name}")
        else:
            print(f"  Cached: {bf.name}")


if __name__ == "__main__":
    fetch_all_agriculture_indicators()
    fetch_barrage_data()
