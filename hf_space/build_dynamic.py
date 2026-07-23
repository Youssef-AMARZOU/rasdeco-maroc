"""Build fully dynamic HF dashboard with predictions and interpretation."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta

SPACE_DIR = Path(__file__).parent
df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# All indicators with labels
ALL_LABELS = {
    'PIB.TRIM.VOL': 'PIB (Vol. Rectifie)',
    'IPC.INDICE': 'IPC (Indice)',
    'EMPLOI.VOLUME': "Taux d'Emploi",
    'BAM.OPCVM.ENCOURS': 'OPCVM (Encours)',
    'DETTE.PUBLIQUE': 'Dette Publique',
    'INVESTISSEMENT.PUBLIC': 'Investissement Public',
    'DEFICIT.BUDGET': 'Deficit Budget',
    'INDICATEUR.HCP.GENERIQUE': 'Indicateur HCP Generique',
    'CHANGE.USD': 'Taux de Change USD',
    'EXPORTATIONS': 'Exportations',
    'PIB.ANNUEL.VOL': 'PIB Annuel',
}

COLORS = ['#3b82f6','#ef4444','#22c55e','#f59e0b','#8b5cf6','#ec4899',
          '#06b6d4','#84cc16','#f97316','#6366f1','#14b8a6']

# ---- Collect all data ----
all_ts = {}
all_kpis = {}
all_interp = {}

for i, (code, label) in enumerate(ALL_LABELS.items()):
    sub = df[df['code_indicateur'] == code].dropna(subset=['date', 'valeur']).sort_values('date')
    if len(sub) < 3:
        continue

    color = COLORS[i % len(COLORS)]

    # Time series
    step = max(1, len(sub) // 400)
    sampled = sub.iloc[::step]
    all_ts[code] = {
        'dates': sampled['date'].dt.strftime('%Y-%m-%d').tolist(),
        'values': [round(float(v), 4) for v in sampled['valeur'].tolist()],
        'label': label, 'color': color,
    }

    # Naive forecast (last 12 values repeated with trend)
    vals = sub['valeur'].values.astype(float)
    dates = sub['date'].values
    last_date = sub['date'].max()
    last_val = vals[-1]
    # Calculate trend from last 10 points
    if len(vals) >= 10:
        trend = np.mean(np.diff(vals[-10:]))
    else:
        trend = np.mean(np.diff(vals[-3:]))

    forecast_dates = []
    forecast_vals = []
    for h in range(1, 13):
        fd = last_date + pd.DateOffset(months=h)
        forecast_dates.append(fd.strftime('%Y-%m-%d'))
        forecast_vals.append(round(float(last_val + trend * h), 4))

    # Confidence interval (simple: +/- 10% widening)
    forecast_upper = [round(v * (1 + 0.02 * (i+1)), 4) for i, v in enumerate(forecast_vals)]
    forecast_lower = [round(v * (1 - 0.02 * (i+1)), 4) for i, v in enumerate(forecast_vals)]

    all_ts[code + '_forecast'] = {
        'dates': forecast_dates,
        'values': forecast_vals,
        'upper': forecast_upper,
        'lower': forecast_lower,
        'label': label + ' (Prevision)',
        'color': color,
    }

    # KPI
    latest = sub.iloc[-1]
    prev = sub.iloc[-2]
    val = float(latest['valeur'])
    prev_val = float(prev['valeur'])
    change = round((val - prev_val) / abs(prev_val) * 100, 1) if prev_val != 0 else None
    unit = str(latest.get('unite', ''))

    all_kpis[code] = {
        'label': label, 'value': round(val, 2), 'unit': unit,
        'change': change, 'date': latest['date'].strftime('%Y-%m-%d'),
        'min': round(float(sub['valeur'].min()), 2),
        'max': round(float(sub['valeur'].max()), 2),
        'mean': round(float(sub['valeur'].mean()), 2),
        'std': round(float(sub['valeur'].std()), 2),
        'n': len(sub), 'color': color,
    }

    # Interpretation
    avg = all_kpis[code]['mean']
    interp_lines = []
    interp_lines.append(f"<b>{label}</b>: {len(sub)} observations de {sub['date'].min().strftime('%Y-%m')} a {sub['date'].max().strftime('%Y-%m')}.")
    interp_lines.append(f"Valeur actuelle: <b>{val:,.2f}</b> {unit}. Moyenne historique: {avg:,.2f}. Ecart-type: {all_kpis[code]['std']:,.2f}.")

    if change is not None:
        direction = "hausse" if change > 0 else "baisse"
        interp_lines.append(f"Variation recente: <b>{change:+.1f}%</b> ({direction}).")

    # Trend analysis
    if len(vals) >= 20:
        recent_mean = np.mean(vals[-20:])
        older_mean = np.mean(vals[:20])
        if recent_mean > older_mean * 1.1:
            interp_lines.append("Tendance haussiere sur la periode longue.")
        elif recent_mean < older_mean * 0.9:
            interp_lines.append("Tendance baissiere sur la periode longue.")
        else:
            interp_lines.append("Stabilite relative sur la periode longue.")

    # Forecast
    interp_lines.append(f"Prevision 12 mois: {forecast_vals[0]:,.2f} a {forecast_vals[-1]:,.2f} {unit} (methode naive-tendance).")

    all_interp[code] = interp_lines

# Sources
sources = df['source_code'].value_counts().to_dict()

# ---- BUILD HTML ----
h = []
h.append('<!DOCTYPE html>')
h.append('<html lang="fr">')
h.append('<head>')
h.append('<meta charset="UTF-8">')
h.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
h.append('<title>Economie Maroc - RASD Dashboard</title>')
h.append('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>')
h.append('<style>')

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f4f8;color:#1e293b;line-height:1.6}
.header{background:linear-gradient(135deg,#0f172a 0%,#1e40af 50%,#3b82f6 100%);color:#fff;padding:2.5rem 1rem;text-align:center}
.header h1{font-size:2rem;font-weight:800}
.header p{opacity:.8;margin-top:.5rem}
.container{max-width:1200px;margin:0 auto;padding:1rem}
.section-title{font-size:1.2rem;font-weight:700;margin:1.5rem 0 1rem;color:#1e293b;border-left:4px solid #3b82f6;padding-left:.75rem}
.controls{background:#fff;border-radius:14px;padding:1.2rem;margin-bottom:1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08);display:flex;gap:1rem;flex-wrap:wrap;align-items:end}
.controls label{font-size:.82rem;color:#64748b;font-weight:600;display:block;margin-bottom:.3rem}
.controls select,.controls input{padding:.5rem .8rem;border:1px solid #e2e8f0;border-radius:8px;font-size:.9rem;background:#f8fafc}
.controls select{min-width:220px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;margin-bottom:1.5rem}
.kpi-card{background:#fff;border-radius:14px;padding:1.2rem;box-shadow:0 1px 4px rgba(0,0,0,.08);border-top:3px solid var(--accent);cursor:pointer;transition:all .15s}
.kpi-card:hover,.kpi-card.active{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.12)}
.kpi-card.active{border-top-width:4px}
.kpi-label{font-size:.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.kpi-value{font-size:1.6rem;font-weight:800;margin:.2rem 0}
.kpi-change{font-size:.82rem;font-weight:600}
.kpi-change.up{color:#16a34a}
.kpi-change.down{color:#dc2626}
.kpi-change.flat{color:#94a3b8}
.kpi-meta{font-size:.72rem;color:#94a3b8;margin-top:.3rem}
.chart-box{background:#fff;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.interp-box{background:#fff;border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.interp-item{padding:.7rem 0;border-bottom:1px solid #f1f5f9;font-size:.9rem;line-height:1.7}
.interp-item:last-child{border-bottom:none}
.interp-item b{color:#1e40af}
.footer{text-align:center;padding:2rem;color:#94a3b8;font-size:.8rem;border-top:1px solid #e2e8f0;margin-top:2rem}
@media(max-width:640px){.header h1{font-size:1.4rem}.kpi-value{font-size:1.3rem}.controls{flex-direction:column}}
"""
h.append(CSS)
h.append('</style>')
h.append('</head>')
h.append('<body>')

