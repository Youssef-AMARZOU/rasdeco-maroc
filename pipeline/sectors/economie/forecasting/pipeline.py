"""
pipeline.py — Orchestrateur de prevision economique.

1. Charge/génère les données
2. Entraîne 3+ baselines : NaiveSaison, Drift, MA
3. Entraîne SARIMA (auto_arima)
4. Entraîne Prophet
5. Walk-forward validation pour chaque modèle
6. Tableau comparatif + recommendation

Usage :
    python -m economie.forecasting.pipeline
    python -m economie.forecasting.pipeline --indicator PIB.CROISSANCE --horizon 4
    python -m economie.forecasting.pipeline --indicator IPC.GLISSEMENT --plot
"""

from __future__ import annotations

import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from .baselines import NaiveSeasonal, DriftModel, MovingAverage
from .sarima_model import SARIMAModel
from .prophet_model import ProphetModel
from .walk_forward import walk_forward
from .metrics import aggregate_results

warnings.filterwarnings("ignore")


def _prepare_data(
    indicator_code: str = "PIB.CROISSANCE",
    exog_codes: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray | None, pd.DataFrame | None]:
    """
    Charge les donnees et prepare X, y.

    Retourne (y, X_past, df_metadata).
    """
    from .synthetic_data import build_feature_matrix

    if exog_codes is None:
        exog_codes = ["IPC.GLISSEMENT", "TAUX.DIRECTEUR", "DEFICIT.BUDGET"]

    df = build_feature_matrix(target_code=indicator_code, exog_codes=exog_codes)

    y = df["y"].values

    # Matrice exogene : lags + dummies
    exog_cols = [c for c in df.columns if c not in ("date", "y", "quarter")]
    X = df[exog_cols].values if exog_cols else None

    return y, X, df


def _build_sarima_fit_fn(exog_cols: list[str] | None = None):
    """Fabrique la fonction fit pour SARIMA walk-forward."""

    def fit_fn(y_train: np.ndarray, X_train: np.ndarray | None) -> SARIMAModel:
        model = SARIMAModel(
            seasonal=4,
            exog_cols=exog_cols or [],
            max_p=2, max_d=1, max_q=2,
            max_P=1, max_D=1, max_Q=1,
        )
        model.fit(y_train, X_train)
        return model

    return fit_fn


def _build_prophet_fit_fn(exog_cols: list[str] | None = None):
    """Fabrique les fonctions fit/predict pour Prophet walk-forward."""

    def fit_fn(y_train: np.ndarray, X_train: np.ndarray | None) -> ProphetModel:
        # Reconstruire le DataFrame ds/y/X
        dates = pd.date_range(
            end=pd.Timestamp.today(),
            periods=len(y_train),
            freq="QS-OCT",
        )
        df = pd.DataFrame({"ds": dates, "y": y_train})
        if X_train is not None and exog_cols:
            for i, col in enumerate(exog_cols):
                df[col] = X_train[:, i]

        model = ProphetModel(exog_cols=exog_cols or [])
        model.fit(df)
        return model

    return fit_fn


def _build_prophet_predict_fn(exog_cols: list[str] | None = None):
    def predict_fn(h: int, X_future: np.ndarray | None, alpha: float) -> tuple:
        from prophet import Prophet
        if X_future is not None and exog_cols:
            # Construire un future_df avec les exogenes
            last_date = pd.Timestamp.today()
            future_dates = pd.date_range(start=last_date, periods=h + 1, freq="QS")[1:]
            future_df = pd.DataFrame({"ds": future_dates})
            for i, col in enumerate(exog_cols):
                future_df[col] = X_future[:, i]
            return _model_cache.predict(h, future_df, alpha)

        return _model_cache.predict(h, alpha=alpha)

    def fit_and_predict(y_train, X_train=None):
        m = fit_fn(y_train, X_train)
        import copy
        return m

    return fit_and_predict


