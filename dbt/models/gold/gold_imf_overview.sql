WITH ranked AS (
    SELECT
        indicator_id,
        indicator_name,
        unit,
        year,
        value,
        ROW_NUMBER() OVER (
            PARTITION BY indicator_id
            ORDER BY year DESC
        ) AS rn
    FROM {{ ref('silver_imf_clean') }}
)
SELECT
    indicator_id,
    indicator_name,
    unit,
    year AS latest_year,
    value AS latest_value
FROM ranked
WHERE rn = 1
ORDER BY indicator_id
