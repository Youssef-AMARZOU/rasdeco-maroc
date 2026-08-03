"""Check Datagov indicators too."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Datagov indicators
dg = df[df['source_code'] == 'DATAGOV']
top = dg['code_indicateur'].value_counts().head(15)
for code, count in top.items():
    sub = dg[dg['code_indicateur'] == code].dropna(subset=['date', 'valeur'])
    if len(sub) == 0:
        continue
    date_min = sub['date'].min().strftime('%Y-%m-%d')
    date_max = sub['date'].max().strftime('%Y-%m-%d')
    print(f"  {code:40s} n={count:6d} dates={date_min}..{date_max}")

# Also check HCP specific indicators
print("\n--- HCP indicators ---")
hcp = df[df['source_code'] == 'HCP']
top2 = hcp['code_indicateur'].value_counts().head(15)
for code, count in top2.items():
    sub = hcp[hcp['code_indicateur'] == code].dropna(subset=['date', 'valeur'])
    if len(sub) == 0:
        continue
    date_min = sub['date'].min().strftime('%Y-%m-%d')
    date_max = sub['date'].max().strftime('%Y-%m-%d')
    unit = sub['unite'].iloc[0] if 'unite' in sub.columns else ''
    print(f"  {code:40s} n={count:6d} dates={date_min}..{date_max} unit={unit}")
