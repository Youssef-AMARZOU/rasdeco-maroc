"""
synthetic_data.py — Generation de donnees economiques marocaines realistes pour test.

Les series sont synthetiques mais calibrees sur les ordres de grandeur reels
(PIB, inflation, taux directeur, chocs COVID/secheresse).

Cible : ~2005-2026, trimestriel (T1=2005-Q1)
"""

from __future__ import annotations

import warnings
from datetime import datetime

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Parametres macro realistes Maroc
# ---------------------------------------------------------------------------
RNG = np.random.default_rng(42)

# Chronologie des chocs
COVID_PERIODS = [
    ("2020-Q1", -1.5),   # debut pandemie
    ("2020-Q2", -5.0),   # confinement strict
    ("2020-Q3", -2.0),   # reprise partielle
    ("2020-Q4", -0.5),   # fin annee
    ("2021-Q1", 3.0),    # rebond
    ("2021-Q2", 5.0),
    ("2021-Q3", 4.0),
    ("2021-Q4", 2.5),
]
DROUGHT_PERIODS = {"2016", "2020", "2022", "2024"}
OIL_SHOCK = {"2021-Q3", "2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4"}

# Rebasages HCP
REBASEMENTS = {"2007-Q1": "base_2007", "2014-Q1": "base_2014", "2017-Q1": "base_2017"}


def _quarterly_dates(start: str = "2005-01-01", end: str = "2026-10-01") -> pd.DatetimeIndex:
    return pd.date_range(start=start, end=end, freq="QS-OCT")


def _quarter_label(dt: pd.Timestamp) -> str:
    return f"{dt.year}-Q{(dt.month - 1) // 3 + 1}"


def generate_pib_croissance() -> pd.DataFrame:
    """
    PIB croissance trimestrielle (T/T-4, en %).
    Tendance longue 2005-2026 avec cycle + chocs.
    """
    dates = _quarterly_dates()
    n = len(dates)
    t = np.arange(n)

    # Tendance : croissance potentielle ~4% au debut, ralentit vers 2.5%
    trend = 4.0 - 0.3 * np.sin(t / 40) - 0.02 * t  # de 4% vers ~2.5%

    # Cycle d'affaires (frequence ~10 ans / 40 quarters)
    cycle = 1.5 * np.sin(2 * np.pi * t / 36 + 0.5)

    # Saisonnalite moderee
    seasonal = 0.3 * np.sin(2 * np.pi * t / 4 + 0.2)

    # Bruit
    noise = RNG.normal(0, 0.4, n)

    values = trend + cycle + seasonal + noise

    # Application des chocs
    shock = np.zeros(n)
    for i, dt in enumerate(dates):
        ql = _quarter_label(dt)
        if dt.year in DROUGHT_PERIODS:
            shock[i] -= 1.5  # secheresse : -1.5% PIB

    # COVID (plus fort que tout)
    for ql, impact in COVID_PERIODS:
        idx = np.where([_quarter_label(d) == ql for d in dates])[0]
        if len(idx) > 0:
            shock[idx[0]] += impact

    # Choc petrolier
    for ql in OIL_SHOCK:
        idx = np.where([_quarter_label(d) == ql for d in dates])[0]
        if len(idx) > 0:
            shock[idx[0]] -= 0.5  # +0.5% inflation via energie

    values += shock

    # Clipping pour eviter des extremes irrealistes
    values = np.clip(values, -10, 8)

    return pd.DataFrame({
        "date": dates,
        "date_label": [_quarter_label(d) for d in dates],
        "code_indicateur": "PIB.CROISSANCE",
        "valeur": np.round(values, 2),
        "region_code": "MA00",
        "domaine_code": "CN",
        "unite": "%",
        "source_code": "HCP",
        "version_serie": "recente",
        "fiabilite": 2,
        "qualite_flag": None,
    })


def generate_ipc_inflation() -> pd.DataFrame:
    """
    IPC glissement annuel (%, mensuel resample en trimestriel).
    """
    dates = _quarterly_dates()
    n = len(dates)
    t = np.arange(n)

    # Inflation de fond ~2% cible BAM
    base = 2.0

    # Cycle alimentaire/energie
    cycle = 1.0 * np.sin(2 * np.pi * t / 24 + 0.8)

    # Saisonnalite (Ramadan, recoltes)
    seasonal = 0.5 * np.sin(2 * np.pi * t / 4 - 0.3)

    noise = RNG.normal(0, 0.3, n)

    values = base + cycle + seasonal + noise

    # Chocs
    shock = np.zeros(n)
    for i, dt in enumerate(dates):
        ql = _quarter_label(dt)

    # COVID : inflation basse en 2020 (demande atone)
    for ql, _ in COVID_PERIODS[:4]:
        idx = np.where([_quarter_label(d) == ql for d in dates])[0]
        if len(idx) > 0:
            shock[idx[0]] -= 1.0

    # Reprise post-COVID + choc petrole : inflation monte
    for ql in {"2021-Q3", "2021-Q4", "2022-Q1", "2022-Q2", "2022-Q3", "2022-Q4", "2023-Q1"}:
        idx = np.where([_quarter_label(d) == ql for d in dates])[0]
        if len(idx) > 0:
            vals = {200: 2.0, 201: 3.5, 202: 5.0, 203: 6.5, 204: 7.0, 205: 6.0, 206: 4.0}
            shock[idx[0]] += vals.get(idx[0], 2.0)

    # Secheresse : inflation alimentaire
    for ql in {"2016-Q2", "2016-Q3", "2022-Q2", "2022-Q3", "2024-Q2"}:
        idx = np.where([_quarter_label(d) == ql for d in dates])[0]
        if len(idx) > 0:
            shock[idx[0]] += 1.5

    values += shock
    values = np.clip(values, -2, 10)

    return pd.DataFrame({
        "date": dates,
        "date_label": [_quarter_label(d) for d in dates],
        "code_indicateur": "IPC.GLISSEMENT",
        "valeur": np.round(values, 2),
        "region_code": "MA00",
        "domaine_code": "PRIX",
        "unite": "%",
        "source_code": "HCP",
        "version_serie": "recente",
        "fiabilite": 2,
        "qualite_flag": None,
    })


