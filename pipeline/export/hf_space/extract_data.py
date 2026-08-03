"""Extract rich data for HF dashboard."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np

df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

LABELS = {
    'PIB.TRIM.VOL': 'PIB (Vol. Rectifie)',
    'IPC.INDICE': 'IPC (Indice)',
    'CHOMAGE.TAUX': 'Taux de Chomage',
    'BALANCE.COM': 'Balance Commerciale',
    'TAUX.CHANGE.EUR': 'Taux de Change EUR',
    'CREDIT.BANCAIRE': 'Credit Bancaire',
    'INVESTISSEMENT.PUBLIC': 'Investissement Public',
    'DETTE.PUBLIQUE': 'Dette Publique',
    'EMPLOI.VOLUME': 'Emploi (Volume)',
    'DEFICIT.BUDGET': 'Deficit Budget',
    'BAM.OPCVM.ENCOURS': 'OPCVM (Encours)',
    'BAM.TAUX.INTERET': 'Taux d\'Interet',
}

result = {}

# 1. KPIs for key indicators
key_indicators = ['PIB.TRIM.VOL', 'IPC.INDICE', 'CHOMAGE.TAUX', 'BALANCE.COM',
                  'TAUX.CHANGE.EUR', 'CREDIT.BANCAIRE', 'INVESTISSEMENT.PUBLIC',
                  'DETTE.PUBLIQUE', 'EMPLOI.VOLUME', 'DEFICIT.BUDGET']

kpis = []
for ind in key_indicators:
    sub = df[df['code_indicateur'] == ind].dropna(subset=['date', 'valeur']).sort_values('date')
    if len(sub) == 0:
        continue
    latest = sub.iloc[-1]
    prev = sub.iloc[-2] if len(sub) > 1 else None
    val = float(latest['valeur'])
    change = None
    if prev is not None:
        prev_val = float(prev['valeur'])
        if prev_val != 0:
            change = round((val - prev_val) / abs(prev_val) * 100, 2)
    unit = str(latest.get('unite', ''))
    kpis.append({
        'code': ind,
        'label': LABELS.get(ind, ind),
        'value': round(val, 2),
        'unit': unit,
        'change_pct': change,
        'date': str(latest['date'].date()),
        'n_points': len(sub),
        'min': round(float(sub['valeur'].min()), 2),
        'max': round(float(sub['valeur'].max()), 2),
        'mean': round(float(sub['valeur'].mean()), 2),
    })

result['kpis'] = kpis

# 2. Time series for main indicators (sampled)
ts = {}
for ind in key_indicators[:6]:
    sub = df[df['code_indicateur'] == ind].dropna(subset=['date', 'valeur']).sort_values('date')
    if len(sub) == 0:
        continue
    if len(sub) > 300:
        step = len(sub) // 300
        sub = sub.iloc[::step]
    ts[ind] = {
        'dates': sub['date'].dt.strftime('%Y-%m-%d').tolist(),
        'values': [round(float(v), 4) for v in sub['valeur'].tolist()],
        'label': LABELS.get(ind, ind),
    }

result['ts'] = ts

# 3. Source stats
result['sources'] = df['source_code'].value_counts().to_dict()

# 4. Indicator counts
result['indicator_counts'] = df['code_indicateur'].value_counts().head(15).to_dict()

# 5. Date range
result['date_range'] = {
    'min': str(df['date'].dropna().min().date()),
    'max': str(df['date'].dropna().max().date()),
}

# 6. Total
result['total'] = len(df)

with open(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\hf_space\dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"OK: {len(kpis)} KPIs, {len(ts)} time series, {result['total']} rows")
