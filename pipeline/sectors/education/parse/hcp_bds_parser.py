"""Parse HCP BDS JSON responses into Polars DataFrames."""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import polars as pl

from education.base import INDICATOR_CODES

RAW_DIR = Path("education/data/raw/hcp_bds")


def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


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
    norm = _normalize(label)
    if norm == "total":
        return "national", "National"
    if norm in HCP_REGIONS_NORMALIZED:
        return "region", HCP_REGIONS_NORMALIZED[norm]
    return "province", ""


def _build_region_hierarchy(modalites: list[dict]) -> dict[int, tuple[str, str, str]]:
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
            lookup[mod_id] = ("province", current_region or "Unknown", mod_label)
    return lookup


def parse_hcp_indicator(code: str) -> pl.DataFrame | None:
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

    dim0_modalites = dims[0].get("modalites", []) if len(dims) > 0 else []
    dim1_modalites = dims[1].get("modalites", []) if len(dims) > 1 else []
    dim0_lookup = {m["id"]: m.get("label", "") for m in dim0_modalites}
    dim1_lookup = {m["id"]: m.get("label", "") for m in dim1_modalites}
    region_hierarchy = _build_region_hierarchy(dim0_modalites)

    rows = []
    for key, val_obj in raw_data.items():
        value = val_obj.get("value") if isinstance(val_obj, dict) else val_obj
        if value is None:
            continue
        try:
            value = float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            continue

        try:
            if "." in key.split("_")[0]:
                ids_part, period = key.rsplit("_", 1)
                dim0_str, dim1_str = ids_part.split(".")
                dim0_id = int(dim0_str)
                dim1_id = int(dim1_str)
                category = dim1_lookup.get(dim1_id, "")
            else:
                dim0_str, period = key.rsplit("_", 1)
                dim0_id = int(dim0_str)
                category = ""
        except (ValueError, IndexError):
            continue

        level, region, location = region_hierarchy.get(dim0_id, ("Unknown", "Unknown", dim0_lookup.get(dim0_id, "")))

        rows.append({
            "indicator_code": code,
            "label": indicator_meta.get("label", data.get("label", "")),
            "domaine": indicator_meta.get("domaine", ""),
            "unite": indicator_meta.get("unite", ""),
            "year": period,
            "region": region,
            "location": location,
            "level": level,
            "category": category,
            "value": value,
        })

    if not rows:
        return None
    return pl.DataFrame(rows)


def parse_all_indicators() -> pl.DataFrame:
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


if __name__ == "__main__":
    print("=== Parsing HCP BDS education indicators ===")
    hcp_df = parse_all_indicators()
    print(f"\nTotal HCP rows: {len(hcp_df)}")
