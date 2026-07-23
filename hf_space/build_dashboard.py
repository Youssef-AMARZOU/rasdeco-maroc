"""Build rich HF dashboard with KPIs, charts, and interpretation."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from pathlib import Path

SPACE_DIR = Path(__file__).parent
df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# ---- CONFIG ----
MAIN_INDICATORS = {
    'PIB.TRIM.VOL': {'label': 'PIB (Vol. Rectifie)', 'unit': 'MAD', 'color': '#3b82f6'},
    'IPC.INDICE': {'label': 'IPC (Indice)', 'unit': 'En millions de dhs', 'color': '#ef4444'},
    'EMPLOI.VOLUME': {'label': 'Taux d\'Emploi', 'unit': '%', 'color': '#22c55e'},
    'BAM.OPCVM.ENCOURS': {'label': 'OPCVM (Encours)', 'unit': 'MAD', 'color': '#f59e0b'},
    'DETTE.PUBLIQUE': {'label': 'Dette Publique', 'unit': '%PIB', 'color': '#8b5cf6'},
    'INVESTISSEMENT.PUBLIC': {'label': 'Investissement Public', 'unit': 'MAD', 'color': '#ec4899'},
}

# ---- KPIs ----
kpis = []
for code, cfg in MAIN_INDICATORS.items():
    sub = df[df['code_indicateur'] == code].dropna(subset=['date', 'valeur']).sort_values('date')
    if len(sub) < 2:
        continue
    latest = sub.iloc[-1]
    prev = sub.iloc[-2]
    val = float(latest['valeur'])
    prev_val = float(prev['valeur'])
    change = round((val - prev_val) / abs(prev_val) * 100, 1) if prev_val != 0 else None
    kpis.append({
        'code': code, 'label': cfg['label'], 'value': round(val, 2),
        'unit': cfg['unit'], 'change': change,
        'date': latest['date'].strftime('%Y-%m-%d'),
        'min': round(float(sub['valeur'].min()), 2),
        'max': round(float(sub['valeur'].max()), 2),
        'mean': round(float(sub['valeur'].mean()), 2),
        'n': len(sub),
        'color': cfg['color'],
    })

# ---- TIME SERIES (sampled for size) ----
ts_data = {}
for code, cfg in MAIN_INDICATORS.items():
    sub = df[df['code_indicateur'] == code].dropna(subset=['date', 'valeur']).sort_values('date')
    if len(sub) == 0:
        continue
    step = max(1, len(sub) // 250)
    sub = sub.iloc[::step]
    ts_data[code] = {
        'dates': sub['date'].dt.strftime('%Y-%m-%d').tolist(),
        'values': [round(float(v), 4) for v in sub['valeur'].tolist()],
        'label': cfg['label'], 'color': cfg['color'],
    }

# ---- SOURCES ----
sources = df['source_code'].value_counts().to_dict()

# ---- SMART INTERPRETATION ----
def fmt_ch(ch):
    return f"{ch:+.1f}%" if ch is not None else "N/A"

interp = []
for kpi in kpis:
    code = kpi['code']
    val = kpi['value']
    ch = kpi['change']
    mn, mx, avg = kpi['min'], kpi['max'], kpi['mean']
    chs = fmt_ch(ch)

    if code == 'PIB.TRIM.VOL':
        if val > 0:
            interp.append(f"<b>{kpi['label']}</b>: Le PIB reel est positif a {val:,.0f} MAD ({kpi['date']}), signe de croissance economique. Variation: {chs} vs periode precedente.")
        else:
            interp.append(f"<b>{kpi['label']}</b>: Le PIB reel est negatif a {val:,.0f} MAD, indiquant une contraction. Variation: {chs}.")
    elif code == 'IPC.INDICE':
        if val > 0:
            interp.append(f"<b>{kpi['label']}</b>: L'indice des prix a la consommation est a {val:,.1f}. Tendance inflationniste detectee. Variation: {chs}.")
        else:
            interp.append(f"<b>{kpi['label']}</b>: IPC negatif ({val:,.1f}), situation deflationniste inhabituelle. Variation: {chs}.")
    elif code == 'EMPLOI.VOLUME':
        emp_msg = "Sous-emploi structurel." if val < 50 else "Taux d'emploi correct."
        interp.append(f"<b>{kpi['label']}</b>: Taux d'emploi a {val:.1f}%. {emp_msg} Variation: {chs} points.")
    elif code == 'DETTE.PUBLIQUE':
        if val > 60:
            interp.append(f"<b>{kpi['label']}</b>: Dette publique a {val:,.1f}% du PIB, au-dela du seuil de Maastricht (60%). Risque de soutenabilite. Variation: {chs}.")
        else:
            interp.append(f"<b>{kpi['label']}</b>: Dette publique a {val:,.1f}% du PIB, dans la zone de confort. Variation: {chs}.")
    elif code == 'BAM.OPCVM.ENCOURS':
        interp.append(f"<b>{kpi['label']}</b>: Encours OPCVM a {val:,.0f} MAD, refletant l'activite du marche financier. Variation: {chs}.")
    elif code == 'INVESTISSEMENT.PUBLIC':
        inv_msg = "Niveau eleve, soutien a la croissance." if val > avg else "En-deca de la moyenne historique, frein potentiel."
        interp.append(f"<b>{kpi['label']}</b>: Investissement public a {val:,.0f} MAD. {inv_msg} Variation: {chs}.")

# Global interpretation
total_rows = len(df)
date_min = df['date'].dropna().min().strftime('%Y-%m-%d')
date_max = df['date'].dropna().max().strftime('%Y-%m-%d')
pib_trend = "croissance" if kpis and kpis[0]['value'] > 0 else "contraction"
ipc_trend = "presente" if len(kpis) > 1 and kpis[1]['value'] > 0 else "controlee"
marche_trend = "actif" if len(kpis) > 3 and kpis[3]['value'] > 0 else "en stabilisation"
interp.insert(0, f"<b>Synthese</b>: {total_rows:,} observations collectees automatiquement de {date_min} a {date_max} aupres de {len(sources)} sources (HCP, BKAM, Finances, Datagov.ma, OC). L'economie marocaine montre des signes de {pib_trend} du PIB reel, avec une inflation {ipc_trend} et un marche financier {marche_trend}.")

# ---- BUILD HTML ----
html = []
html.append('<!DOCTYPE html>')
html.append('<html lang="fr">')
html.append('<head>')
html.append('<meta charset="UTF-8">')
html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
html.append('<title>Economie Maroc - RASD Dashboard</title>')
html.append('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>')
html.append('<style>')
html.append('')

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f4f8;color:#1e293b;line-height:1.6}
.header{background:linear-gradient(135deg,#0f172a 0%,#1e40af 50%,#3b82f6 100%);color:#fff;padding:2.5rem 1rem;text-align:center}
.header h1{font-size:2rem;font-weight:800;letter-spacing:-0.5px}
.header p{opacity:.8;margin-top:.5rem;font-size:1rem}
.container{max-width:1200px;margin:0 auto;padding:1rem}
.section-title{font-size:1.2rem;font-weight:700;margin:1.5rem 0 1rem;color:#1e293b;border-left:4px solid #3b82f6;padding-left:.75rem}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-bottom:1.5rem}
.kpi-card{background:#fff;border-radius:14px;padding:1.2rem 1.4rem;box-shadow:0 1px 4px rgba(0,0,0,.08);border-top:3px solid var(--accent);transition:transform .15s}
.kpi-card:hover{transform:translateY(-2px)}
.kpi-label{font-size:.82rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.kpi-value{font-size:1.8rem;font-weight:800;margin:.3rem 0}
.kpi-change{font-size:.85rem;font-weight:600}
.kpi-change.up{color:#16a34a}
.kpi-change.down{color:#dc2626}
.kpi-meta{font-size:.75rem;color:#94a3b8;margin-top:.4rem}
.chart-box{background:#fff;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.interp-box{background:#fff;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.interp-item{padding:.8rem 0;border-bottom:1px solid #f1f5f9;font-size:.92rem;line-height:1.7}
.interp-item:last-child{border-bottom:none}
.interp-item b{color:#1e40af}
.footer{text-align:center;padding:2rem;color:#94a3b8;font-size:.8rem;border-top:1px solid #e2e8f0;margin-top:2rem}
@media(max-width:640px){.header h1{font-size:1.4rem}.kpi-value{font-size:1.4rem}}
"""
html.append(CSS)
html.append('</style>')
html.append('</head>')
html.append('<body>')

