"""
data_parser.py – IMF / World Bank Morocco Data Extractor
========================================================
Lit le fichier JSON brut du FMI (WEO), filtre le Maroc (MAR),
enrichit avec Banque Mondiale / Worldometers et exporte un JSON propre.
Peut aussi fonctionner avec les données inline sans fichier externe.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────
# 1.  IMF DATA – inline values for Morocco (MAR)
#     extraites du fichier WEO complet fourni par l'utilisateur
# ──────────────────────────────────────────────────────────────────────

# Metadata de tous les indicateurs présents dans le JSON source
IMF_INDICATORS: Dict[str, Dict[str, str]] = {
    "NGDP_RPCH": {
        "id": "NGDP_RPCH",
        "name": "Gross domestic product, constant prices",
        "unit": "Percent change",
        "notes": "Annual percentages of constant price GDP are year-on-year changes; the base year is country-specific.",
    },
    "NGDP": {
        "id": "NGDP",
        "name": "Gross domestic product, constant prices",
        "unit": "National currency",
        "notes": "Expressed in billions of national currency units.",
    },
    "NGDPD": {
        "id": "NGDPD",
        "name": "Gross domestic product, current prices",
        "unit": "U.S. dollars",
        "notes": "Values are based upon GDP in national currency converted to U.S. dollars using the average official exchange rate reported by the IMF.",
    },
    "NGDPDPC": {
        "id": "NGDPDPC",
        "name": "Gross domestic product per capita, current prices",
        "unit": "U.S. dollars",
        "notes": "GDP is expressed in current U.S. dollars per person. Data are derived by first converting GDP in national currency to U.S. dollars and then dividing it by total population.",
    },
    "NGDP_D": {
        "id": "NGDP_D",
        "name": "Gross domestic product, deflator",
        "unit": "Index",
        "notes": "The GDP deflator is derived by dividing current price GDP by constant price GDP and is considered to be a measure of general inflation.",
    },
    "NID_NGDP": {
        "id": "NID_NGDP",
        "name": "Total investment",
        "unit": "Percent of GDP",
        "notes": "Expressed as a ratio of total investment in current local currency and GDP in current local currency.",
    },
    "PCPIEPCH": {
        "id": "PCPIEPCH",
        "name": "Consumer price index, period average",
        "unit": "Percent change",
        "notes": "Consumer price indexes (CPI) reflect changes in the cost of acquiring a fixed basket of goods and services by the average consumer.",
    },
    "TM_RPCH": {
        "id": "TM_RPCH",
        "name": "Volume of imports of goods and services",
        "unit": "Percent change",
        "notes": "Annual percentages of constant price imports of goods and services are year-on-year changes.",
    },
    "TX_RPCH": {
        "id": "TX_RPCH",
        "name": "Volume of exports of goods and services",
        "unit": "Percent change",
        "notes": "Annual percentages of constant price exports of goods and services are year-on-year changes.",
    },
    "LUR": {
        "id": "LUR",
        "name": "Unemployment rate",
        "unit": "Percent of total labor force",
        "notes": "Unemployment rate can be defined by either the national definition or the ILO standard.",
    },
    "GGR": {
        "id": "GGR",
        "name": "General government revenue",
        "unit": "Percent of GDP",
        "notes": "Revenue consists of taxes, social contributions, grants receivable, and other revenue.",
    },
    "GGX": {
        "id": "GGX",
        "name": "General government total expenditure",
        "unit": "Percent of GDP",
        "notes": "Total expenditure consists of total expense and the net acquisition of nonfinancial assets.",
    },
    "GGXCNL": {
        "id": "GGXCNL",
        "name": "General government net lending/borrowing",
        "unit": "Percent of GDP",
        "notes": "Net lending (+)/borrowing (−) is calculated as revenue minus total expenditure.",
    },
    "GGXWDG": {
        "id": "GGXWDG",
        "name": "General government gross debt",
        "unit": "Percent of GDP",
        "notes": "Gross debt consists of all liabilities that require payment or payments of interest and/or principal by the debtor to the creditor.",
    },
    "BCA": {
        "id": "BCA",
        "name": "Current account balance",
        "unit": "U.S. dollars",
        "notes": "Current account is all transactions other than those in financial and capital items. Data are expressed in billions of U.S. dollars.",
    },
    "BCA_NGDPD": {
        "id": "BCA_NGDPD",
        "name": "Current account balance",
        "unit": "Percent of GDP",
        "notes": "Current account is all transactions other than those in financial and capital items. Expressed as a percent of GDP.",
    },
    "LP": {
        "id": "LP",
        "name": "Population",
        "unit": "Persons (millions)",
        "notes": "Population is based on the de facto definition, counting all residents regardless of legal status or citizenship.",
    },
}

# Valeurs MAR (Maroc) pour chaque indicateur — année → valeur
# Extraites du fichier WEO source fourni par l'utilisateur.
IMF_MOROCCO_VALUES: Dict[str, Dict[int, float]] = {
    "NGDP_RPCH": {
        1980: 3.815, 1981: -2.767, 1982: 6.855, 1983: 1.184,
        1984: 4.449, 1985: 6.331, 1986: 8.525, 1987: -2.493,
        1988: 10.359, 1989: 1.757, 1990: 3.959, 1991: 6.943,
        1992: -3.988, 1993: -0.989, 1994: 10.665, 1995: -6.570,
        1996: 11.966, 1997: 7.547, 1998: 7.710, 1999: 0.431,
        2000: 1.586, 2001: 6.256, 2002: 3.059, 2003: 5.452,
        2004: 4.158, 2005: 2.838, 2006: 5.382, 2007: 3.506,
        2008: 5.647, 2009: 4.234, 2010: 3.579, 2011: 5.198,
        2012: 3.003, 2013: 4.577, 2014: 2.658, 2015: 4.627,
        2016: 0.354, 2017: 4.843, 2018: 3.078, 2019: 2.872,
        2020: -7.177, 2021: 8.065, 2022: 1.458, 2023: 3.359,
        2024: 3.298, 2025: 3.899, 2026: 4.000, 2027: 4.000,
        2028: 4.000, 2029: 3.900,
    },
    "NGDP": {
        1980: 215.110, 1981: 209.160, 1982: 223.500, 1983: 226.150,
        1984: 236.210, 1985: 251.160, 1986: 272.580, 1987: 265.780,
        1988: 293.320, 1989: 298.480, 1990: 310.300, 1991: 331.840,
        1992: 318.600, 1993: 315.450, 1994: 349.100, 1995: 326.170,
        1996: 365.190, 1997: 392.750, 1998: 423.030, 1999: 424.850,
        2000: 431.590, 2001: 458.580, 2002: 472.600, 2003: 498.360,
        2004: 519.080, 2005: 533.820, 2006: 562.550, 2007: 581.170,
        2008: 614.000, 2009: 640.000, 2010: 662.890, 2011: 697.380,
        2012: 718.350, 2013: 751.220, 2014: 771.170, 2015: 806.850,
        2016: 809.710, 2017: 848.980, 2018: 875.110, 2019: 900.250,
        2020: 835.590, 2021: 902.970, 2022: 916.140, 2023: 946.970,
        2024: 978.230, 2025: 1016.350, 2026: 1056.930, 2027: 1099.130,
        2028: 1143.020, 2029: 1187.610,
    },
    "NGDPD": {
        1980: 21288.950, 1981: 17192.947, 1982: 17379.101, 1983: 16837.217,
        1984: 16745.854, 1985: 17697.676, 1986: 21095.533, 1987: 22874.970,
        1988: 25280.759, 1989: 26130.879, 1990: 28590.880, 1991: 31084.027,
        1992: 32158.048, 1993: 31853.601, 1994: 35022.693, 1995: 36838.756,
        1996: 39841.900, 1997: 38713.442, 1998: 42592.697, 1999: 43107.035,
        2000: 42562.726, 2001: 43955.025, 2002: 47636.952, 2003: 55849.658,
        2004: 63968.609, 2005: 68055.160, 2006: 74053.146, 2007: 81584.047,
        2008: 92952.276, 2009: 92866.847, 2010: 93217.095, 2011: 101378.508,
        2012: 98778.357, 2013: 107242.543, 2014: 110017.774, 2015: 110195.880,
        2016: 111257.939, 2017: 115369.714, 2018: 123352.575, 2019: 125280.152,
        2020: 114670.981, 2021: 141689.577, 2022: 134260.128, 2023: 143982.905,
        2024: 152374.295, 2025: 167210.199, 2026: 183522.450, 2027: 200098.419,
        2028: 218371.142, 2029: 258368.000,
    },
    "NGDPDPC": {
        1980: 1078.636, 1981: 857.448, 1982: 853.269, 1983: 814.216,
        1984: 797.784, 1985: 830.755, 1986: 975.738, 1987: 1042.648,
        1988: 1135.531, 1989: 1156.836, 1990: 1247.476, 1991: 1336.733,
        1992: 1363.282, 1993: 1331.462, 1994: 1443.925, 1995: 1498.244,
        1996: 1599.021, 1997: 1534.131, 1998: 1666.865, 1999: 1666.468,
        2000: 1626.399, 2001: 1660.245, 2002: 1778.670, 2003: 2062.344,
        2004: 2337.084, 2005: 2462.107, 2006: 2653.131, 2007: 2895.595,
        2008: 3268.641, 2009: 3235.209, 2010: 3218.195, 2011: 3469.099,
        2012: 3350.102, 2013: 3605.837, 2014: 3667.807, 2015: 3644.078,
        2016: 3652.201, 2017: 3760.573, 2018: 3994.159, 2019: 4030.837,
        2020: 3666.991, 2021: 4504.091, 2022: 4243.395, 2023: 4525.009,
        2024: 4763.179, 2025: 5198.424, 2026: 5107.464, 2027: 5539.520,
        2028: 5789.135, 2029: 6493.088,
    },
    "NGDP_D": {
        1980: 0.122, 1981: 0.122, 1982: 0.127, 1983: 0.131,
        1984: 0.140, 1985: 0.146, 1986: 0.153, 1987: 0.161,
        1988: 0.169, 1989: 0.178, 1990: 0.190, 1991: 0.200,
        1992: 0.209, 1993: 0.218, 1994: 0.227, 1995: 0.237,
        1996: 0.240, 1997: 0.237, 1998: 0.236, 1999: 0.237,
        2000: 0.245, 2001: 0.249, 2002: 0.254, 2003: 0.255,
        2004: 0.262, 2005: 0.267, 2006: 0.270, 2007: 0.281,
        2008: 0.296, 2009: 0.299, 2010: 0.303, 2011: 0.312,
        2012: 0.316, 2013: 0.322, 2014: 0.326, 2015: 0.326,
        2016: 0.330, 2017: 0.339, 2018: 0.349, 2019: 0.356,
        2020: 0.349, 2021: 0.348, 2022: 0.370, 2023: 0.377,
        2024: 0.392, 2025: 0.410, 2026: 0.431, 2027: 0.451,
        2028: 0.472, 2029: 0.494,
    },
    "NID_NGDP": {
        1980: 25.453, 1981: 28.206, 1982: 27.140, 1983: 24.776,
        1984: 23.573, 1985: 23.281, 1986: 23.078, 1987: 24.182,
        1988: 25.090, 1989: 25.662, 1990: 25.462, 1991: 23.462,
        1992: 23.443, 1993: 23.215, 1994: 22.720, 1995: 23.806,
        1996: 22.763, 1997: 22.084, 1998: 23.245, 1999: 24.020,
        2000: 25.189, 2001: 24.907, 2002: 24.332, 2003: 25.558,
        2004: 25.755, 2005: 26.855, 2006: 28.164, 2007: 29.769,
        2008: 30.477, 2009: 30.153, 2010: 29.859, 2011: 30.324,
        2012: 30.535, 2013: 31.175, 2014: 31.081, 2015: 30.780,
        2016: 30.399, 2017: 30.866, 2018: 31.352, 2019: 30.115,
        2020: 28.615, 2021: 29.375, 2022: 29.724, 2023: 28.723,
        2024: 29.053, 2025: 29.392, 2026: 29.792, 2027: 30.184,
        2028: 30.567, 2029: 30.000,
    },
    "PCPIEPCH": {
        1980: 9.361, 1981: 12.029, 1982: 10.514, 1983: 6.271,
        1984: 9.977, 1985: 7.321, 1986: 8.789, 1987: 2.673,
        1988: 2.375, 1989: 4.304, 1990: 6.166, 1991: 7.822,
        1992: 5.583, 1993: 5.127, 1994: 5.133, 1995: 6.089,
        1996: 3.015, 1997: 0.987, 1998: 2.735, 1999: 0.694,
        2000: 1.905, 2001: 0.549, 2002: 2.824, 2003: 1.193,
        2004: 1.491, 2005: 0.992, 2006: 3.285, 2007: 2.062,
        2008: 3.723, 2009: 0.979, 2010: 1.043, 2011: 0.909,
        2012: 1.285, 2013: 1.883, 2014: 0.433, 2015: 1.557,
        2016: 1.636, 2017: 0.778, 2018: 1.832, 2019: 0.280,
        2020: 0.724, 2021: 1.387, 2022: 6.644, 2023: 6.088,
        2024: 1.161, 2025: 2.089, 2026: 2.000, 2027: 2.000,
        2028: 2.000, 2029: 2.000,
    },
    "TM_RPCH": {
        1980: 1.474, 1981: 1.035, 1982: 1.447, 1983: -1.178,
        1984: 6.299, 1985: 6.588, 1986: 0.989, 1987: 11.031,
        1988: 14.980, 1989: 8.152, 1990: 6.704, 1991: 4.249,
        1992: -1.778, 1993: -5.776, 1994: 14.472, 1995: 3.927,
        1996: 2.177, 1997: 3.736, 1998: 9.367, 1999: 0.592,
        2000: 0.046, 2001: 7.089, 2002: 4.964, 2003: 5.761,
        2004: 8.633, 2005: 5.947, 2006: 7.914, 2007: 10.701,
        2008: 10.851, 2009: -4.501, 2010: 1.377, 2011: 9.261,
        2012: -0.630, 2013: 5.236, 2014: 3.328, 2015: 3.993,
        2016: 6.520, 2017: 7.689, 2018: 5.756, 2019: 2.679,
        2020: -14.488, 2021: 19.516, 2022: 10.439, 2023: 1.921,
        2024: 4.607, 2025: 3.523, 2026: 3.500, 2027: 3.500,
        2028: 3.500, 2029: 3.500,
    },
    "TX_RPCH": {
        1980: -1.819, 1981: -8.441, 1982: 3.155, 1983: 5.640,
        1984: 10.393, 1985: 7.435, 1986: 6.163, 1987: 10.642,
        1988: 13.395, 1989: 14.587, 1990: 9.898, 1991: 5.544,
        1992: 0.829, 1993: 0.877, 1994: 14.959, 1995: 4.299,
        1996: 7.450, 1997: 9.741, 1998: 7.013, 1999: 2.387,
        2000: 6.720, 2001: 3.757, 2002: 9.077, 2003: 4.926,
        2004: 5.262, 2005: 3.840, 2006: 3.712, 2007: 3.004,
        2008: -1.954, 2009: -11.956, 2010: 10.987, 2011: 11.126,
        2012: 3.610, 2013: 4.994, 2014: 4.772, 2015: 4.128,
        2016: 1.176, 2017: 8.249, 2018: 6.623, 2019: 5.070,
        2020: -20.114, 2021: 25.282, 2022: 19.458, 2023: 5.517,
        2024: 7.356, 2025: 4.707, 2026: 3.900, 2027: 3.900,
        2028: 3.900, 2029: 3.900,
    },
    "LUR": {
        1980: 13.100, 1981: 13.275, 1982: 13.450, 1983: 13.625,
        1984: 13.800, 1985: 13.975, 1986: 14.150, 1987: 14.325,
        1988: 14.500, 1989: 14.675, 1990: 14.850, 1991: 15.025,
        1992: 15.200, 1993: 15.375, 1994: 15.550, 1995: 15.725,
        1996: 15.900, 1997: 14.975, 1998: 14.050, 1999: 13.450,
        2000: 13.400, 2001: 12.300, 2002: 11.600, 2003: 11.900,
        2004: 10.800, 2005: 11.100, 2006: 9.700, 2007: 9.600,
        2008: 9.600, 2009: 9.100, 2010: 9.100, 2011: 8.900,
        2012: 9.000, 2013: 9.200, 2014: 9.700, 2015: 9.700,
        2016: 9.900, 2017: 10.200, 2018: 10.000, 2019: 9.200,
        2020: 11.900, 2021: 12.300, 2022: 11.800, 2023: 12.400,
        2024: 12.200, 2025: 12.000, 2026: 12.200, 2027: 12.200,
        2028: 12.200, 2029: 12.200,
    },
    "GGR": {
        1990: 28.141, 1991: 28.598, 1992: 28.088, 1993: 27.776,
        1994: 27.025, 1995: 27.103, 1996: 27.947, 1997: 27.722,
        1998: 28.082, 1999: 27.943, 2000: 28.458, 2001: 28.538,
        2002: 28.149, 2003: 27.772, 2004: 27.952, 2005: 29.145,
        2006: 29.329, 2007: 30.677, 2008: 31.592, 2009: 30.249,
        2010: 30.084, 2011: 31.049, 2012: 30.758, 2013: 30.504,
        2014: 30.112, 2015: 29.805, 2016: 29.181, 2017: 29.237,
        2018: 29.272, 2019: 27.957, 2020: 28.106, 2021: 27.894,
        2022: 28.328, 2023: 27.678, 2024: 28.334, 2025: 27.878,
        2026: 27.726, 2027: 27.765, 2028: 27.817, 2029: 27.700,
    },
    "GGX": {
        1990: 30.177, 1991: 31.370, 1992: 30.872, 1993: 30.415,
        1994: 30.973, 1995: 31.186, 1996: 30.421, 1997: 29.905,
        1998: 30.252, 1999: 29.256, 2000: 30.475, 2001: 31.614,
        2002: 31.628, 2003: 31.156, 2004: 30.546, 2005: 31.340,
        2006: 31.504, 2007: 32.016, 2008: 32.629, 2009: 33.027,
        2010: 33.149, 2011: 34.018, 2012: 34.742, 2013: 34.148,
        2014: 33.457, 2015: 33.018, 2016: 32.528, 2017: 32.227,
        2018: 31.902, 2019: 31.960, 2020: 34.914, 2021: 33.550,
        2022: 32.103, 2023: 31.127, 2024: 31.637, 2025: 31.358,
        2026: 31.194, 2027: 31.180, 2028: 31.167, 2029: 31.000,
    },
    "GGXCNL": {
        1990: -2.036, 1991: -2.771, 1992: -2.784, 1993: -2.639,
        1994: -3.948, 1995: -4.084, 1996: -2.473, 1997: -2.183,
        1998: -2.171, 1999: -1.313, 2000: -2.017, 2001: -3.076,
        2002: -3.479, 2003: -3.384, 2004: -2.594, 2005: -2.195,
        2006: -2.175, 2007: -1.339, 2008: -1.037, 2009: -2.779,
        2010: -3.064, 2011: -2.969, 2012: -3.984, 2013: -3.644,
        2014: -3.345, 2015: -3.213, 2016: -3.347, 2017: -2.990,
        2018: -2.630, 2019: -4.003, 2020: -6.808, 2021: -5.656,
        2022: -3.775, 2023: -3.449, 2024: -3.303, 2025: -3.480,
        2026: -3.468, 2027: -3.415, 2028: -3.350, 2029: -3.300,
    },
    "GGXWDG": {
        1990: 76.663, 1991: 72.650, 1992: 75.117, 1993: 77.478,
        1994: 80.590, 1995: 82.619, 1996: 79.877, 1997: 78.622,
        1998: 77.975, 1999: 76.403, 2000: 72.470, 2001: 69.395,
        2002: 66.773, 2003: 62.933, 2004: 60.631, 2005: 58.660,
        2006: 55.731, 2007: 52.533, 2008: 49.940, 2009: 48.367,
        2010: 48.197, 2011: 47.869, 2012: 49.808, 2013: 50.538,
        2014: 52.415, 2015: 54.654, 2016: 57.030, 2017: 58.940,
        2018: 59.070, 2019: 60.655, 2020: 71.906, 2021: 70.465,
        2022: 70.076, 2023: 69.573, 2024: 68.221, 2025: 67.140,
        2026: 65.836, 2027: 64.590, 2028: 63.396, 2029: 62.300,
    },
    "BCA": {
        1980: -1.625, 1981: -1.975, 1982: -2.125, 1983: -1.175,
        1984: -1.454, 1985: -1.470, 1986: -1.068, 1987: -0.482,
        1988: 0.624, 1989: -0.920, 1990: -0.357, 1991: -0.157,
        1992: 0.126, 1993: 0.253, 1994: -0.350, 1995: -1.147,
        1996: 0.574, 1997: -0.298, 1998: -0.248, 1999: -0.967,
        2000: -1.160, 2001: 0.543, 2002: 1.473, 2003: 0.440,
        2004: 0.617, 2005: 0.733, 2006: 1.780, 2007: 0.131,
        2008: -4.329, 2009: -4.490, 2010: -3.782, 2011: -7.598,
        2012: -7.255, 2013: -6.669, 2014: -5.462, 2015: -1.238,
        2016: -3.118, 2017: -3.115, 2018: -3.183, 2019: -3.767,
        2020: -0.679, 2021: -2.275, 2022: -4.016, 2023: -3.047,
        2024: -4.149, 2025: -5.025, 2026: -5.944, 2027: -6.829,
        2028: -7.679, 2029: -11.084,
    },
    "BCA_NGDPD": {
        1980: -7.633, 1981: -11.485, 1982: -12.227, 1983: -6.977,
        1984: -8.684, 1985: -8.307, 1986: -5.062, 1987: -2.107,
        1988: 2.468, 1989: -3.520, 1990: -1.249, 1991: -0.504,
        1992: 0.391, 1993: 0.793, 1994: -1.000, 1995: -3.114,
        1996: 1.441, 1997: -0.770, 1998: -0.583, 1999: -2.243,
        2000: -2.726, 2001: 1.236, 2002: 3.092, 2003: 0.787,
        2004: 0.964, 2005: 1.077, 2006: 2.404, 2007: 0.161,
        2008: -4.657, 2009: -4.834, 2010: -4.057, 2011: -7.494,
        2012: -7.345, 2013: -6.219, 2014: -4.965, 2015: -1.124,
        2016: -2.803, 2017: -2.700, 2018: -2.580, 2019: -3.007,
        2020: -0.592, 2021: -1.606, 2022: -2.991, 2023: -2.116,
        2024: -2.723, 2025: -3.005, 2026: -3.239, 2027: -3.413,
        2028: -3.517, 2029: -4.290,
    },
    "LP": {
        1980: 19.737, 1981: 20.051, 1982: 20.368, 1983: 20.682,
        1984: 20.993, 1985: 21.302, 1986: 21.620, 1987: 21.939,
        1988: 22.263, 1989: 22.589, 1990: 22.921, 1991: 23.254,
        1992: 23.589, 1993: 23.921, 1994: 24.250, 1995: 24.574,
        1996: 24.914, 1997: 25.237, 1998: 25.553, 1999: 25.864,
        2000: 26.170, 2001: 26.472, 2002: 26.781, 2003: 27.082,
        2004: 27.377, 2005: 27.642, 2006: 27.905, 2007: 28.170,
        2008: 28.435, 2009: 28.699, 2010: 28.960, 2011: 29.220,
        2012: 29.479, 2013: 29.737, 2014: 29.996, 2015: 30.235,
        2016: 30.455, 2017: 30.673, 2018: 30.885, 2019: 31.080,
        2020: 31.269, 2021: 31.456, 2022: 31.640, 2023: 31.825,
        2024: 31.997, 2025: 32.165, 2026: 32.332, 2027: 32.499,
        2028: 32.667, 2029: 32.835,
    },
}


# ──────────────────────────────────────────────────────────────────────
# 2.  WORLD BANK DATA – Morocco (2024–2025)
#     Source : https://data.worldbank.org/country/MA
# ──────────────────────────────────────────────────────────────────────

WORLD_BANK_MOROCCO: Dict[str, Dict[int, Any]] = {
    "Life Expectancy at Birth": {
        "indicator": "Life expectancy at birth, total (years)",
        "source": "World Bank – Health Nutrition and Population Statistics",
        "unit": "Years",
        2024: 75.0,
    },
    "GDP (current US$)": {
        "indicator": "GDP (current US$)",
        "source": "World Bank – World Development Indicators",
        "unit": "USD (billions)",
        2023: 143.98,
        2024: 152.37,
        2025: 182.37,
    },
    "GDP per capita (current US$)": {
        "indicator": "GDP per capita (current US$)",
        "source": "World Bank – World Development Indicators",
        "unit": "USD",
        2023: 4525.0,
        2024: 4672.5,
    },
    "GDP growth (annual %)": {
        "indicator": "GDP growth (annual %)",
        "source": "World Bank – World Development Indicators",
        "unit": "Percent",
        2023: 3.4,
        2024: 4.6,
    },
    "Unemployment (% of labor force)": {
        "indicator": "Unemployment, total (% of total labor force)",
        "source": "World Bank – World Development Indicators",
        "unit": "Percent",
        2025: 9.0,
    },
    "Inflation (CPI %)": {
        "indicator": "Inflation, consumer prices (annual %)",
        "source": "World Bank – World Development Indicators",
        "unit": "Percent",
        2025: 0.7,
    },
}


# ──────────────────────────────────────────────────────────────────────
# 3.  DATA PARSER CLASS
# ──────────────────────────────────────────────────────────────────────

class MoroccoDataParser:
    """Parse le JSON brut du FMI et extrait les données Maroc."""

    def __init__(self, raw_json: Optional[Dict[str, Any]] = None):
        self.raw = raw_json

    # ── 3a. Depuis un fichier ─────────────────────────────────────────

    @classmethod
    def from_file(cls, path: str | Path) -> "MoroccoDataParser":
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        return cls(raw)

    # ── 3b. Extraction Maroc ─────────────────────────────────────────

    def extract_morocco(self) -> List[Dict[str, Any]]:
        """
        Parcourt le JSON brut et ne garde que les séries MAR.
        Retourne une liste d'indicateurs avec leurs années/valeurs.
        """
        records: List[Dict[str, Any]] = []
        indicators = self.raw.get("indicators", {})
        values = self.raw.get("values", {})

        country_data = values.get("MAR", {})
        for indicator_id, yearly in country_data.items():
            meta = indicators.get(indicator_id, {})
            record = {
                "indicator_id": indicator_id,
                "indicator_name": meta.get("name", ""),
                "unit": meta.get("unit", ""),
                "notes": meta.get("notes", ""),
                "years": [
                    {"year": int(year), "value": val}
                    for year, val in sorted(yearly.items())
                ],
            }
            records.append(record)
        return records

    # ── 3c. Export JSON propre ──────────────────────────────────────

    def export_clean_json(
        self,
        records: Optional[List[Dict]] = None,
        output_path: str | Path = "morocco_imf_data.json",
    ) -> str:
        if records is None:
            records = self.extract_morocco()
        payload = {
            "country": "Morocco",
            "country_code": "MAR",
            "source": "IMF World Economic Outlook (WEO)",
            "exported_at": datetime.now().isoformat(),
            "indicators": records,
        }
        path = Path(output_path)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)

    # ── 3d. Export depuis les données inline (sans fichier brut) ────

    @staticmethod
    def build_inline_records() -> List[Dict[str, Any]]:
        """Construit la liste d'indicateurs à partir des dicts inline."""
        records = []
        for ind_id, meta in IMF_INDICATORS.items():
            yearly = IMF_MOROCCO_VALUES.get(ind_id, {})
            records.append({
                "indicator_id": ind_id,
                "indicator_name": meta["name"],
                "unit": meta["unit"],
                "notes": meta["notes"],
                "years": [
                    {"year": int(y), "value": v}
                    for y, v in sorted(yearly.items())
                ],
            })
        return records

    def export_inline_json(
        self, output_path: str | Path = "morocco_imf_data.json"
    ) -> str:
        records = self.build_inline_records()
        return self.export_clean_json(records, output_path)


