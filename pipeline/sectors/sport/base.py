"""Base constants for the SPORT module."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Indicator metadata for SPORT module
# Note: Very limited data in HCP BDS (only 1 national indicator: I202)
# Primary data source: FIFA rankings (football-ranking.com)
# ---------------------------------------------------------------------------
INDICATOR_CODES: dict[str, dict[str, str]] = {
    "I202": {
        "label": "Nombre de licenciés de la FRM",
        "domaine": "Football",
        "unite": "Nombre",
        "granularite": "national",
    },
    "FIFA_RANK": {
        "label": "Classement FIFA du Maroc",
        "domaine": "Football",
        "unite": "Rang",
        "granularite": "national",
    },
    "FIFA_POINTS": {
        "label": "Points FIFA du Maroc",
        "domaine": "Football",
        "unite": "Points",
        "granularite": "national",
    },
}

# FIFA ranking source
FIFA_URL = "https://football-ranking.com/matchByTeam?team=MAR"

# ---------------------------------------------------------------------------
# HCP BDS API configuration
# ---------------------------------------------------------------------------
HCP_BDS_BASE = "https://bds.hcp.ma/api/v1"
HCP_BDS_INDICATORS = f"{HCP_BDS_BASE}/indicators"
