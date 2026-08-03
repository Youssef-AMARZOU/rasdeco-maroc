"""Check actual indicator codes and their data quality."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Top 20 indicators with stats
top = df['code_indicateur'].value_counts().head(20)
for code, count in top.items():
    sub = df[df['code_indicateur'] == code].dropna(subset=['date', 'valeur'])
    if len(sub) == 0:
        continue
    date_min = sub['date'].min().strftime('%Y-%m-%d')
    date_max = sub['date'].max().strftime('%Y-%m-%d')
    val_min = sub['valeur'].min()
    val_max = sub['valeur'].max()
    unit = sub['unite'].iloc[0] if 'unite' in sub.columns else ''
    src = sub['source_code'].iloc[0] if 'source_code' in sub.columns else ''
    print(f"{code:40s} n={count:6d} dates={date_min}..{date_max} val={val_min:.1f}..{val_max:.1f} unit={unit} src={src}")
