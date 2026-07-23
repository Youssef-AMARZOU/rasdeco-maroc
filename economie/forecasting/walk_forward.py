"""
walk_forward.py — Validation walk-forward stricte pour series temporelles.

Principe :
  - Fenetre d'entrainement glissante (expanding)
  - Entraine sur [0:t], predit [t:t+h]
  - Mesure l'ecart entre prevision et vraie valeur
  - Aucun point futur ne fuit dans l'entrainement

Supporte les modeles avec ou sans exogenes.
"""

from __future__ import annotations

import warnings
from typing import Any, Callable

import numpy as np
import pandas as pd

from .metrics import compute_all_metrics

warnings.filterwarnings("ignore")

ModelFitFn = Callable[[np.ndarray, np.ndarray | None], Any]
ModelPredictFn = Callable[[int, np.ndarray | None, float], tuple[np.ndarray, np.ndarray, np.ndarray]]


def walk_forward(
    y: np.ndarray,
    fit_fn: ModelFitFn,
    predict_fn: ModelPredictFn,
    horizon: int = 4,
    min_train: int = 20,
    X: np.ndarray | None = None,
    X_future_fn: Callable[[int, int], np.ndarray | None] | None = None,
    model_name: str = "model",
    alpha: float = 0.2,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Validation walk-forward.

    Parametres
    ----------
    y : series temporelle (n,)
    fit_fn : fonction fit(y_train, X_train) -> model
    predict_fn : fonction predict(h, X_future, alpha) -> (preds, lower, upper)
    horizon : horizon de prevision
    min_train : nb minimum d'obs pour entrainer
    X : matrice exogene (n, n_features) ou None
    X_future_fn : fonction(step, h) -> X pour la fenetre future
    model_name : nom du modele pour le rapport
    alpha : niveau de confiance (0.2 = 80% intervalle)
    verbose : afficher la progression

    Retourne
    --------
    DataFrame avec colonnes : modele, fenetre, debut_train, fin_train,
                               debut_test, fin_test, y_true, y_pred,
                               y_lower, y_upper, mae, rmse, mape, coverage
    """
    n = len(y)
    if n < min_train + horizon:
        raise ValueError(
            f"Pas assez de donnees : {n} obs, besoin min_train={min_train} + horizon={horizon}"
        )

    results = []
    nb_steps = n - min_train - horizon + 1

    for step in range(nb_steps):
        train_end = min_train + step
        test_start = train_end
        test_end = test_start + horizon

        if test_end > n:
            break

        y_train = y[:train_end]
        y_test = y[test_start:test_end]

        X_train = X[:train_end] if X is not None else None
        X_future = X_future_fn(step, horizon) if X_future_fn is not None else None

        try:
            model = fit_fn(y_train, X_train)
            y_pred, y_lower, y_upper = predict_fn(horizon, X_future, alpha)
        except Exception as e:
            if verbose:
                print(f"  [WARN] Step {step}: {e}")
            continue

        # Aligner les longueurs
        h_actual = min(len(y_pred), len(y_test))
        if h_actual < 1:
            continue

        y_pred = y_pred[:h_actual]
        y_lower = y_lower[:h_actual]
        y_upper = y_upper[:h_actual]
        y_true = y_test[:h_actual]

        metrics = compute_all_metrics(y_true, y_pred, y_lower, y_upper)

        results.append({
            "modele": model_name,
            "fenetre": step + 1,
            "debut_train": str(step),
            "fin_train": str(train_end - 1),
            "debut_test": str(test_start),
            "fin_test": str(test_end - 1),
            "y_true_list": y_true.tolist(),
            "y_pred_list": y_pred.tolist(),
            "y_lower_list": y_lower.tolist(),
            "y_upper_list": y_upper.tolist(),
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "mape": metrics["mape"],
            "coverage": metrics.get("coverage_80pct", 0.0),
        })

        if verbose and (step + 1) % 5 == 0:
            print(f"  Walk-forward step {step + 1}/{nb_steps} ...")

    if not results:
        return pd.DataFrame(columns=[
            "modele", "fenetre", "mae", "rmse", "mape", "coverage"
        ])

    return pd.DataFrame(results)
