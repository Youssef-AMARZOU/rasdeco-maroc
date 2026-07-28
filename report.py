"""
generate_report.py — Génère un rapport HTML statique avec toutes les visualisations RASD-Maroc.

Usage : python report.py
Ouvre ensuite report_rasd_maroc.html dans le navigateur.
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import plotly.express as px
import plotly.graph_objects as go

OUT = Path("report_rasd_maroc.html")
GEOJSON_PATH = Path("dashboard/assets/regions_maroc.geojson")
GEOJSON: dict = {}
if GEOJSON_PATH.exists():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        GEOJSON = json.load(f)

REGIONS = {
    "MA01": "Tanger-Tetouan-Al Hoceima", "MA02": "Oriental", "MA03": "Fes-Meknes",
    "MA04": "Rabat-Sale-Kenitra", "MA05": "Beni Mellal-Khenifra", "MA06": "Casablanca-Settat",
    "MA07": "Marrakech-Safi", "MA08": "Draa-Tafilalet", "MA09": "Souss-Massa",
    "MA10": "Guelmim-Oued Noun", "MA11": "Laayoune-Sakia El Hamra", "MA12": "Dakhla-Oued Ed-Dahab",
}

PARQUET_FILES = {
    "Agriculture": "agriculture/data/output/agriculture_complet.parquet",
    "Social": "social/data/output/social_complet.parquet",
    "Education": "education/data/output/education_complet.parquet",
    "Sante": "sante/data/output/sante_complet.parquet",
    "Sport": "sport/data/output/sport_complet.parquet",
}

def _carte(df: pl.DataFrame, titre: str) -> str:
    """Choroplethe 12 regions."""
    if df.is_empty() or "region" not in df.columns:
        return "<p>Aucune donnee regionale</p>"
    region_nom = df["region"].unique().to_list()
    fig = go.Figure()
    dfp = df.filter(pl.col("level") == "region")
    if dfp.is_empty():
        return "<p>Pas de niveau regional</p>"
    latest = dfp.sort("year", descending=True).unique(subset=["region"], keep="first")
    fig = px.choropleth(
        latest.to_pandas(), geojson=GEOJSON,
        locations="region", featureidkey="properties.name",
        color="value", color_continuous_scale="YlOrRd",
        title=titre, labels={"value": "Valeur"},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=450)
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

def _serie(df: pl.DataFrame, titre: str) -> str:
    """Courbe temporelle nationale."""
    if df.is_empty() or "year" not in df.columns:
        return "<p>Aucune donnee temporelle</p>"
    national = df.filter(pl.col("level") == "national")
    if national.is_empty():
        nat = df.group_by("year").agg(pl.mean("value").alias("valeur")).sort("year")
    else:
        nat = national.group_by("year").agg(pl.mean("value").alias("valeur")).sort("year")
    if nat.is_empty():
        return "<p>Pas de serie nationale</p>"
    fig = px.line(nat.to_pandas(), x="year", y="valeur", title=titre)
    fig.update_layout(hovermode="x unified", height=350, margin=dict(l=50, r=20, t=40, b=30))
    return fig.to_html(include_plotlyjs="cdn", full_html=False)

def _top_kpi(df: pl.DataFrame, nom: str) -> str:
    """Extrait un KPI cle."""
    if df.is_empty() or "value" not in df.columns:
        return f"<tr><td>{nom}</td><td>—</td><td>—</td></tr>"
    nat = df.filter(pl.col("level") == "national")
    if nat.is_empty():
        nat = df
    moyenne = nat.select(pl.mean("value")).item()
    max_v = nat.select(pl.max("value")).item()
    return f"<tr><td>{nom}</td><td>{moyenne:.1f}</td><td>{max_v:.1f}</td></tr>"

def _render_module(nom: str, path: str) -> str:
    df = pl.read_parquet(path)
    n = len(df)
    indics = df.select(pl.n_unique("indicator_code")).item()
    regions = df.select(pl.n_unique("region")).item() if "region" in df.columns else 0
    years = df.select(pl.n_unique("year")).item() if "year" in df.columns else 0
    carte = _carte(df, f"{nom} — Carte regionale")
    serie = _serie(df, f"{nom} — Evolution temporelle")
    kpi = _top_kpi(df, nom)
    return f"""
    <div class="module" id="{nom.lower()}">
      <h2>{nom} <span class="badge">{n:,} lignes</span></h2>
      <p>{indics} indicateurs · {regions} régions · {years} années</p>
      <div class="grid-2">
        <div>{carte}</div>
        <div>{serie}</div>
      </div>
      <table class="kpi-table">
        <tr><th>Module</th><th>Moyenne</th><th>Maximum</th></tr>
        {kpi}
      </table>
    </div>
    <hr>
    """

def build():
    sections = ""
    for nom, path in PARQUET_FILES.items():
        p = Path(path)
        if p.exists():
            sections += _render_module(nom, path)
        else:
            sections += f"<h2>{nom}</h2><p class='warn'>Fichier non trouve : {path}</p><hr>"

    # Stats globales
    total_rows = sum(pl.read_parquet(p).select(pl.len()).item() for p in PARQUET_FILES.values() if Path(p).exists())

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><title>RASD-Maroc — Rapport</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font: 14px/1.5 'Segoe UI',sans-serif; color:#333; background:#f8f9fa; }}
  .header {{ background:linear-gradient(135deg,#1a1a2e,#16213e); color:#fff; padding:2em; text-align:center; }}
  .header h1 {{ font-size:1.8em; }}
  .header p {{ color:#aaa; margin-top:.5em; }}
  .badge {{ display:inline-block; background:#e67e22; color:#fff; padding:2px 10px; border-radius:12px; font-size:.7em; vertical-align:middle; }}
  .container {{ max-width:1200px; margin:auto; padding:1em; }}
  .module {{ background:#fff; border-radius:8px; padding:1.5em; margin:1em 0; box-shadow:0 1px 3px rgba(0,0,0,.1); }}
  .module h2 {{ color:#1a1a2e; margin-bottom:.5em; }}
  .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:1em; }}
  .kpi-table {{ width:100%; border-collapse:collapse; margin-top:1em; }}
  .kpi-table th,.kpi-table td {{ border:1px solid #dee2e6; padding:8px 12px; text-align:left; }}
  .kpi-table th {{ background:#1a1a2e; color:#fff; }}
  .warn {{ color:#e74c3c; font-weight:bold; }}
  .nav {{ position:sticky; top:0; background:#fff; padding:.5em 1em; border-bottom:2px solid #1a1a2e; z-index:100; }}
  .nav a {{ color:#1a1a2e; text-decoration:none; margin:0 1em; font-weight:bold; }}
  .nav a:hover {{ color:#e67e22; }}
  @media (max-width:800px) {{ .grid-2 {{ grid-template-columns:1fr; }} }}
</style></head>
<body>
<div class="header">
  <h1>RASD-Maroc · Rapport multi-module</h1>
  <p>{total_rows:,} lignes de donnees · {len(PARQUET_FILES)} modules</p>
</div>
<div class="nav">
  <a href="#agriculture">Agriculture</a>
  <a href="#social">Social</a>
  <a href="#education">Education</a>
  <a href="#sante">Sante</a>
  <a href="#sport">Sport</a>
</div>
<div class="container">
  <p style="margin:1em 0;color:#666;">
    Rapport genere le <strong>{__import__('datetime').datetime.now().strftime('%d/%m/%Y a %H:%M')}</strong>
    a partir des fichiers Parquet locaux.
  </p>
  {sections}
</div>
<script>
  document.querySelectorAll('.module h2').forEach(h => {{
    h.style.cursor = 'pointer';
    h.addEventListener('click', () => {{
      let div = h.closest('.module').querySelector('.grid-2, .kpi-table');
      if(div) div.style.display = div.style.display === 'none' ? '' : 'none';
    }});
  }});
</script>
</body></html>"""

    OUT.write_text(html, encoding="utf-8")
    print(f"Rapport genere : {OUT.resolve()} ({OUT.stat().st_size/1024:.0f} Ko)")
    print("Ouvre-le dans ton navigateur pour voir les KPIs.")

if __name__ == "__main__":
    build()
