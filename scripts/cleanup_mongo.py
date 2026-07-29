"""Clean up MongoDB collections - drop test/year collections, deduplicate."""
from pymongo import MongoClient
from ingest_all import MONGO_URI, MONGO_TLS

client = MongoClient(MONGO_URI, tls=MONGO_TLS)
db = client["rasd_maroc"]

# Drop test collection
if "test_col" in db.list_collection_names():
    db["test_col"].drop()
    print("Dropped test_col")

# Drop year-based collections (2015-2026)
for y in range(2015, 2027):
    name = str(y)
    if name in db.list_collection_names():
        db[name].drop()
        print(f"Dropped {name}")

# Deduplicate imf_weo
coll = db["imf_weo"]
pipeline = [
    {"$group": {
        "_id": {"code": "$code", "year": "$year"},
        "ids": {"$addToSet": "$_id"},
        "count": {"$sum": 1}
    }},
    {"$match": {"count": {"$gt": 1}}}
]
dups = list(coll.aggregate(pipeline))
removed = 0
for dup in dups:
    ids = dup["ids"]
    for _id in ids[1:]:
        coll.delete_one({"_id": _id})
        removed += 1
print(f"Removed {removed} duplicates from imf_weo")

# Deduplicate imf_wide
coll = db["imf_wide"]
pipeline = [
    {"$group": {
        "_id": {"code": "$code"},
        "ids": {"$addToSet": "$_id"},
        "count": {"$sum": 1}
    }},
    {"$match": {"count": {"$gt": 1}}}
]
dups = list(coll.aggregate(pipeline))
removed = 0
for dup in dups:
    ids = dup["ids"]
    for _id in ids[1:]:
        coll.delete_one({"_id": _id})
        removed += 1
print(f"Removed {removed} duplicates from imf_wide")

print()
print("=== Final collections ===")
for name in sorted(db.list_collection_names()):
    print(f"  {name}: {db[name].estimated_document_count()} docs")

client.close()
