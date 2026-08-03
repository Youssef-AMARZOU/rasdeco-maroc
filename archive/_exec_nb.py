"""Execute notebook locally and save with outputs."""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

import nbformat
from nbclient import NotebookClient

ROOT = r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc'
NOTEBOOK_IN = os.path.join(ROOT, 'kaggle_dataset', 'notebook.ipynb')
NOTEBOOK_OUT = os.path.join(ROOT, 'kaggle_dataset', 'notebook.ipynb')
EXPORT_DIR = os.path.join(ROOT, 'data', 'export')
PARQUET_PATH = os.path.join(EXPORT_DIR, 'economie_maroc.parquet')

with open(NOTEBOOK_IN, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Patch paths
for cell in nb.cells:
    if cell.cell_type == 'code':
        src = cell.source
        src = src.replace("/kaggle/input/economie-maroc-rasd/", EXPORT_DIR.replace('\\', '/') + "/")
        src = src.replace("pf = '/kaggle/input/economie-maroc-rasd/economie_maroc.parquet'", f"pf = r'{PARQUET_PATH}'")
        src = src.replace("jf = '/kaggle/input/economie-maroc-rasd/economie_maroc.json'", f"jf = r'{os.path.join(EXPORT_DIR, 'economie_maroc.json')}'")
        src = src.replace("for f in os.listdir('/kaggle/input/economie-maroc-rasd/'):", f"for f in os.listdir(r'{EXPORT_DIR}'):")
        src = src.replace("df = pd.read_parquet(f'/kaggle/input/economie-maroc-rasd/{f}')", "df = pd.read_parquet(f'{EXPORT_DIR}/{f}')")
        src = src.replace("df = pd.read_json(f'/kaggle/input/economie-maroc-rasd/{f}', lines=True)", "df = pd.read_json(f'{EXPORT_DIR}/{f}', lines=True)")
        cell.source = src

# Execute
print("Executing notebook...")
client = NotebookClient(nb, timeout=300, kernel_name='python3')
try:
    client.execute()
    print("Done!")
except Exception as e:
    print(f"Error: {e}")

# Save with outputs
with open(NOTEBOOK_OUT, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

n_out = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f"Saved: {NOTEBOOK_OUT} ({n_out} cells with outputs)")
