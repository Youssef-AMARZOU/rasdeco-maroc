WITH cleaned AS (
    SELECT
        date,
        date_label,
        COALESCE(region_code, 'NATIONAL') AS region_code,
        domaine_code,
        code_indicateur,
        valeur,
        unite,
        source_code,
        version_serie,
        CASE
            WHEN fiabilite >= 3 THEN 'haute'
            WHEN fiabilite >= 1 THEN 'moyenne'
            ELSE 'faible'
        END AS fiabilite_label,
        date_insertion
    FROM {{ ref('bronze_economie_maroc') }}
    WHERE
        valeur IS NOT NULL
        AND code_indicateur IS NOT NULL
        AND date IS NOT NULL
)
SELECT
    date,
    date_label,
    region_code,
    domaine_code,
    code_indicateur,
    valeur,
    unite,
    source_code,
    version_serie,
    fiabilite_label,
    date_insertion
FROM cleaned
