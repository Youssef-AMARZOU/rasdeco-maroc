"""
prophet_model.py — Modele Prophet avec regresseurs exogenes.

Inclut :
  - Saisonnalite annuelle et trimestrielle (Fourier order ajustable)
  - Regresseurs exogenes : COVID, secheresse, taux directeur, inflation
  - Points de changement de tendance (changepoint_prior_scale)

Intervalle de confiance : Prophet les fournit nativement
via uncertainty_samples.
"""

from __future__ import annotations

import warnings
from typing import Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


class ProphetModel:
    """
    Prophet avec regresseurs.

    Usage :
        model = ProphetModel(exog_cols=["covid", "secheresse"])
        model.fit(df_train)   # df avec colonnes ds, y + exog
        preds, lower, upper = model.predict(h=4, future_df=df_future)
    """

    def __init__(
        self,
        exog_cols: list[str] | None = None,
        seasonality_mode: str = "additive",
        yearly_seasonality: int = 4,
        changepoint_prior_scale: float = 0.05,
        uncertainty_samples: int = 100,
    ):
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("prophet requis : pip install prophet")

        self.exog_cols = exog_cols or []
        self.seasonality_mode = seasonality_mode
        self.yearly_seasonality = yearly_seasonality
        self.changepoint_prior_scale = changepoint_prior_scale
        self.uncertainty_samples = uncertainty_samples
        self._model: Prophet | None = None

    @property
    def name(self) -> str:
        return "Prophet"

    def fit(self, df: pd.DataFrame) -> "ProphetModel":
        """
        Entraine Prophet.

        df doit avoir :
            - ds : date (datetime ou str)
            - y  : valeur cible
            - colonnes exogenes (optionnel)
        """
        from prophet import Prophet

        model = Prophet(
            seasonality_mode=self.seasonality_mode,
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=self.changepoint_prior_scale,
            uncertainty_samples=self.uncertainty_samples,
        )

        # Saisonnalite trimestrielle explicite
        model.add_seasonality(name="quarterly", period=4, fourier_order=3)

        df_in = df[["ds", "y"]].copy()
        for col in self.exog_cols:
            if col in df.columns:
                model.add_regressor(col)
                df_in[col] = df[col].values

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(df_in)

        self._model = model
        return self

    def predict(
        self,
        h: int = 4,
        future_df: pd.DataFrame | None = None,
        alpha: float = 0.2,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prevoyance sur h pas.

        Si future_df est fourni, il est utilise directement.
        Sinon, on cree un horizon Prophet basique.

        Retourne (y_pred, y_lower, y_upper).
        """
        from prophet import Prophet

        if self._model is None:
            raise RuntimeError("fit() d'abord")

        if future_df is not None:
            future = future_df
        else:
            # Creer un futur basique sans regresseurs
            future = self._model.make_future_dataframe(periods=h, freq="QS")

        fcst = self._model.predict(future)

        if future_df is not None:
            # Prendre les h dernieres lignes (les vraies futures)
            preds = fcst["yhat"].values[-h:]
            lower = fcst["yhat_lower"].values[-h:]
            upper = fcst["yhat_upper"].values[-h:]
        else:
            preds = fcst["yhat"].values[-h:]
            lower = fcst["yhat_lower"].values[-h:]
            upper = fcst["yhat_upper"].values[-h:]

        return np.array(preds), np.array(lower), np.array(upper)

    def get_components(self) -> pd.DataFrame | None:
        """Retourne les composantes de la prevision (tendance, saison, regresseurs)."""
        from prophet import Prophet
        if self._model is None:
            return None
        return self._model.predict(self._model.history)
