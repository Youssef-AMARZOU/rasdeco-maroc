"""Generate static HTML dashboard for HF Space."""
import json
from pathlib import Path

SPACE_DIR = Path(__file__).parent
DATA_FILE = SPACE_DIR / "data_summary.json"

LABELS = {
    "PIB": "PIB", "IPC": "IPC", "CHOMAGE": "Chomage", "BALANCE_COM": "Balance Commerciale",
    "TAUX_CHANGES": "Taux de Change", "TAUX_REMUNERATION": "Taux Remuneration",
    "CREDIT": "Credit Bancaire", "AGRI": "Agriculture", "INDUSTRIE": "Industrie",
    "TOURISME": "Tourisme", "ENERGIE": "Energie", "DEMOGRAPHIE": "Population",
    "TRANSFERTS": "Transferts", "DROITS": "Droits Douane", "RECETTES_FISC": "Recettes Fiscales",
    "DEPENSES_PUB": "Depenses Publiques", "RESSOURCES_NAT": "Ressources Nat",
    "PRIX_FUEL": "Prix Carburants", "PRIX_CEREALES": "Prix Cereales",
}

with open(DATA_FILE) as f:
    d = json.load(f)

ind_labels = [LABELS.get(k, k) for k in d["indicators"].keys()]
ind_values = list(d["indicators"].values())

src_labels = list(d["sources"].keys())
src_values = list(d["sources"].values())

colors = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6", "#ec4899"]
ts_traces = []
for i, (ind, vals) in enumerate(d["ts"].items()):
    lbl = LABELS.get(ind, ind)
    ts_traces.append({
        "x": vals["dates"],
        "y": vals["values"],
        "type": "scatter",
        "mode": "lines",
        "name": lbl,
        "line": {"color": colors[i % len(colors)]},
    })

total = f"{d['total']:,}"
n_ind = len(d["indicators"])
n_src = len(d["sources"])

html_parts = []
html_parts.append('<!DOCTYPE html>')
html_parts.append('<html lang="fr">')
html_parts.append('<head>')
html_parts.append('<meta charset="UTF-8">')
html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
html_parts.append('<title>Economie Maroc - RASD</title>')
html_parts.append('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>')
html_parts.append('<style>')
html_parts.append('*{margin:0;padding:0;box-sizing:border-box}')
html_parts.append("body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8fafc;color:#1e293b}")
html_parts.append('.header{background:linear-gradient(135deg,#1e3a5f,#2563eb);color:#fff;padding:2rem;text-align:center}')
html_parts.append('.header h1{font-size:1.8rem;margin-bottom:.5rem}')
html_parts.append('.header p{opacity:.85;font-size:.95rem}')
html_parts.append('.stats{display:flex;justify-content:center;gap:2rem;padding:1.5rem;flex-wrap:wrap}')
html_parts.append('.stat{background:#fff;border-radius:12px;padding:1.2rem 2rem;box-shadow:0 1px 3px rgba(0,0,0,.1);text-align:center}')
html_parts.append('.stat .num{font-size:2rem;font-weight:700;color:#2563eb}')
html_parts.append('.stat .lbl{font-size:.85rem;color:#64748b;margin-top:.3rem}')
html_parts.append('.charts{max-width:1200px;margin:0 auto;padding:1rem}')
html_parts.append('.chart{background:#fff;border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;box-shadow:0 1px 3px rgba(0,0,0,.1)}')
html_parts.append('.row{display:flex;gap:1.5rem;flex-wrap:wrap}')
html_parts.append('.row .chart{flex:1;min-width:300px}')
html_parts.append('.footer{text-align:center;padding:2rem;color:#94a3b8;font-size:.8rem}')
html_parts.append('</style>')
html_parts.append('</head>')
html_parts.append('<body>')
html_parts.append('<div class="header">')
html_parts.append('<h1>Economie Maroc - RASD</h1>')
html_parts.append('<p>Tableau de bord interactif | Donnees collectees automatiquement</p>')
html_parts.append('</div>')
html_parts.append('<div class="stats">')
html_parts.append(f'<div class="stat"><div class="num">{total}</div><div class="lbl">Observations</div></div>')
html_parts.append(f'<div class="stat"><div class="num">{n_ind}</div><div class="lbl">Indicateurs</div></div>')
html_parts.append(f'<div class="stat"><div class="num">{n_src}</div><div class="lbl">Sources</div></div>')
html_parts.append('</div>')
html_parts.append('<div class="charts">')
html_parts.append('<div class="chart"><div id="ts"></div></div>')
html_parts.append('<div class="row">')
html_parts.append('<div class="chart"><div id="ind"></div></div>')
html_parts.append('<div class="chart"><div id="src"></div></div>')
html_parts.append('</div>')
html_parts.append('</div>')
html_parts.append('<div class="footer">RASD-Maroc | Youssef Amarzou | Donnees: HCP, BKAM, Finances, Datagov.ma, OC</div>')
html_parts.append('<script>')
html_parts.append(f"Plotly.newPlot('ts',{json.dumps(ts_traces)},{{title:'Series Temporelles',height:420,template:'plotly_white',xaxis:{{title:'Date'}},yaxis:{{title:'Valeur'}}}});")
html_parts.append(f"Plotly.newPlot('ind',{json.dumps([{'x': ind_labels, 'y': ind_values, 'type': 'bar', 'marker': {'color': '#3b82f6'}}])},{{title:'Observations par Indicateur',height:380,template:'plotly_white',xaxis:{{tickangle:-45}}}});")
html_parts.append(f"Plotly.newPlot('src',{json.dumps([{'labels': src_labels, 'values': src_values, 'type': 'pie', 'hole': 0.4}])},{{title:'Repartition par Source',height:380,template:'plotly_white'}});")
html_parts.append('</script>')
html_parts.append('</body>')
html_parts.append('</html>')

html = "\n".join(html_parts)

out = SPACE_DIR / "index.html"
out.write_text(html, encoding="utf-8")
print(f"OK {len(html)} bytes -> {out}")
