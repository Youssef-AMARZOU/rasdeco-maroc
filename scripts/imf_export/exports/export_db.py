"""
export_db.py – Exporte les donnees FMI Maroc vers SQLite et Parquet
====================================================================
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_parser import IMF_INDICATORS, IMF_MOROCCO_VALUES

OUT = Path(__file__).parent


def export_sqlite():
    db_path = OUT / "morocco_imf.db"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS indicators (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            unit TEXT,
            notes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS timeseries (
            indicator_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            value REAL,
            PRIMARY KEY (indicator_id, year),
            FOREIGN KEY (indicator_id) REFERENCES indicators(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Insert metadata
    meta = [
        ("source", "IMF World Economic Outlook (WEO) — April 2026"),
        ("country", "Morocco"),
        ("country_code", "MAR"),
        ("exported_at", __import__("datetime").datetime.now().isoformat()),
        ("years_range", "1980-2029"),
        ("indicators_count", str(len(IMF_INDICATORS))),
    ]
    c.executemany("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", meta)

    # Insert indicators
    for ind_id, meta_info in IMF_INDICATORS.items():
        c.execute(
            "INSERT OR REPLACE INTO indicators (id, name, unit, notes) VALUES (?, ?, ?, ?)",
            (ind_id, meta_info["name"], meta_info["unit"], meta_info.get("notes", "")),
        )

    # Insert timeseries
    for ind_id, yearly in IMF_MOROCCO_VALUES.items():
        for year, value in yearly.items():
            c.execute(
                "INSERT OR REPLACE INTO timeseries (indicator_id, year, value) VALUES (?, ?, ?)",
                (ind_id, year, value),
            )

    conn.commit()

    # Verify
    ind_count = c.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
    ts_count = c.execute("SELECT COUNT(*) FROM timeseries").fetchone()[0]
    conn.close()

    print(f"[OK] SQLite exporte: {db_path}")
    print(f"     {ind_count} indicateurs, {ts_count} points de donnees")
    return str(db_path)


def export_parquet():
    """Export vers Parquet via pyarrow."""
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("[SKIP] pyarrow non installe. pip install pyarrow")
        return None

    import pandas as pd

    # Build long-format dataframe
    rows = []
    for ind_id, yearly in IMF_MOROCCO_VALUES.items():
        meta = IMF_INDICATORS.get(ind_id, {})
        for year, value in yearly.items():
            rows.append({
                "indicator_id": ind_id,
                "indicator_name": meta.get("name", ""),
                "unit": meta.get("unit", ""),
                "year": year,
                "value": value,
            })

    df = pd.DataFrame(rows)

    # Wide format also
    wide = df.pivot_table(index=["indicator_id", "indicator_name", "unit"],
                          columns="year", values="value").reset_index()
    wide.columns = [str(c) if isinstance(c, int) else c for c in wide.columns]

    parquet_long = OUT / "morocco_imf_long.parquet"
    parquet_wide = OUT / "morocco_imf_wide.parquet"

    pq.write_table(pa.Table.from_pandas(df), str(parquet_long))
    pq.write_table(pa.Table.from_pandas(wide), str(parquet_wide))

    size_long = parquet_long.stat().st_size / 1024
    size_wide = parquet_wide.stat().st_size / 1024
    print(f"[OK] Parquet long:  {parquet_long} ({size_long:.1f} KB)")
    print(f"[OK] Parquet wide:  {parquet_wide} ({size_wide:.1f} KB)")
    return str(parquet_long)


def export_json():
    """Export JSON clean."""
    records = []
    for ind_id, meta in IMF_INDICATORS.items():
        yearly = IMF_MOROCCO_VALUES.get(ind_id, {})
        records.append({
            "indicator_id": ind_id,
            "indicator_name": meta["name"],
            "unit": meta["unit"],
            "notes": meta.get("notes", ""),
            "years": [{"year": y, "value": v} for y, v in sorted(yearly.items())],
        })

    payload = {
        "country": "Morocco",
        "country_code": "MAR",
        "source": "IMF World Economic Outlook (WEO)",
        "exported_at": __import__("datetime").datetime.now().isoformat(),
        "indicators": records,
    }

    json_path = OUT / "morocco_imf.json"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] JSON exporte: {json_path} ({json_path.stat().st_size / 1024:.1f} KB)")
    return str(json_path)


def main():
    print("=" * 60)
    print("EXPORT — SQLite / Parquet / JSON")
    print("=" * 60)
    export_sqlite()
    export_parquet()
    export_json()
    print("=" * 60)


if __name__ == "__main__":
    main()