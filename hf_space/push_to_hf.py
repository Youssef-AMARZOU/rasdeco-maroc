"""Push to Hugging Face: dataset + Gradio Space"""
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

    parquet_files = sorted(DATA_DIR.glob("*.parquet"))
    csv_files = sorted(DATA_DIR.glob("economie_*.csv"))
    json_files = list((DATA_DIR / "economie_data.json").glob("*")) if (DATA_DIR / "economie_data.json").is_dir() else []

    upload_files = []
    for f in parquet_files:
        upload_files.append(str(f))
    for f in csv_files:
        upload_files.append(str(f))

    data_json = DATA_DIR / "economie_data.json"
    if data_json.exists():
        upload_files.append(str(data_json))

    print(f"Uploading {len(upload_files)} files...")
    for fp in upload_files:
        fname = Path(fp).name
        print(f"  {fname}...", end=" ", flush=True)
        api.upload_file(
            path_or_fileobj=fp,
            path_in_repo=fname,
            repo_id=DATASET_ID,
            repo_type="dataset",
        )
        print("OK")
    print("Dataset done!")

    # --- Space (static, Gradio needs PRO) ---
    print(f"\n=== Space: {SPACE_ID} ===")
    try:
        api.create_repo(SPACE_ID, repo_type="space", exist_ok=True, space_sdk="static")
        print("Repo ready (static)")
    except Exception as e:
        print(f"Repo creation: {e}")
        print("Skipping Space upload. Create it manually or upgrade to PRO for Gradio.")
        return

    space_files = list(SPACE_DIR.glob("index.html")) + list(SPACE_DIR.glob("README.md"))
    if not space_files:
        print("No index.html found, skipping Space upload.")
        return

    print(f"Uploading {len(space_files)} space files...")
    for fp in space_files:
        fname = fp.name
        print(f"  {fname}...", end=" ", flush=True)
        api.upload_file(
            path_or_fileobj=str(fp),
            path_in_repo=fname,
            repo_id=SPACE_ID,
            repo_type="space",
        )
        print("OK")

    print("\nAll done!")
    print(f"Dataset: https://huggingface.co/datasets/{DATASET_ID}")
    print(f"Space:   https://huggingface.co/spaces/{SPACE_ID}")


if __name__ == "__main__":
    main()
