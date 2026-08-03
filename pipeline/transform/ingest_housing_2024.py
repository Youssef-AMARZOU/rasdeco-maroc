"""Parse HCP RGPH 2024 housing communal indicators and ingest into MongoDB + Iceberg"""
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

EXCEL_PATH = r"C:\Users\youss\Downloads\Indicateurs communaux du parc logement urbain au Maroc en 2024.xlsx"
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "export"

# Indicator mapping: (col_idx, indicator_code, label, unit)
INDICATORS = [
    # Total
    (2, "LOGEMENT.TOTAL", "Total logements urbains", "unite"),
    # Occupation nature
    (3, "OCCUPATION.OCCUPE", "Logement occupe", "pct"),
    (4, "OCCUPATION.VACANT", "Logement vacant", "pct"),
    (5, "OCCUPATION.SECONDAIRE", "Logement secondaire/saisonnier", "pct"),
    (6, "OCCUPATION.NON_OCCUPE", "Total logement non occupe", "pct"),
    # Type - non precaire
    (7, "TYPE.VILLA", "Villa ou niveau de villa", "pct"),
    (8, "TYPE.APPARTEMENT", "Appartement", "pct"),
    (9, "TYPE.TRADITIONNELLE", "Maison marocaine traditionnelle", "pct"),
    (10, "TYPE.MODERNE", "Maison marocaine moderne", "pct"),
    (11, "TYPE.NON_PRECAIRE", "Total non precaire", "pct"),
    # Type - precaire
    (12, "TYPE.BIDONVILLE", "Maison sommaire ou bidonville", "pct"),
    (13, "TYPE.RURAL", "Logement en type rural", "pct"),
    (14, "TYPE.AUTRE", "Autres type", "pct"),
    (15, "TYPE.PRECAIRE", "Total precaire", "pct"),
    # Age
    (16, "AGE.MOINS_20", "Moins de 20 ans", "pct"),
    (17, "AGE.20_50", "De 20 a moins de 50 ans", "pct"),
    (18, "AGE.50_PLUS", "50 ans et plus", "pct"),
    # Age x Type - Villa
    (19, "AGE_DETAIL.VILLA.MOINS_20", "Villa - Moins de 20 ans", "pct"),
    (20, "AGE_DETAIL.VILLA.20_50", "Villa - 20 a 50 ans", "pct"),
    (21, "AGE_DETAIL.VILLA.50_PLUS", "Villa - 50 ans et plus", "pct"),
    # Age x Type - Appartement
    (22, "AGE_DETAIL.APPARTEMENT.MOINS_20", "Appartement - Moins de 20 ans", "pct"),
    (23, "AGE_DETAIL.APPARTEMENT.20_50", "Appartement - 20 a 50 ans", "pct"),
    (24, "AGE_DETAIL.APPARTEMENT.50_PLUS", "Appartement - 50 ans et plus", "pct"),
    # Age x Type - Traditionnelle
    (25, "AGE_DETAIL.TRADITIONNELLE.MOINS_20", "Traditionnelle - Moins de 20 ans", "pct"),
    (26, "AGE_DETAIL.TRADITIONNELLE.20_50", "Traditionnelle - 20 a 50 ans", "pct"),
    (27, "AGE_DETAIL.TRADITIONNELLE.50_PLUS", "Traditionnelle - 50 ans et plus", "pct"),
    # Age x Type - Moderne
    (28, "AGE_DETAIL.MODERNE.MOINS_20", "Moderne - Moins de 20 ans", "pct"),
    (29, "AGE_DETAIL.MODERNE.20_50", "Moderne - 20 a 50 ans", "pct"),
    (30, "AGE_DETAIL.MODERNE.50_PLUS", "Moderne - 50 ans et plus", "pct"),
    # Age x Type - Total non precaire
    (31, "AGE_DETAIL.NON_PRECAIRE.MOINS_20", "Non precaire - Moins de 20 ans", "pct"),
    (32, "AGE_DETAIL.NON_PRECAIRE.20_50", "Non precaire - 20 a 50 ans", "pct"),
    (33, "AGE_DETAIL.NON_PRECAIRE.50_PLUS", "Non precaire - 50 ans et plus", "pct"),
    # Age x Type - Bidonville
    (34, "AGE_DETAIL.BIDONVILLE.MOINS_20", "Bidonville - Moins de 20 ans", "pct"),
    (35, "AGE_DETAIL.BIDONVILLE.20_50", "Bidonville - 20 a 50 ans", "pct"),
    (36, "AGE_DETAIL.BIDONVILLE.50_PLUS", "Bidonville - 50 ans et plus", "pct"),
    # Age x Type - Rural
    (37, "AGE_DETAIL.RURAL.MOINS_20", "Rural - Moins de 20 ans", "pct"),
    (38, "AGE_DETAIL.RURAL.20_50", "Rural - 20 a 50 ans", "pct"),
    (39, "AGE_DETAIL.RURAL.50_PLUS", "Rural - 50 ans et plus", "pct"),
    # Age x Type - Autre
    (40, "AGE_DETAIL.AUTRE.MOINS_20", "Autre - Moins de 20 ans", "pct"),
    (41, "AGE_DETAIL.AUTRE.20_50", "Autre - 20 a 50 ans", "pct"),
    (42, "AGE_DETAIL.AUTRE.50_PLUS", "Autre - 50 ans et plus", "pct"),
    # Age x Type - Total precaire
    (43, "AGE_DETAIL.PRECAIRE.MOINS_20", "Precaire - Moins de 20 ans", "pct"),
    (44, "AGE_DETAIL.PRECAIRE.20_50", "Precaire - 20 a 50 ans", "pct"),
    (45, "AGE_DETAIL.PRECAIRE.50_PLUS", "Precaire - 50 ans et plus", "pct"),
    # Walls
    (46, "MUR.BETON", "Mur - Beton arme, briques avec mortier", "pct"),
    (47, "MUR.PIERRE", "Mur - Pierre agglomeree avec mortier", "pct"),
    (48, "MUR.AUTRE", "Mur - Autres materiaux", "pct"),
    # Roof
    (49, "TOIT.DALLE", "Toit - Dalle en beton", "pct"),
    (50, "TOIT.PLANCHE", "Toit - Planches, bois ou tuiles", "pct"),
    (51, "TOIT.TOLE", "Toit - Tole en ciment ou en zinc", "pct"),
    (52, "TOIT.AUTRE", "Toit - Autres materiaux", "pct"),
    # Services
    (53, "SERVICE.ELECTRICITE", "Reseau public d'electricite", "pct"),
    (54, "SERVICE.EAU", "Reseau public d'eau", "pct"),
    (55, "SERVICE.ASSAINISSEMENT", "Reseau public d'assainissement", "pct"),
    # Deficit
    (56, "DEFICIT.QUANTITATIF", "Taux de deficit quantitatif en logement", "taux"),
]


