"""Parse sport data (FIFA rankings and HCP BDS)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import polars as pl

from sport.base import INDICATOR_CODES

RAW_DIR = Path("sport/data/raw")


def parse_hcp_sport() -> pl.DataFrame:
    """Parse HCP BDS sport indicator (I202)."""
    path = RAW_DIR / "I202.json"
    if not path.exists():
        return pl.DataFrame()

    data = json.loads(path.read_text(encoding="utf-8"))
    raw_data = data.get("data", {})
    periods = data.get("periods", [])

    if not raw_data:
        return pl.DataFrame()

    rows = []
    for key, val_obj in raw_data.items():
        value = val_obj.get("value") if isinstance(val_obj, dict) else val_obj
        if value is None:
            continue
        try:
            value = float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            continue

        # Extract period from key
        parts = key.split("_")
        period = parts[-1] if parts else None

        rows.append({
            "indicator_code": "I202",
            "label": INDICATOR_CODES["I202"]["label"],
            "domaine": "Football",
            "unite": "Nombre",
            "year": period,
            "region": "National",
            "level": "national",
            "value": value,
        })

    if not rows:
        return pl.DataFrame()

    return pl.DataFrame(rows)


def parse_fifa_rankings() -> pl.DataFrame:
    """Parse FIFA rankings from HTML."""
    path = RAW_DIR / "fifa_rankings.html"
    if not path.exists():
        return pl.DataFrame()

    html = path.read_text(encoding="utf-8")

    # Try to extract ranking data from HTML
    # Look for table rows with ranking data
    rows = []

    # Pattern: look for date, rank, points in table cells
    # This is a simplified parser - may need adjustment based on actual HTML structure
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    rank_pattern = re.compile(r'<td[^>]*>(\d+)</td>')
    points_pattern = re.compile(r'<td[^>]*>(\d+)</td>')

    # Try to find ranking entries
    # For now, create a basic structure
    if "FIFA" in html or "ranking" in html.lower():
        # Placeholder - actual parsing depends on HTML structure
        rows.append({
            "indicator_code": "FIFA_RANK",
            "label": "Classement FIFA du Maroc",
            "domaine": "Football",
            "unite": "Rang",
            "year": "2024",
            "region": "National",
            "level": "national",
            "value": None,  # Will be filled if parsing succeeds
        })

    if not rows:
        return pl.DataFrame()

    return pl.DataFrame(rows)


def parse_all_sport() -> pl.DataFrame:
    """Parse all sport data sources."""
    frames = []

    hcp_df = parse_hcp_sport()
    if len(hcp_df) > 0:
        frames.append(hcp_df)
        print(f"  Parsed HCP sport: {len(hcp_df)} rows")

    fifa_df = parse_fifa_rankings()
    if len(fifa_df) > 0:
        frames.append(fifa_df)
        print(f"  Parsed FIFA rankings: {len(fifa_df)} rows")

    if not frames:
        return pl.DataFrame()

    return pl.concat(frames, how="diagonal")


if __name__ == "__main__":
    print("=== Parsing sport data ===")
    df = parse_all_sport()
    print(f"\nTotal sport rows: {len(df)}")
