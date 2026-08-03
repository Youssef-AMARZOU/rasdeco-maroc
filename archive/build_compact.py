"""Build compressed HF dashboard under 100KB."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

SPACE_DIR = Path(__file__).parent
df = pd.read_parquet(r'C:\Users\youss\OneDrive\Desktop\Yoyo\prediction maroc\data\export\economie_maroc.parquet')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

ALL = {
    'PIB.TRIM.VOL': ('PIB', 'MAD'),
    'IPC.INDICE': ('IPC', 'Indice'),
    'EMPLOI.VOLUME': ('Emploi', '%'),
    'BAM.OPCVM.ENCOURS': ('OPCVM', 'MAD'),
    'DETTE.PUBLIQUE': ('Dette', '%PIB'),
    'INVESTISSEMENT.PUBLIC': ('Invest.', 'MAD'),
    'DEFICIT.BUDGET': ('Deficit', '%PIB'),
    'INDICATEUR.HCP.GENERIQUE': ('HCP', '%'),
    'CHANGE.USD': ('Change', 'MAD/USD'),
    'EXPORTATIONS': ('Export', 'MAD'),
    'PIB.ANNUEL.VOL': ('PIB Ann.', 'MAD'),
}
COLORS = ['#3b82f6','#ef4444','#22c55e','#f59e0b','#8b5cf6','#ec4899','#06b6d4','#84cc16','#f97316','#6366f1','#14b8a6']

# ---- Extract data (compact) ----
ts_data = {}
kpis = {}
interp_data = {}

for i, (code, (short, unit)) in enumerate(ALL.items()):
    sub = df[df['code_indicateur'] == code].dropna(subset=['date', 'valeur']).sort_values('date')
    if len(sub) < 3:
        continue

    color = COLORS[i % len(COLORS)]
    vals = sub['valeur'].values.astype(float)

    # Sample to max 150 points
    step = max(1, len(sub) // 150)
    sampled = sub.iloc[::step]

    ts_data[code] = [
        sampled['date'].dt.strftime('%Y-%m-%d').tolist(),
        [round(float(v), 2) for v in sampled['valeur'].tolist()],
        short, color, unit
    ]

    # Forecast
    if len(vals) >= 10:
        trend = float(np.mean(np.diff(vals[-10:])))
    else:
        trend = float(np.mean(np.diff(vals[-3:])))
    last = float(vals[-1])
    fc = [round(last + trend * (j + 1), 2) for j in range(12)]

    # KPI
    latest = float(vals[-1])
    prev = float(vals[-2])
    ch = round((latest - prev) / (abs(prev) + 1e-9) * 100, 1)
    avg = float(np.mean(vals))
    std = float(np.std(vals))

    # Trend test
    x = np.arange(len(vals))
    slope, _, r_val, p_val, _ = stats.linregress(x, vals)
    trend_dir = 'H' if slope > 0 and p_val < 0.05 else ('B' if slope < 0 and p_val < 0.05 else 'S')

    kpis[code] = [round(latest, 2), ch, unit, short, round(avg, 2), round(std, 2),
                   trend_dir, round(float(r_val**2), 3), len(sub)]

    # Interpretation (compact strings)
    interp_parts = []
    interp_parts.append(f"{short}: {len(sub)} pts ({sub['date'].min().strftime('%Y-%m')} a {sub['date'].max().strftime('%Y-%m')})")
    interp_parts.append(f"Valeur: {latest:,.2f} {unit} | Moy: {avg:,.2f} | Std: {std:,.2f}")
    if ch != 0:
        interp_parts.append(f"Variation: {ch:+.1f}% ({'hausse' if ch > 0 else 'baisse'})")
    interp_parts.append(f"Tendance: {'haussiere' if trend_dir == 'H' else 'baisissiere' if trend_dir == 'B' else 'stable'} (R2={r_val**2:.3f})")
    interp_parts.append(f"Prevision M+1: {fc[0]:,.2f} | M+6: {fc[5]:,.2f} | M+12: {fc[-1]:,.2f}")
    interp_data[code] = interp_parts

sources = df['source_code'].value_counts().to_dict()
total = len(df)
dmin = df['date'].dropna().min().strftime('%Y-%m-%d')
dmax = df['date'].dropna().max().strftime('%Y-%m-%d')

# ---- Build HTML (compact) ----
h = []
h.append('<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
h.append('<title>RASD-Maroc</title>')
h.append('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>')
h.append('<style>')
h.append('*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,sans-serif;background:#f0f4f8;color:#1e293b}')
h.append('.hd{background:linear-gradient(135deg,#0f172a,#3b82f6);color:#fff;padding:2rem;text-align:center}')
h.append('.hd h1{font-size:1.8rem;font-weight:800}.hd p{opacity:.8;margin-top:.4rem}')
h.append('.ct{max-width:1200px;margin:0 auto;padding:1rem}')
h.append('.st{font-size:1.1rem;font-weight:700;margin:1.2rem 0 .8rem;border-left:4px solid #3b82f6;padding-left:.6rem}')
h.append('.ctrl{background:#fff;border-radius:12px;padding:1rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08);display:flex;gap:.8rem;flex-wrap:wrap;align-items:end}')
h.append('.ctrl label{font-size:.78rem;color:#64748b;font-weight:600;display:block;margin-bottom:.2rem}')
h.append('.ctrl select{padding:.4rem .6rem;border:1px solid #e2e8f0;border-radius:6px;font-size:.85rem}')
h.append('.kg{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:.8rem;margin-bottom:1rem}')
h.append('.kc{background:#fff;border-radius:12px;padding:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08);border-top:3px solid var(--a);cursor:pointer;transition:.15s}')
h.append('.kc:hover,.kc.on{transform:translateY(-2px);box-shadow:0 3px 10px rgba(0,0,0,.1)}')
h.append('.kl{font-size:.72rem;color:#64748b;text-transform:uppercase;font-weight:600}')
h.append('.kv{font-size:1.5rem;font-weight:800;margin:.2rem 0}')
h.append('.kc div:nth-child(3){font-size:.78rem;font-weight:600}.kc div:nth-child(4){font-size:.68rem;color:#94a3b8;margin-top:.2rem}')
h.append('.up{color:#16a34a}.dn{color:#dc2626}.fl{color:#94a3b8}')
h.append('.cb{background:#fff;border-radius:12px;padding:1.2rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}')
h.append('.ib{background:#fff;border-radius:12px;padding:1.2rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}')
h.append('.ii{padding:.6rem 0;border-bottom:1px solid #f1f5f9;font-size:.85rem;line-height:1.6}.ii:last-child{border-bottom:none}.ii b{color:#1e40af}')
h.append('.ft{text-align:center;padding:1.5rem;color:#94a3b8;font-size:.75rem;border-top:1px solid #e2e8f0;margin-top:1.5rem}')
h.append('.chat{height:250px;overflow-y:auto;padding:.8rem;background:#f8fafc;border-radius:8px;margin-bottom:.8rem;font-size:.85rem}')
h.append('.chI{padding:.5rem .7rem;margin:.3rem 0;border-radius:8px;max-width:85%;font-size:.85rem;line-height:1.5}')
h.append('.chU{background:#3b82f6;color:#fff;margin-left:auto;text-align:right}.chB{background:#fff;border:1px solid #e2e8f0}')
h.append('.chE{display:flex;gap:.4rem;flex-wrap:wrap;margin-top:.6rem}')
h.append('.chE button{padding:.25rem .6rem;background:#e2e8f0;border:none;border-radius:5px;cursor:pointer;font-size:.75rem}')
h.append('@media(max-width:640px){.hd h1{font-size:1.3rem}.kv{font-size:1.2rem}.ctrl{flex-direction:column}}')
h.append('</style></head><body>')

# Header
h.append(f'<div class="hd"><h1>Economie Maroc - RASD</h1><p>{total:,} observations | {dmin} a {dmax} | 5 sources</p></div>')
h.append('<div class="ct">')

# Controls
h.append('<div class="ctrl"><div><label>Indicateur</label><select id="si">')
for code in kpis:
    h.append(f'<option value="{code}">{kpis[code][3]}</option>')
h.append('</select></div><div><label>Periode</label><select id="sp"><option value="all">Tout</option><option value="10">10a</option><option value="5" selected>5a</option><option value="3">3a</option><option value="1">1a</option></select></div>')
h.append('<div><label>Previsions</label><select id="sf"><option value="1">Oui</option><option value="0">Non</option></select></div></div>')

# KPIs
h.append('<div class="st">Indicateurs Cles</div><div class="kg" id="kg">')
for code, k in kpis.items():
    v, ch, unit, short, avg, std, td, r2, n = k
    cls = 'up' if ch > 0 else ('dn' if ch < 0 else 'fl')
    vs = f"{v:,.0f}" if abs(v) > 10000 else f"{v:,.2f}"
    h.append(f'<div class="kc" data-c="{code}" style="--a:{COLORS[list(kpis.keys()).index(code) % len(COLORS)]}" onclick="sel(\'{code}\')"><div class="kl">{short}</div><div class="kv" style="color:{COLORS[list(kpis.keys()).index(code) % len(COLORS)]}">{vs}</div><div class="{cls}">{ch:+.1f}%</div><div>{unit} | {n} pts | R2={r2}</div></div>')
h.append('</div>')

# Charts
h.append('<div class="st">Evolution et Previsions</div><div class="cb"><div id="mc" style="height:450px"></div></div>')
h.append('<div class="st">Sources</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem"><div class="cb"><div id="sp1" style="height:320px"></div></div><div class="cb"><div id="sp2" style="height:320px"></div></div></div>')

# Interpretation
h.append('<div class="st">Analyse et Interpretation</div><div class="ib" id="ib"></div>')

# Agent
h.append('<div class="st">Agent IA</div><div class="cb"><div class="chat" id="chat"></div>')
h.append('<div style="display:flex;gap:.4rem"><input id="ai" type="text" placeholder="PIB, inflation, emploi, dette, resume..." style="flex:1;padding:.5rem .8rem;border:1px solid #e2e8f0;border-radius:6px;font-size:.85rem" onkeydown="if(event.key===\'Enter\')send()"><button onclick="send()" style="padding:.5rem 1rem;background:#3b82f6;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:600">OK</button></div>')
h.append('<div class="chE" id="chE"></div></div>')

h.append('</div>')
h.append(f'<div class="ft">RASD-Maroc | Youssef Amarzou | HCP, BKAM, Finances, Datagov.ma, OC | Agent IA integre</div>')

# JS
h.append('<script>')
h.append(f'var T={json.dumps(ts_data)};')
h.append(f'var K={json.dumps(kpis)};')
h.append(f'var I={json.dumps(interp_data)};')
h.append(f'var SL={json.dumps(list(sources.keys()))};')
h.append(f'var SV={json.dumps(list(sources.values()))};')
h.append(f'var C={json.dumps(COLORS)};')

JS = """function sel(c){document.getElementById('si').value=c;upd()}
function fp(d,v,p){if(p==='all')return{d:d,v:v};var co=new Date();co.setFullYear(co.getFullYear()-parseInt(p));var fd=[],fv=[];for(var i=0;i<d.length;i++)if(new Date(d[i])>=co){fd.push(d[i]);fv.push(v[i])}return{d:fd,v:fv}}
function upd(){
var c=document.getElementById('si').value,p=document.getElementById('sp').value,sf=document.getElementById('sf').value==='1';
var t=T[c],k=K[c],it=I[c];if(!t)return;
var f=fp(t[0],t[1],p);
var tr=[{x:f.d,y:f.v,type:'scatter',mode:'lines',name:t[2],line:{color:t[3],width:2.5}}];
if(sf){var n=t[1].length,step=Math.max(1,Math.floor(n/20)),last=t[1][n-1],prev=t[1][Math.max(0,n-10)];
var trend=(last-(prev||0))/Math.max(1,n-10);
var fd=[],fv=[],fu=[],fl=[];
for(var j=1;j<=12;j++){var dt=new Date(t[0][n-1]);dt.setMonth(dt.getMonth()+j);fd.push(dt.toISOString().slice(0,10));
var v=last+trend*j;fv.push(v);fu.push(v*(1+.02*j));fl.push(v*(1-.02*j))}
tr.push({x:fd,y:fv,type:'scatter',mode:'lines+markers',name:'Prevision',line:{color:t[3],width:2,dash:'dash'},marker:{size:5}});
tr.push({x:fd.concat(fd.slice().reverse()),y:fu.concat(fl.slice().reverse()),fill:'toself',fillcolor:t[3]+'20',line:{color:'transparent'},name:'IC 80%'})}
Plotly.newPlot('mc',tr,{title:{text:t[2],font:{size:15}},height:450,template:'plotly_white',xaxis:{title:'Date',rangeslider:{visible:true}},yaxis:{title:k[2]},legend:{orientation:'h',y:-.25},hovermode:'x unified'});
var box=document.getElementById('ib');box.innerHTML=it.map(function(l){return'<div class="ii">'+l+'</div>'}).join('');
document.querySelectorAll('.kc').forEach(function(e){e.classList.toggle('on',e.getAttribute('data-c')===c)})}
Plotly.newPlot('sp1',[{labels:SL,values:SV,type:'pie',hole:.4,textinfo:'label+percent'}],{title:'Repartition',height:320,template:'plotly_white'});
Plotly.newPlot('sp2',[{x:SL,y:SV,type:'bar',marker:{color:C.slice(0,5)}}],{title:'Volume',height:320,template:'plotly_white',xaxis:{tickangle:-30}});
document.getElementById('si').addEventListener('change',upd);
document.getElementById('sp').addEventListener('change',upd);
document.getElementById('sf').addEventListener('change',upd);
upd();

