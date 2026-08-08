"""
FastAPI server for RASD-Maroc dashboard v2.
Serves data from MongoDB (ingested by scripts/ingest_all.py).
Falls back to file-based reads if MongoDB is unavailable.
"""
import decimal
import json
import math
import os
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient, errors

from ..models import REGISTRY, available_models, model_info, predict


def _clean_json(obj: Any) -> Any:
    """Recursively replace NaN/Inf and convert non-serializable types."""
    if isinstance(obj, dict):
        return {k: _clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return obj


class SafeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            _clean_json(content),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rasd_maroc")
MONGO_TLS = os.getenv("MONGODB_TLS", "false").lower() == "true"
ROOT = Path(__file__).resolve().parent.parent.parent.parent

app = FastAPI(title="RASD-Maroc Data API v2", version="2.0", default_response_class=SafeJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = None
redis_cache = None

@app.on_event("startup")
def startup():
    global db, redis_cache
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000, tls=MONGO_TLS)
        client.admin.command("ping")
        db = client["rasd_maroc"]
        print(f"MongoDB connected: {MONGODB_URI}")
    except errors.ServerSelectionTimeoutError:
        print("WARNING: MongoDB unavailable, will use file fallback")

    try:
        import redis as r
        redis_cache = r.from_url(REDIS_URL, decode_responses=True)
        redis_cache.ping()
        print(f"Redis connected: {REDIS_URL}")
    except Exception:
        redis_cache = None
        print("WARNING: Redis unavailable")


def cached(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if redis_cache:
                key = f"{func.__name__}:{hash(frozenset(kwargs.items()))}"
                cached_val = redis_cache.get(key)
                if cached_val:
                    return JSONResponse(content=json.loads(cached_val))
            result = func(*args, **kwargs)
            if redis_cache:
                redis_cache.setex(key, ttl, json.dumps(result, default=str))
            return result
        return wrapper
    return decorator


def collection(name: str):
    return db[name] if db else None


def economie_df() -> pd.DataFrame:
    coll = collection("economie")
    if coll:
        docs = list(coll.find({}, {"_id": 0}).limit(0))
        cursor = coll.find({}, {"_id": 0}).limit(10000)
        return pd.DataFrame(list(cursor))
    p = ROOT / "kaggle_dataset" / "economie_maroc.parquet"
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()


def imf_df() -> pd.DataFrame:
    coll = collection("imf_weo")
    if coll:
        cursor = coll.find({}, {"_id": 0})
        return pd.DataFrame(list(cursor))
    p = ROOT / "kaggle_dataset" / "morocco_imf.parquet"
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()


@app.get("/")
def root():
    status = "live" if db else "file_fallback"
    return {
        "name": "RASD-Maroc Data API v2",
        "status": status,
        "endpoints": {
            "GET /health": "System health",
            "GET /indicators": "List all indicators",
            "GET /sources": "List all sources",
            "GET /source/{name}": "Data by source (HCP, BAM, FIN, OC, DATAGOV)",
            "GET /timeseries/{code}": "Time series for indicator code",
            "GET /imf": "List IMF indicators",
            "GET /imf/{code}": "IMF WEO data by code",
            "GET /summary": "Summary statistics",
            "GET /collections": "List all MongoDB collections",
            "GET /search?q=...": "Full-text search across all data (Redis-cached)",
            "GET /models": "List available ML models",
            "POST /models/{name}/predict": "Run cached inference (spam-classifier, econ-forecaster, waste-classifier)",
        },
    }


@app.get("/health")
@cached(ttl=10)
def health():
    checks = {"mongodb": False, "redis": False, "files": True}
    if db:
        try:
            db.command("ping")
            checks["mongodb"] = True
        except Exception:
            pass
    if redis_cache:
        try:
            redis_cache.ping()
            checks["redis"] = True
        except Exception:
            pass
    return {"status": "ok", "checks": checks, "timestamp": datetime.utcnow().isoformat()}


@app.get("/collections")
def list_collections():
    if db:
        names = db.list_collection_names()
        sizes = {}
        for n in names:
            sizes[n] = db[n].estimated_document_count()
        return {"collections": names, "counts": sizes}
    return {"error": "MongoDB unavailable"}


@app.get("/search")
@cached(ttl=120)
def search(q: str = Query(""), limit: int = Query(default=20, le=100)):
    if db:
        results = []
        for coll_name in db.list_collection_names():
            coll = db[coll_name]
            cursor = coll.find({"$text": {"$search": q}}, {"_id": 0}).limit(limit)
            for doc in cursor:
                results.append(doc)
            if len(results) >= limit:
                break
        return {"query": q, "total": len(results), "results": results[:limit]}
    return {"error": "MongoDB unavailable for search"}


@app.get("/indicators")
@cached(ttl=120)
def list_indicators():
    df = economie_df()
    if df.empty:
        return {"error": "No data found"}
    if "code_indicateur" in df.columns:
        codes = df["code_indicateur"].unique().tolist()
        return {"total": len(codes), "indicators": sorted(codes)}
    return {"error": "No indicators found"}


@app.get("/sources")
@cached(ttl=120)
def list_sources():
    df = economie_df()
    if df.empty or "source_code" not in df.columns:
        return {"error": "No data found"}
    sources = df.groupby("source_code").agg(
        obs=("valeur", "count"),
        indicateurs=("code_indicateur", "nunique"),
    ).reset_index()
    return sources.to_dict(orient="records")


@app.get("/source/{name}")
def get_source(name: str):
    coll = collection(name.upper())
    if coll:
        docs = list(coll.find({}, {"_id": 0}).limit(500))
        return {"source": name, "rows": len(docs), "data": docs[:100]}
    # fallback: read CSV
    for base in [ROOT / "kaggle_dataset" / "by_source", ROOT / "data" / "export" / "by_source"]:
        p = base / f"{name}.csv"
        if p.exists():
            df = pd.read_csv(p)
            return {"source": name, "rows": len(df), "data": df.head(100).to_dict(orient="records")}
    return {"error": f"Source '{name}' not found"}


@app.get("/timeseries/{code}")
@cached(ttl=60)
def get_timeseries(code: str, year_min: Optional[int] = Query(None), year_max: Optional[int] = Query(None)):
    coll = collection("economie")
    if coll:
        query = {"code_indicateur": code}
        if year_min or year_max:
            query["year"] = {}
            if year_min:
                query["year"]["$gte"] = year_min
            if year_max:
                query["year"]["$lte"] = year_max
        cursor = coll.find(query, {"_id": 0, "date": 1, "valeur": 1, "unite": 1, "source_code": 1}).sort("date", 1)
        data = list(cursor)
        return {"indicator": code, "rows": len(data), "data": data}
    # fallback
    df = economie_df()
    if df.empty:
        return {"error": "No data found"}
    mask = df["code_indicateur"] == code
    if year_min:
        mask &= pd.to_datetime(df["date"]).dt.year >= year_min
    if year_max:
        mask &= pd.to_datetime(df["date"]).dt.year <= year_max
    result = df[mask].sort_values("date")
    return {"indicator": code, "rows": len(result), "data": result[["date", "valeur", "unite", "source_code"]].to_dict(orient="records")}


@app.get("/imf")
@cached(ttl=300)
def list_imf_indicators():
    coll = collection("imf_weo")
    if coll:
        pipeline = [
            {"$group": {
                "_id": "$code",
                "indicator": {"$first": "$indicator"},
                "unit": {"$first": "$unit"},
                "year_min": {"$min": "$year"},
                "year_max": {"$max": "$year"},
            }},
            {"$sort": {"_id": 1}},
        ]
        results = list(coll.aggregate(pipeline))
        for r in results:
            r["code"] = r.pop("_id")
        return results
    df = imf_df()
    if df.empty:
        return {"error": "No IMF data found"}
    codes = df.groupby("code").agg(
        indicator=("indicator", "first"),
        unit=("unit", "first"),
        year_min=("year", "min"),
        year_max=("year", "max"),
    ).reset_index()
    return codes.to_dict(orient="records")


@app.get("/imf/{code}")
@cached(ttl=120)
def get_imf(code: str):
    coll = collection("imf_weo")
    if coll:
        docs = list(coll.find({"code": code}, {"_id": 0}).sort("year", 1))
        if docs:
            return {
                "code": code,
                "indicator": docs[0]["indicator"],
                "unit": docs[0]["unit"],
                "data": [{"year": d["year"], "value": d["value"]} for d in docs],
            }
        return {"error": f"Indicator '{code}' not found"}
    df = imf_df()
    if df.empty:
        return {"error": "No IMF data found"}
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
@cached(ttl=60)
def get_summary():
    coll_eco = collection("economie")
    coll_imf = collection("imf_weo")
    result = {"mongodb": False, "economie": {}, "imf_weo": {}, "collections": {}}
    if db:
        result["mongodb"] = True
        for name in db.list_collection_names():
            result["collections"][name] = db[name].estimated_document_count()
    if coll_eco:
        eco_info = coll_eco.aggregate([
            {"$group": {
                "_id": None,
                "rows": {"$sum": 1},
                "indicators": {"$addToSet": "$code_indicateur"},
                "sources": {"$addToSet": "$source_code"},
                "date_min": {"$min": "$date"},
                "date_max": {"$max": "$date"},
            }}
        ])
        info = list(eco_info)
        if info:
            result["economie"] = {
                "rows": info[0]["rows"],
                "indicators": len(info[0]["indicators"]),
                "sources": len(info[0]["sources"]),
                "date_min": info[0]["date_min"],
                "date_max": info[0]["date_max"],
            }
    elif not db:
        eco = economie_df()
        if not eco.empty:
            result["economie"] = {
                "rows": len(eco),
                "indicators": eco["code_indicateur"].nunique(),
                "sources": eco["source_code"].nunique(),
                "date_min": str(eco["date"].min()),
                "date_max": str(eco["date"].max()),
            }
    if coll_imf:
        imf_info = coll_imf.aggregate([
            {"$group": {
                "_id": None,
                "rows": {"$sum": 1},
                "indicators": {"$addToSet": "$code"},
                "year_min": {"$min": "$year"},
                "year_max": {"$max": "$year"},
            }}
        ])
        info = list(imf_info)
        if info:
            result["imf_weo"] = {
                "rows": info[0]["rows"],
                "indicators": len(info[0]["indicators"]),
                "year_min": info[0]["year_min"],
                "year_max": info[0]["year_max"],
            }
    elif not db:
        imf = imf_df()
        if not imf.empty:
            result["imf_weo"] = {
                "rows": len(imf),
                "indicators": imf["code"].nunique(),
                "year_min": int(imf["year"].min()),
                "year_max": int(imf["year"].max()),
            }
    return result


@app.get("/models")
def list_models():
    names = list(available_models())
    info = [model_info(n) for n in names]
    return {
        "models": info,
        "loaded": len(info),
        "registered": len(REGISTRY),
    }


@app.post("/models/{name}/predict")
def model_predict(name: str, payload: dict = None):
    if payload is None:
        payload = {}
    return predict(name, payload)


@app.middleware("http")
async def count_requests(request, call_next):
    app.state.request_count = getattr(app.state, "request_count", 0) + 1
    return await call_next(request)

@app.get("/stream")
async def stream(collections: str = "economie,imf_weo"):
    """SSE endpoint for real-time data streaming.
    Pushes new documents from MongoDB collections as Server-Sent Events.
    Usage:  const evtSource = new EventSource('/stream?collections=economie,imf_weo');
    """
    from fastapi.responses import StreamingResponse
    import asyncio, json

    cols = [c.strip() for c in collections.split(",") if c.strip()]
    last_ids = {}

    async def event_stream():
        while True:
            events = []
            if db is not None:
                for name in cols:
                    if name not in db.list_collection_names():
                        continue
                    query = {}
                    if name in last_ids and last_ids[name] is not None:
                        query = {"_id": {"$gt": last_ids[name]}}
                    cursor = db[name].find(query).sort("$natural", 1).limit(50)
                    docs = []
                    for doc in cursor:
                        doc.pop("_id", None)
                        docs.append(doc)
                    if docs:
                        last_ids[name] = docs[-1].get("_id", docs[-1])
                        events.append({"collection": name, "count": len(docs), "docs": docs})
                if events:
                    yield f"data: {json.dumps({'type': 'update', 'events': events}, default=str)}\n\n"
            # Heartbeat
            yield f": heartbeat {int(time.time())}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "Connection": "keep-alive",
                                      "X-Accel-Buffering": "no"})

@app.get("/metrics")
async def metrics():
    """Prometheus-format metrics endpoint."""
    import sys, time as t
    lines = [
        '# HELP rasd_api_info RASD-Maroc API metadata',
        '# TYPE rasd_api_info gauge',
        f'rasd_api_info{{version="2.0",python="{sys.version.split()[0]}"}} 1',
        '# HELP rasd_requests_total Total API requests',
        '# TYPE rasd_requests_total counter',
        f'rasd_requests_total {getattr(app.state, "request_count", 0)}',
        '# HELP rasd_db_up Database connectivity',
        '# TYPE rasd_db_up gauge',
        f'rasd_db_up {"1" if db else "0"}',
        '# HELP rasd_redis_up Redis connectivity',
        '# TYPE rasd_redis_up gauge',
        f'rasd_redis_up {"1" if redis else "0"}',
        '# HELP rasd_uptime_seconds Application uptime',
        '# TYPE rasd_uptime_seconds gauge',
        f'rasd_uptime_seconds {int(t.time() - app.state.start_time)}',
    ]
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines) + "\n")

@app.on_event("startup")
async def _startup():
    app.state.start_time = time.time()
    app.state.request_count = 0


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
