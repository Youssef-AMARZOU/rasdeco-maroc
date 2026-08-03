import json, re

# Load IMF data
with open('public/data/imf.json', 'r', encoding='utf-8') as f:
    imf_data = json.load(f)

# Load ts_data keys
import glob, os
ts_keys = {}
for path in sorted(glob.glob(os.path.join('public/data', 'ts_*.json'))):
    with open(path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    key = list(content.keys())[0]
    data = content[key].get('data', [])
    if len(data) > 0:
        ts_keys[key] = len(data)

# CODE_TO_IMF from data-service.ts
code_to_imf = {
    "PIB_CROISSANCE": "NGDP_RPCH", "IPC_GLISSEMENT": "PCPIEPCH", "CHOMAGE": "LUR",
    "DETTE_PUBLIQUE": "GGXWDG", "PIB_PAR_HAB": "NGDPDPC", "POPULATION": "LP",
    "BALANCE_COURANTE": "BCA_NGDPD", "DEFICIT_BUDGET": "GGXCNL",
}

# CODE_TO_ECONOMIE from data-service.ts
code_to_economie = {
    "PIB_CROISSANCE": "PIB.CROISSANCE", "IPC_GLISSEMENT": "IPC.GLISSEMENT",
    "CHOMAGE": "CHOMAGE.TAUX", "DETTE_PUBLIQUE": "DETTE.PUBLIQUE",
    "RESERVES_CHANGE": "RESERVES.CHANGE", "IDE_FLUX": "IDE.FLUX",
    "DEFICIT_BUDGET": "DEFICIT.BUDGET", "EXPORTATIONS": "EXPORTATIONS",
    "IMPORTATIONS": "IMPORTATIONS", "BALANCE_COURANTE": "BALANCE.COMMERCIALE",
    "EMPLOI": "EMPLOI.VOLUME", "INVESTISSEMENT_PUBLIC": "INVESTISSEMENT.PUBLIC",
}

# IMF_KEYWORDS from data-service.ts
imf_keywords = {
    "pib": "NGDP_RPCH", "inflation": "PCPIEPCH", "chomage": "LUR",
    "dette": "GGXWDG", "deficit": "GGXCNL", "investissement": "NID_NGDP",
    "exportation": "TX_RPCH", "importation": "TM_RPCH", "population": "LP",
    "balance courante": "BCA_NGDPD", "recette publique": "GGR",
    "depense publique": "GGX", "pib.*habitant": "NGDPDPC",
}

# Read rasd-data.ts to extract KPI definitions
with open('src/lib/rasd-data.ts', 'r', encoding='utf-8') as f:
    rasd_content = f.read()

# Find all KPIs with indicatorCode - extract module name and code
# Pattern: a module definition contains kpis array with indicatorCode entries
# Simpler: just find all indicatorCode and their surrounding context

codes_found = set()
for match in re.finditer(r'indicatorCode:\s*"([^"]+)"', rasd_content):
    codes_found.add(match.group(1))

print(f'=== KPI Resolution Audit ({len(codes_found)} codes) ===')
print()

imf_resolved = 0
ts_resolved = 0
unresolved = 0
unresolved_list = []

for code in sorted(codes_found):
    dot = code.replace('_', '.')
    
    # Check IMF resolution
    if code in code_to_imf:
        imf_code = code_to_imf[code]
        if imf_code in imf_data and imf_data[imf_code].get('data'):
            print(f'  [IMF]  {code:30s} -> {imf_code:15s} (IMF)')
            imf_resolved += 1
            continue
    
    # Check ts_data resolution via toDotCode
    if dot in ts_keys:
        print(f'  [TS]   {code:30s} -> {dot:25s} (ts_data, {ts_keys[dot]} rows)')
        ts_resolved += 1
        continue
    
    # Check ts_data via CODE_TO_ECONOMIE
    if code in code_to_economie:
        mapped = code_to_economie[code]
        if mapped in ts_keys:
            print(f'  [TS]   {code:30s} -> {mapped:25s} (CODE_TO_ECONOMIE, {ts_keys[mapped]} rows)')
            ts_resolved += 1
            continue
        else:
            print(f'  [MISS] {code:30s} -> CODE_TO_ECONOMIE maps to {mapped:25s} but ts_data has no such key')
            unresolved += 1
            unresolved_list.append(code)
            continue
    
    unresolved += 1
    unresolved_list.append(code)
    print(f'  [MISS] {code:30s} -> no IMF mapping, no ts_data match (dot={dot})')

print(f'\n=== Summary ===')
print(f'  IMF resolved:  {imf_resolved}')
print(f'  TS_DATA resolved: {ts_resolved}')
print(f'  Unresolved:    {unresolved}')
if unresolved_list:
    print(f'  Unresolved codes: {", ".join(unresolved_list)}')
