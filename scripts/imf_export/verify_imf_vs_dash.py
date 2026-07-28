"""Verify specific IMF data points in dashboard match data_parser."""
import sys
sys.path.insert(0, 'scripts/imf_export')
from data_parser import IMF_MOROCCO_VALUES as IMF

t = open('src/lib/rasd-data.ts', encoding='utf-8').read()

# Mapping: IMF code -> dashboard code
MAP = {
    'NGDP_RPCH': 'PIB_CROISSANCE',
    'PCPIEPCH': 'IPC_GLISSEMENT',
    'LUR': 'CHOMAGE',
    'GGXWDG': 'DETTE_PUBLIQUE',
    'GGXCNL': 'DEFICIT_BUDGET',
    'NGDPDPC': 'PIB_PAR_HAB',
    'BCA_NGDPD': 'BALANCE_COURANTE',
    'LP': 'POPULATION',
    'TX_RPCH': 'EXPORTATIONS',
    'TM_RPCH': 'IMPORTATIONS',
    'NID_NGDP': 'INVESTISSEMENT',
}

errors = []

for imf_code, dash_code in MAP.items():
    imf_data = IMF.get(imf_code, {})
    if not imf_data:
        errors.append(f"MISSING IMF DATA: {imf_code}")
        continue

    # Find the indicator block in dashboard
    code_str = f'code: "{dash_code}"'
    idx = t.find(code_str)
    if idx == -1:
        errors.append(f"MISSING DASHBOARD CODE: {dash_code}")
        continue

    # Find the national: ts([...]) block after this code
    block_start = t.find('national: ts([', idx)
    if block_start == -1:
        errors.append(f"MISSING national ts for {dash_code}")
        continue

    # Find closing ])
    block_end = t.find('])', block_start)
    block = t[block_start:block_end+2]

    # Parse all [year, value] pairs
    import re
    pairs = re.findall(r'\[(\d+),\s*([-\d.]+)\]', block)
    dash_data = {int(y): float(v) for y, v in pairs}

    # Compare specific years
    check_years = [1990, 2000, 2010, 2020, 2024, 2025, 2026]
    for yr in check_years:
        if yr in imf_data and yr in dash_data:
            iv = imf_data[yr]
            dv = dash_data[yr]
            diff = abs(iv - dv)
            if diff > 0.01:
                errors.append(f"{dash_code} ({yr}): IMF={iv} vs DASH={dv} diff={diff:.4f}")
        elif yr in imf_data and yr not in dash_data:
            errors.append(f"{dash_code}: missing year {yr} in dashboard")
        elif yr not in imf_data and yr in dash_data:
            pass  # IMF may not have all years
        else:
            errors.append(f"{dash_code} ({yr}): not in either source")

if errors:
    print(f"\nWARN  {len(errors)} DISCREPANCIES:")
    for e in errors:
        print(f"   * {e}")
else:
    print("\nOK  ALL DATA POINTS MATCH IMF REFERENCES")

print(f"\nChecked {len(MAP)} indicators across {len(check_years)} years each")
