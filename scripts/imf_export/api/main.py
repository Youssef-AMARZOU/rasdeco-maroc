"""
api/main.py — API REST FastAPI pour les donnees macroeconomiques du Maroc
=========================================================================
Endpoints:
  GET  /                    → Liste des routes disponibles
  GET  /indicators          → Tous les indicateurs
  GET  /indicator/{code}    → Un indicateur specifique
  GET  /morocco/summary     → Resume Maroc (dernieres annees)
  GET  /morocco/timeseries  → Matrice temps (lignes=indicateurs, colonnes=annees)
  GET  /search?q=...        → Recherche dans les indicateurs

Usage:
  uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data_parser import IMF_INDICATORS, IMF_MOROCCO_VALUES

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Morocco Macro Data API",
    description="API REST pour les donnees macroeconomiques du Maroc (FMI WEO 1980-2029)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "Morocco Macro Data API",
        "source": "IMF World Economic Outlook (WEO) — April 2026",
        "country": "Morocco (MAR)",
        "endpoints": {
            "/indicators": "Tous les indicateurs",
            "/indicator/{code}": "Un indicateur par code",
            "/morocco/summary": "Resume Maroc 2024-2029",
            "/morocco/timeseries": "Matrice temps complete",
            "/search?q=...": "Rechercher un indicateur",
        },
    }


def _build_indicator(ind_id: str) -> Optional[Dict[str, Any]]:
    meta = IMF_INDICATORS.get(ind_id)
    vals = IMF_MOROCCO_VALUES.get(ind_id)
    if not meta or not vals:
        return None
    return {
        "id": ind_id,
        "name": meta["name"],
        "unit": meta["unit"],
        "notes": meta.get("notes", ""),
        "years": [{"year": y, "value": v} for y, v in sorted(vals.items())],
    }


@app.get("/indicators")
def list_indicators():
    results = []
    for ind_id in IMF_INDICATORS:
        item = _build_indicator(ind_id)
        if item:
            results.append(item)
    return {
        "country": "Morocco",
        "country_code": "MAR",
        "count": len(results),
        "indicators": results,
    }


@app.get("/indicator/{code}")
def get_indicator(code: str):
    item = _build_indicator(code.upper())
    if not item:
        raise HTTPException(404, f"Indicateur '{code}' introuvable. Codes: {', '.join(IMF_INDICATORS.keys())}")
    return item


@app.get("/morocco/summary")
def summary():
    years = [2023, 2024, 2025, 2026, 2029]
    rows = []
    for ind_id, meta in IMF_INDICATORS.items():
        vals = IMF_MOROCCO_VALUES.get(ind_id, {})
        row = {"id": ind_id, "name": meta["name"], "unit": meta["unit"]}
        for y in years:
            row[str(y)] = vals.get(y)
        rows.append(row)
    return {"country": "Morocco", "period": years, "indicators": rows}


@app.get("/morocco/timeseries")
def timeseries():
    """Matrice: lignes = indicateurs, colonnes = annees"""
    all_years = set()
    for vals in IMF_MOROCCO_VALUES.values():
        all_years.update(vals.keys())
    sorted_years = sorted(all_years)

    rows = []
    for ind_id, meta in IMF_INDICATORS.items():
        vals = IMF_MOROCCO_VALUES.get(ind_id, {})
        row = {"id": ind_id, "name": meta["name"], "unit": meta["unit"]}
        for y in sorted_years:
            row[str(y)] = vals.get(y)
        rows.append(row)

    return {
        "country": "Morocco",
        "years": sorted_years,
        "indicators": rows,
    }


@app.get("/search")
def search(q: str = Query("", min_length=1)):
    q = q.lower()
    results = []
    for ind_id, meta in IMF_INDICATORS.items():
        if q in ind_id.lower() or q in meta["name"].lower() or q in meta["unit"].lower():
            results.append(_build_indicator(ind_id))
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }