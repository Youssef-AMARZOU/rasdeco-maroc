import json

with open('public/data/imf.json', 'r', encoding='utf-8') as f:
    content = json.load(f)

print('=== IMF available codes ===')
for k, v in sorted(content.items()):
    data = v.get('data', [])
    years = [d['year'] for d in data] if data else []
    print(f'  {k:25s} {v["indicator"]:45s} ({len(data)} rows, {min(years) if years else "?"}-{max(years) if years else "?"})')
