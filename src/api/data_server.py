"""
Data API server for RASD-Maroc dashboard.
Reads from Parquet/CSV/SQLite datasets at each request.
When data files are updated by the ETL pipeline, the API immediately serves fresh data.
"""
import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn

app = FastAPI(title="RASD-Maroc Data API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parent.parent.parent

DATA_DIRS = [
    ROOT / "kaggle_dataset",
    ROOT / "scripts" / "imf_export" / "exports",
]

def _find_file(name: str):
    for d in DATA_DIRS:
        p = d / name
        if p.exists():
            return p
    # fallback: search recursively
    for d in DATA_DIRS:
        for f in d.rglob(name):
            return f
    return None

def _load_economie() -> pd.DataFrame:
    p = _find_file("economie_maroc.parquet")
    if p:
        return pd.read_parquet(p)
    return pd.DataFrame()

def _load_imf() -> pd.DataFrame:
    p = _find_file("morocco_imf.parquet")
    if p:
        return pd.read_parquet(p)
    return pd.DataFrame()

def _load_imf_wide() -> pd.DataFrame:
    p = _find_file("morocco_imf_wide.parquet")
    if p:
        return pd.read_parquet(p)
    return pd.DataFrame()

def _load_source(name: str) -> pd.DataFrame:
    p = _find_file(f"by_source/{name}.csv")
    if not p:
        p = _find_file(f"{name}.csv")
    if p:
        return pd.read_csv(p)
    return pd.DataFrame()

@app.get("/")
def root():
    return {
        "name": "RASD-Maroc Data API",
        "version": "1.0",
        "endpoints": {
            "GET /indicators": "List all available indicators",
            "GET /kpis/:module": "KPI values for a module",
            "GET /timeseries/:code": "Time series for an indicator",
            "GET /sources/:source": "Data by source (HCP, BAM, FIN, OC, DATAGOV)",
            "GET /regions": "Data by region",
            "GET /imf/:code": "IMF WEO data by indicator code",
            "GET /summary": "Summary statistics",
        },
    }

@app.get("/indicators")
def list_indicators():
    df = _load_economie()
    if df.empty:
        return {"error": "No data file found"}
    codes = df["code_indicateur"].unique().tolist()
    return {"total": len(codes), "indicators": sorted(codes)}

@app.get("/sources")
def list_sources():
    df = _load_economie()
    if df.empty:
        return {"error": "No data file found"}
    sources = df.groupby("source_code").agg(
        obs=("valeur", "count"),
        indicateurs=("code_indicateur", "nunique"),
        date_min=("date", "min"),
        date_max=("date", "max"),
    ).reset_index()
    return sources.to_dict(orient="records")

@app.get("/source/{name}")
def get_source(name: str):
    df = _load_source(name)
    if df.empty:
        return {"error": f"Source '{name}' not found"}
    return {"source": name, "rows": len(df), "columns": list(df.columns), "data": df.head(100).to_dict(orient="records")}

@app.get("/timeseries/{code}")
def get_timeseries(code: str, year_min: Optional[int] = Query(None), year_max: Optional[int] = Query(None)):
    df = _load_economie()
    if df.empty:
        return {"error": "No data file found"}
    mask = df["code_indicateur"] == code
    if year_min:
        mask &= pd.to_datetime(df["date"]).dt.year >= year_min
    if year_max:
        mask &= pd.to_datetime(df["date"]).dt.year <= year_max
    result = df[mask].sort_values("date")
    return {
        "indicator": code,
        "rows": len(result),
        "data": result[["date", "valeur", "unite", "source_code"]].to_dict(orient="records"),
    }

@app.get("/imf")
def list_imf_indicators():
    df = _load_imf()
    if df.empty:
        return {"error": "No IMF data file found"}
    codes = df.groupby("code").agg(
        indicator=("indicator", "first"),
        unit=("unit", "first"),
        year_min=("year", "min"),
        year_max=("year", "max"),
    ).reset_index()
    return codes.to_dict(orient="records")

@app.get("/imf/{code}")
def get_imf(code: str):
    df = _load_imf()
    if df.empty:
        return {"error": "No IMF data file found"}
    result = df[df["code"] == code].sort_values("year")
    if result.empty:
        return {"error": f"Indicator '{code}' not found"}
    return {
        "code": code,
        "indicator": result.iloc[0]["indicator"],
        "unit": result.iloc[0]["unit"],
        "data": result[["year", "value"]].to_dict(orient="records"),
    }

@app.get("/summary")
def get_summary():
    eco = _load_economie()
    imf = _load_imf()
    return {
        "economie": {
            "rows": len(eco),
            "indicators": eco["code_indicateur"].nunique() if not eco.empty else 0,
            "sources": eco["source_code"].nunique() if not eco.empty else 0,
            "date_min": str(eco["date"].min()) if not eco.empty else None,
            "date_max": str(eco["date"].max()) if not eco.empty else None,
        },
        "imf_weo": {
            "rows": len(imf),
            "indicators": imf["code"].nunique() if not imf.empty else 0,
            "year_min": int(imf["year"].min()) if not imf.empty else None,
            "year_max": int(imf["year"].max()) if not imf.empty else None,
        },
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)