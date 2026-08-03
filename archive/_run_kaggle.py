"""Run the Kaggle notebook locally and save with outputs."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess
import os

NOTEBOOK = r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\kaggle_dataset\notebook.ipynb'
WORKDIR = r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc'

# First, patch the notebook to use local data paths
import json
with open(NOTEBOOK, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Replace Kaggle paths with local paths
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            line = line.replace('/kaggle/input/economie-maroc-rasd/', 
                               os.path.join(WORKDIR, 'data', 'export', '').replace('\\', '/'))
            line = line.replace("os.path.exists(pf)", "os.path.exists(pf)")
            new_source.append(line)
        cell['source'] = new_source

# Save patched version
PATCHED = os.path.join(WORKDIR, 'kaggle_dataset', '_patched.ipynb')
with open(PATCHED, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Patched notebook saved to {PATCHED}")
print("Run with: jupyter nbconvert --execute --to notebook --inplace")
