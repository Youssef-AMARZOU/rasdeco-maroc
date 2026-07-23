"""
baselines.py — Modeles naifs de reference.

Implemente :
  1. Naive saisonnier : repetition de la derniere valeur a la meme saison
  2. Naive tendance / drift : pente lineaire sur les N dernieres observations
  3. Moyenne mobile 4 trimestres

Chaque modele fournit predict() avec intervalle de confiance.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class NaiveSeasonal:
    """
    Naive saisonnier : la prevision pour horizon h est la valeur
    observee a la meme periode l'annee precedente.

    Intervalle : quantiles empiriques des erreurs historiques
    sur la meme saison.
    """

    def __init__(self, season_period: int = 4):
        self.season_period = season_period
        self._train: np.ndarray | None = None
        self._residuals: np.ndarray | None = None

    def fit(self, y: np.ndarray) -> "NaiveSeasonal":
        self._train = y.copy()
        if len(y) > self.season_period * 2:
            self._residuals = y[self.season_period:] - y[:-self.season_period]
        return self

    def predict(self, h: int = 4, alpha: float = 0.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Retourne (y_pred, y_lower, y_upper) pour les h prochains pas.
        alpha = 0.2 -> intervalle a 80%.
        """
        if self._train is None:
            raise RuntimeError("fit() d'abord")

        preds = np.zeros(h)
        for i in range(h):
            idx = -(self.season_period - i % self.season_period)
            preds[i] = self._train[idx] if abs(idx) <= len(self._train) else self._train[-1]

        # Intervalle base sur l'ecart-type des residus saisonniers
        if self._residuals is not None and len(self._residuals) > 3:
            se = np.std(self._residuals, ddof=1)
        else:
            se = np.std(self._train) * 0.1

        z = np.abs(np.percentile(np.random.standard_normal(10000), alpha / 2 * 100))
        lower = preds - z * se
        upper = preds + z * se

        return preds, lower, upper


class DriftModel:
    """
    Modele de derive : pente calculee sur les 'window' dernieres obs,
    extrapolee lineairement.

    y_{t+h} = y_t + h * pente
    """

    def __init__(self, window: int = 8):
        self.window = window
        self._slope = 0.0
        self._last = 0.0
        self._residuals: np.ndarray | None = None

    def fit(self, y: np.ndarray) -> "DriftModel":
        train = y[-self.window:] if len(y) > self.window else y
        t = np.arange(len(train))
        self._slope, _ = np.polyfit(t, train, 1)
        self._last = train[-1]
        # Residus
        fitted = self._last + self._slope * (t - len(train) + 1)
        self._residuals = train - fitted
        return self

    def predict(self, h: int = 4, alpha: float = 0.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        preds = self._last + self._slope * np.arange(1, h + 1)

        if self._residuals is not None and len(self._residuals) > 3:
            se = np.std(self._residuals, ddof=1)
        else:
            se = 0.5

        z = np.abs(np.percentile(np.random.standard_normal(10000), alpha / 2 * 100))
        lower = preds - z * se
        upper = preds + z * se

        return preds, lower, upper


class MovingAverage:
    """
    Moyenne mobile des 4 derniers trimestres, repeter pour horizon h.
    Intervalle : erreur passée de la MA.
    """

    def __init__(self, window: int = 4):
        self.window = window
        self._train: np.ndarray | None = None
        self._residuals: np.ndarray | None = None

    def fit(self, y: np.ndarray) -> "MovingAverage":
        self._train = y.copy()
        if len(y) > self.window + 1:
            # MA historique
            ma = pd.Series(y).rolling(self.window, min_periods=self.window).mean().values
            self._residuals = y[self.window:] - ma[self.window:]
        return self

    def predict(self, h: int = 4, alpha: float = 0.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self._train is None:
            raise RuntimeError("fit() d'abord")
        last_ma = np.mean(self._train[-self.window:])
        preds = np.full(h, last_ma)

        if self._residuals is not None and len(self._residuals) > 3:
            se = np.std(self._residuals, ddof=1)
        else:
            se = np.std(self._train[-self.window:]) * 0.5

        z = np.abs(np.percentile(np.random.standard_normal(10000), alpha / 2 * 100))
        lower = preds - z * se
        upper = preds + z * se

        return preds, lower, upper
