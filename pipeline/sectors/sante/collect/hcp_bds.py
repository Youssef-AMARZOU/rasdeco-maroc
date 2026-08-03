"""Collector for HCP BDS health indicators."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx

from sante.base import HCP_BDS_INDICATORS, INDICATOR_CODES

RAW_DIR = Path("sante/data/raw/hcp_bds")
RAW_DIR.mkdir(parents=True, exist_ok=True)

REGIONAL_INDICATORS = [k for k, v in INDICATOR_CODES.items() if v["granularite"] in ("region_province", "region")]
NATIONAL_INDICATORS = [k for k, v in INDICATOR_CODES.items() if v["granularite"] == "national"]


def fetch_indicator(client: httpx.Client, code: str) -> dict[str, Any] | None:
    url = f"{HCP_BDS_INDICATORS}/{code}"
    try:
        resp = client.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] Failed to fetch {code}: {e}")
        return None


def fetch_all_sante_indicators(delay: float = 0.3) -> None:
    codes_to_fetch = list(set(REGIONAL_INDICATORS + NATIONAL_INDICATORS))
    print(f"Fetching {len(codes_to_fetch)} health indicators from HCP BDS...")

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

    print("Done fetching HCP BDS health indicators.")


if __name__ == "__main__":
    fetch_all_sante_indicators()
