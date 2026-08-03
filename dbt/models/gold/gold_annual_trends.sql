SELECT
    source_code,
    domaine_code,
    EXTRACT(YEAR FROM DATE(date)) AS year,
    COUNT(*) AS obs_count,
    ROUND(AVG(valeur), 4) AS avg_value,
    ROUND(MIN(valeur), 4) AS min_value,
    ROUND(MAX(valeur), 4) AS max_value
FROM {{ ref('silver_economie_clean') }}
GROUP BY
    source_code,
    domaine_code,
    EXTRACT(YEAR FROM DATE(date))
ORDER BY
    source_code,
    domaine_code,
    year
