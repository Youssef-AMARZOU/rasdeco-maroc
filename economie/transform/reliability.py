"""
reliability.py -- Score de fiabilite cross-source (1-3).

Methode :
  1. Pour chaque serie de la table fact, on interroge une source secondaire
     (Banque Mondiale API / FMI IFS) pour le meme indicateur.
  2. On calcule la correlation et l'erreur moyenne absolue (MAPE) entre
     les series HCP et la source secondaire.
  3. Score attribue :
       3 = corr ≥ 0.95 et MAPE < 5%
       2 = corr ≥ 0.80 ou MAPE < 15%
       1 = en dessous

  Si aucune source secondaire n'est disponible -> score par defaut = 2.

Usage :
    fiabilite = ReliabilityScorer()
    df = fiabilite.score(df)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import polars as pl
import requests

# ---------------------------------------------------------------------------
# Correspondance codes RASD -> codes Banque Mondiale / FMI
# ---------------------------------------------------------------------------
_WB_MAP = {
    "PIB.CROISSANCE": "NY.GDP.MKTP.KD.ZG",
    "PIB.TETE": "NY.GDP.PCAP.CD",
    "IPC.GLISSEMENT": "FP.CPI.TOTL.ZG",
    "CHOMAGE.TAUX": "SL.UEM.TOTL.ZS",
    "EXPORTATIONS": "NE.EXP.GNFS.CD",
    "IMPORTATIONS": "NE.IMP.GNFS.CD",
    "CHANGE.USD": "PA.NUS.FCRF",
}

_FMI_MAP = {
    "M3": "FIMB_MAR_M3",
    "RESERVES.CHANGE": "FIMB_MAR_RESERVES",
    "IDE.FLUX": "FIMB_MAR_FDI",
}

_CROSS_SOURCE_DIR = Path(__file__).resolve().parent / "cross_source"


class ReliabilityScorer:
    """
    Calcule un score de fiabilite (1-3) par code_indicateur × source.

    Consulte la Banque Mondiale (API REST) et le FMI comme
    sources de reference.
    """

    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or _CROSS_SOURCE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._wb_cache: dict[str, pl.DataFrame] = {}
        self._fmi_cache: dict[str, pl.DataFrame] = {}

    # ------------------------------------------------------------------
    # API Banque Mondiale
    # ------------------------------------------------------------------
    def _fetch_wb(self, indicator_code: str) -> Optional[pl.DataFrame]:
        """Recupere une serie depuis l'API Banque Mondiale."""
        wb_code = _WB_MAP.get(indicator_code)
        if wb_code is None:
            return None

        cache_path = self.cache_dir / f"wb_{wb_code}.parquet"
        if cache_path.exists():
            return pl.read_parquet(cache_path)

        url = f"https://api.worldbank.org/v2/country/MA/indicator/{wb_code}?format=json"
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if len(data) < 2:
                return None
            records = []
            for entry in data[1]:
                if entry.get("value") is not None:
                    records.append({
                        "date": str(entry["date"]),
                        "valeur": float(entry["value"]),
                    })
            if records:
                df = pl.DataFrame(records).sort("date")
                df.write_parquet(cache_path)
                self._wb_cache[indicator_code] = df
                return df
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------
    # FMI IFS
    # ------------------------------------------------------------------
    def _fetch_fmi(self, indicator_code: str) -> Optional[pl.DataFrame]:
        """Recupere une serie depuis l'API FMI IFS (simule)."""
        # L'API FMI IFS necessite generalement une cle ou est payante.
        # On implemente un fallback fichier local ou API simplifiee.
        fmi_code = _FMI_MAP.get(indicator_code)
        if fmi_code is None:
            return None

        cache_path = self.cache_dir / f"fmi_{fmi_code}.parquet"
        if cache_path.exists():
            return pl.read_parquet(cache_path)

        # Tentative API FMI IFS
        try:
            url = (
                f"https://www.imf.org/external/datamapper/api/v1/"
                f"{fmi_code}?periods=2000-{datetime.now().year}"
            )
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            values = data.get("values", {}).get(fmi_code, {}).get("MA", {})
            if values:
                records = [{"date": k, "valeur": float(v)} for k, v in values.items() if v is not None]
                df = pl.DataFrame(records).sort("date")
                df.write_parquet(cache_path)
                self._fmi_cache[indicator_code] = df
                return df
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------
    # Calcul du score
    # ------------------------------------------------------------------
    def score(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Ajoute/modifie la colonne fiabilite (1-3) pour chaque ligne.

        Logique :
          - Si une source secondaire existe -> correlation et MAPE
          - Sinon -> score par defaut selon la source
        """
        df = df.with_columns(pl.lit(2, dtype=pl.Int8).alias("fiabilite_baseline"))

        # Regrouper par code_indicateur pour comparaison
        for code in df["code_indicateur"].unique().to_list():
            wb_df = self._fetch_wb(code)
            fmi_df = self._fetch_fmi(code)

            reference = wb_df if wb_df is not None else fmi_df
            if reference is None:
                # Pas de source secondaire : score par defaut
                # HCP = 2, BAM = 2, DATAGOV = 1 (source indirecte)
                continue

            # Pour chaque combinaison code_indicateur × source
            for source in df.filter(pl.col("code_indicateur") == code)["source_code"].unique().to_list():
                local = (
                    df
                    .filter((pl.col("code_indicateur") == code) & (pl.col("source_code") == source))
                    .with_columns(pl.col("date").str.to_date())
                    .sort("date")
                )

                if len(local) < 5:
                    continue

                # Fusion avec la reference sur la date (annee)
                local_yr = local.with_columns(pl.col("date").dt.year().alias("annee"))
                ref_yr = reference.with_columns(
                    pl.col("date").str.to_date()
                    .dt.year().alias("annee")
                )

                merged = local_yr.join(ref_yr, on="annee", how="inner", suffix="_ref")
                if len(merged) < 5:
                    continue

                corr = merged["valeur"].corr(merged["valeur_ref"])
                if corr is None:
                    continue

                mape = (
                    (merged["valeur"] - merged["valeur_ref"]).abs()
                    / merged["valeur_ref"].abs()
                ).mean()

                if mape is not None:
                    score = 3 if (corr >= 0.95 and mape < 0.05) else 2 if (corr >= 0.80 or mape < 0.15) else 1
                else:
                    score = 2

                df = df.with_columns(
                    pl.when((pl.col("code_indicateur") == code) & (pl.col("source_code") == source))
                    .then(pl.lit(score, dtype=pl.Int8))
                    .otherwise(pl.col("fiabilite"))
                    .alias("fiabilite")
                )

        # Remplir les NULL avec la baseline (2)
        df = df.with_columns(
            pl.col("fiabilite").fill_null(pl.col("fiabilite_baseline"))
        ).drop("fiabilite_baseline")

        return df
