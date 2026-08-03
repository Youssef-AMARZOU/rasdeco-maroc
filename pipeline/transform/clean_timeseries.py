import json, re, os

data_dir = 'public/data'

files_to_clean = {
    'ts_change.json': 'CHANGE.USD',
    'ts_chomage.json': 'CHOMAGE.TAUX',
    'ts_deficit.json': 'DEFICIT.BUDGET',
    'ts_dette.json': 'DETTE.PUBLIQUE',
    'ts_emploi.json': 'EMPLOI.VOLUME',
    'ts_other.json': None,  # will detect key
    'ts_pib.json': 'PIB.TRIM.VOL',
}

total_removed = 0
total_kept = 0

for fname in sorted(os.listdir(data_dir)):
    if not fname.startswith('ts_') or not fname.endswith('.json'):
        continue
    
    path = os.path.join(data_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    key = list(content.keys())[0]
    rows = content[key].get('rows', 0)
    data = content[key].get('data', [])
    original_count = len(data)
    
    # Keep only rows with proper date format "YYYY-MM-DD"
    cleaned_data = [d for d in data if re.match(r'^\d{4}-\d{2}-\d{2}$', d.get('date', ''))]
    
    removed = original_count - len(cleaned_data)
    total_removed += removed
    total_kept += len(cleaned_data)
    
    if removed > 0:
        content[key]['data'] = cleaned_data
        content[key]['rows'] = len(cleaned_data)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False)
        
        pct = removed / original_count * 100 if original_count else 0
        print(f'{fname:30s} {key:25s} {original_count:6d} -> {len(cleaned_data):6d}  removed {removed:6d} ({pct:.1f}%)')
    else:
        print(f'{fname:30s} {key:25s} {original_count:6d} -> {len(cleaned_data):6d}  (clean)')

print(f'\nTotal: kept={total_kept}, removed={total_removed}')
