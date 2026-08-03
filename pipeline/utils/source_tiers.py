"""Assign source reliability tiers and update MongoDB/parquet metadata.

Tier 1 (fiabilite=5): Moroccan national sources — HCP, BAM, DATAGOV, FIN, OC
Tier 2 (fiabilite=3): International organizations — IMF, WB, UN
Tier 3 (fiabilite=1): Web-driven sites — Worldometer, other scraped data
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

TIERS = {
    # Tier 1 — Moroccan official sources (fiabilite=5)
    "HCP": {"tier": 1, "fiabilite": 5, "label": "Haut-Commissariat au Plan", "type": "national"},
    "BAM": {"tier": 1, "fiabilite": 5, "label": "Bank Al-Maghrib", "type": "national"},
    "DATAGOV": {"tier": 1, "fiabilite": 5, "label": "Open Data Maroc (data.gov.ma)", "type": "national"},
    "FIN": {"tier": 1, "fiabilite": 5, "label": "Ministere des Finances", "type": "national"},
    "OC": {"tier": 1, "fiabilite": 5, "label": "Office des Changes", "type": "national"},
    "MESRS": {"tier": 1, "fiabilite": 5, "label": "Ministere de l'Enseignement Superieur", "type": "national"},
    "MEN": {"tier": 1, "fiabilite": 5, "label": "Ministere de l'Education Nationale", "type": "national"},
    "MS": {"tier": 1, "fiabilite": 5, "label": "Ministere de la Sante", "type": "national"},
    "MAP": {"tier": 1, "fiabilite": 5, "label": "Maghreb Arabe Presse", "type": "national"},
    "ONEE": {"tier": 1, "fiabilite": 5, "label": "Office National de l'Electricite et de l'Eau", "type": "national"},
    "ONCF": {"tier": 1, "fiabilite": 5, "label": "ONCF", "type": "national"},
    "ADM": {"tier": 1, "fiabilite": 5, "label": "Autoroutes du Maroc", "type": "national"},
    "ONDA": {"tier": 1, "fiabilite": 5, "label": "ONDA", "type": "national"},
    "ANP": {"tier": 1, "fiabilite": 5, "label": "Agence Nationale des Ports", "type": "national"},
    "TMSA": {"tier": 1, "fiabilite": 5, "label": "Tanger Med Special Agency", "type": "national"},
    "AMDIE": {"tier": 1, "fiabilite": 5, "label": "AMDIE", "type": "national"},
    "DEPP": {"tier": 1, "fiabilite": 5, "label": "Direction des Etudes et Previsions", "type": "national"},
    # Tier 2 — International organizations (fiabilite=3)
    "IMF": {"tier": 2, "fiabilite": 3, "label": "Fonds Monetaire International", "type": "international"},
    "IMF_WEO": {"tier": 2, "fiabilite": 3, "label": "Fonds Monetaire International (WEO)", "type": "international"},
    "WB": {"tier": 2, "fiabilite": 3, "label": "Banque Mondiale", "type": "international"},
    "WORLD_BANK": {"tier": 2, "fiabilite": 3, "label": "Banque Mondiale", "type": "international"},
    "WEO": {"tier": 2, "fiabilite": 3, "label": "IMF World Economic Outlook", "type": "international"},
    "GLOBAL": {"tier": 2, "fiabilite": 3, "label": "Sources Globales Officielles", "type": "international"},
    "UN": {"tier": 2, "fiabilite": 3, "label": "Nations Unies", "type": "international"},
    "UNDP": {"tier": 2, "fiabilite": 3, "label": "PNUD", "type": "international"},
    "WHO": {"tier": 2, "fiabilite": 3, "label": "Organisation Mondiale de la Sante", "type": "international"},
    "FAO": {"tier": 2, "fiabilite": 3, "label": "FAO", "type": "international"},
    "ILO": {"tier": 2, "fiabilite": 3, "label": "Organisation Internationale du Travail", "type": "international"},
    "UNESCO": {"tier": 2, "fiabilite": 3, "label": "UNESCO", "type": "international"},
    "AFDB": {"tier": 2, "fiabilite": 3, "label": "Banque Africaine de Developpement", "type": "international"},
    "OECD": {"tier": 2, "fiabilite": 3, "label": "OCDE", "type": "international"},
    # Tier 3 — Data-driven web sources (fiabilite=1)
    "WORLDOMETER": {"tier": 3, "fiabilite": 1, "label": "Worldometer", "type": "web"},
    "KAGGLE": {"tier": 3, "fiabilite": 1, "label": "Kaggle", "type": "web"},
    "WEB": {"tier": 3, "fiabilite": 1, "label": "Web scraping", "type": "web"},
}

SOURCE_TIER_MAP = {k.lower(): v for k, v in TIERS.items()}


def get_source_tier(source_code):
    return SOURCE_TIER_MAP.get(source_code.lower(), {"tier": 0, "fiabilite": 0, "label": "Inconnu", "type": "unknown"})


def update_mongodb_fiabilite():
    """Update fiabilite field in MongoDB based on source_code"""
    try:
        from pymongo import MongoClient

        client = MongoClient("mongodb://localhost:27017")
        db = client["rasd_maroc"]

        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            updated = 0
            for doc in collection.find({"source_code": {"$exists": True}}):
                src = doc.get("source_code", "")
                tier_info = get_source_tier(src)
                new_fiabilite = tier_info["fiabilite"]
                if doc.get("fiabilite") != new_fiabilite:
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"fiabilite": new_fiabilite, "source_tier": tier_info["tier"]}},
                    )
                    updated += 1
            if updated:
                print(f"  {collection_name}: {updated} docs updated")

        # Update housing_2024 specifically
        if "housing_2024" in db.list_collection_names():
            col = db["housing_2024"]
            r = col.update_many({}, {"$set": {"fiabilite": 5, "source_tier": 1}})
            print(f"  housing_2024: {r.modified_count} docs set to tier 1 (HCP)")

        client.close()
        print("MongoDB fiabilite updated")
    except Exception as e:
        print(f"MongoDB update skipped: {e}")


def main():
    print("=" * 50)
    print("  Source Tier Classification")
    print("=" * 50)

    print(f"\nTier 1 (fiabilite=5) — Maroc officiel: {sum(1 for v in TIERS.values() if v['tier'] == 1)} sources")
    print(f"Tier 2 (fiabilite=3) — International: {sum(1 for v in TIERS.values() if v['tier'] == 2)} sources")
    print(f"Tier 3 (fiabilite=1) — Web: {sum(1 for v in TIERS.values() if v['tier'] == 3)} sources")

    update_mongodb_fiabilite()

    source_summary = {
        k.lower(): {"tier": v["tier"], "fiabilite": v["fiabilite"], "label": v["label"], "type": v["type"]}
        for k, v in TIERS.items()
    }
    path = ROOT / "data" / "source_tiers.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(source_summary, f, ensure_ascii=False, indent=2)
    print(f"\nSource tiers saved to {path}")


if __name__ == "__main__":
    main()
