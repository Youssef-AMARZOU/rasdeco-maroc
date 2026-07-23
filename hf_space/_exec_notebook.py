"""Execute notebook locally and save with outputs."""
import sys, os, json, time
sys.stdout.reconfigure(encoding='utf-8')

import nbformat
from nbclient import NotebookClient

ROOT = r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc'
NOTEBOOK_IN = os.path.join(ROOT, 'kaggle_dataset', 'notebook.ipynb')
NOTEBOOK_OUT = os.path.join(ROOT, 'kaggle_dataset', 'notebook.ipynb')

# Read notebook
with open(NOTEBOOK_IN, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Patch paths: replace Kaggle paths with local
EXPORT_DIR = os.path.join(ROOT, 'data', 'export').replace('\\', '/')
PARQUET_PATH = os.path.join(EXPORT_DIR, 'economie_maroc.parquet').replace('\\', '/')
JSON_PATH = os.path.join(EXPORT_DIR, 'economie_maroc.json').replace('\\', '/')

# Add a setup cell at the beginning
setup_source = f"""import os, sys
# Local paths (patched for local execution)
_LOCAL_PARQUET = r'{PARQUET_PATH}'
_LOCAL_JSON = r'{JSON_PATH}'
print(f'Local parquet: {{_LOCAL_PARQUET}}')
print(f'Local JSON: {{_LOCAL_JSON}}')
print(f'Parquet exists: {{os.path.exists(_LOCAL_PARQUET)}}')
print(f'JSON exists: {{os.path.exists(_LOCAL_JSON)}}')
"""

setup_cell = nbformat.v4.new_code_cell(setup_source)
nb.cells.insert(1, setup_cell)

# Replace kaggle paths in all code cells
for cell in nb.cells:
    if cell.cell_type == 'code':
        for i, line in enumerate(cell.source):
            cell.source[i] = line.replace(
                "/kaggle/input/economie-maroc-rasd/",
                EXPORT_DIR + "/"
            )
            # Fix the file loading to use local paths
            if 'pf = ' in line and 'economie_maroc.parquet' in line:
                cell.source[i] = f"pf = r'{PARQUET_PATH}'"
            if 'jf = ' in line and 'economie_maroc.json' in line:
                cell.source[i] = f"jf = r'{JSON_PATH}'"
            if "os.listdir('/kaggle/input" in line:
                cell.source[i] = f"print('Files:', os.listdir('{EXPORT_DIR}'))"

# Execute
print("Executing notebook...")
client = NotebookClient(nb, timeout=300, kernel_name='python3')
try:
    client.execute()
    print("Execution complete!")
except Exception as e:
    print(f"Execution error (partial): {e}")

# Remove the setup cell (index 1)
del nb.cells[1]

# Clear outputs from setup cells that show path info
for cell in nb.cells:
    if cell.cell_type == 'code':
        if any(x in ''.join(cell.source) for x in ['_LOCAL_PARQUET', 'Files:', 'Local parquet']):
            cell.outputs = []
            cell.execution_count = None

# Save with outputs
with open(NOTEBOOK_OUT, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print(f"Saved: {NOTEBOOK_OUT}")

# Count outputs
n_outputs = sum(1 for c in nb.cells if c.cell_type == 'code' and c.outputs)
print(f"Cells with outputs: {n_outputs}")
