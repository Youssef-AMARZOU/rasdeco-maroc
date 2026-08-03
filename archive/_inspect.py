import sys; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
print('Shape:', df.shape)
print('Date range:', df['date'].min(), '->', df['date'].max())
print()
for code, cnt in df['code_indicateur'].value_counts().head(15).items():
    sub = df[df['code_indicateur']==code].dropna(subset=['date','valeur'])
    if len(sub)==0: continue
    dmin = sub['date'].min().date()
    dmax = sub['date'].max().date()
    vmin = sub['valeur'].min()
    vmax = sub['valeur'].max()
    print(f'  {code:40s} n={cnt:6d} {dmin}..{dmax} val={vmin:.1f}..{vmax:.1f}')
print()
print('Sources:', df['source_code'].value_counts().to_dict())
print('Regions:', df['region_code'].value_counts().head(5).to_dict())