def parse_excel():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Indicateurs-parc logement-urb", header=None)

    # Data starts at row 5 (0-indexed), row 5 = national summary
    data = df.iloc[5:].copy()
    data.columns = range(57)

    # Drop rows where geo code is NaN
    data = data.dropna(subset=[0])

    # Determine geographic level from code length
    def get_level(code_str):
        code_str = str(code_str).strip()
        l = len(code_str)
        if l == 0:
            return "national"
        elif l == 1:
            return "region"
        elif l in (3, 4):
            return "province"
        elif l in (5, 6, 7):
            return "commune"
        else:
            return "arrondissement"

    records = []
    for _, row in data.iterrows():
        code_geo = str(int(float(str(row[0]).strip()))) if str(row[0]).strip() else ""
        nom = str(row[1]).strip() if pd.notna(row[1]) else ""
        niveau = get_level(code_geo)

        for col_idx, indicator_code, label, unit in INDICATORS:
            val = row[col_idx]
            if pd.notna(val) and val != "":
                try:
                    valeur = float(val)
                except (ValueError, TypeError):
                    continue
            else:
                continue

            records.append(
                {
                    "code_geo": code_geo,
                    "nom": nom,
                    "niveau": niveau,
                    "indicateur": indicator_code,
                    "libelle": label,
                    "valeur": valeur,
                    "unite": unit,
                    "source_code": "HCP",
                    "annee": 2024,
                }
            )

    result = pd.DataFrame(records)
    result["date_insertion"] = datetime.now()
    return result


