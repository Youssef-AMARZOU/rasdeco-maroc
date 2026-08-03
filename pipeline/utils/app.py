"""Economie Maroc - RASD | Dashboard interactif + Agent IA"""
import json
import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# ---- Load data ----
DATA_DIR = Path(__file__).parent / "data"
PARQUET = DATA_DIR / "economie_maroc.parquet"

if PARQUET.exists():
    DF = pd.read_parquet(str(PARQUET))
else:
    DF = pd.DataFrame()

DF["date"] = pd.to_datetime(DF.get("date", []), errors="coerce")

LABELS = {
    "PIB.TRIM.VOL": "PIB (Vol. Rectifie)",
    "IPC.INDICE": "IPC (Indice)",
    "EMPLOI.VOLUME": "Taux d'Emploi",
    "BAM.OPCVM.ENCOURS": "OPCVM (Encours)",
    "DETTE.PUBLIQUE": "Dette Publique",
    "INVESTISSEMENT.PUBLIC": "Investissement Public",
    "DEFICIT.BUDGET": "Deficit Budget",
    "INDICATEUR.HCP.GENERIQUE": "Indicateur HCP",
    "CHANGE.USD": "Taux de Change USD",
    "EXPORTATIONS": "Exportations",
    "PIB.ANNUEL.VOL": "PIB Annuel",
}

UNIT_MAP = {
    "PIB.TRIM.VOL": "MAD",
    "IPC.INDICE": "Indice",
    "EMPLOI.VOLUME": "%",
    "BAM.OPCVM.ENCOURS": "MAD",
    "DETTE.PUBLIQUE": "% PIB",
    "INVESTISSEMENT.PUBLIC": "MAD",
    "DEFICIT.BUDGET": "% PIB",
    "INDICATEUR.HCP.GENERIQUE": "%",
    "CHANGE.USD": "MAD/USD",
    "EXPORTATIONS": "MAD",
    "PIB.ANNUEL.VOL": "MAD",
}


def get_indicator_data(code):
    sub = DF[DF["code_indicateur"] == code].dropna(subset=["date", "valeur"]).sort_values("date")
    return sub


def naive_forecast(vals, horizon=12):
    arr = vals.values.astype(float)
    if len(arr) < 3:
        return [], [], []
    if len(arr) >= 10:
        trend = np.mean(np.diff(arr[-10:]))
    else:
        trend = np.mean(np.diff(arr[-3:]))
    last = arr[-1]
    fc = [round(float(last + trend * (i + 1)), 4) for i in range(horizon)]
    upper = [round(v * (1 + 0.02 * (i + 1)), 4) for i, v in enumerate(fc)]
    lower = [round(v * (1 - 0.02 * (i + 1)), 4) for i, v in enumerate(fc)]
    return fc, upper, lower


def make_timeseries_plot(code, period="all", show_forecast=True):
    sub = get_indicator_data(code)
    if sub.empty:
        return go.Figure().update_layout(title="Aucune donnee")

    if period != "all":
        cutoff = sub["date"].max() - pd.DateOffset(years=int(period))
        sub = sub[sub["date"] >= cutoff]

    label = LABELS.get(code, code)
    unit = UNIT_MAP.get(code, "")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=sub["date"], y=sub["valeur"], mode="lines", name=label,
                   line=dict(color="#3b82f6", width=2.5)),
        secondary_y=False,
    )

    if show_forecast:
        fc, upper, lower = naive_forecast(sub["valeur"])
        if fc:
            last_date = sub["date"].max()
            fc_dates = [last_date + pd.DateOffset(months=i + 1) for i in range(len(fc))]
            fig.add_trace(
                go.Scatter(x=fc_dates, y=fc, mode="lines+markers", name="Prevision",
                           line=dict(color="#ef4444", width=2, dash="dash"), marker=dict(size=6)),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=fc_dates + fc_dates[::-1], y=upper + lower[::-1],
                           fill="toself", fillcolor="rgba(239,68,68,0.1)",
                           line=dict(color="transparent"), name="IC 80%"),
                secondary_y=False,
            )

    fig.update_layout(title=f"{label} - Previsions", height=450, template="plotly_white",
                      xaxis_title="Date", legend=dict(orientation="h", y=-0.2), hovermode="x unified")
    fig.update_yaxes(title_text=unit, secondary_y=False)
    return fig


def make_all_indicators_plot():
    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, code in enumerate(LABELS):
        sub = get_indicator_data(code)
        if sub.empty or len(sub) < 5:
            continue
        vals = sub["valeur"].values.astype(float)
        norm = (vals - vals.mean()) / (vals.std() + 1e-9)
        fig.add_trace(go.Scatter(x=sub["date"], y=norm, mode="lines",
                                  name=LABELS.get(code, code), line=dict(width=1.5)))
    fig.update_layout(title="Tous les indicateurs (normalises)", height=400,
                      template="plotly_white", legend=dict(orientation="h", y=-0.15))
    return fig


