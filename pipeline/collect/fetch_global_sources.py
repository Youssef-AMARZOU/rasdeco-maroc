import json
import os
import sys
from pathlib import Path
import urllib.request

sys.path.append(str(Path(__file__).resolve().parent.parent / "sectors" / "economie"))
from utils import get_logger, RAW_ROOT

logger = get_logger("global_sources")

# World Bank indicators we want to fetch for Morocco
INDICATORS = {
    "PIB_CROISSANCE": "NY.GDP.MKTP.KD.ZG",
    "IPC_GLISSEMENT": "FP.CPI.TOTL.ZG",
    "CHOMAGE": "SL.UEM.TOTL.ZS",
    "POPULATION": "SP.POP.TOTL",
    "ESPERANCE_VIE": "SP.DYN.LE00.IN",
    "CO2_EMISSIONS": "EN.ATM.CO2E.PC",
    "ELECTRICITY_ACCESS": "EG.ELC.ACCS.ZS"
}

def fetch_world_bank_data(indicator_code, indicator_id):
    url = f"http://api.worldbank.org/v2/country/MA/indicator/{indicator_id}?format=json&date=1999:2026&per_page=1000"
    logger.info(f"Fetching {indicator_code} ({indicator_id}) from World Bank API...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            if len(data) > 1 and isinstance(data[1], list):
                records = data[1]
                time_series = []
                for rec in records:
                    year = int(rec['date'])
                    val = rec['value']
                    if val is not None:
                        time_series.append({"year": year, "value": float(val)})
                time_series.reverse() # Order chronologically
                return time_series
            else:
                logger.warning(f"No valid data returned for {indicator_code}")
                return []
    except Exception as e:
        logger.error(f"Error fetching {indicator_code}: {e}")
        return []

def main():
    logger.info("=" * 60)
    logger.info("START COLLECTING GLOBAL SOURCES (WORLD BANK)")
    logger.info("=" * 60)

    output_dir = RAW_ROOT / "global"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_data = {}
    for code, ind_id in INDICATORS.items():
        ts_data = fetch_world_bank_data(code, ind_id)
        if ts_data:
            all_data[code] = ts_data
            # Save individual files
            filepath = output_dir / f"wb_{code.lower()}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"indicator": code, "world_bank_id": ind_id, "data": ts_data}, f, indent=2)
            logger.info(f"Saved {len(ts_data)} data points for {code} to {filepath.name}")

    # Save meta
    meta_path = output_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "source": "World Bank API",
            "country": "Morocco (MA)",
            "indicators_fetched": list(INDICATORS.keys()),
            "date": "2026-07-31"
        }, f, indent=2)
    logger.info(f"Saved global source meta to {meta_path.name}")
    logger.info("FINISH COLLECTING GLOBAL SOURCES")

if __name__ == "__main__":
    main()