def run_forecast(
    indicator_code: str = "PIB.CROISSANCE",
    horizon: int = 4,
    exog_codes: list[str] | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Execute le pipeline de prevision complet.

    Retourne le tableau comparatif des modeles.
    """
    if exog_codes is None:
        exog_codes = ["IPC.GLISSEMENT", "TAUX.DIRECTEUR", "DEFICIT.BUDGET"]

    print("=" * 70)
    print(f"  PIPELINE PREVISION - RASD-Maroc")
    print(f"  Cible : {indicator_code}")
    print(f"  Horizon : {horizon} trimestres")
    print(f"  Exogenes : {', '.join(exog_codes)}")
    print("=" * 70)

    # -- Chargement des donnees
    print("\n-> Chargement des donnees...")
    y, X_past, df_meta = _prepare_data(indicator_code, exog_codes)
    n = len(y)
    print(f"  {n} observations chargees (de {df_meta['date'].min()} a {df_meta['date'].max()})")

    min_train = max(20, horizon * 4)

    # Fonction X_future : pour walk-forward, on utilise les vraies valeurs futures
    # (simulation "parfait" pour les exogenes — en production, il faudrait les prevoir aussi)
    def x_future_fn(step: int, h: int) -> np.ndarray | None:
        if X_past is None:
            return None
        train_end = min_train + step
        future_start = train_end
        future_end = future_start + h
        if future_end > len(X_past):
            future_end = len(X_past)
        return X_past[future_start:future_end]

    all_results = []

    # ------------------------------------------------------------------
    # 1. Naive saisonnier
    # ------------------------------------------------------------------
    if verbose:
        print("\n--- 1. Naive Saisonnier ---")

    def fit_naive(y_tr, _):
        m = NaiveSeasonal(season_period=4)
        m.fit(y_tr)
        return m

    def pred_naive(h, _, alpha):
        return _model_cache.predict(h, alpha=alpha)

    _model_cache = NaiveSeasonal()  # will be replaced

    # Wrapper approprie
    def fit_naive_wrapper(y_tr, _):
        m = NaiveSeasonal(season_period=4)
        m.fit(y_tr)
        return m

    def pred_naive_wrapper(h, X_f, alpha):
        return _model_cache.predict(h, alpha)

    _model_cache = None

    # On utilise des closures simples
    results_naive = []
    # Marche directe car les fonctions sont simples
    for step in range(n - min_train - horizon + 1):
        train_end = min_train + step
        test_start = train_end
        test_end = test_start + horizon
        if test_end > n:
            break
        y_train = y[:train_end]
        y_test = y[test_start:test_end]

        model = NaiveSeasonal(season_period=4)
        model.fit(y_train)
        preds, lower, upper = model.predict(h=horizon, alpha=0.2)

        h_actual = min(len(preds), len(y_test))
        if h_actual < 1:
            continue
        from .metrics import compute_all_metrics
        met = compute_all_metrics(y_test[:h_actual], preds[:h_actual], lower[:h_actual], upper[:h_actual])
        results_naive.append({
            "modele": "Naive Saisonnier", "fenetre": step + 1,
            "mae": met["mae"], "rmse": met["rmse"],
            "mape": met["mape"], "coverage": met.get("coverage_80pct", 0.0),
        })

    all_results.extend(results_naive)
    if verbose:
        print(f"  -> {len(results_naive)} fenetres")

    # ------------------------------------------------------------------
    # 2. Drift Model
    # ------------------------------------------------------------------
    if verbose:
        print("\n--- 2. Drift (tendance lineaire) ---")

    results_drift = []
    for step in range(n - min_train - horizon + 1):
        train_end = min_train + step
        test_start = train_end
        test_end = test_start + horizon
        if test_end > n:
            break
        y_train = y[:train_end]
        y_test = y[test_start:test_end]

        model = DriftModel(window=8)
        model.fit(y_train)
        preds, lower, upper = model.predict(h=horizon, alpha=0.2)

        h_actual = min(len(preds), len(y_test))
        if h_actual < 1:
            continue
        from .metrics import compute_all_metrics
        met = compute_all_metrics(y_test[:h_actual], preds[:h_actual], lower[:h_actual], upper[:h_actual])
        results_drift.append({
            "modele": "Drift", "fenetre": step + 1,
            "mae": met["mae"], "rmse": met["rmse"],
            "mape": met["mape"], "coverage": met.get("coverage_80pct", 0.0),
        })

    all_results.extend(results_drift)
    if verbose:
        print(f"  -> {len(results_drift)} fenetres")

    # ------------------------------------------------------------------
    # 3. Moving Average
    # ------------------------------------------------------------------
    if verbose:
        print("\n--- 3. Moyenne Mobile (4T) ---")

    results_ma = []
    for step in range(n - min_train - horizon + 1):
        train_end = min_train + step
        test_start = train_end
        test_end = test_start + horizon
        if test_end > n:
            break
        y_train = y[:train_end]
        y_test = y[test_start:test_end]

        model = MovingAverage(window=4)
        model.fit(y_train)
        preds, lower, upper = model.predict(h=horizon, alpha=0.2)

        h_actual = min(len(preds), len(y_test))
        if h_actual < 1:
            continue
        from .metrics import compute_all_metrics
        met = compute_all_metrics(y_test[:h_actual], preds[:h_actual], lower[:h_actual], upper[:h_actual])
        results_ma.append({
            "modele": "MA(4)", "fenetre": step + 1,
            "mae": met["mae"], "rmse": met["rmse"],
            "mape": met["mape"], "coverage": met.get("coverage_80pct", 0.0),
        })

    all_results.extend(results_ma)
    if verbose:
        print(f"  -> {len(results_ma)} fenetres")

    # ------------------------------------------------------------------
    # 4. SARIMA (auto_arima)
    # ------------------------------------------------------------------
    if verbose:
        print("\n--- 4. SARIMA (auto_arima) ---")

    results_sarima = []
    for step in range(n - min_train - horizon + 1):
        train_end = min_train + step
        test_start = train_end
        test_end = test_start + horizon
        if test_end > n:
            break
        y_train = y[:train_end]
        y_test = y[test_start:test_end]
        X_train = X_past[:train_end] if X_past is not None else None
        X_future = X_past[test_start:test_end] if X_past is not None else None

        try:
            model = SARIMAModel(seasonal=4, max_p=2, max_d=1, max_q=2, max_P=1, max_D=1, max_Q=1)
            model.fit(y_train, X_train)
            preds, lower, upper = model.predict(h=horizon, X_future=X_future, alpha=0.2)
        except Exception as e:
            if verbose and step == 0:
                print(f"  [SKIP] SARIMA a echoue : {e}")
            continue

        h_actual = min(len(preds), len(y_test))
        if h_actual < 1:
            continue
        from .metrics import compute_all_metrics
        met = compute_all_metrics(y_test[:h_actual], preds[:h_actual], lower[:h_actual], upper[:h_actual])
        results_sarima.append({
            "modele": f"SARIMA{model._order if model._order else ''}",
            "fenetre": step + 1,
            "mae": met["mae"], "rmse": met["rmse"],
            "mape": met["mape"], "coverage": met.get("coverage_80pct", 0.0),
        })

    all_results.extend(results_sarima)
    if verbose:
        print(f"  -> {len(results_sarima)} fenetres")

    # ------------------------------------------------------------------
    # 5. Prophet
    # ------------------------------------------------------------------
    if verbose:
        print("\n--- 5. Prophet ---")

    results_prophet = []
    # Prophet est lent (MCMC) : echantillonnage 1 fenetre sur 3
    prophet_step_size = max(1, (n - min_train - horizon + 1) // 20)
    for step in range(0, n - min_train - horizon + 1, prophet_step_size):
        train_end = min_train + step
        test_start = train_end
        test_end = test_start + horizon
        if test_end > n:
            break
        y_train = y[:train_end]
        y_test = y[test_start:test_end]

        # Construire le DataFrame Prophet
        dates = pd.date_range(
            end=pd.Timestamp(df_meta["date"].max()) if step == 0 else pd.Timestamp.today(),
            periods=len(y_train),
            freq="QS-OCT",
        )
        df_train = pd.DataFrame({"ds": dates, "y": y_train})

        exog_cols_used = []
        if X_past is not None:
            X_train = X_past[:train_end]
            X_future = X_past[test_start:test_end]
            # Nommer les colonnes exogenes
            feature_names = [c for c in df_meta.columns if c not in ("date", "y", "quarter")]
            for i, col in enumerate(feature_names):
                if i < X_train.shape[1]:
                    df_train[col] = X_train[:, i]
                    exog_cols_used.append(col)
        else:
            X_future = None
            exog_cols_used = []

        try:
            model = ProphetModel(exog_cols=exog_cols_used)
            model.fit(df_train)

            # Construire future_df
            last_dt = df_train["ds"].iloc[-1]
            future_dates = pd.date_range(start=last_dt, periods=horizon + 1, freq="QS")[1:]
            future_df = pd.DataFrame({"ds": future_dates})
            if X_future is not None:
                for i, col in enumerate(exog_cols_used):
                    if i < X_future.shape[1]:
                        future_df[col] = X_future[:horizon, i]

            preds, lower, upper = model.predict(h=horizon, future_df=future_df, alpha=0.2)
        except Exception as e:
            if verbose and step == 0:
                print(f"  [SKIP] Prophet a echoue : {e}")
            continue

        h_actual = min(len(preds), len(y_test))
        if h_actual < 1:
            continue
        from .metrics import compute_all_metrics
        met = compute_all_metrics(y_test[:h_actual], preds[:h_actual], lower[:h_actual], upper[:h_actual])
        results_prophet.append({
            "modele": "Prophet", "fenetre": step + 1,
            "mae": met["mae"], "rmse": met["rmse"],
            "mape": met["mape"], "coverage": met.get("coverage_80pct", 0.0),
        })

    all_results.extend(results_prophet)
    if verbose:
        print(f"  -> {len(results_prophet)} fenetres")

    # ------------------------------------------------------------------
    # Tableau comparatif
    # ------------------------------------------------------------------
    if not all_results:
        print("\n! Aucun resultat. Verifiez que les donnees sont disponibles.")
        return pd.DataFrame()

    df_results = pd.DataFrame(all_results)
    summary = aggregate_results(df_results)

    print("\n" + "=" * 70)
    print("  TABLEAU COMPARATIF")
    print("=" * 70)
    print(summary.to_string(index=False))

    # Meilleur modele
    best = summary.iloc[0]
    print(f"\n  -> Modele recommande : {best['modele']}")
    print(f"     MAE={best['mae_mean']}, RMSE={best['rmse_mean']}, "
          f"MAPE={best['mape_mean']}%, Coverage={best['coverage_mean']}")
    print(f"     Avis : {best['recommandation']}")
    print("=" * 70)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline prevision ECONOMIE RASD-Maroc"
    )
    parser.add_argument(
        "--indicator", default="PIB.CROISSANCE",
        choices=["PIB.CROISSANCE", "IPC.GLISSEMENT", "TAUX.DIRECTEUR", "DEFICIT.BUDGET"],
        help="Indicateur a prevoir"
    )
    parser.add_argument("--horizon", type=int, default=4, help="Horizon en trimestres")
    parser.add_argument("--plot", action="store_true", help="Afficher les graphiques")
    args = parser.parse_args()

    summary = run_forecast(
        indicator_code=args.indicator,
        horizon=args.horizon,
        verbose=True,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
