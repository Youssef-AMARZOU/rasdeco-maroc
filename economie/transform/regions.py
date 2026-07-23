"""
regions.py -- Correspondance 16 anciennes regions (pre-2015) ↔ 12 regions actuelles.

Regles d'agregation explicites pour les cas ambigus (1 ancienne -> plusieurs nouvelles).

Source : decoupage territorial Maroc 2015 (regions)
"""

from __future__ import annotations

import polars as pl

# ---------------------------------------------------------------------------
# Mapping 12 regions actuelles -> old codes
# ---------------------------------------------------------------------------
REGIONS_12: dict[str, dict] = {
    "MA01": {"nom": "Tanger-Tetouan-Al Hoceïma", "ancien": ["MA15", "MA16"]},
    "MA02": {"nom": "Oriental", "ancien": ["MA10"]},
    "MA03": {"nom": "Fes-Meknes", "ancien": ["MA04", "MA09", "MA16"]},
    "MA04": {"nom": "Rabat-Sale-Kenitra", "ancien": ["MA05", "MA12"]},
    "MA05": {"nom": "Beni Mellal-Khenifra", "ancien": ["MA01", "MA14"]},
    "MA06": {"nom": "Casablanca-Settat", "ancien": ["MA01", "MA02", "MA07"]},
    "MA07": {"nom": "Marrakech-Safi", "ancien": ["MA02", "MA08"]},
    "MA08": {"nom": "Drâa-Tafilalet", "ancien": ["MA09", "MA13"]},
    "MA09": {"nom": "Souss-Massa", "ancien": ["MA13"]},
    "MA10": {"nom": "Guelmim-Oued Noun", "ancien": ["MA06"]},
    "MA11": {"nom": "Laâyoune-Sakia El Hamra", "ancien": ["MA07"]},
    "MA12": {"nom": "Dakhla-Oued Ed-Dahab", "ancien": ["MA11"]},
}

# ---------------------------------------------------------------------------
# Mapping 16 anciennes regions -> nouvelles
# ---------------------------------------------------------------------------
# Regle pour les cas ambigus (split) :
#   "AGReGATION" = la donnee ancienne region est dupliquee vers toutes les
#                   nouvelles avec un flag "ambigu" dans qualite_flag.
#   "PONDeRe"    = proportion connue (PIB, population) -- cle de partage.
#   "PARTIEL"    = ne concerne qu'une partie de l'ancienne region.
REGIONS_16: dict[str, dict] = {
    "MA01": {
        "nom": "Chaouia-Ouardigha",
        "nouvelles": {
            "MA05": {"regle": "PARTIEL", "note": "Province Khouribga, portion Beni Mellal-Khenifra"},
            "MA06": {"regle": "PARTIEL", "note": "Provinces Settat, Berchid -> Casablanca-Settat"},
        },
    },
    "MA02": {
        "nom": "Doukkala-Abda",
        "nouvelles": {
            "MA06": {"regle": "PARTIEL", "note": "Province El Jadida, Sidi Bennour -> Casablanca-Settat"},
            "MA07": {"regle": "PARTIEL", "note": "Province Safi -> Marrakech-Safi"},
        },
    },
    "MA03": {"nom": "Fes-Boulemane", "nouvelles": {"MA03": {"regle": "AGReGATION", "note": "Cœur Fes-Meknes"}}},
    "MA04": {
        "nom": "Gharb-Chrarda-Beni Hssen",
        "nouvelles": {"MA04": {"regle": "AGReGATION", "note": "Fusionne dans Rabat-Sale-Kenitra"}},
    },
    "MA05": {"nom": "Grand Casablanca", "nouvelles": {"MA06": {"regle": "AGReGATION", "note": "Devenu Casablanca-Settat"}}},
    "MA06": {
        "nom": "Guelmim-Es Semara",
        "nouvelles": {"MA10": {"regle": "AGReGATION", "note": "Devenu Guelmim-Oued Noun"}},
    },
    "MA07": {
        "nom": "Laâyoune-Boujdour-Sakia El Hamra",
        "nouvelles": {"MA11": {"regle": "AGReGATION", "note": "Devenu Laâyoune-Sakia El Hamra"}},
    },
    "MA08": {
        "nom": "Marrakech-Tensift-Al Haouz",
        "nouvelles": {"MA07": {"regle": "AGReGATION", "note": "Devenu Marrakech-Safi"}},
    },
    "MA09": {
        "nom": "Meknes-Tafilalet",
        "nouvelles": {
            "MA03": {"regle": "PARTIEL", "note": "Meknes, El Hajeb, Ifrane -> Fes-Meknes"},
            "MA08": {"regle": "PARTIEL", "note": "Errachidia, Midelt -> Drâa-Tafilalet"},
        },
    },
    "MA10": {"nom": "Oriental", "nouvelles": {"MA02": {"regle": "AGReGATION", "note": "Devenu Oriental"}}},
    "MA11": {
        "nom": "Oued Ed-Dahab-Lagouira",
        "nouvelles": {"MA12": {"regle": "AGReGATION", "note": "Devenu Dakhla-Oued Ed-Dahab"}},
    },
    "MA12": {
        "nom": "Rabat-Sale-Zemmour-Zaër",
        "nouvelles": {"MA04": {"regle": "AGReGATION", "note": "Devenu Rabat-Sale-Kenitra"}},
    },
    "MA13": {
        "nom": "Souss-Massa-Drâa",
        "nouvelles": {
            "MA08": {"regle": "PARTIEL", "note": "Zagora, Tinghir -> Drâa-Tafilalet"},
            "MA09": {"regle": "PARTIEL", "note": "Agadir, Taroudant, Tiznit -> Souss-Massa"},
        },
    },
    "MA14": {
        "nom": "Tadla-Azilal",
        "nouvelles": {"MA05": {"regle": "AGReGATION", "note": "Devenu Beni Mellal-Khenifra"}},
    },
    "MA15": {
        "nom": "Tanger-Tetouan",
        "nouvelles": {"MA01": {"regle": "AGReGATION", "note": "Cœur Tanger-Tetouan-Al Hoceïma"}},
    },
    "MA16": {
        "nom": "Taza-Al Hoceïma-Taounate",
        "nouvelles": {
            "MA01": {"regle": "PARTIEL", "note": "Al Hoceïma, Taounate -> Tanger-Tetouan-Al Hoceïma"},
            "MA03": {"regle": "PARTIEL", "note": "Taza -> Fes-Meknes"},
        },
    },
}