# Header
html.append('<div class="header">')
html.append('<h1>Economie Maroc - RASD</h1>')
html.append(f'<p>Observatoire Predictif | {total_rows:,} observations | {date_min} a {date_max}</p>')
html.append('</div>')

html.append('<div class="container">')

# Section: KPIs
html.append('<div class="section-title">Indicateurs Cles</div>')
html.append('<div class="kpi-grid">')
for kpi in kpis:
    ch = kpi['change']
    ch_cls = 'up' if ch and ch > 0 else 'down'
    ch_str = f'{ch:+.1f}%' if ch is not None else 'N/A'
    html.append(f'<div class="kpi-card" style="--accent:{kpi["color"]}">')
    html.append(f'<div class="kpi-label">{kpi["label"]}</div>')
    if abs(kpi['value']) > 10000:
        html.append(f'<div class="kpi-value" style="color:{kpi["color"]}">{kpi["value"]:,.0f}</div>')
    else:
        html.append(f'<div class="kpi-value" style="color:{kpi["color"]}">{kpi["value"]:,.2f}</div>')
    html.append(f'<div class="kpi-change {ch_cls}">{ch_str} vs periode precedente</div>')
    html.append(f'<div class="kpi-meta">{kpi["unit"]} | {kpi["n"]} pts | Min: {kpi["min"]:,.1f} | Max: {kpi["max"]:,.1f}</div>')
    html.append('</div>')
