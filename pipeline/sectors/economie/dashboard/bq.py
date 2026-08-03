"""
bq.py -- Couche d'acces BigQuery avec cache TTL (cachetools).

Schema aligne sur le pipeline economie :
  - fact_indicateurs : date, region_code, code_indicateur, valeur, unite, ...
  - previsions       : date, code_indicateur, yhat, yhat_lower, yhat_upper
  - dim_regions      : region_code, region_nom
"""

from __future__ import annotations

import os

import pandas as pd
from cachetools import TTLCache, cached
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Configuration (meme source que bigquery_loader.py)
# ---------------------------------------------------------------------------
PROJECT = os.environ.get("RASD_BQ_PROJECT", "rasd-maroc")
DATASET = os.environ.get("RASD_BQ_DATASET", "economie")

_client: bigquery.Client | None = None

# Cache : indicateurs = 24 h (quasi-statique), series = 1 h
_cache_ind = TTLCache(maxsize=1, ttl=86400)
_cache_serie = TTLCache(maxsize=128, ttl=3600)
_cache_prev = TTLCache(maxsize=128, ttl=3600)

# Mapping region_code -> nom pour la GeoJSON
REGION_NAMES: dict[str, str] = {
    "MA00": "Maroc (National)",
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

# Mapping inverse pour la carte
_NAME_TO_CODE = {v: k for k, v in REGION_NAMES.items()}

# Labels lisibles pour les codes indicateurs
INDICATOR_LABELS: dict[str, str] = {
    "PIB.TRIM.VOL": "PIB trimestriel (volume)",
    "PIB.ANNUEL.VOL": "PIB annuel (volume)",
    "IPC.INDICE": "Indice des prix a la consommation",
    "CHOMAGE.TAUX": "Taux de chomage",
    "CHOMAGE.TRIM": "Chomage trimestriel",
    "VAB.SERVICES": "Valeur ajoutee services",
    "EMPLOI.VOLUME": "Volume de l'emploi",
    "CHANGE.USD": "Taux de change USD/MAD",
    "IMPORTATIONS": "Importations",
    "EXPORTATIONS": "Exportations",
    "DETTE.PUBLIQUE": "Dette publique",
    "DETTE.PUBLIQUE.TAUX": "Dette publique (% PIB)",
    "DETTE.PUBLIQUE.MONTANT": "Dette publique (MDH)",
    "DEFICIT.BUDGET": "Deficit budgetaire",
    "TOURISME.ARRIVEES": "Arrivees touristiques",
    "AGRICULTURE.PRODUCTION": "Production agricole",
    "BAM.ACTIF": "BAM - Actifs",
    "BAM.PASSIF": "BAM - Passifs",
    "BAM.TITRES": "BAM - Titres",
    "BAM.OPCVM.ENCOURS": "OPCVM - Encours",
    "IDE.FLUX": "IDE - Flux",
    "INDICATEUR.HCP.GENERIQUE": "Indicateur HCP",
}


def _client_factory() -> bigquery.Client:
    global _client
    if _client is None:
        creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        if creds and os.path.exists(creds):
            from google.oauth2 import service_account
            sa = service_account.Credentials.from_service_account_file(creds)
            _client = bigquery.Client(project=PROJECT, credentials=sa)
        else:
            _client = bigquery.Client(project=PROJECT)
    return _client


def _query(sql: str, **params) -> pd.DataFrame:
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(k, "STRING", v)
            for k, v in params.items()
        ]
    )
    return _client_factory().query(sql, job_config=job_config).to_dataframe()


# ---------------------------------------------------------------------------
# Indicateurs (liste distincte, cache 24 h)
# ---------------------------------------------------------------------------

@cached(_cache_ind)
def liste_indicateurs() -> pd.DataFrame:
    """Retourne un DataFrame [code_indicateur, nom_indicateur]."""
    try:
        df = _query(f"""
            SELECT DISTINCT code_indicateur
            FROM `{PROJECT}.{DATASET}.fact_indicateurs`
            ORDER BY code_indicateur
        """)
    except Exception:
        return pd.DataFrame(columns=["code_indicateur", "nom_indicateur"])

    df["nom_indicateur"] = df["code_indicateur"].map(
        lambda c: INDICATOR_LABELS.get(c, c)
    )
    return df[["code_indicateur", "nom_indicateur"]]


# ---------------------------------------------------------------------------
# Series historiques (cache 1 h)
# ---------------------------------------------------------------------------

@cached(_cache_serie)
def serie(code: str) -> pd.DataFrame:
    """Serie temporelle regionale pour un indicateur."""
    return _query(f"""
        SELECT date, region_code, code_indicateur, valeur, unite
        FROM `{PROJECT}.{DATASET}.fact_indicateurs`
        WHERE code_indicateur = @code
        ORDER BY date
    """, code=code)


@cached(_cache_serie)
def serie_national(code: str) -> pd.DataFrame:
    """Serie nationale (moyenne ou valeur MA00)."""
    return _query(f"""
        SELECT date, AVG(valeur) AS valeur
        FROM `{PROJECT}.{DATASET}.fact_indicateurs`
        WHERE code_indicateur = @code
          AND region_code != 'MA00'
        GROUP BY date
        ORDER BY date
    """, code=code)


# ---------------------------------------------------------------------------
# Previsions (cache 1 h, tableeoptionnelle)
# ---------------------------------------------------------------------------

@cached(_cache_prev)
def previsions(code: str) -> pd.DataFrame:
    """Previsions pour un indicateur. Retourne DF vide si la table n'existe pas."""
    try:
        return _query(f"""
            SELECT date, yhat, yhat_lower, yhat_upper
            FROM `{PROJECT}.{DATASET}.previsions`
            WHERE code_indicateur = @code
            ORDER BY date
        """, code=code)
    except Exception:
        return pd.DataFrame(columns=["date", "yhat", "yhat_lower", "yhat_upper"])


# ---------------------------------------------------------------------------
# Invalidation du cache (appele apres rechargement BQ)
# ---------------------------------------------------------------------------

def invalidate_all():
    """Vide tous les caches pour forcer un refresh au prochain acces."""
    _cache_ind.clear()
    _cache_serie.clear()
    _cache_prev.clear()