def generate_taux_directeur() -> pd.DataFrame:
    """
    Taux directeur BAM (palier de 0.25%, modifie ~2x/an).
    """
    dates = _quarterly_dates()
    n = len(dates)

    # Taux directeur : decision de politique monetaire
    # Simplification : valeurs calibrees
    raw = [2.50] * 30 + [2.50] * 5 + [3.00] * 5 + [3.00] * 10 + \
           [2.50] * 4 + [2.00] * 4 + [1.50] * 4 + [1.50] * 8 + \
           [3.00] * 8 + [3.50] * 4 + [3.00] * 4 + [2.75] * 4

    # Ajustement pour correspondre a la longueur exacte
    raw = raw[:n]
    while len(raw) < n:
        raw.append(raw[-1])

    return pd.DataFrame({
        "date": dates,
        "date_label": [_quarter_label(d) for d in dates],
        "code_indicateur": "TAUX.DIRECTEUR",
        "valeur": raw,
        "region_code": "MA00",
        "domaine_code": "MONETAIRE",
        "unite": "%",
        "source_code": "BAM",
        "version_serie": "recente",
        "fiabilite": 2,
        "qualite_flag": None,
    })


def generate_deficit_budget() -> pd.DataFrame:
    """
    Deficit budgetaire (% PIB). Annuel, resample en trimestriel constant.
    """
    dates = _quarterly_dates()
    n = len(dates)
    t = np.arange(n)

    base = -3.5  # deficit structurel ~3.5%
    values = base + 1.0 * np.sin(2 * np.pi * t / 40) + RNG.normal(0, 0.5, n)

    # Chocs COVID (+ deficit)
    for i, dt in enumerate(dates):
        y = dt.year
        if y == 2020:
            values[i] = -7.5
        elif y == 2021:
            values[i] = -6.0
        elif y == 2022:
            values[i] = -5.2

    return pd.DataFrame({
        "date": dates,
        "date_label": [_quarter_label(d) for d in dates],
        "code_indicateur": "DEFICIT.BUDGET",
        "valeur": np.round(values, 1),
        "region_code": "MA00",
        "domaine_code": "BUDGET",
        "unite": "%PIB",
        "source_code": "FIN",
        "version_serie": "recente",
        "fiabilite": 2,
        "qualite_flag": None,
    })


def generate_indicateur_principal(code: str = "PIB.CROISSANCE") -> pd.DataFrame:
    """Generateur unique dispatche sur le code."""
    generators = {
        "PIB.CROISSANCE": generate_pib_croissance,
        "IPC.GLISSEMENT": generate_ipc_inflation,
        "TAUX.DIRECTEUR": generate_taux_directeur,
        "DEFICIT.BUDGET": generate_deficit_budget,
    }
    gen = generators.get(code)
    if gen is None:
        raise ValueError(f"Indicateur non supporte: {code}")
    return gen()


def build_feature_matrix(
    target_code: str = "PIB.CROISSANCE",
    exog_codes: list[str] | None = None,
) -> pd.DataFrame:
    """
    Construit une matrice X,Y pour la prevision.

    Y = target_code (valeur)
    X = exog_codes (valeurs) + dummy COVID + drought + rebasements
    """
    if exog_codes is None:
        exog_codes = ["IPC.GLISSEMENT", "TAUX.DIRECTEUR", "DEFICIT.BUDGET"]

    # Charger target
    y_df = generate_indicateur_principal(target_code)
    y_df = y_df[["date", "valeur"]].rename(columns={"valeur": "y"})

    # Charger exogenes
    result = y_df.copy()
    for code in exog_codes:
        if code == target_code:
            continue
        x_df = generate_indicateur_principal(code)
        x_df = x_df[["date", "valeur"]].rename(columns={"valeur": code.lower()})
        result = result.merge(x_df, on="date", how="left")

    # Ajouter les dummies de choc
    result["covid"] = result["date"].apply(
        lambda d: 1 if d.year == 2020 and d.month in (4, 7, 10) else 0
    ).astype(int)
    result["secheresse"] = result["date"].apply(
        lambda d: 1 if d.year in {2016, 2020, 2022, 2024} else 0
    ).astype(int)

    # Lags de 1 trimestre pour les exogenes
    for col in [c.lower() for c in exog_codes if c != target_code]:
        result[f"{col}_lag1"] = result[col].shift(1)

    # Mois / trimestre
    result["quarter"] = result["date"].dt.quarter

    result = result.dropna().reset_index(drop=True)
    return result


def load_real_data(source: str = "economie") -> pd.DataFrame:
    """
    Tentative de chargement des donnees reelles depuis le pipeline.
    Si indisponible, retombe sur les donnees synthetiques.
    """
    try:
        import sys
        sys.path.insert(0, ".")
        from transform.pipeline import run_pipeline
        fact = run_pipeline(dry_run=False)
        if fact is not None and len(fact) > 0:
            return fact
    except Exception:
        pass

    # Fallback synthetique
    dfs = [generate_indicateur_principal(c) for c in
           ["PIB.CROISSANCE", "IPC.GLISSEMENT", "TAUX.DIRECTEUR", "DEFICIT.BUDGET"]]
    return pd.concat(dfs, ignore_index=True)
