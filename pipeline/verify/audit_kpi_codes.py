import json, re, glob, os

# Get all ts_data keys that have data
ts_keys = {}
data_dir = 'public/data'
for path in sorted(glob.glob(os.path.join(data_dir, 'ts_*.json'))):
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    key = list(content.keys())[0]
    data = content[key].get('data', [])
    if len(data) > 0:
        ts_keys[key] = len(data)

print('=== Available ts_data keys with data ===')
for k, v in sorted(ts_keys.items()):
    print(f'  {k:30s} ({v} rows)')
print()

# Get indicatorCodes from rasd-data.ts
with open('src/lib/rasd-data.ts', 'r', encoding='utf-8') as f:
    content = f.read()

codes = set()
for match in re.finditer(r'indicatorCode:\s*"([^"]+)"', content):
    codes.add(match.group(1))

print(f'=== KPI indicatorCodes ({len(codes)}) ===')
matched = 0
unmatched = 0
for c in sorted(codes):
    dot = c.replace('_', '.')
    if dot in ts_keys:
        print(f'  [MATCH] {c:30s} -> {dot}')
        matched += 1
    else:
        # Check if any key starts with the same prefix
        prefix = dot.split('.')[0]
        related = [k for k in ts_keys if k.startswith(prefix)]
        print(f'  [MISS]  {c:30s} -> {dot:25s}  (related: {", ".join(related) if related else "none"})')
        unmatched += 1

print(f'\nMatched: {matched}, Unmatched: {unmatched}')
