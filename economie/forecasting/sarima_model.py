"""
sarima_model.py — Modele SARIMA/SARIMAX avec auto_arima.

Trouve automatiquement les ordres (p,d,q)(P,D,Q,S) via
pmdarima.auto_arima, integre les regresseurs exogenes
(chocs COVID, secheresse, lags d'inflation/taux).

Intervalle de confiance : analytique via statsmodels.
"""

from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


class SARIMAModel:
    """
    SARIMAX avec auto_arima pour la selection d'ordre.

    Usage :
        model = SARIMAModel(seasonal=4, exog_cols=["covid", "secheresse"])
        model.fit(y_train, X_train=X_train)
        preds, lower, upper = model.predict(h=4, X_future=X_future)
    """

    def __init__(
        self,
        seasonal: int = 4,
        exog_cols: list[str] | None = None,
        max_p: int = 3,
        max_d: int = 1,
        max_q: int = 3,
        max_P: int = 2,
        max_D: int = 1,
        max_Q: int = 2,
        trace: bool = False,
    ):
        self.seasonal = seasonal
        self.exog_cols = exog_cols or []
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q
        self.max_P = max_P
        self.max_D = max_D
        self.max_Q = max_Q
        self.trace = trace
        self._model = None
        self._order = None
        self._seasonal_order = None

    @property
    def name(self) -> str:
        if self._order:
            return f"SARIMA{self._order}{self._seasonal_order}"
        return "SARIMA(auto)"

    def fit(self, y: np.ndarray, X: np.ndarray | None = None) -> "SARIMAModel":
        """
        Entraine auto_arima sur y avec exogenes X.

        Parametres
        ----------
        y : array (n,)
        X : array (n, n_exog) ou None
        """
        try:
            from pmdarima import auto_arima
        except ImportError:
            raise ImportError("pmdarima requis : pip install pmdarima")

        # auto_arima avec X si fourni
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = auto_arima(
                y,
                X=X,
                start_p=0, max_p=self.max_p,
                start_d=0, max_d=self.max_d,
                start_q=0, max_q=self.max_q,
                start_P=0, max_P=self.max_P,
                max_D=self.max_D,
                start_Q=0, max_Q=self.max_Q,
                m=self.seasonal,
                seasonal=True,
                stepwise=True,
                trace=self.trace,
                error_action="ignore",
                suppress_warnings=True,
                n_fits=20,
                information_criterion="aic",
                with_intercept=True,
            )

        self._model = result
        self._order = result.order
        self._seasonal_order = result.seasonal_order
        return self

    def predict(
        self,
        h: int = 4,
        X_future: np.ndarray | None = None,
        alpha: float = 0.2,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prevoyance sur h pas.

        Retourne (y_pred, y_lower, y_upper) tableaux de taille (h,).
        Intervalle de confiance a (1-alpha)*100%.
        """
        if self._model is None:
            raise RuntimeError("fit() d'abord")

        # Predire h pas a la fois (direct, pas recursif)
        forecast_result = self._model.predict(
            n_periods=h,
            X=X_future,
            return_conf_int=True,
            alpha=alpha,
        )

        if isinstance(forecast_result, tuple) and len(forecast_result) == 2:
            preds, conf_int = forecast_result
        else:
            preds = np.asarray(forecast_result)
            conf_int = np.zeros((h, 2))

        preds = np.asarray(preds).flatten()
        lower = conf_int[:, 0]
        upper = conf_int[:, 1]

        # Fallback si intervalle pas disponible
        if len(lower) < h:
            lower = np.full(h, preds[-1] - 2 * np.std(self._model.resid()) if hasattr(self._model, 'resid') else preds[-1] - 1)
            upper = np.full(h, preds[-1] + 2 * np.std(self._model.resid()) if hasattr(self._model, 'resid') else preds[-1] + 1)

        return np.array(preds), np.array(lower), np.array(upper)
