import json, re

# Load IMF data
with open('public/data/imf.json', 'r', encoding='utf-8') as f:
    imf_data = json.load(f)

# Load ts_data
import glob, os
ts_data = {}
for path in sorted(glob.glob(os.path.join('public/data', 'ts_*.json'))):
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    key = list(content.keys())[0]
    data = content[key].get('data', [])
    if len(data) > 0:
        ts_data[key] = data

# Mapping from indicatorCode to data source
code_to_imf = {
    "PIB_CROISSANCE": "NGDP_RPCH",
    "IPC_GLISSEMENT": "PCPIEPCH",
    "CHOMAGE": "LUR",
    "DETTE_PUBLIQUE": "GGXWDG",
    "PIB_PAR_HAB": "NGDPDPC",
    "POPULATION": "LP",
    "BALANCE_COURANTE": "BCA_NGDPD",
    "DEFICIT_BUDGET": "GGXCNL",
}

code_to_ts = {
    "IDE_FLUX": "IDE.FLUX",
    "RESERVES_CHANGE": "RESERVES.CHANGE",
}

# Read rasd-data.ts
with open('src/lib/rasd-data.ts', 'r', encoding='utf-8') as f:
    content = f.read()

def extract_kpi_value(code):
    """Extract hardcoded value and previousValue for a KPI by indicatorCode."""
    # Find the KPI object containing this indicatorCode
    pattern = r'\{[^}]*indicatorCode:\s*"' + re.escape(code) + r'"[^}]*\}'
    match = re.search(pattern, content)
    if not match:
        return None
    obj = match.group()
    value_m = re.search(r'value:\s*([\d.]+)', obj)
    prev_m = re.search(r'previousValue:\s*([\d.]+)', obj)
    label_m = re.search(r'label:\s*"([^"]+)"', obj)
    return {
        'label': label_m.group(1) if label_m else 'unknown',
        'value': float(value_m.group(1)) if value_m else None,
        'previousValue': float(prev_m.group(1)) if prev_m else None,
    }

print('=== IMF-Resolved KPI Values ===')
for code, imf_code in sorted(code_to_imf.items()):
    hc = extract_kpi_value(code)
    if not hc:
        print(f'{code}: could not find in rasd-data.ts')
        continue
    
    imf_entries = imf_data[imf_code]['data']
    latest = imf_entries[-1]
    prev = imf_entries[-2] if len(imf_entries) > 1 else None
    
    print(f'\n--- {hc["label"]} ({code} -> IMF:{imf_code}) ---')
    print(f'  Hardcoded:      value={hc["value"]}, previous={hc["previousValue"]}')
    print(f'  IMF latest:     year={latest["year"]}, value={latest["value"]}')
    if prev:
        print(f'  IMF previous:   year={prev["year"]}, value={prev["value"]}')
    
    # Find the last 5 IMF entries
    print(f'  IMF last 5 years:')
    for entry in imf_entries[-5:]:
        print(f'    {entry["year"]}: {entry["value"]}')

print('\n\n=== TS_DATA-Resolved KPI Values ===')
for code, ts_key in sorted(code_to_ts.items()):
    hc = extract_kpi_value(code)
    if not hc:
        print(f'{code}: could not find in rasd-data.ts')
        continue
    
    points = ts_data[ts_key]
    sorted_points = sorted(points, key=lambda x: x['date'], reverse=True)
    latest = sorted_points[0]
    prev = sorted_points[1] if len(sorted_points) > 1 else None
    
    print(f'\n--- {hc["label"]} ({code} -> ts_data:{ts_key}) ---')
    print(f'  Hardcoded:      value={hc["value"]}, previous={hc["previousValue"]}')
    print(f'  TS latest:      date={latest["date"]}, valeur={latest["valeur"]} {latest["unite"]}')
    if prev:
        print(f'  TS previous:    date={prev["date"]}, valeur={prev["valeur"]} {prev["unite"]}')
    print(f'  TS last 5 entries:')
    for p in sorted_points[:5]:
        print(f'    {p["date"]}: {p["valeur"]} {p["unite"]} ({p["source_code"]})')
