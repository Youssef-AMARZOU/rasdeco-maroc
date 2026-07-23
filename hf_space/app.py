"""Dashboard Economie Maroc - RASD"""
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

INDICATOR_LABELS = {
    "PIB": "Produit Interieur Brut",
    "IPC": "Indice des Prix a la Consommation",
    "CHOMAGE": "Taux de Chomage",
    "BALANCE_COM": "Balance Commerciale",
    "TAUX_CHANGES": "Taux de Change",
    "TAUX_REMUNERATION": "Taux de Remuneration",
    "CREDIT": "Credit Bancaire",
    "AGRI": "Production Agricole",
    "INDUSTRIE": "Production Industrielle",
    "TOURISME": "Arrivees Touristiques",
    "ENERGIE": "Consommation Energetique",
    "DEMOGRAPHIE": "Population",
    "TRANSFERTS": "Transferts Migratoires",
    "DROITS": "Droits de Douane",
    "RECETTES_FISC": "Recettes Fiscales",
    "DEPENSES_PUB": "Depenses Publiques",
    "RESSOURCES_NAT": "Ressources Naturelles",
    "PRIX_FUEL": "Prix des Carburants",
    "PRIX_CEREALES": "Prix des Cereales",
}

REGION_NAMES = {
    "MA01": "Tanger-Tetouan-Al Hoceima",
    "MA02": "Oriental",
    "MA03": "Fes-Meknes",
    "MA04": "Rabat-Sale-Kenitra",
    "MA05": "Beni Mellal-Khenifra",
    "MA06": "Casablanca-Settat",
    "MA07": "Marrakech-Safi",
    "MA08": "Draa-Tafilalet",
    "MA09": "Souss-Massa",
    "MA10": "Guelmim-Oued Noun",
    "MA11": "Laayoune-Sakia El Hamra",
    "MA12": "Dakhla-Oued Ed-Dahab",
}


def load_data():
    frames = []
    for f in sorted(DATA_DIR.glob("*.parquet")):
        try:
            frames.append(pd.read_parquet(f))
        except Exception:
            pass
    if not frames:
        for f in sorted(DATA_DIR.glob("*.csv")):
            try:
                frames.append(pd.read_csv(f))
            except Exception:
                pass
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "code_indicateur" in df.columns:
        df["label"] = df["code_indicateur"].map(INDICATOR_LABELS).fillna(df["code_indicateur"])
    if "code_region" in df.columns:
        df["region"] = df["code_region"].map(REGION_NAMES).fillna(df["code_region"])
    return df


DF = load_data()

INDICATORS = sorted(DF["label"].unique().tolist()) if "label" in DF.columns else []
SOURCES = sorted(DF["source"].unique().tolist()) if "source" in DF.columns else []


def plot_indicator_timeseries(indicator, source):
    d = DF.copy()
    if indicator != "Tous":
        d = d[d["label"] == indicator]
    if source != "Toutes":
        d = d[d["source"] == source]
    d = d.dropna(subset=["date", "valeur"])
    d = d.sort_values("date")
    if d.empty:
        return go.Figure().update_layout(title="Aucune donnee")
    if "version_serie" in d.columns:
        fig = px.line(d, x="date", y="valeur", color="version_serie",
                       title=f"{indicator} - {source}",
                       labels={"valeur": "Valeur", "date": "Date"})
    else:
        fig = px.line(d, x="date", y="valeur",
                       title=f"{indicator} - {source}",
                       labels={"valeur": "Valeur", "date": "Date"})
    fig.update_layout(template="plotly_white", height=500)
    return fig


def plot_region_map(indicator):
    d = DF.copy()
    if indicator != "Tous":
        d = d[d["label"] == indicator]
    if "region" not in d.columns or d["region"].isna().all():
        return go.Figure().update_layout(title="Pas de donnees regionales")
    d = d.dropna(subset=["region", "valeur"])
    latest = d.sort_values("date").groupby("region").last().reset_index()
    fig = px.bar(latest, x="region", y="valeur", color="valeur",
                  title=f"Derniere valeur par region - {indicator}",
                  labels={"valeur": "Valeur", "region": "Region"})
    fig.update_layout(template="plotly_white", height=500, xaxis_tickangle=-45)
    return fig


