"""
app.py -- Dashboard Dash pour RASD-Maroc : Economie.

Trois onglets :
  1. Carte choroplethe des 12 regions
  2. Series temporelles + bande de prediction
  3. Comparateur multi-indicateurs (axes doubles)

Lance avec :  python app.py
Deploie avec : gunicorn app:server
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

import bq

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
ASSETS_DIR = Path(__file__).parent / "assets"
GEOJSON_PATH = ASSETS_DIR / "regions_maroc.geojson"

app = Dash(
    __name__,
    title="RASD-Maroc :: Economie",
    update_title="Chargement...",
)
server = app.server  # expose pour gunicorn / Cloud Run

# Charger le GeoJSON une seule fois
GEOJSON: dict = {}
if GEOJSON_PATH.exists():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        GEOJSON = json.load(f)
else:
    logger.warning("GeoJSON non trouve : %s — la carte ne s'affichera pas.", GEOJSON_PATH)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_options() -> tuple[list[dict], dict[str, str]]:
    """Construit les options du dropdown et le mapping code->label."""
    df = bq.liste_indicateurs()
    if df.empty:
        return [], {}
    options = [
        {"label": row.nom_indicateur, "value": row.code_indicateur}
        for _, row in df.iterrows()
    ]
    mapping = {row.code_indicateur: row.nom_indicateur for _, row in df.iterrows()}
    return options, mapping


OPTIONS, NOMS = _build_options()
DEFAULT_VALUE = OPTIONS[0]["value"] if OPTIONS else ""

# Mapping region_code -> nom region (pour la carte)
REGION_NAMES = bq.REGION_NAMES


def _add_empty_fig_placeholder(fig: go.Figure, msg: str):
    fig.update_layout(
        annotations=[dict(text=msg, showarrow=False, font=dict(size=16, color="gray"))],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = html.Div(
    [
        html.H1(
            "Observatoire economique — Maroc",
            style={"textAlign": "center", "marginBottom": "0.2em"},
        ),
        html.P(
            "Donnees source : HCP, BAM, Finances, OC, data.gov.ma  |  Mise a jour automatique",
            style={"textAlign": "center", "color": "#666", "marginTop": 0},
        ),
        dcc.Tabs(
            id="onglets",
            value="carte",
            children=[
                dcc.Tab(label="Carte regionale", value="carte"),
                dcc.Tab(label="Series & previsions", value="series"),
                dcc.Tab(label="Comparateur", value="compare"),
            ],
        ),
        html.Div(id="contenu", style={"padding": "1em"}),
    ],
    style={"maxWidth": "1200px", "margin": "auto", "fontFamily": "sans-serif"},
)


# ---------------------------------------------------------------------------
# Layout dynamique selon l'onglet
# ---------------------------------------------------------------------------
@app.callback(Output("contenu", "children"), Input("onglets", "value"))
def render_tab(tab):
    if tab == "carte":
        return html.Div([
            html.Label("Indicateur"),
            dcc.Dropdown(
                id="ind-carte",
                options=OPTIONS,
                value=DEFAULT_VALUE,
                clearable=False,
            ),
            dcc.Loading(
                dcc.Graph(id="fig-carte", style={"height": "600px"}),
                type="circle",
            ),
        ])
    elif tab == "series":
        return html.Div([
            html.Label("Indicateur"),
            dcc.Dropdown(
                id="ind-serie",
                options=OPTIONS,
                value=DEFAULT_VALUE,
                clearable=False,
            ),
            dcc.Loading(
                dcc.Graph(id="fig-serie"),
                type="circle",
            ),
        ])
    elif tab == "compare":
        return html.Div([
            html.Div([
                html.Div([
                    html.Label("Indicateur A (axe gauche)"),
                    dcc.Dropdown(
                        id="ind-a",
                        options=OPTIONS,
                        value=DEFAULT_VALUE,
                        clearable=False,
                    ),
                ], style={"width": "48%", "display": "inline-block"}),
                html.Div([
                    html.Label("Indicateur B (axe droit)"),
                    dcc.Dropdown(
                        id="ind-b",
                        options=OPTIONS,
                        value=OPTIONS[1]["value"] if len(OPTIONS) > 1 else DEFAULT_VALUE,
                        clearable=False,
                    ),
                ], style={"width": "48%", "display": "inline-block", "float": "right"}),
            ]),
            dcc.Loading(
                dcc.Graph(id="fig-compare"),
                type="circle",
            ),
        ])
    return html.Div()


# ---------------------------------------------------------------------------
# 1. Choroplethe des 12 regions
# ---------------------------------------------------------------------------
@app.callback(Output("fig-carte", "figure"), Input("ind-carte", "value"))
def update_carte(code):
    fig = go.Figure()
    if not GEOJSON:
        _add_empty_fig_placeholder(fig, "GeoJSON non disponible")
        return fig

    df = bq.serie(code)
    if df.empty:
        _add_empty_fig_placeholder(fig, "Aucune donnee regionale pour cet indicateur")
        return fig

    # Derniere valeur par region
    df["region_nom"] = df["region_code"].map(REGION_NAMES)
    df = df.dropna(subset=["region_nom"])
    df_latest = df.sort_values("date").groupby("region_nom", as_index=False).last()

    # Exclure le national pour la carte
    df_map = df_latest[df_latest["region_nom"] != "Maroc (National)"]

    if df_map.empty:
        _add_empty_fig_placeholder(fig, "Pas de donnees regionales (national uniquement)")
        return fig

    unite = df["unite"].iloc[0] if "unite" in df.columns else ""

    fig = px.choropleth(
        df_map,
        geojson=GEOJSON,
        locations="region_nom",
        featureidkey="properties.name",
        color="valeur",
        color_continuous_scale="YlOrRd",
        labels={"valeur": unite},
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        title=f"{NOMS.get(code, code)} — derniere valeur par region",
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title=unite),
    )

    # Annotations avec les valeurs
    for _, row in df_map.iterrows():
        fig.add_scattergeo(
            locations=[row["region_nom"]],
            featureidkey="properties.name",
            text=f'{row["valeur"]:.1f}',
            mode="text",
            showlegend=False,
            textfont=dict(size=10, color="black"),
        )

    return fig


# ---------------------------------------------------------------------------
# 2. Series temporelles + bande de prediction
# ---------------------------------------------------------------------------
@app.callback(Output("fig-serie", "figure"), Input("ind-serie", "value"))
def update_series(code):
    fig = go.Figure()

    # Historique national (moyenne regionale ou MA00)
    hist = bq.serie_national(code)
    if hist.empty:
        hist = bq.serie(code)
        if not hist.empty and "region_code" in hist.columns:
            # Utiliser MA00 si disponible, sinon moyenne
            national = hist[hist["region_code"] == "MA00"]
            if not national.empty:
                hist = national[["date", "valeur"]].sort_values("date")
            else:
                hist = hist.groupby("date", as_index=False)["valeur"].mean().sort_values("date")

    if hist.empty:
        _add_empty_fig_placeholder(fig, "Aucune donnee historique")
        return fig

    # Previsions (optionnel — peut etre vide)
    prev = bq.previsions(code)
    has_prev = not prev.empty

    if has_prev:
        # Bande de confiance
        fig.add_trace(go.Scatter(
            x=prev["date"], y=prev["yhat_upper"],
            line=dict(width=0), showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=prev["date"], y=prev["yhat_lower"],
            fill="tonexty", fillcolor="rgba(0,116,217,0.15)",
            line=dict(width=0), name="IC 80 %",
        ))
        fig.add_trace(go.Scatter(
            x=prev["date"], y=prev["yhat"],
            line=dict(dash="dash", color="#0074D9", width=2),
            name="Prevision",
        ))

    # Historique
    fig.add_trace(go.Scatter(
        x=hist["date"], y=hist["valeur"],
        line=dict(color="#111", width=1.5),
        name="Historique",
        mode="lines",
    ))

    title = NOMS.get(code, code)
    if not has_prev:
        title += " (pas de previsions disponibles)"

    fig.update_layout(
        title=title,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=20, t=50, b=30),
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Comparateur double axe
# ---------------------------------------------------------------------------
@app.callback(
    Output("fig-compare", "figure"),
    Input("ind-a", "value"),
    Input("ind-b", "value"),
)
def update_compare(code_a, code_b):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for code, color, side in [(code_a, "#0074D9", False), (code_b, "#FF4136", True)]:
        h = bq.serie_national(code)
        if h.empty:
            h = bq.serie(code)
            if not h.empty and "region_code" in h.columns:
                h = h.groupby("date", as_index=False)["valeur"].mean()
        if h.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=h["date"],
                y=h["valeur"],
                name=NOMS.get(code, code),
                line=dict(color=color, width=1.5),
            ),
            secondary_y=side,
        )

    fig.update_yaxes(title_text=NOMS.get(code_a, code_a), secondary_y=False)
    fig.update_yaxes(title_text=NOMS.get(code_b, code_b), secondary_y=True)
    fig.update_layout(
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=30, b=30),
    )
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=os.environ.get("DASH_DEBUG", "0") == "1", host="0.0.0.0", port=port)
