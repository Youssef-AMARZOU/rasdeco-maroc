"""Collector for HCP BDS social indicators."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx

from social.base import HCP_BDS_INDICATORS, INDICATOR_CODES

RAW_DIR = Path("social/data/raw/hcp_bds")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Fetch indicators with regional/provincial data (most valuable)
REGIONAL_INDICATORS = [k for k, v in INDICATOR_CODES.items() if v["granularite"] in ("region_province", "region", "region_milieu", "region_milieu_sexe", "region_sexe", "province_milieu")]

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


def fetch_all_social_indicators(delay: float = 0.3) -> None:
    """Fetch all social-related indicators and save raw JSON."""
    codes_to_fetch = list(set(REGIONAL_INDICATORS + NATIONAL_INDICATORS))
    print(f"Fetching {len(codes_to_fetch)} social indicators from HCP BDS...")

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

    print("Done fetching HCP BDS social indicators.")


if __name__ == "__main__":
    fetch_all_social_indicators()