def make_sources_plot():
    counts = DF["source_code"].value_counts()
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "bar"}]])
    fig.add_trace(go.Pie(labels=counts.index.tolist(), values=counts.values.tolist(),
                          hole=0.4, textinfo="label+percent"), row=1, col=1)
    fig.add_trace(go.Bar(x=counts.index.tolist(), y=counts.values.tolist(),
                          marker_color=["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"]),
                  row=1, col=2)
    fig.update_layout(title="Sources de Donnees", height=380, template="plotly_white", showlegend=False)
    return fig


def make_correlation_plot():
    pivot_data = {}
    for code in ["PIB.TRIM.VOL", "IPC.INDICE", "EMPLOI.VOLUME", "BAM.OPCVM.ENCOURS", "DETTE.PUBLIQUE"]:
        sub = get_indicator_data(code)
        if len(sub) < 5:
            continue
        sub = sub.set_index("date")["valeur"].resample("Y").mean()
        pivot_data[LABELS.get(code, code)] = sub
    if not pivot_data:
        return go.Figure().update_layout(title="Pas assez de donnees")
    corr_df = pd.DataFrame(pivot_data).corr()
    fig = px.imshow(corr_df, text_auto=".2f", color_continuous_scale="RdBu_r",
                     zmin=-1, zmax=1, title="Correlations entre indicateurs")
    fig.update_layout(height=400, template="plotly_white")
    return fig


# ---- Agent IA ----
AGENT_SYSTEM = """Tu es un assistant expert en economie marocaine. Tu analyses les donnees du RASD (Ressemble de Donnees Economiques du Maroc).
Sources: HCP (Haut-Commissariat au Plan), BKAM (Bank Al-Maghrib), Finances, Datagov.ma, OC.
Indicateurs: PIB, IPC, Emploi, Dette Publique, Investissement Public, OPCVM, Taux de Change, Exportations, Budget.
Reponds toujours en francais, de maniere concise et factuelle. Cite les chiffres quand possible."""


def agent_respond(message, history):
    msg = message.lower()

    # Direct data queries
    for code, label in LABELS.items():
        keywords = label.lower().split()
        if any(k in msg for k in keywords) or code.lower().replace(".", " ") in msg:
            sub = get_indicator_data(code)
            if sub.empty:
                return f"Donnees non disponibles pour {label}."

            latest = sub.iloc[-1]
            val = float(latest["valeur"])
            prev = sub.iloc[-2] if len(sub) > 1 else None
            change = None
            if prev is not None:
                pv = float(prev["valeur"])
                if pv != 0:
                    change = (val - pv) / abs(pv) * 100

            unit = UNIT_MAP.get(code, "")
            fc, upper, lower = naive_forecast(sub["valeur"])

            response = f"**{label}** ({unit}):\n\n"
            response += f"- Valeur latest: **{val:,.2f}** ({latest['date'].strftime('%Y-%m')})\n"
            if change is not None:
                response += f"- Variation: **{change:+.1f}%**\n"
            response += f"- Periode: {sub['date'].min().strftime('%Y-%m')} a {sub['date'].max().strftime('%Y-%m')}\n"
            response += f"- Min: {sub['valeur'].min():,.2f} | Max: {sub['valeur'].max():,.2f} | Moy: {sub['valeur'].mean():,.2f}\n"

            if fc:
                response += f"\n**Previsions 12 mois** (naive-tendance):\n"
                response += f"- Mois 1: {fc[0]:,.2f}\n"
                response += f"- Mois 6: {fc[5]:,.2f}\n"
                response += f"- Mois 12: {fc[-1]:,.2f}\n"

            return response

    # Generic queries
    if any(w in msg for w in ["pib", "croissance", "economie"]):
        sub = get_indicator_data("PIB.TRIM.VOL")
        if not sub.empty:
            latest = sub.iloc[-1]
            return f"Le PIB reel du Maroc (derniere valeur: {latest['valeur']:,.0f} MAD, {latest['date'].strftime('%Y-%m')}) montre une {'croissance' if latest['valeur'] > 0 else 'contraction'}. Le Maroc affiche une diversification progressive avec le tourisme, l'automobile et l'aeronautique comme moteurs."
        return "Donnees PIB non disponibles."

    if any(w in msg for w in ["inflation", "ipc", "prix"]):
        sub = get_indicator_data("IPC.INDICE")
        if not sub.empty:
            latest = sub.iloc[-1]
            return f"L'IPC est a {latest['valeur']:,.2f} ({latest['date'].strftime('%Y-%m')}). L'inflation au Maroc est generelement moderee, sous l'influence de la politique monetaire de Bank Al-Maghrib."
        return "Donnees IPC non disponibles."

    if any(w in msg for w in ["chomage", "emploi"]):
        sub = get_indicator_data("EMPLOI.VOLUME")
        if not sub.empty:
            latest = sub.iloc[-1]
            return f"Le taux d'emploi est a {latest['valeur']:.1f}% ({latest['date'].strftime('%Y-%m')}). Le marche du travail marocain reste structurellement tendu, avec un ecart important entre zones urbaines et rurales."
        return "Donnees emploi non disponibles."

    if any(w in msg for w in ["dette", "budget", "deficit"]):
        sub_d = get_indicator_data("DETTE.PUBLIQUE")
        sub_b = get_indicator_data("DEFICIT.BUDGET")
        resp = ""
        if not sub_d.empty:
            latest = sub_d.iloc[-1]
            resp += f"Dette publique: {latest['valeur']:,.1f}% du PIB ({latest['date'].strftime('%Y-%m')}). "
        if not sub_b.empty:
            latest = sub_b.iloc[-1]
            resp += f"Deficit budgetaire: {latest['valeur']:,.1f}% du PIB."
        return resp or "Donnees budget non disponibles."

    if any(w in msg for w in ["source", "donnees", "collecte"]):
        counts = DF["source_code"].value_counts()
        resp = "**Sources de donnees**:\n\n"
        for src, cnt in counts.items():
            resp += f"- {src}: {cnt:,} observations\n"
        resp += f"\nTotal: {len(DF):,} observations, {len(DF['code_indicateur'].unique())} indicateurs."
        return resp

    if any(w in msg for w in ["resume", "synthese", "sommaire", "resume"]):
        total = len(DF)
        n_ind = DF["code_indicateur"].nunique()
        n_src = DF["source_code"].nunique()
        dmin = DF["date"].dropna().min().strftime("%Y-%m-%d")
        dmax = DF["date"].dropna().max().strftime("%Y-%m-%d")
        return (f"**Synthese RASD-Maroc**\n\n"
                f"- {total:,} observations\n"
                f"- {n_ind} indicateurs economiques\n"
                f"- {n_src} sources (HCP, BKAM, Finances, Datagov.ma, OC)\n"
                f"- Periode: {dmin} a {dmax}\n"
                f"- Indicateurs cles: PIB, IPC, Emploi, Dette, Investissement, OPCVM, Taux de Change, Exportations\n\n"
                f"Posez-moi des questions sur un indicateur specifique!")

    if any(w in msg for w in ["bonjour", "salut", "hello", "help", "aide"]):
        return ("Bienvenue! Je suis l'assistant economie du RASD-Maroc.\n\n"
                "Je peux vous renseigner sur:\n"
                "- **PIB**: Produit Interieur Brut\n"
                "- **IPC**: Indice des Prix a la Consommation\n"
                "- **Emploi**: Taux d'emploi\n"
                "- **Dette**: Dette publique\n"
                "- **Budget**: Deficit budgetaire\n"
                "- **OPCVM**: Marche financier\n"
                "- **Taux de change**\n"
                "- **Exportations**\n"
                "- **Sources de donnees**\n\n"
                "Demandez par exemple: 'Quel est le PIB?' ou 'Donne-moi un resume'")

    return (f"Je ne suis pas sur de comprendre. Essayez:\n"
            f"- 'Quel est le PIB?'\n"
            f"- 'Resume'\n"
            f"- 'Sources'\n"
            f"- 'Inflation'\n"
            f"- 'Emploi'\n"
            f"- 'Dette publique'")


