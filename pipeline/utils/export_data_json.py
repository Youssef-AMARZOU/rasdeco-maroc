"""
Generate a data.json file from the actual datasets.
This file is used by the dashboard when no API server is available (static export).
Run this after the ETL pipeline updates the data files.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

def main():
    # Load IMF WEO
    imf_path = ROOT / "kaggle_dataset" / "morocco_imf.parquet"
    imf = pd.read_parquet(imf_path) if imf_path.exists() else pd.DataFrame()

    # Load economie dataset
    eco_path = ROOT / "kaggle_dataset" / "economie_maroc.parquet"
    eco = pd.read_parquet(eco_path) if eco_path.exists() else pd.DataFrame()

    # Source data
    sources = {}
    for name in ["hcp", "bam", "fin", "datagov", "oc", "imf_weo"]:
        p = ROOT / "kaggle_dataset" / "by_source" / f"{name}.csv"
        if p.exists():
            sources[name] = pd.read_csv(p)

    # Build output
    output = {}

    # Summary stats
    output["summary"] = {
        "economie_rows": len(eco),
        "economie_indicators": int(eco["code_indicateur"].nunique()) if not eco.empty else 0,
        "economie_sources": int(eco["source_code"].nunique()) if not eco.empty else 0,
        "economie_date_min": str(eco["date"].min()) if not eco.empty else None,
        "economie_date_max": str(eco["date"].max()) if not eco.empty else None,
        "imf_indicators": int(imf["code"].nunique()) if not imf.empty else 0,
        "imf_year_min": int(imf["year"].min()) if not imf.empty else None,
        "imf_year_max": int(imf["year"].max()) if not imf.empty else None,
    }

    # IMF data by code
    output["imf"] = {}
    if not imf.empty:
        for code in imf["code"].unique():
            subset = imf[imf["code"] == code].sort_values("year")
            output["imf"][code] = {
                "indicator": subset.iloc[0]["indicator"],
                "unit": subset.iloc[0]["unit"],
                "data": subset[["year", "value"]].to_dict(orient="records"),
            }

    # Source summaries
    output["sources"] = {}
    for name, df in sources.items():
        output["sources"][name] = {
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.head(500).to_dict(orient="records"),
        }

    # Timeseries by indicator code (top 100 indicators by row count)
    if not eco.empty:
        indicator_counts = eco["code_indicateur"].value_counts()
        top_indicators = indicator_counts.head(100).index.tolist()
        output["timeseries"] = {}
        for code in top_indicators:
            subset = eco[eco["code_indicateur"] == code].sort_values("date")
            output["timeseries"][code] = {
                "rows": len(subset),
                "data": subset[["date", "valeur", "unite", "source_code"]].to_dict(orient="records"),
            }

    # Write output
    out_path = ROOT / "public" / "data.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Data exported to {out_path}")
    print(f"  - {len(output.get('imf', {}))} IMF indicators")
    print(f"  - {len(output.get('timeseries', {}))} economie timeseries")
    print(f"  - {len(output.get('sources', {}))} sources")

if __name__ == "__main__":
    main()