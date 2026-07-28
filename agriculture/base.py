"""Base constants for the AGRICULTURE module."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Region mapping: 12 current regions (post-2015) → codes used by HCP BDS
# ---------------------------------------------------------------------------
REGIONS_12: dict[int, str] = {
    5293: "Tanger-Tétouan-Al Hoceïma",
    5294: "L'Oriental",
    5295: "Fès-Meknès",
    5296: "Rabat-Salé-Kénitra",
    5297: "Béni Mellal-Khénifra",
    5298: "Casablanca-Settat",
    5299: "Marrakech-Safi",
    5300: "Drâa-Tafilalet",
    5301: "Souss-Massa",
    5302: "Guelmim-Oued Noun",
    5303: "Laâyoune-Sakia El Hamra",
    5304: "Dakhla-Oued Ed-Dahab",
}

# 16 pre-2015 regions (for historical RGPH data)
REGIONS_16: dict[int, str] = {
    1001: "Tanger-Tétouan",
    1002: "L'Oriental",
    1003: "Fès-Boulemane",
    1004: "Rabat-Salé-Zemmour-Zaer",
    1005: "Gharb-Chrarda-Béni Hsen",
    1006: "Meknès-Tafilalet",
    1007: "Tadla-Azilal",
    1008: "Casablanca-Settat",
    1009: "Marrakech-Tensift-Al Haouz",
    1010: "Souss-Massa-Draa",
    1011: "Guelmim-Smara",
    1012: "Laâyoune-Boujdour-Sakia El Hamra",
    1013: "Oued Ed-Dahab-Lagouira",
    1014: "Chaouia-Ouardigha",
    1015: "Doukkala-Abda",
    1016: "Taza-Al Hoceïma-Taounate",
}

# ---------------------------------------------------------------------------
# Indicator metadata for AGRICULTURE module
# Source: HCP BDS API /api/v1/subject-groups  (Theme: EN, Subject: S13)
# ---------------------------------------------------------------------------
INDICATOR_CODES: dict[str, dict[str, str]] = {
    # ── Superficies cultivées (T13.1) ──────────────────────────────────────
    "I4343": {
        "label": "Superficie cultivée des céréales par région et province",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "region_province",
    },
    "I4344": {
        "label": "Superficie cultivée des légumineuses par région et province",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "region_province",
    },
    "I4521": {
        "label": "Évolution superficie cultures maraîchères",
        "domaine": "Superficies",
        "unite": "%",
        "granularite": "national",
    },
    "I4483": {
        "label": "Évolution superficie fruitière",
        "domaine": "Superficies",
        "unite": "%",
        "granularite": "national",
    },
    "I4481": {
        "label": "Évolution superficie agrumes",
        "domaine": "Superficies",
        "unite": "%",
        "granularite": "national",
    },
    "I480": {
        "label": "Superficie cultures fourragères",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "national",
    },
    "I463": {
        "label": "Superficie laissée en jachère",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "national",
    },
    "I457": {
        "label": "Superficie agricole utile",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "national",
    },
    "I460": {
        "label": "Superficie cultures en sous-étages",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "national",
    },
    "I455": {
        "label": "Superficie des plantations denses",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "national",
    },
    "I479": {
        "label": "Superficie cultivée des légumineuses",
        "domaine": "Superficies",
        "unite": "Ha",
        "granularite": "national",
    },

    # ── Productions Agricoles (T13.2) ─────────────────────────────────────
    "I3824": {
        "label": "Évolution production céréales",
        "domaine": "Productions",
        "unite": "%",
        "granularite": "national",
    },
    "I4341": {
        "label": "Production céréales par région et province",
        "domaine": "Productions",
        "unite": "Qté",
        "granularite": "region_province",
    },
    "I4342": {
        "label": "Production légumineuses par région et province",
        "domaine": "Productions",
        "unite": "Qté",
        "granularite": "region_province",
    },
    "I4392": {
        "label": "Production oléagineuses par région et province",
        "domaine": "Productions",
        "unite": "Qté",
        "granularite": "region_province",
    },
    "I4501": {
        "label": "Évolution production maraîchères",
        "domaine": "Productions",
        "unite": "%",
        "granularite": "national",
    },
    "I4482": {
        "label": "Évolution production fruitière",
        "domaine": "Productions",
        "unite": "%",
        "granularite": "national",
    },
    "I465": {
        "label": "Évolution production agrumes",
        "domaine": "Productions",
        "unite": "%",
        "granularite": "national",
    },

    # ── Élevage (T13.3) ───────────────────────────────────────────────────
    "I4345": {
        "label": "Évolution effectif du cheptel",
        "domaine": "Élevage",
        "unite": "%",
        "granularite": "national",
    },
    "I616": {
        "label": "Effectif animaux de trait",
        "domaine": "Élevage",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I4346": {
        "label": "Abattages contrôlés (Nombre de têtes)",
        "domaine": "Élevage",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I4347": {
        "label": "Abattages contrôlés (Poids de viande)",
        "domaine": "Élevage",
        "unite": "Qté",
        "granularite": "national",
    },
    "I736": {
        "label": "Production de la viande rouge",
        "domaine": "Élevage",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1247": {
        "label": "Production de la viande blanche",
        "domaine": "Élevage",
        "unite": "Qté",
        "granularite": "national",
    },
    "I735": {
        "label": "Production d'oeufs",
        "domaine": "Élevage",
        "unite": "Qté",
        "granularite": "national",
    },

    # ── Forêt (T13.4) ─────────────────────────────────────────────────────
    "I4348": {
        "label": "Production forestière",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1244": {
        "label": "Production de bois d'oeuvre",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1243": {
        "label": "Production de bois industriel",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1245": {
        "label": "Production de bois de feu",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1246": {
        "label": "Production de liège",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1242": {
        "label": "Production de l'écorce à Tanin",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },
    "I1241": {
        "label": "Production d'alpha",
        "domaine": "Forêt",
        "unite": "Qté",
        "granularite": "national",
    },

    # ── Water / Environment (EE theme, S22) ────────────────────────────────
    "I1363": {
        "label": "ONEP Ventes par région",
        "domaine": "Eau",
        "unite": "m³",
        "granularite": "region",
    },
    "I1362": {
        "label": "ONEP Production par région",
        "domaine": "Eau",
        "unite": "m³",
        "granularite": "region",
    },
    "I1361": {
        "label": "ONEP Nombre d'abonnés par région",
        "domaine": "Eau",
        "unite": "Nombre",
        "granularite": "region",
    },
    "I1383": {
        "label": "Ressources en eau",
        "domaine": "Eau",
        "unite": "Milliards m³",
        "granularite": "national",
    },
    "I1382": {
        "label": "Ressources en eau - Précipitation",
        "domaine": "Eau",
        "unite": "Milliards m³",
        "granularite": "national",
    },
    "I1381": {
        "label": "Ressources en eau - Évapotranspiration",
        "domaine": "Eau",
        "unite": "Milliards m³",
        "granularite": "national",
    },
    "I4461": {
        "label": "Bilan pollution eau pesticides par bassin hydraulique",
        "domaine": "Eau",
        "unite": "Qté",
        "granularite": "bassin",
    },

    # ── Barrage / pluviometry (local raw files) ────────────────────────────
    # These are collected from local barrage files, not HCP BDS
    "BARRAGE_PLUVIO": {
        "label": "Pluviométrie journalière des barrages",
        "domaine": "Pluviométrie",
        "unite": "mm",
        "granularite": "station",
    },
    "BARRAGE_RESERVOIR": {
        "label": "Volume de réservoir des barrages",
        "domaine": "Réservoir",
        "unite": "Millions m³",
        "granularite": "station",
    },
}

# ---------------------------------------------------------------------------
# Drought campaigns (rupture variable for modeling)
# Based on historical rainfall patterns in Morocco
# ---------------------------------------------------------------------------
DROUGHT_CAMPAIGNS: list[int] = [
    1980, 1981, 1982, 1983, 1984, 1985, 1986, 1990, 1991, 1992, 1993, 1994,
    1995, 1997, 1999, 2000, 2001, 2002, 2007, 2008, 2015, 2016, 2017, 2022, 2023,
]

# ---------------------------------------------------------------------------
# HCP BDS API configuration
# ---------------------------------------------------------------------------
HCP_BDS_BASE = "https://bds.hcp.ma/api/v1"
HCP_BDS_INDICATORS = f"{HCP_BDS_BASE}/indicators"