# ---- Gradio UI ----
INDICATOR_CHOICES = [(LABELS.get(c, c), c) for c in LABELS if not get_indicator_data(c).empty]

with gr.Blocks(title="Economie Maroc - RASD", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Dashboard Economie Maroc - RASD")
    gr.Markdown(f"**{len(DF):,} observations** | **{DF['code_indicateur'].nunique()} indicateurs** | **{DF['source_code'].nunique()} sources**")

    with gr.Tabs():
        with gr.Tab("Series + Previsions"):
            with gr.Row():
                ind_sel = gr.Dropdown(choices=INDICATOR_CHOICES, value=INDICATOR_CHOICES[0][1] if INDICATOR_CHOICES else None, label="Indicateur")
                period_sel = gr.Dropdown(choices=[("Tout", "all"), ("10 ans", "10"), ("5 ans", "5"), ("3 ans", "3"), ("1 an", "1")], value="5", label="Periode")
                fc_toggle = gr.Checkbox(value=True, label="Afficher previsions")
            ts_plot = gr.Plot()
            ind_sel.change(make_timeseries_plot, [ind_sel, period_sel, fc_toggle], ts_plot)
            period_sel.change(make_timeseries_plot, [ind_sel, period_sel, fc_toggle], ts_plot)
            fc_toggle.change(make_timeseries_plot, [ind_sel, period_sel, fc_toggle], ts_plot)
            demo.load(make_timeseries_plot, [ind_sel, period_sel, fc_toggle], ts_plot)

        with gr.Tab("Comparaison Normalisee"):
            norm_plot = gr.Plot(value=make_all_indicators_plot())

        with gr.Tab("Correlations"):
            corr_plot = gr.Plot(value=make_correlation_plot())

        with gr.Tab("Sources"):
            src_plot = gr.Plot(value=make_sources_plot())

        with gr.Tab("Agent IA"):
            gr.Markdown("Posez des questions sur l'economie marocaine.")
            chatbot = gr.ChatInterface(
                fn=agent_respond,
                examples=[
                    "Resume",
                    "Quel est le PIB?",
                    "Inflation IPC",
                    "Emploi",
                    "Dette publique",
                    "Sources de donnees",
                ],
                retry_btn=None,
                undo_btn=None,
            )

if __name__ == "__main__":
    demo.launch()
