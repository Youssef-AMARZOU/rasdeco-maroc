"""Base constants for the SANTE module."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Region mapping: 12 current regions (post-2015)
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

# ---------------------------------------------------------------------------
# Indicator metadata for SANTE module
# Source: HCP BDS API  (Theme: RC, Subject: S8)
# ---------------------------------------------------------------------------
INDICATOR_CODES: dict[str, dict[str, str]] = {
    # ── Infrastructures Sanitaires (T8.1) ─────────────────────────────────
    "I3770": {
        "label": "Nombre formations de soins de santé de base par régions et provinces",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3771": {
        "label": "Nombre d'hôpitaux publics par région et province",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I3772": {
        "label": "Nombre de lits des hôpitaux publics par régions et provinces",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "NLFC2": {
        "label": "Nombre de lits fonctionnels par catégorie Hôpital et par région et province",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "NLFD": {
        "label": "Nombre de lits fonctionnels par Discipline et par région et province",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I238": {
        "label": "Nombre de centres de santé",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I234": {
        "label": "Nombre de dispensaires ruraux",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I257": {
        "label": "Nombre d'hôpitaux",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I259": {
        "label": "Capacité litière existante",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I262": {
        "label": "Capacité litière fonctionnelle",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I235": {
        "label": "Nombre de cliniques privées",
        "domaine": "Infrastructure",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Personnel médical (T8.2) ─────────────────────────────────────────
    "I3773": {
        "label": "Nombre de médecins par région et province",
        "domaine": "Personnel",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I629": {
        "label": "Nombre de médecins",
        "domaine": "Personnel",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I266": {
        "label": "Nombre de pharmaciens",
        "domaine": "Personnel",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I268": {
        "label": "Nombre d'infirmiers",
        "domaine": "Personnel",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Production de la Santé (T8.3) ────────────────────────────────────
    "I5019": {
        "label": "Nombre de femmes utilisant contraception par région et province",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I440": {
        "label": "Nombre d'admissions des malades",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I438": {
        "label": "Nombre d'accouchements dans les formations sanitaires publiques",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I436": {
        "label": "Nombre de morts-nés",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I435": {
        "label": "Nombre de décès maternels",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I570": {
        "label": "Nombre de consultations curatives",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I427": {
        "label": "Nombre de vaccins",
        "domaine": "Production",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Statistiques de morbidité (T8.4) ─────────────────────────────────
    "I1484": {
        "label": "Quotient de mortalité infanto juvénile",
        "domaine": "Morbidité",
        "unite": "‰",
        "granularite": "national",
    },
    "I1483": {
        "label": "Quotient de mortalité infantile",
        "domaine": "Morbidité",
        "unite": "‰",
        "granularite": "national",
    },
    "I1482": {
        "label": "Taux de mortalité maternelle",
        "domaine": "Morbidité",
        "unite": "‰",
        "granularite": "national",
    },
    "I3241": {
        "label": "Nombre de cas de maladies signalés",
        "domaine": "Morbidité",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I4365": {
        "label": "Vaccination des enfants de moins de 5 ans",
        "domaine": "Morbidité",
        "unite": "%",
        "granularite": "national",
    },
    "I3212": {
        "label": "Taux de vaccination des enfants âgés de 12-23 mois",
        "domaine": "Morbidité",
        "unite": "%",
        "granularite": "national",
    },

    # ── COVID-19 rupture variable ────────────────────────────────────────
    # Not an indicator code but documented as rupture for modeling
}

# COVID-19 years as rupture variable
COVID_YEARS: list[int] = [2020, 2021, 2022]

# ---------------------------------------------------------------------------
# HCP BDS API configuration
# ---------------------------------------------------------------------------
HCP_BDS_BASE = "https://bds.hcp.ma/api/v1"
HCP_BDS_INDICATORS = f"{HCP_BDS_BASE}/indicators"