def plot_distribution(indicator):
    d = DF.copy()
    if indicator != "Tous":
        d = d[d["label"] == indicator]
    d = d.dropna(subset=["valeur"])
    if d.empty:
        return go.Figure().update_layout(title="Aucune donnee")
    fig = px.histogram(d, x="valeur", nbins=50,
                        title=f"Distribution - {indicator}",
                        labels={"valeur": "Valeur"})
    fig.update_layout(template="plotly_white", height=400)
    return fig


def plot_source_pie():
    if "source" not in DF.columns:
        return go.Figure()
    counts = DF["source"].value_counts().reset_index()
    counts.columns = ["source", "lignes"]
    fig = px.pie(counts, names="source", values="lignes",
                  title="Repartition des donnees par source")
    fig.update_layout(template="plotly_white", height=400)
    return fig


def stats_summary(indicator):
    d = DF.copy()
    if indicator != "Tous":
        d = d[d["label"] == indicator]
    d = d.dropna(subset=["valeur"])
    if d.empty:
        return "Aucune donnee"
    n = len(d)
    n_sources = d["source"].nunique() if "source" in d.columns else 0
    n_regions = d["region"].nunique() if "region" in d.columns else 0
    date_min = d["date"].min().strftime("%Y-%m-%d") if "date" in d.columns else "N/A"
    date_max = d["date"].max().strftime("%Y-%m-%d") if "date" in d.columns else "N/A"
    return (
        f"**{indicator}**\n\n"
        f"- {n:,} observations\n"
        f"- {n_sources} sources\n"
        f"- {n_regions} regions\n"
        f"- Periode: {date_min} a {date_max}\n"
        f"- Min: {d['valeur'].min():,.2f}\n"
        f"- Max: {d['valeur'].max():,.2f}\n"
        f"- Median: {d['valeur'].median():,.2f}"
    )


with gr.Blocks(title="Economie Maroc - RASD", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Dashboard Economie Maroc - RASD")
    gr.Markdown(f"**{len(DF):,} observations** | **{len(INDICATORS)} indicateurs** | **{len(SOURCES)} sources**")

    with gr.Tabs():
        with gr.Tab("Series Temporelles"):
            with gr.Row():
                ind1 = gr.Dropdown(choices=["Tous"] + INDICATORS, value="Tous", label="Indicateur")
                src1 = gr.Dropdown(choices=["Toutes"] + SOURCES, value="Toutes", label="Source")
            plot1 = gr.Plot()
            btn1 = gr.Button("Afficher")
            btn1.click(plot_indicator_timeseries, [ind1, src1], plot1)

        with gr.Tab("Regions"):
            ind2 = gr.Dropdown(choices=["Tous"] + INDICATORS, value="Tous", label="Indicateur")
            plot2 = gr.Plot()
            btn2 = gr.Button("Afficher")
            btn2.click(plot_region_map, [ind2], plot2)

        with gr.Tab("Distribution"):
            ind3 = gr.Dropdown(choices=["Tous"] + INDICATORS, value="Tous", label="Indicateur")
            plot3 = gr.Plot()
            btn3 = gr.Button("Afficher")
            btn3.click(plot_distribution, [ind3], plot3)

        with gr.Tab("Sources"):
            plot4 = gr.Plot(value=plot_source_pie())

        with gr.Tab("Statistiques"):
            ind5 = gr.Dropdown(choices=["Tous"] + INDICATORS, value="Tous", label="Indicateur")
            stats = gr.Markdown()
            btn5 = gr.Button("Calculer")
            btn5.click(stats_summary, [ind5], stats)

if __name__ == "__main__":
    demo.launch()
