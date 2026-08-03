"""Base constants for the SOCIAL module."""
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
# Indicator metadata for SOCIAL module
# Source: HCP BDS API /api/v1/subject-groups  (Themes: PD, RC, MT)
# ---------------------------------------------------------------------------
INDICATOR_CODES: dict[str, dict[str, str]] = {
    # ── Population & Démographie (PD theme) ────────────────────────────────
    "I1587": {
        "label": "Projections de la population des régions par milieu 2014 à 2030",
        "domaine": "Population",
        "unite": "Nombre",
        "granularite": "region",
    },
    "I2782": {
        "label": "Projections de la population des provinces et préfectures",
        "domaine": "Population",
        "unite": "Nombre",
        "granularite": "region_province",
    },
    "I1481": {
        "label": "Population selon les groupes d'âge et le sexe",
        "domaine": "Population",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I2818": {
        "label": "Population âgée de 15 ans et plus selon l'état matrimonial",
        "domaine": "Population",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I1486": {
        "label": "Taux de fécondité des femmes",
        "domaine": "Démographie",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I1488": {
        "label": "Taux de fécondité des adolescentes (15-19 ans)",
        "domaine": "Démographie",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I2788": {
        "label": "Taux de prévalence contraceptive",
        "domaine": "Démographie",
        "unite": "%",
        "granularite": "national",
    },
    "I2789": {
        "label": "Âge moyen au premier mariage",
        "domaine": "Démographie",
        "unite": "Années",
        "granularite": "national",
    },
    "I2830": {
        "label": "Quotient de mortalité infantile",
        "domaine": "Démographie",
        "unite": "‰",
        "granularite": "national",
    },
    "I4386": {
        "label": "Demandes enregistrées de mariage des mineurs par milieu",
        "domaine": "Démographie",
        "unite": "Nombre",
        "granularite": "milieu",
    },
    "I4362": {
        "label": "Demandes enregistrées de mariage des mineurs par milieu",
        "domaine": "Démographie",
        "unite": "Nombre",
        "granularite": "milieu",
    },
    "I4386": {
        "label": "Demandes enregistrées de mariage des mineurs par milieu",
        "domaine": "Démographie",
        "unite": "Nombre",
        "granularite": "milieu",
    },
    "I4386": {
        "label": "Demandes enregistrées de mariage des mineurs par milieu",
        "domaine": "Démographie",
        "unite": "Nombre",
        "granularite": "milieu",
    },

    # ── Conditions sociales — Pauvreté (RC > S15) ─────────────────────────
    "TP": {
        "label": "Taux de pauvreté selon la région et la province",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "region_province",
    },
    "I4390": {
        "label": "Taux de pauvreté seuil national par région",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "region",
    },
    "I4389": {
        "label": "Taux de pauvreté seuil national par milieu",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "milieu",
    },
    "I1493": {
        "label": "Taux de pauvreté",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "national",
    },
    "I2932": {
        "label": "Profondeur de la pauvreté absolue",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "national",
    },
    "I2933": {
        "label": "Sévérité de la pauvreté absolue",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "national",
    },
    "I2937": {
        "label": "Taux de vulnérabilité",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "national",
    },
    "I3753": {
        "label": "Part ménages eau courante par région et milieu",
        "domaine": "Conditions de vie",
        "unite": "%",
        "granularite": "region_milieu",
    },
    "I3752": {
        "label": "Part ménages disposant électricité par région et milieu",
        "domaine": "Conditions de vie",
        "unite": "%",
        "granularite": "region_milieu",
    },
    "I3755": {
        "label": "Part ménages raccordés eau courante",
        "domaine": "Conditions de vie",
        "unite": "%",
        "granularite": "national",
    },
    "I3754": {
        "label": "Part ménages équipés système évacuation amélioré",
        "domaine": "Conditions de vie",
        "unite": "%",
        "granularite": "national",
    },
    "I1530": {
        "label": "Dépense annuelle moyenne par personne",
        "domaine": "Conditions de vie",
        "unite": "DH",
        "granularite": "national",
    },
    "I4391": {
        "label": "Taux pauvreté seuil national par sexe",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "sexe",
    },
    "I4388": {
        "label": "Taux pauvreté seuil national par chef de ménage",
        "domaine": "Pauvreté",
        "unite": "%",
        "granularite": "categorie",
    },

    # ── Marché du travail (MT theme) ──────────────────────────────────────
    "I1462": {
        "label": "Taux de chômage selon le Milieu, le sexe et les régions",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "region_milieu_sexe",
    },
    "I3287": {
        "label": "Taux de chômage par sexe et région",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "region_sexe",
    },
    "IMT_TXCH_02": {
        "label": "Taux de chômage selon les Provinces/Préfectures et le Milieu",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "province_milieu",
    },
    "IMT_TXACT_02": {
        "label": "Taux d'activité selon les Provinces/Préfectures et le Milieu",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "province_milieu",
    },
    "IMT_TXEMP_02": {
        "label": "Taux d'emploi selon les Provinces/Préfectures et le Milieu",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "province_milieu",
    },
    "I4242": {
        "label": "Durée de chômage par milieu (Trimestriel)",
        "domaine": "Emploi",
        "unite": "Mois",
        "granularite": "milieu",
    },
    "I4247": {
        "label": "Taux de chômage selon diplôme et milieu (Trimestriel)",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "milieu",
    },
    "I4249": {
        "label": "Taux de chômage selon tranches d'âge et milieu (Trimestriel)",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "milieu",
    },
    "I40": {
        "label": "Taux net d'activité",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "national",
    },
    "I39": {
        "label": "Taux brut d'activité",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "national",
    },
    "I2868": {
        "label": "Effectif des chômeurs",
        "domaine": "Emploi",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I1465": {
        "label": "Taux d'emploi des 15 ans et plus",
        "domaine": "Emploi",
        "unite": "%",
        "granularite": "national",
    },

    # ── Enquêtes ménages (RC > S17) ──────────────────────────────────────
    "I2797": {
        "label": "Enquête Nationale sur la Distribution des Revenus et des Dépenses des Ménages",
        "domaine": "Conditions de vie",
        "unite": "DH",
        "granularite": "national",
    },
    "I2802": {
        "label": "Accouchement milieu surveillé",
        "domaine": "Santé ménages",
        "unite": "%",
        "granularite": "national",
    },
    "I2803": {
        "label": "Soins prénatals",
        "domaine": "Santé ménages",
        "unite": "%",
        "granularite": "national",
    },
    "I2804": {
        "label": "Consulté personnel médico-sanitaire",
        "domaine": "Santé ménages",
        "unite": "%",
        "granularite": "national",
    },
    "I2832": {
        "label": "Couverture vaccinale",
        "domaine": "Santé ménages",
        "unite": "%",
        "granularite": "national",
    },
    "I4234": {
        "label": "Insecurity alimentaire",
        "domaine": "Conditions de vie",
        "unite": "%",
        "granularite": "national",
    },
    "I4232": {
        "label": "Émaciation <5ans",
        "domaine": "Santé ménages",
        "unite": "%",
        "granularite": "national",
    },

    # ── Bâtiment (RC > S24) — ADC by region ──────────────────────────────
    "I3456": {
        "label": "Surface bâtie (ADC National)",
        "domaine": "Bâtiment",
        "unite": "m²",
        "granularite": "national",
    },
    "I3457": {
        "label": "Nombre logements (ADC National)",
        "domaine": "Bâtiment",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I3458": {
        "label": "Autorisations construire (ADC National)",
        "domaine": "Bâtiment",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Secteur informel (RC > S17.4) ────────────────────────────────────
    "I2806": {
        "label": "Secteur informel - Nombre d'unités",
        "domaine": "Informel",
        "unite": "Nombre",
        "granularite": "national",
    },
    "I2807": {
        "label": "Secteur informel - Effectif",
        "domaine": "Informel",
        "unite": "Nombre",
        "granularite": "national",
    },

    # ── Justice (RC > S9) ─────────────────────────────────────────────────
    "I24": {
        "label": "Nombre de magistrats",
        "domaine": "Justice",
        "unite": "Nombre",
        "granularite": "national",
    },
}

# ---------------------------------------------------------------------------
# Census anchor points for SOCIAL modeling (linear interpolation only)
# Based on RGPH 2004, RGPH 2014, RGPH 2024
# ---------------------------------------------------------------------------
RGPH_ANCHORS: dict[str, dict[int, float]] = {
    # Example: poverty rate by region (%)
    "I4390": {
        2004: 18.9,  # RGPH 2004 national
        2014: 15.3,  # RGPH 2014 national
        # Regional values would be filled from actual data
    },
}

# ---------------------------------------------------------------------------
# HCP BDS API configuration
# ---------------------------------------------------------------------------
HCP_BDS_BASE = "https://bds.hcp.ma/api/v1"
HCP_BDS_INDICATORS = f"{HCP_BDS_BASE}/indicators"