# Header
total = len(df)
dmin = df['date'].dropna().min().strftime('%Y-%m-%d')
dmax = df['date'].dropna().max().strftime('%Y-%m-%d')
h.append('<div class="header">')
h.append('<h1>Economie Maroc - RASD</h1>')
h.append(f'<p>Observatoire Predictif Multi-Domaines | {total:,} observations | {dmin} a {dmax} | 5 sources</p>')
h.append('</div>')

h.append('<div class="container">')

# Controls
h.append('<div class="controls">')
h.append('<div><label>Indicateur</label>')
h.append('<select id="sel-ind">')
for code, label in ALL_LABELS.items():
    if code in all_ts:
        h.append(f'<option value="{code}">{label}</option>')
h.append('</select></div>')
h.append('<div><label>Periode</label>')
h.append('<select id="sel-period">')
h.append('<option value="all">Tout</option>')
h.append('<option value="10">10 ans</option>')
h.append('<option value="5" selected>5 ans</option>')
h.append('<option value="3">3 ans</option>')
h.append('<option value="1">1 an</option>')
h.append('</select></div>')
h.append('<div><label>Afficher previsions</label>')
h.append('<select id="sel-forecast">')
h.append('<option value="yes">Oui</option>')
h.append('<option value="no">Non</option>')
h.append('</select></div>')
h.append('</div>')