def save_parquet(df):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "housing_2024.parquet"
    df.to_parquet(path, index=False)
    print(f"Saved {len(df)} records to {path}")
    return path


def load_mongodb(df):
    try:
        from pymongo import MongoClient

        client = MongoClient("mongodb://localhost:27017")
        db = client["rasd_maroc"]
        col = db["housing_2024"]

        # Drop existing
        col.drop()
        records = df.to_dict("records")
        col.insert_many(records, ordered=False)

        # Create indexes
        col.create_index("code_geo")
        col.create_index("indicateur")
        col.create_index("niveau")
        col.create_index([("code_geo", 1), ("indicateur", 1)])

        print(f"Inserted {len(records)} docs into MongoDB housing_2024")
        client.close()
    except Exception as e:
        print(f"MongoDB ingestion skipped: {e}")


def update_data_json(df):
    """Append housing data to public/data.json for Electron/Next.js"""
    import json

    data_json_path = ROOT / "public" / "data.json"
    if data_json_path.exists():
        with open(data_json_path, encoding="utf-8") as f:
            existing = json.load(f)

        # Group by indicator for timeseries
        timeseries = existing.get("timeseries", {})
        for indicator_code in df["indicateur"].unique():
            subset = df[df["indicateur"] == indicator_code]
            key = f"HOUSING.{indicator_code}"
            rows = []
            for _, r in subset.iterrows():
                rows.append(
                    {
                        "date": "2024",
                        "valeur": r["valeur"],
                        "unite": r["unite"],
                        "source_code": "HCP",
                        "code_geo": r["code_geo"],
                        "nom": r["nom"],
                        "niveau": r["niveau"],
                    }
                )
            timeseries[key] = {"data": rows, "indicator": indicator_code, "unite": subset.iloc[0]["unite"]}

        existing["timeseries"] = timeseries
        existing["sources"] = list(set(existing.get("sources", []) + ["HCP"]))
        existing["housing_2024"] = {
            "total_records": len(df),
            "communes": int(df[df["niveau"] == "commune"]["code_geo"].nunique()),
            "indicators": int(df["indicateur"].nunique()),
        }

        with open(data_json_path, "w", encoding="utf-8") as f:
            json.dump(existing, f)
        print(f"Updated {data_json_path}")
    else:
        print(f"{data_json_path} not found, skipping JSON update")


def main():
    print("=" * 50)
    print("  HCP RGPH 2024 - Housing Communal Indicators")
    print("=" * 50)

    df = parse_excel()
    print(f"Parsed {len(df)} records: {df['niveau'].value_counts().to_dict()}")

    # 1. Save parquet
    save_parquet(df)

    # 2. Load into MongoDB
    load_mongodb(df)

    # 3. Update data.json
    update_data_json(df)

    # Summary by level
    print("\n--- Summary by level ---")
    for niveau in ["national", "region", "province", "commune", "arrondissement"]:
        subset = df[df["niveau"] == niveau]
        if len(subset):
            print(f"  {niveau}: {subset['code_geo'].nunique()} entities, {len(subset)} records")

    print("\nDone! Housing data ingested.")


if __name__ == "__main__":
    main()
