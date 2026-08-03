import json, re, os

data_dir = 'public/data'

# Analyze CHANGE bad rows in detail
with open(os.path.join(data_dir, 'ts_change.json'), 'r', encoding='utf-8') as f:
    content = json.load(f)
key = list(content.keys())[0]
data = content[key]['data']
bad = [d for d in data if not re.match(r'^\d{4}-\d{2}-\d{2}$', d.get('date', ''))]
print(f'=== ts_change.json ({key}) ===')
print(f'Bad rows: {len(bad)}')
for d in bad[:5]:
    print(f'  date={d["date"]} valeur={d["valeur"]} unite={d["unite"]} source={d["source_code"]}')
good = [d for d in data if re.match(r'^\d{4}-\d{2}-\d{2}$', d.get('date', ''))]
print(f'Good rows: {len(good)}')
for d in good[:3]:
    print(f'  date={d["date"]} valeur={d["valeur"]} unite={d["unite"]} source={d["source_code"]}')
print()

# Analyze other files
for fname in ['ts_chomage.json', 'ts_dette.json', 'ts_emploi.json', 'ts_deficit.json', 'ts_pib.json', 'ts_other.json']:
    with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
        content = json.load(f)
    key = list(content.keys())[0]
    data = content[key]['data']
    bad = [d for d in data if not re.match(r'^\d{4}-\d{2}-\d{2}$', d.get('date', ''))]
    
    dates = sorted(set(d['date'] for d in bad))[:12]
    pct = len(bad)/len(data)*100 if data else 0
    print(f'=== {fname} ({key}) ===')
    print(f'  Total={len(data)}, Bad={len(bad)} ({pct:.1f}%)')
    print(f'  Sample dates: {" | ".join(dates)}')
    print(f'  First bad entry: {bad[0]}')
    if len(bad) > 1:
        print(f'  Second bad entry: {bad[1]}')
    print()
