"""
metrics.py — Metriques d'evaluation pour prevision temporelle.

Calcule MAE, RMSE, MAPE, coverage des intervalles de confiance.
Agrege en tableau comparatif.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = np.abs(y_true) > 1e-6
    if mask.sum() == 0:
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def prediction_interval_coverage(
    y_true: np.ndarray,
    y_lower: np.ndarray,
    y_upper: np.ndarray,
    nominal: float = 0.80,
) -> float:
    """Proportion de vraies valeurs dans l'intervalle de confiance."""
    inside = np.sum((y_true >= y_lower) & (y_true <= y_upper))
    return float(inside / len(y_true)) if len(y_true) > 0 else 0.0


def compute_all_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_lower: np.ndarray | None = None,
    y_upper: np.ndarray | None = None,
) -> dict:
    """
    Calcule toutes les metriques pour un modele.

    Retourne un dict : {mae, rmse, mape, coverage}
    """
    metrics = {
        "mae": round(mae(y_true, y_pred), 3),
        "rmse": round(rmse(y_true, y_pred), 3),
        "mape": round(mape(y_true, y_pred), 2),
    }
    if y_lower is not None and y_upper is not None:
        metrics["coverage_80pct"] = round(
            prediction_interval_coverage(y_true, y_lower, y_upper), 3
        )
    return metrics


def aggregate_results(results: list[dict]) -> pd.DataFrame:
    """
    Agrège les resultats walk-forward en tableau comparatif.

    Entree : liste de dicts avec clefs :
        modele, fenetre, mae, rmse, mape, coverage

    Sortie : DataFrame resume par modele
    """
    df = pd.DataFrame(results)

    if df.empty:
        return pd.DataFrame(columns=["modele", "mae_mean", "rmse_mean", "mape_mean",
                                     "coverage_mean", "mae_std"])

    grouped = df.groupby("modele").agg({
        "mae": ["mean", "std"],
        "rmse": ["mean", "std"],
        "mape": ["mean", "std"],
        "coverage": "mean",
    }).round(3)

    grouped.columns = ["mae_mean", "mae_std", "rmse_mean", "rmse_std",
                       "mape_mean", "mape_std", "coverage_mean"]
    grouped = grouped.reset_index()

    # Recommentation
    def recommander(row):
        mape_v = row["mape_mean"]
        cv = row["coverage_mean"]
        if mape_v < 10 and cv > 0.7:
            return "PRODUCTION - Bonne precision + calibration"
        elif mape_v < 20:
            return "ACCEPTABLE - Precision moyenne"
        else:
            return "A EVITER - Trop d'erreur"

    grouped["recommandation"] = grouped.apply(recommander, axis=1)
    return grouped.sort_values("mape_mean")