def build_dim_regions() -> pl.DataFrame:
    """Construit la table dimension regions (12 + 16 = 28 rows)."""
    rows = []
    for code, info in REGIONS_12.items():
        rows.append({
            "region_code": code,
            "region_nom_fr": info["nom"],
            "region_nom_ar": "",
            "niveau": "Region",
            "ancien_code": ",".join(info["ancien"]),
            "actif": True,
        })
    for code, info in REGIONS_16.items():
        rows.append({
            "region_code": code,
            "region_nom_fr": info["nom"],
            "region_nom_ar": "",
            "niveau": "Region (ancienne)",
            "ancien_code": code,
            "actif": False,
        })
    # National
    rows.append({
        "region_code": "MA00",
        "region_nom_fr": "Maroc (National)",
        "region_nom_ar": "",
        "niveau": "National",
        "ancien_code": "",
        "actif": True,
    })
    return pl.DataFrame(rows)


def ancien_to_nouveau(code_ancien: str) -> list[tuple[str, str, str]]:
    """
    Convertit un code region 16 -> liste de (code_12, regle, note).
    Pour les splits, retourne plusieurs possibilites avec leur regle.
    """
    info = REGIONS_16.get(code_ancien)
    if not info:
        return []
    return [
        (n_code, n_info["regle"], n_info["note"])
        for n_code, n_info in info["nouvelles"].items()
    ]


def aggregate_ancien_region(
    df: pl.DataFrame,
    region_col: str = "region_code",
    valeur_col: str = "valeur",
) -> pl.DataFrame:
    """
    Agrege les donnees des anciennes regions vers les nouvelles.

    Regles :
      - AGReGATION : la valeur est recopiee a l'identique vers la nouvelle region.
      - PARTIEL : la valeur est dupliquee avec flag 'ambig' (pas de cle de partage
        generique -- l'utilisateur doit fournir une ponderation externe).
    """
    mappings = []
    for code_16 in df[region_col].unique().to_list():
        if code_16 not in REGIONS_16:
            continue
        for n_code, regle, note in ancien_to_nouveau(code_16):
            mappings.append({"ancien": code_16, "nouveau": n_code, "regle": regle, "note": note})

    map_df = pl.DataFrame(mappings)

    result = df.join(map_df, left_on=region_col, right_on="ancien", how="inner").with_columns(
        pl.when(pl.col("regle") == "PARTIEL")
        .then(pl.lit("ambig_ancien_vers_nouveau"))
        .otherwise(pl.lit(None))
        .alias("qualite_flag")
    ).rename({"nouveau": region_col}).drop("ancien", "regle", "note")

    return result