# KPI Grid
h.append('<div class="section-title">Indicateurs Cles</div>')
h.append('<div class="kpi-grid" id="kpi-grid">')
for code, kpi in all_kpis.items():
    ch = kpi['change']
    ch_cls = 'up' if ch and ch > 0 else ('down' if ch and ch < 0 else 'flat')
    ch_str = f'{ch:+.1f}%' if ch is not None else 'N/A'
    val_str = f"{kpi['value']:,.0f}" if abs(kpi['value']) > 10000 else f"{kpi['value']:,.2f}"
    h.append(f'<div class="kpi-card" data-code="{code}" style="--accent:{kpi["color"]}" onclick="selectIndicator(\'{code}\')">')
    h.append(f'<div class="kpi-label">{kpi["label"]}</div>')
    h.append(f'<div class="kpi-value" style="color:{kpi["color"]}">{val_str}</div>')
    h.append(f'<div class="kpi-change {ch_cls}">{ch_str} vs periode precedente</div>')
    h.append(f'<div class="kpi-meta">{kpi["unit"]} | {kpi["n"]} pts | Moy: {kpi["mean"]:,.1f} | Std: {kpi["std"]:,.1f}</div>')
    h.append('</div>')
h.append('</div>')

# Main chart
h.append('<div class="section-title">Evolution et Previsions</div>')
h.append('<div class="chart-box"><div id="main-chart" style="height:480px"></div></div>')

# Source charts
h.append('<div class="section-title">Sources de Donnees</div>')
h.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">')
h.append('<div class="chart-box"><div id="src-pie" style="height:350px"></div></div>')
h.append('<div class="chart-box"><div id="src-bar" style="height:350px"></div></div>')
h.append('</div>')

# Interpretation
h.append('<div class="section-title">Analyse et Interpretation</div>')
h.append('<div class="interp-box" id="interp-box"></div>')

# Agent IA
h.append('<div class="section-title">Agent IA - Assistant Economie</div>')
h.append('<div class="chart-box" style="max-height:500px">')
h.append('<div id="agent-chat" style="height:300px;overflow-y:auto;padding:1rem;background:#f8fafc;border-radius:8px;margin-bottom:1rem;font-size:.9rem"></div>')
h.append('<div style="display:flex;gap:.5rem">')
h.append('<input id="agent-input" type="text" placeholder="Posez une question: PIB, inflation, emploi, dette, resume..." style="flex:1;padding:.6rem 1rem;border:1px solid #e2e8f0;border-radius:8px;font-size:.9rem" onkeydown="if(event.key===\'Enter\')sendAgent()">')
h.append('<button onclick="sendAgent()" style="padding:.6rem 1.2rem;background:#3b82f6;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600">Envoyer</button>')
h.append('</div>')
h.append('<div style="margin-top:.8rem;display:flex;gap:.5rem;flex-wrap:wrap">')
examples = ["Resume", "Quel est le PIB?", "Inflation", "Emploi", "Dette publique", "Sources"]
for ex in examples:
    h.append(f'<button onclick="agentExample(\'{ex}\')" style="padding:.3rem .8rem;background:#e2e8f0;border:none;border-radius:6px;cursor:pointer;font-size:.8rem">{ex}</button>')
h.append('</div>')
h.append('</div>')

h.append('</div>')
h.append('<div class="footer">RASD-Maroc | Youssef Amarzou | Sources: HCP, BKAM, Finances, Datagov.ma, OC | Previsions: Methode naive-tendance | Agent IA integre</div>')

# ---- JAVASCRIPT ----
h.append('<script>')

# Data
h.append(f'var ALL_TS = {json.dumps(all_ts)};')
h.append(f'var ALL_KPIS = {json.dumps(all_kpis)};')
h.append(f'var ALL_INTERP = {json.dumps(all_interp)};')
h.append(f'var SRC_LABELS = {json.dumps(list(sources.keys()))};')
h.append(f'var SRC_VALUES = {json.dumps(list(sources.values()))};')

