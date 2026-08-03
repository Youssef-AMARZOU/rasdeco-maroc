WITH cleaned AS (
    SELECT
        indicator_id,
        indicator_name,
        unit,
        year,
        value
    FROM {{ ref('bronze_imf_weo') }}
    WHERE
        value IS NOT NULL
        AND indicator_id IS NOT NULL
)
SELECT
    indicator_id,
    indicator_name,
    unit,
    year,
    value
FROM cleaned
