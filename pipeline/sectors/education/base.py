"""Base constants for the EDUCATION module."""
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
# Indicator metadata for EDUCATION module
# Source: HCP BDS API /api/v1/subject-groups  (Theme: EC, Subject: S7)
# ---------------------------------------------------------------------------
INDICATOR_CODES: dict[str, dict[str, str]] = {
    # ── Enseignement préscolaire (T7.1) ───────────────────────────────────
    "I3807": {
        "label": "Élèves préscolaire traditionnel par région et province",
        "domaine": "Préscolaire",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3806": {
        "label": "Élèves préscolaire privée et public par régions et provinces",
        "domaine": "Préscolaire",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I4213": {
        "label": "Élèves préscolaire traditionnel",
        "domaine": "Préscolaire",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I1052": {
        "label": "Élèves du préscolaire moderne",
        "domaine": "Préscolaire",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Enseignement primaire public (T7.2) ───────────────────────────────
    "I3797": {
        "label": "Élèves primaire public par régions et provinces",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3826": {
        "label": "Enseignants primaire public par régions et provinces",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3803": {
        "label": "Écoles publiques par régions et provinces",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3210": {
        "label": "Élèves du primaire public",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I1762": {
        "label": "Taux de scolarisation du primaire",
        "domaine": "Primaire",
        "unite": "%",
        "granularite": "national",
    },
    "I957": {
        "label": "Nombre d'écoles publiques",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I959": {
        "label": "Nombre de classes du primaire public",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I958": {
        "label": "Nombre d'enseignants du primaire public",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I948": {
        "label": "Effectif des élèves du primaire public",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I947": {
        "label": "Effectif des élèves du primaire (total)",
        "domaine": "Primaire",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Enseignement secondaire collégial public (T7.3) ──────────────────
    "I3795": {
        "label": "Élèves secondaire collégial par régions et provinces",
        "domaine": "Collégial",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3825": {
        "label": "Enseignants secondaire collégial par régions et provinces",
        "domaine": "Collégial",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3801": {
        "label": "Établissements secondaire collégial par régions et provinces",
        "domaine": "Collégial",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I964": {
        "label": "Élèves du secondaire collégial public",
        "domaine": "Collégial",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Enseignement secondaire qualifiant public (T7.4) ─────────────────
    "I3799": {
        "label": "Élèves secondaire qualifiant par régions et provinces",
        "domaine": "Qualifiant",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3827": {
        "label": "Enseignants secondaire qualifiant par régions et provinces",
        "domaine": "Qualifiant",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3805": {
        "label": "Établissements secondaire qualifiant par régions et provinces",
        "domaine": "Qualifiant",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I1766": {
        "label": "Élèves du secondaire qualifiant public",
        "domaine": "Qualifiant",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Enseignement primaire privé (T7.5) ───────────────────────────────
    "I3796": {
        "label": "Élèves primaire privé par régions et provinces",
        "domaine": "Primaire privé",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3802": {
        "label": "Écoles privées par régions et provinces",
        "domaine": "Primaire privé",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I893": {
        "label": "Élèves du primaire privé",
        "domaine": "Primaire privé",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Enseignement secondaire privé (T7.6) ────────────────────────────
    "I3794": {
        "label": "Élèves secondaire privé par régions et provinces",
        "domaine": "Secondaire privé",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3798": {
        "label": "Enseignants secondaire privé par régions et provinces",
        "domaine": "Secondaire privé",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3800": {
        "label": "Établissements secondaire privé par régions et provinces",
        "domaine": "Secondaire privé",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3804": {
        "label": "Classes secondaire privé par régions et provinces",
        "domaine": "Secondaire privé",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I913": {
        "label": "Élèves du secondaire privé",
        "domaine": "Secondaire privé",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Statistiques des bacheliers (T7.7) ──────────────────────────────
    "I4285": {
        "label": "Candidats baccalauréat par région",
        "domaine": "Baccalauréat",
        "unite": "Nombre",
        "granularite": "region",
    },
    "I4281": {
        "label": "Admis baccalauréat par région",
        "domaine": "Baccalauréat",
        "unite": "Nombre",
        "granularite": "region",
    },
    "I924": {
        "label": "Nombre de candidats au baccalauréat",
        "domaine": "Baccalauréat",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I919": {
        "label": "Nombre d'admis au baccalauréat",
        "domaine": "Baccalauréat",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Formation professionnelle (T7.8) ────────────────────────────────
    "I1781": {
        "label": "Écoles de formation professionnelle",
        "domaine": "Formation",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I1782": {
        "label": "Élèves de la formation professionnelle",
        "domaine": "Formation",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Budget (T7.9) ───────────────────────────────────────────────────
    "I1821": {
        "label": "Budget de l'éducation nationale",
        "domaine": "Budget",
        "unite": "MDH",
        "granularite": "national",
    },
    "I4282": {
        "label": "Budget de l'enseignement supérieur",
        "domaine": "Budget",
        "unite": "MDH",
        "granularite": "national",
    },

    # ── Scolarisation (T7.10) ───────────────────────────────────────────
    "I4193": {
        "label": "Taux d'achèvement avec redoublement par cycle",
        "domaine": "Scolarisation",
        "unite": "%",
        "granularite": "national",
    },
    "I4194": {
        "label": "Taux de transition du collégial au qualifiant",
        "domaine": "Scolarisation",
        "unite": "%",
        "granularite": "national",
    },
    "I4187": {
        "label": "Taux de transition du primaire au collégial",
        "domaine": "Scolarisation",
        "unite": "%",
        "granularite": "national",
    },
}

# ---------------------------------------------------------------------------
# HCP BDS API configuration
# ---------------------------------------------------------------------------
HCP_BDS_BASE = "https://bds.hcp.ma/api/v1"
HCP_BDS_INDICATORS = f"{HCP_BDS_BASE}/indicators"
