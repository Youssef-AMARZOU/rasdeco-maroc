WITH ranked AS (
    SELECT
        code_indicateur AS indicator_code,
        date,
        valeur AS value,
        unite AS unit,
        source_code,
        ROW_NUMBER() OVER (
            PARTITION BY code_indicateur
            ORDER BY date DESC
        ) AS rn
    FROM {{ ref('silver_economie_clean') }}
)
SELECT
    indicator_code,
    date,
    value,
    unit,
    source_code
FROM ranked
WHERE rn = 1
ORDER BY indicator_code
