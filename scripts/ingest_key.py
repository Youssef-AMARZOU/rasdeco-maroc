"""Ingest only the key datasets into MongoDB (skip full directory scan)."""
import sys
sys.stdout.reconfigure(line_buffering=True)

from pathlib import Path
from pymongo import MongoClient, errors

from ingest_all import ingest_file, read_file, file_hash, add_metadata, determine_collection, MONGO_URI, MONGO_TLS

ROOT = Path(__file__).resolve().parent.parent

client = MongoClient(MONGO_URI, tls=MONGO_TLS)
db = client["rasd_maroc"]

key_files = [
    ROOT / "kaggle_dataset" / "morocco_imf.parquet",
    # ROOT / "kaggle_dataset" / "morocco_imf_wide.parquet",  # wide format has non-string keys
    ROOT / "agriculture" / "data" / "output" / "agriculture_complet.parquet",
    ROOT / "education" / "data" / "output" / "education_complet.parquet",
    ROOT / "sante" / "data" / "output" / "sante_complet.parquet",
    ROOT / "social" / "data" / "output" / "social_complet.parquet",
    ROOT / "sport" / "data" / "output" / "sport_complet.parquet",
    ROOT / "scripts" / "imf_export" / "exports" / "morocco_imf_long.parquet",
    ROOT / "scripts" / "imf_export" / "exports" / "morocco_imf_wide.parquet",
    ROOT / "scripts" / "imf_export" / "exports" / "morocco_imf.json",
    ROOT / "data" / "export" / "by_source" / "hcp.csv",
    ROOT / "data" / "export" / "by_source" / "bam.csv",
    ROOT / "data" / "export" / "by_source" / "fin.csv",
    ROOT / "data" / "export" / "by_source" / "oc.csv",
    ROOT / "data" / "export" / "by_source" / "datagov.csv",
]

for fp in key_files:
    if not fp.exists():
        print(f"NOT FOUND: {fp}")
        continue
    print(f"Ingesting {fp.name}...", flush=True)
    records = read_file(fp)
    if not records:
        print(f"  SKIP (empty)", flush=True)
        continue
    fhash = file_hash(fp)
    add_metadata(records, fp, fhash)
    cname = determine_collection(fp)
    coll = db[cname]
    existing = coll.count_documents({"_file_hash": fhash})
    if existing > 0:
        print(f"  Already ingested ({existing} docs in {cname})", flush=True)
        continue
    batch_size = 5000
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        try:
            r = coll.insert_many(batch, ordered=False)
            total += len(r.inserted_ids)
        except errors.BulkWriteError as bwe:
            total += bwe.details.get("nInserted", 0)
            print(f"    Partial: {bwe.details.get('nInserted', 0)}/{len(batch)}", flush=True)
    print(f"  DONE: {total} docs into {cname}", flush=True)

print()
print("=== Final collections ===")
for name in sorted(db.list_collection_names()):
    if name == "test_col":
        continue
    print(f"  {name}: {db[name].estimated_document_count()} docs")

client.close()
