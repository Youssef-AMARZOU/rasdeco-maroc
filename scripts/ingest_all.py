"""
Comprehensive data ingestion pipeline for RASD-Maroc.
Reads ALL datasets (parquet, csv, json, xlsx, db) and imports into MongoDB.
Supports --watch mode for real-time ingestion every N seconds.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pymongo import MongoClient, UpdateOne, errors

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOTS = [
    ROOT / "data",
    ROOT / "economie",
    ROOT / "agriculture",
    ROOT / "education",
    ROOT / "sante",
    ROOT / "social",
    ROOT / "sport",
    ROOT / "kaggle_dataset",
    ROOT / "scripts" / "imf_export" / "exports",
    ROOT / "upload",
    ROOT / "hf_space",
    ROOT / "public",
]
EXCLUDE_DIRS = {"node_modules", ".next", "__pycache__", ".git", ".venv"}

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rasd_maroc")
MONGO_TLS = os.getenv("MONGODB_TLS", "false").lower() == "true"
DB_NAME = "rasd_maroc"
COLLECTION_MAP = {
    "economie_maroc": "economie",
    "morocco_imf": "imf_weo",
    "morocco_imf_long": "imf_weo",
    "morocco_imf_wide": "imf_wide",
    "agriculture_complet": "agriculture",
    "education_complet": "education",
    "sante_complet": "sante",
    "social_complet": "social",
    "sport_complet": "sport",
}


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _ensure_str_keys(d: dict) -> dict:
    """Convert any non-string keys to strings (for MongoDB compatibility)."""
    return {str(k): v for k, v in d.items()}


def read_file(path: Path) -> Optional[List[Dict[str, Any]]]:
    ext = path.suffix.lower()
    try:
        if ext == ".parquet":
            df = pd.read_parquet(path)
            df = df.where(pd.notna(df), None)
            records = df.to_dict(orient="records")
            return [_ensure_str_keys(r) for r in records]
        elif ext == ".csv":
            df = pd.read_csv(path, low_memory=False)
            df = df.where(pd.notna(df), None)
            records = df.to_dict(orient="records")
            return [_ensure_str_keys(r) for r in records]
        elif ext == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return [_ensure_str_keys(r) if isinstance(r, dict) else r for r in data]
            elif isinstance(data, dict):
                records = data.get("data") or data.get("records") or data.get("kpis") or data.get("indicators") or []
                if isinstance(records, list):
                    return [_ensure_str_keys(r) if isinstance(r, dict) else r for r in records]
                return [_ensure_str_keys(data)]
            return None
        elif ext == ".xlsx":
            df = pd.read_excel(path, sheet_name=None)
            result = []
            for sheet_name, sheet_df in df.items():
                sheet_df = sheet_df.where(pd.notna(sheet_df), None)
                records = sheet_df.to_dict(orient="records")
                records = [_ensure_str_keys(r) for r in records]
                for r in records:
                    r["_sheet"] = sheet_name
                result.extend(records)
            return result
        elif ext == ".db":
            conn = sqlite3.connect(str(path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            result = []
            for table in tables:
                df = pd.read_sql(f"SELECT * FROM \"{table}\"", conn)
                df = df.where(pd.notna(df), None)
                records = df.to_dict(orient="records")
                records = [_ensure_str_keys(r) for r in records]
                for r in records:
                    r["_source_table"] = table
                result.extend(records)
            conn.close()
            return result
    except Exception as e:
        print(f"  [WARN] Failed to parse {path.name}: {e}", file=sys.stderr)
    return None


def determine_collection(path: Path) -> str:
    stem = path.stem.replace(" ", "_").replace("-", "_").lower()
    if stem in COLLECTION_MAP:
        return COLLECTION_MAP[stem]
    parent = path.parent.name.lower()
    if parent in COLLECTION_MAP:
        return COLLECTION_MAP[parent]
    grandparent = path.parent.parent.name.lower()
    if grandparent in COLLECTION_MAP:
        return COLLECTION_MAP[grandparent]
    return stem


def add_metadata(records: List[Dict], path: Path, fhash: str):
    for r in records:
        r["_file_hash"] = fhash
        r["_file_path"] = str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
        r["_file_name"] = path.name
        r["_file_ext"] = path.suffix.lower()
        r["_file_size"] = path.stat().st_size
        r["_file_mtime"] = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        r["_ingested_at"] = datetime.now(timezone.utc)


def ingest_file(path: Path, client: MongoClient, dry_run: bool = False) -> int:
    try:
        print(f"  [{path.parent.name}/{path.name}]", flush=True)
    except Exception:
        print(f"  [{path.name}]", flush=True)
    records = read_file(path)
    if not records:
        print("SKIP (empty/unreadable)")
        return 0
    fhash = file_hash(path)
    add_metadata(records, path, fhash)
    collection_name = determine_collection(path)
    db = client[DB_NAME]
    coll = db[collection_name]
    # deduplicate by file_hash
    existing = coll.count_documents({"_file_hash": fhash})
    if existing > 0:
        print(f"SKIP (already ingested, {existing} docs)")
        return existing
    if dry_run:
        print(f"DRY-RUN: would insert {len(records)} docs into '{collection_name}'")
        return len(records)
    batch_size = 5000
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            result = coll.insert_many(batch, ordered=False)
            total += len(result.inserted_ids)
        except errors.BulkWriteError as bwe:
            total += bwe.details.get("nInserted", 0)
            print(f"    [WARN] Bulk write partial: {bwe.details.get('nInserted', 0)}/{len(batch)}")
    print(f"DONE ({total} docs into '{collection_name}')")
    return total


def scan_and_ingest(client: MongoClient, dry_run: bool = False) -> int:
    total = 0
    found = 0
    allowed_exts = {".parquet", ".csv", ".json", ".xlsx", ".db"}
    for data_root in DATA_ROOTS:
        if not data_root.exists():
            continue
        # Use os.walk to avoid collecting all files in memory
        for dirpath, dirnames, filenames in os.walk(str(data_root)):
            # Prune excluded dirs in-place so os.walk skips them
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith("__")]
            rel_dir = Path(dirpath).relative_to(ROOT)
            for fname in sorted(filenames):
                ext = Path(fname).suffix.lower()
                if ext not in allowed_exts:
                    continue
                fpath = Path(dirpath) / fname
                if fpath.stat().st_size < 50:
                    continue
                found += 1
                n = ingest_file(fpath, client, dry_run)
                total += n
    print(f"\nSummary: {found} files processed, {total} documents ingested into MongoDB", flush=True)
    return total


def run_watch(client: MongoClient, interval: int = 60):
    print(f"Watch mode enabled, scanning every {interval}s. Press Ctrl+C to stop.")
    while True:
        try:
            scan_and_ingest(client)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"Error during scan: {e}", file=sys.stderr)
            traceback.print_exc()
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="RASD-Maroc Data Ingestion Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Scan without importing")
    parser.add_argument("--watch", action="store_true", help="Watch mode (scan every N seconds)")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")
    parser.add_argument("--file", type=str, help="Ingest a single file only")
    args = parser.parse_args()
    print(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tls=MONGO_TLS)
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully")
    except errors.ServerSelectionTimeoutError:
        print("ERROR: Cannot connect to MongoDB. Is it running?", file=sys.stderr)
        print("Start with: docker compose up -d mongodb", file=sys.stderr)
        sys.exit(1)
    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        ingest_file(path, client, args.dry_run)
    elif args.watch:
        run_watch(client, args.interval)
    else:
        scan_and_ingest(client, args.dry_run)
    client.close()


if __name__ == "__main__":
    main()
