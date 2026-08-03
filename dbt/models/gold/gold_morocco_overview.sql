SELECT
    'PIB_CROISSANCE' AS kpi_id,
    code_indicateur,
    valeur,
    date
FROM {{ ref('silver_economie_clean') }}
WHERE code_indicateur = 'PIB.CROISSANCE'
UNION ALL
SELECT
    'INFLATION' AS kpi_id,
    code_indicateur,
    valeur,
    date
FROM {{ ref('silver_economie_clean') }}
WHERE code_indicateur = 'IPC.GLISSEMENT'
UNION ALL
SELECT
    'CHOMAGE' AS kpi_id,
    code_indicateur,
    valeur,
    date
FROM {{ ref('silver_economie_clean') }}
WHERE code_indicateur = 'CHOMAGE.TAUX'
ORDER BY kpi_id, date DESC