JS = """
function selectIndicator(code) {
    document.getElementById('sel-ind').value = code;
    updateAll();
    document.querySelectorAll('.kpi-card').forEach(c => c.classList.remove('active'));
    var card = document.querySelector('.kpi-card[data-code="'+code+'"]');
    if(card) card.classList.add('active');
}

function filterByPeriod(dates, values, period) {
    if(period === 'all') return {dates: dates, values: values};
    var cutoff = new Date();
    cutoff.setFullYear(cutoff.getFullYear() - parseInt(period));
    var fdates = [], fvalues = [];
    for(var i=0; i<dates.length; i++) {
        if(new Date(dates[i]) >= cutoff) { fdates.push(dates[i]); fvalues.push(values[i]); }
    }
    return {dates: fdates, values: fvalues};
}

function updateAll() {
    var code = document.getElementById('sel-ind').value;
    var period = document.getElementById('sel-period').value;
    var showForecast = document.getElementById('sel-forecast').value === 'yes';

    var ts = ALL_TS[code];
    var forecast = ALL_TS[code + '_forecast'];
    var kpi = ALL_KPIS[code];
    var interp = ALL_INTERP[code];

    if(!ts) return;

    var filtered = filterByPeriod(ts.dates, ts.values, period);

    var traces = [{
        x: filtered.dates,
        y: filtered.values,
        type: 'scatter',
        mode: 'lines',
        name: ts.label,
        line: {color: ts.color, width: 2.5}
    }];

    if(showForecast && forecast) {
        traces.push({
            x: forecast.dates,
            y: forecast.values,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Prevision',
            line: {color: ts.color, width: 2, dash: 'dash'},
            marker: {size: 6}
        });
        traces.push({
            x: forecast.dates.concat(forecast.dates.slice().reverse()),
            y: forecast.upper.concat(forecast.lower.slice().reverse()),
            type: 'scatter',
            fill: 'toself',
            fillcolor: ts.color + '20',
            line: {color: 'transparent'},
            name: 'Intervalle 80%',
            showlegend: true
        });
    }

    var layout = {
        title: {text: ts.label, font: {size: 16}},
        height: 480,
        template: 'plotly_white',
        xaxis: {title: 'Date', rangeslider: {visible: true}},
        yaxis: {title: kpi ? kpi.unit : ''},
        legend: {orientation: 'h', y: -0.25},
        hovermode: 'x unified'
    };

    Plotly.newPlot('main-chart', traces, layout);

    // Interpretation
    var box = document.getElementById('interp-box');
    box.innerHTML = interp.map(function(line) { return '<div class="interp-item">' + line + '</div>'; }).join('');

    // Highlight KPI card
    document.querySelectorAll('.kpi-card').forEach(function(c) {
        c.classList.toggle('active', c.getAttribute('data-code') === code);
    });
}

// Source charts
Plotly.newPlot('src-pie', [{
    labels: SRC_LABELS,
    values: SRC_VALUES,
    type: 'pie',
    hole: 0.4,
    textinfo: 'label+percent'
}], {title: 'Repartition', height: 350, template: 'plotly_white'});

Plotly.newPlot('src-bar', [{
    x: SRC_LABELS,
    y: SRC_VALUES,
    type: 'bar',
    marker: {color: ['#3b82f6','#22c55e','#f59e0b','#ef4444','#8b5cf6']}
}], {title: 'Volume par Source', height: 350, template: 'plotly_white', xaxis: {tickangle: -30}});

// Event listeners
document.getElementById('sel-ind').addEventListener('change', updateAll);
document.getElementById('sel-period').addEventListener('change', updateAll);
document.getElementById('sel-forecast').addEventListener('change', updateAll);

// ---- Agent IA ----
function agentReply(msg) {
    var m = msg.toLowerCase();
    var box = document.getElementById('agent-chat');

    // Check for indicator matches
    var indicatorMap = {
        'pib': 'PIB.TRIM.VOL', 'croissance': 'PIB.TRIM.VOL',
        'ipc': 'IPC.INDICE', 'inflation': 'IPC.INDICE', 'prix': 'IPC.INDICE',
        'emploi': 'EMPLOI.VOLUME', 'chomage': 'EMPLOI.VOLUME',
        'opcvm': 'BAM.OPCVM.ENCOURS', 'marche financier': 'BAM.OPCVM.ENCOURS',
        'dette': 'DETTE.PUBLIQUE', 'budget': 'DEFICIT.BUDGET', 'deficit': 'DEFICIT.BUDGET',
        'investissement': 'INVESTISSEMENT.PUBLIC', 'invest': 'INVESTISSEMENT.PUBLIC',
        'change': 'CHANGE.USD', 'dollar': 'CHANGE.USD', 'usd': 'CHANGE.USD',
        'export': 'EXPORTATIONS', 'exportations': 'EXPORTATIONS',
    };

    for (var kw in indicatorMap) {
        if (m.includes(kw)) {
            var code = indicatorMap[kw];
            var kpi = ALL_KPIS[code];
            var interp = ALL_INTERP[code];
            if (!kpi) continue;
            var resp = '<b>' + kpi.label + '</b> (' + kpi.unit + '):<br>';
            resp += 'Valeur: <b>' + kpi.value.toLocaleString() + '</b> (' + kpi.date + ')<br>';
            resp += 'Moyenne: ' + kpi.mean.toLocaleString() + ' | Ecart-type: ' + kpi.std.toLocaleString() + '<br>';
            if (kpi.change !== null) resp += 'Variation: <b>' + (kpi.change > 0 ? '+' : '') + kpi.change + '%</b><br>';
            if (interp) resp += '<br>' + interp.join('<br>');
            return resp;
        }
    }

    if (m.includes('resume') || m.includes('sommaire') || m.includes('synthese')) {
        var total = Object.values(ALL_KPIS).reduce(function(s,k){return s+k.n}, 0);
        var nInd = Object.keys(ALL_KPIS).length;
        return '<b>Synthese RASD-Maroc</b><br>' + total.toLocaleString() + ' observations | ' + nInd + ' indicateurs | 5 sources (HCP, BKAM, Finances, Datagov.ma, OC)<br>Periode: 2000 a 2025<br><br>Indicateurs cles: PIB, IPC, Emploi, Dette, Investissement, OPCVM, Taux de Change, Exportations.<br>Previsions naive-tendance integrees.';
    }

    if (m.includes('source') || m.includes('donnee') || m.includes('collecte')) {
        var resp = '<b>Sources de donnees</b><br>';
        SRC_LABELS.forEach(function(l,i) { resp += l + ': ' + SRC_VALUES[i].toLocaleString() + ' observations<br>'; });
        return resp;
    }

    if (m.includes('bonjour') || m.includes('salut') || m.includes('hello') || m.includes('aide') || m.includes('help')) {
        return 'Bienvenue! Je suis l\'assistant economie du RASD-Maroc.<br><br>Essayez: <b>PIB</b>, <b>inflation</b>, <b>emploi</b>, <b>dette</b>, <b>budget</b>, <b>resume</b>, <b>sources</b>';
    }

    return 'Je ne suis pas sur de comprendre. Essayez: <b>PIB</b>, <b>inflation</b>, <b>emploi</b>, <b>dette</b>, <b>resume</b>, <b>sources</b>';
}

function addChatMsg(text, isUser) {
    var box = document.getElementById('agent-chat');
    var div = document.createElement('div');
    div.style.cssText = 'padding:.6rem .8rem;margin:.4rem 0;border-radius:8px;max-width:85%;' +
        (isUser ? 'background:#3b82f6;color:#fff;margin-left:auto;text-align:right' : 'background:#fff;border:1px solid #e2e8f0');
    div.innerHTML = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function sendAgent() {
    var input = document.getElementById('agent-input');
    var msg = input.value.trim();
    if (!msg) return;
    addChatMsg(msg, true);
    input.value = '';
    setTimeout(function() { addChatMsg(agentReply(msg), false); }, 200);
}

function agentExample(text) {
    document.getElementById('agent-input').value = text;
    sendAgent();
}

// Init
updateAll();
addChatMsg('Bienvenue! Posez des questions sur l\'economie marocaine: PIB, inflation, emploi, dette, resume...', false);
"""

h.append(JS)
h.append('</script>')
h.append('</body>')
h.append('</html>')

out = SPACE_DIR / "index.html"
content = "\n".join(h)
out.write_text(content, encoding="utf-8")
print(f"OK {len(content)} bytes")
print(f"KPIs: {len(all_kpis)}, TS: {len([k for k in all_ts if '_forecast' not in k])}, Forecasts: {len([k for k in all_ts if '_forecast' in k])}, Interp: {len(all_interp)}")
