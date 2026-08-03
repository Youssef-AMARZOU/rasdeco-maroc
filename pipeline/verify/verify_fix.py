import json

with open('public/data/imf.json', 'r', encoding='utf-8') as f:
    imf = json.load(f)

codes = {
    'NGDP_RPCH': 'PIB_CROISSANCE (hardcoded: 3.9)',
    'PCPIEPCH': 'IPC_GLISSEMENT (hardcoded: 2.1)',
    'LUR': 'CHOMAGE (hardcoded: 12.0)',
    'GGXWDG': 'DETTE_PUBLIQUE (hardcoded: 67.1)',
    'NGDPDPC': 'PIB_PAR_HAB (hardcoded: 5198)',
    'LP': 'POPULATION (hardcoded: 32.2)',
    'BCA_NGDPD': 'BALANCE_COURANTE (hardcoded: none)',
    'GGXCNL': 'DEFICIT_BUDGET (hardcoded: none)',
}

print('=== IMF 2025-target verification ===')
for imf_code, desc in sorted(codes.items()):
    data = imf[imf_code]['data']
    old = data[-1]
    target = 2025
    best = min(data, key=lambda p: abs(p['year'] - target))
    idx = data.index(best)
    prev = data[idx - 1] if idx > 0 else None
    diff = best['value'] - (prev['value'] if prev else 0)
    trend = "up" if diff > 0.01 else "down" if diff < -0.01 else "stable"

    print(f'\n{desc} (IMF:{imf_code})')
    print(f'  OLD (last entry):    year={old["year"]}, value={old["value"]}')
    print(f'  NEW (closest 2025):  year={best["year"]}, value={best["value"]}')
    if prev:
        print(f'  Previous year:       year={prev["year"]}, value={prev["value"]}')
    print(f'  Trend: {trend}')