// Agent
function aR(m){
var ml=m.toLowerCase();
var mapi={'pib':'PIB.TRIM.VOL','croissance':'PIB.TRIM.VOL','ipc':'IPC.INDICE','inflation':'IPC.INDICE','prix':'IPC.INDICE','emploi':'EMPLOI.VOLUME','chomage':'EMPLOI.VOLUME','opcvm':'BAM.OPCVM.ENCOURS','dette':'DETTE.PUBLIQUE','budget':'DEFICIT.BUDGET','deficit':'DEFICIT.BUDGET','invest':'INVESTISSEMENT.PUBLIC','change':'CHANGE.USD','dollar':'CHANGE.USD','export':'EXPORTATIONS'};
for(var kw in mapi){if(ml.includes(kw)){var c=mapi[kw],k=K[c],it=I[c];if(!k)continue;
return'<b>'+k[3]+'</b> ('+k[2]+'): '+k[0].toLocaleString()+' | Var: '+(k[1]>0?'+':'')+k[1]+'% | Moy: '+k[4].toLocaleString()+'<br>'+it.join('<br>')}}
if(ml.includes('resume')||ml.includes('sommaire'))return'<b>Synthese</b><br>'+Object.values(K).reduce(function(s,k){return s+k[8]},0).toLocaleString()+' observations | '+Object.keys(K).length+' indicateurs | 5 sources<br>Periode: '+['PIB','IPC','Emploi','Dette','Invest','OPCVM','Change','Export'].join(', ');
if(ml.includes('source'))return'<b>Sources</b><br>'+SL.map(function(l,i){return l+': '+SV[i].toLocaleString()}).join('<br>');
if(ml.includes('bonjour')||ml.includes('aide')||ml.includes('help'))return'Bienvenue! Essayez: <b>PIB</b>, <b>inflation</b>, <b>emploi</b>, <b>dette</b>, <b>resume</b>, <b>sources</b>';
return'Essayez: <b>PIB</b>, <b>inflation</b>, <b>emploi</b>, <b>dette</b>, <b>resume</b>, <b>sources</b>'}
function aM(t,u){var d=document.createElement('div');d.className='chI '+(u?'chU':'chB');d.innerHTML=t;document.getElementById('chat').appendChild(d);document.getElementById('chat').scrollTop=99999}
function send(){var i=document.getElementById('ai'),m=i.value.trim();if(!m)return;aM(m,1);i.value='';setTimeout(function(){aM(aR(m),0)},100)}
function ex(t){document.getElementById('ai').value=t;send()}
// Examples
['Resume','PIB','inflation','emploi','dette','sources'].forEach(function(e){var b=document.createElement('button');b.textContent=e;b.onclick=function(){ex(e)};document.getElementById('chE').appendChild(b)});
aM('Posez des questions sur l economie marocaine!',0);
"""
h.append(JS)
h.append('</script></body></html>')

out = SPACE_DIR / "index.html"
content = "\n".join(h)
out.write_text(content, encoding="utf-8")
print(f"OK {len(content)} bytes ({len(content)/1024:.1f} KB)")