html.append('</div>')

# Section: Time Series
html.append('<div class="section-title">Series Temporelles</div>')
html.append('<div class="chart-box"><div id="ts-main"></div></div>')

# Section: Source distribution
html.append('<div class="section-title">Repartition par Source</div>')
html.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">')
html.append('<div class="chart-box"><div id="src-pie"></div></div>')
html.append('<div class="chart-box"><div id="src-bar"></div></div>')
html.append('</div>')

# Section: Interpretation
html.append('<div class="section-title">Analyse et Interpretation</div>')
html.append('<div class="interp-box">')
for line in interp:
    html.append(f'<div class="interp-item">{line}</div>')
html.append('</div>')

html.append('</div>')  # container

# Footer
html.append('<div class="footer">')
html.append('RASD-Maroc | Youssef Amarzou | Sources: HCP, BKAM, Finances, Datagov.ma, OC')
html.append('</div>')

# Plotly JS
html.append('<script>')

# Time series - one trace per indicator
traces = []
for code, data in ts_data.items():
    traces.append({
        'x': data['dates'], 'y': data['values'],
        'type': 'scatter', 'mode': 'lines',
        'name': data['label'], 'line': {'color': data['color'], 'width': 2},
    })
ts_layout = {
    'title': {'text': 'Evolution des Indicateurs Economiques', 'font': {'size': 16}},
    'height': 450, 'template': 'plotly_white',
    'xaxis': {'title': 'Date'},
    'yaxis': {'title': 'Valeur'},
    'legend': {'orientation': 'h', 'y': -0.2},
    'hovermode': 'x unified',
}
html.append(f"Plotly.newPlot('ts-main',{json.dumps(traces)},{json.dumps(ts_layout)});")

# Pie
src_labels = list(sources.keys())
src_values = list(sources.values())
html.append(f"Plotly.newPlot('src-pie',[{{labels:{json.dumps(src_labels)},values:{json.dumps(src_values)},type:'pie',hole:0.4,textinfo:'label+percent'}}],{{title:'Sources de Donnees',height:350,template:'plotly_white'}});")

# Bar
html.append(f"Plotly.newPlot('src-bar',[{{x:{json.dumps(src_labels)},y:{json.dumps(src_values)},type:'bar',marker:{{color:['#3b82f6','#22c55e','#f59e0b','#ef4444','#8b5cf6']}}}}],{{title:'Volume par Source',height:350,template:'plotly_white',xaxis:{{tickangle:-30}}}});")

html.append('</script>')
html.append('</body>')
html.append('</html>')

out = SPACE_DIR / "index.html"
out.write_text("\n".join(html), encoding="utf-8")
print(f"OK {len(chr(10).join(html))} bytes -> {out}")
print(f"KPIs: {len(kpis)}, TS: {len(ts_data)}, Interp: {len(interp)} items")