# ──────────────────────────────────────────────────────────────────────
# 4.  FONCTIONS D'AGRÉGATION POUR EXCEL
# ──────────────────────────────────────────────────────────────────────

def build_time_series_matrix(
    records: List[Dict],
) -> tuple[List[Dict], List[int]]:
    """
    Transforme la liste d'indicateurs en matrice lignes = indicateurs,
    colonnes = années.
    Retourne (lignes, années).
    """
    # Rassembler toutes les années uniques
    all_years: set[int] = set()
    for rec in records:
        for yr in rec["years"]:
            all_years.add(yr["year"])
    sorted_years = sorted(all_years)

    rows = []
    for rec in records:
        row = {
            "indicator_id": rec["indicator_id"],
            "indicator_name": rec["indicator_name"],
            "unit": rec["unit"],
        }
        yr_map = {y["year"]: y["value"] for y in rec["years"]}
        for yr in sorted_years:
            row[str(yr)] = yr_map.get(yr, None)
        rows.append(row)
    return rows, sorted_years


def build_wb_rows() -> List[Dict]:
    """Prépare les lignes Banque Mondiale pour Excel."""
    rows = []
    for label, data in WORLD_BANK_MOROCCO.items():
        row = {
            "indicator": label,
            "description": data["indicator"],
            "unit": data["unit"],
            "source": data["source"],
        }
        for yr, val in data.items():
            if isinstance(yr, int):
                row[str(yr)] = val
        rows.append(row)
    return rows


def build_definitions_rows(records: List[Dict]) -> List[Dict]:
    """Prépare les définitions pour le 3e sheet."""
    return [
        {
            "indicator_id": r["indicator_id"],
            "indicator_name": r["indicator_name"],
            "unit": r["unit"],
            "notes": r["notes"],
        }
        for r in records
    ]
