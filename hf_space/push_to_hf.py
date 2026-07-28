"""Push to Hugging Face: dataset + Static Space (Next.js dashboard)"""
import os
import sys
from pathlib import Path

os.environ["HF_HUB_DISABLE_TQDM"] = "1"

from huggingface_hub import HfApi, login

TOKEN = os.environ.get("HF_TOKEN", "")
if not TOKEN:
    print("ERROR: Set HF_TOKEN environment variable first.")
    print("  $env:HF_TOKEN = 'hf_...'  (PowerShell)")
    sys.exit(1)
USER = "YsfMO98"
DATASET_ID = f"{USER}/economie-maroc-rasd"
SPACE_ID = f"{USER}/economie-maroc-rasd"

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "export"
SPACE_DIR = ROOT / "hf_space"
IMF_EXPORT_DIR = ROOT / "scripts" / "imf_export"


def upload_dir(api, local_dir, repo_id, repo_type, prefix=""):
    """Upload all files in a directory recursively."""
    for fp in sorted(local_dir.rglob("*")):
        if fp.is_file():
            # Skip hidden files, caches, etc.
            if fp.name.startswith("_") and fp.suffix in (".py", ".ipynb", ".json"):
                continue
            if fp.name.startswith("."):
                continue
            if "__pycache__" in fp.parts:
                continue
            rel = fp.relative_to(local_dir)
            path_in_repo = f"{prefix}/{rel}" if prefix else str(rel)
            path_in_repo = path_in_repo.replace("\\", "/")
            print(f"  {path_in_repo}...", end=" ", flush=True)
            api.upload_file(
                path_or_fileobj=str(fp),
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type=repo_type,
            )
            print("OK")


def main():
    print("Login...")
    login(token=TOKEN)
    api = HfApi()

    # --- Dataset ---
    print(f"\n=== Dataset: {DATASET_ID} ===")
    try:
        api.create_repo(DATASET_ID, repo_type="dataset", exist_ok=True)
        print("Repo ready")
    except Exception as e:
        print(f"Repo: {e}")

    # Upload existing data export files
    parquet_files = sorted(DATA_DIR.glob("*.parquet"))
    csv_files = sorted(DATA_DIR.glob("economie_*.csv"))
    upload_files = list(parquet_files) + list(csv_files)

    data_json = DATA_DIR / "economie_data.json"
    if data_json.exists():
        upload_files.append(data_json)

    # Also upload IMF export data
    imf_json = IMF_EXPORT_DIR / "morocco_imf_data.json"
    if imf_json.exists():
        upload_files.append(imf_json)
    imf_xlsx = IMF_EXPORT_DIR / "morocco_data.xlsx"
    if imf_xlsx.exists():
        upload_files.append(imf_xlsx)

    # Upload IMF export files (parquet, db, etc.)
    imf_exports = IMF_EXPORT_DIR / "exports"
    if imf_exports.exists():
        for f in imf_exports.iterdir():
            if f.is_file() and not f.name.startswith("."):
                upload_files.append(f)

    print(f"Uploading {len(upload_files)} files to dataset...")
    for fp in upload_files:
        fname = fp.name
        print(f"  {fname}...", end=" ", flush=True)
        api.upload_file(
            path_or_fileobj=str(fp),
            path_in_repo=fname,
            repo_id=DATASET_ID,
            repo_type="dataset",
        )
        print("OK")
    print("Dataset done!")

    # --- Space (static Next.js dashboard) ---
    print(f"\n=== Space: {SPACE_ID} ===")
    try:
        api.create_repo(SPACE_ID, repo_type="space", exist_ok=True, space_sdk="static")
        print("Repo ready (static)")
    except Exception as e:
        print(f"Repo creation: {e}")
        print("Skipping Space upload.")
        return

    print("Uploading space files...")
    upload_dir(api, SPACE_DIR, SPACE_ID, "space")
    print("Space done!")

    print("\nAll done!")
    print(f"Dataset: https://huggingface.co/datasets/{DATASET_ID}")
    print(f"Space:   https://huggingface.co/spaces/{SPACE_ID}")


if __name__ == "__main__":
    main()