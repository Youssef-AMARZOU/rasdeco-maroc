"""Parse HCP BDS JSON responses into Polars DataFrames."""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import polars as pl

from agriculture.base import INDICATOR_CODES, REGIONS_12

RAW_DIR = Path("agriculture/data/raw/hcp_bds")


def _normalize(s: str) -> str:
    """Normalize Unicode string: remove accents, lowercase, strip."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # remove combining marks
    return s.lower().strip()


# Region names normalized (accent-stripped, lowercase)
HCP_REGIONS_NORMALIZED: dict[str, str] = {
    _normalize("Tanger - Tétouan - Al Hoceima"): "Tanger-Tétouan-Al Hoceïma",
    _normalize("Oriental"): "L'Oriental",
    _normalize("Fès - Meknès"): "Fès-Meknès",
    _normalize("Rabat - Salé - Kenitra"): "Rabat-Salé-Kénitra",
    _normalize("Béni Mellal - Kénifra"): "Béni Mellal-Khénifra",
    _normalize("Casablanca-Settat"): "Casablanca-Settat",
    _normalize("Marrakech - Safi"): "Marrakech-Safi",
    _normalize("Draa - Tafilalet"): "Drâa-Tafilalet",
    _normalize("Souss - Massa"): "Souss-Massa",
    _normalize("Guelmim - Oued Noun"): "Guelmim-Oued Noun",
    _normalize("Laayoune - Sakia El Hamra"): "Laâyoune-Sakia El Hamra",
    _normalize("Dakhla - Oued Ed Dahab"): "Dakhla-Oued Ed-Dahab",
}


def _classify_region(label: str) -> tuple[str, str]:
    """Classify a dim0 label as region/province/national.

    Returns (level, region_name).
    """
    norm = _normalize(label)

    if norm == "total":
        return "national", "National"

    if norm in HCP_REGIONS_NORMALIZED:
        return "region", HCP_REGIONS_NORMALIZED[norm]

    # Check if it's a known province (not in region set, not total)
    return "province", ""


def _build_region_hierarchy(modalites: list[dict]) -> dict[int, tuple[str, str, str]]:
    """Build modality_id → (level, region_name, location_name) mapping."""
    lookup: dict[int, tuple[str, str, str]] = {}
    current_region = None

    for mod in modalites:
        mod_id = mod["id"]
        mod_label = mod.get("label", "")

        level, region = _classify_region(mod_label)

        if level == "national":
            lookup[mod_id] = ("national", "National", "Total")
        elif level == "region":
            current_region = region
            lookup[mod_id] = ("region", region, region)
        else:
            # Province under current region
            lookup[mod_id] = ("province", current_region or "Unknown", mod_label)

    return lookup


def parse_hcp_indicator(code: str) -> pl.DataFrame | None:
    """Parse a single HCP BDS indicator JSON into a long-format DataFrame."""
    path = RAW_DIR / f"{code}.json"
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    indicator_meta = INDICATOR_CODES.get(code, {})

    dims = data.get("dimensions", [])
    periods = data.get("periods", [])
    raw_data = data.get("data", {})

    if not dims or not periods or not raw_data:
        return None

    # Build dimension lookups
    dim0_modalites = dims[0].get("modalites", []) if len(dims) > 0 else []
    dim1_modalites = dims[1].get("modalites", []) if len(dims) > 1 else []

    dim0_lookup = {m["id"]: m.get("label", "") for m in dim0_modalites}
    dim1_lookup = {m["id"]: m.get("label", "") for m in dim1_modalites}

    # Build region hierarchy from dim0
    region_hierarchy = _build_region_hierarchy(dim0_modalites)

    # Parse data keys: format is "{dim0_id}.{dim1_id}_{period}"
    rows = []
    for key, val_obj in raw_data.items():
        value = val_obj.get("value") if isinstance(val_obj, dict) else val_obj
        if value is None:
            continue
        try:
            value = float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            continue

        # Split key
        try:
            ids_part, period = key.rsplit("_", 1)
            dim0_str, dim1_str = ids_part.split(".")
            dim0_id = int(dim0_str)
            dim1_id = int(dim1_str)
        except (ValueError, IndexError):
            continue

        # Determine level and region
        level, region, location = region_hierarchy.get(dim0_id, ("Unknown", "Unknown", dim0_lookup.get(dim0_id, "")))

        row = {
            "indicator_code": code,
            "label": indicator_meta.get("label", data.get("label", "")),
            "domaine": indicator_meta.get("domaine", ""),
            "unite": indicator_meta.get("unite", ""),
            "year": period,
            "region": region,
            "location": location,
            "level": level,
            "category": dim1_lookup.get(dim1_id, ""),
            "value": value,
        }
        rows.append(row)

    if not rows:
        return None

    return pl.DataFrame(rows)


def parse_all_indicators() -> pl.DataFrame:
    """Parse all downloaded HCP BDS agriculture indicators."""
    frames = []
    json_files = sorted(RAW_DIR.glob("*.json"))

    for path in json_files:
        code = path.stem
        df = parse_hcp_indicator(code)
        if df is not None and len(df) > 0:
            frames.append(df)
            print(f"  Parsed {code}: {len(df)} rows")
        else:
            print(f"  Skipped {code}: no data")

    if not frames:
        return pl.DataFrame()

    return pl.concat(frames, how="diagonal")


def parse_barrage_files() -> pl.DataFrame:
    """Parse barrage pluviometry Excel files."""
    barrage_dir = RAW_DIR / "barrage"
    if not barrage_dir.exists():
        return pl.DataFrame()

    frames = []
    for path in sorted(barrage_dir.glob("*.xlsx")):
        try:
            df = pl.read_excel(path)
            # Normalize column names
            col_map = {}
            for col in df.columns:
                cl = col.lower().strip()
                if "date" in cl or "jour" in cl:
                    col_map[col] = "date"
                elif "pluviom" in cl or "precip" in cl or "rain" in cl or "rr" in cl:
                    col_map[col] = "precipitation_mm"
                elif "station" in cl or "barrage" in cl:
                    col_map[col] = "station"
                elif "reservoir" in cl or "volume" in cl:
                    col_map[col] = "volume_m3"

            if col_map:
                df = df.rename(col_map)

            df = df.with_columns(pl.lit(path.stem).alias("source_file"))
            frames.append(df)
            print(f"  Parsed barrage: {path.name} ({len(df)} rows)")
        except Exception as e:
            print(f"  Failed to parse {path.name}: {e}")

    if not frames:
        return pl.DataFrame()

    return pl.concat(frames, how="diagonal")


if __name__ == "__main__":
    print("=== Parsing HCP BDS agriculture indicators ===")
    hcp_df = parse_all_indicators()
    print(f"\nTotal HCP rows: {len(hcp_df)}")

    print("\n=== Parsing barrage files ===")
    barrage_df = parse_barrage_files()
    print(f"\nTotal barrage rows: {len(barrage_df)}")
