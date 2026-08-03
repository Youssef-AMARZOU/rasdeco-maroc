"""Scraper for FIFA rankings of Morocco."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx

from pipeline.sectors.sport.base import FIFA_URL, HCP_BDS_INDICATORS

RAW_DIR = Path("pipeline/sectors/sport/data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_fifa_rankings() -> dict[str, Any] | None:
    """Fetch FIFA rankings for Morocco from football-ranking.com."""
    try:
        resp = httpx.get(FIFA_URL, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        return {"html": resp.text, "status": resp.status_code}
    except Exception as e:
        print(f"  [WARN] Failed to fetch FIFA rankings: {e}")
        return None


def fetch_hcp_sport_indicator() -> dict[str, Any] | None:
    """Fetch the single sport indicator from HCP BDS (I202)."""
    url = f"{HCP_BDS_INDICATORS}/I202"
    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] Failed to fetch I202: {e}")
        return None


def fetch_all_sport_data() -> None:
    """Fetch all sport data sources."""
    print("Fetching sport data...")

    # Fetch HCP BDS sport indicator
    print("  Fetching HCP BDS I202 (FRM licenciés)...")
    hcp_data = fetch_hcp_sport_indicator()
    if hcp_data:
        out = RAW_DIR / "I202.json"
        out.write_text(json.dumps(hcp_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("    OK")
    else:
        print("    SKIP")

    # Fetch FIFA rankings
    print("  Fetching FIFA rankings...")
    fifa_data = fetch_fifa_rankings()
    if fifa_data:
        out = RAW_DIR / "fifa_rankings.html"
        out.write_text(fifa_data["html"], encoding="utf-8")
        print("    OK")
    else:
        print("    SKIP")

    print("Done fetching sport data.")


if __name__ == "__main__":
    fetch_all_sport_data()
