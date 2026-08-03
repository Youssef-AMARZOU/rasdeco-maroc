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
    fiabilite,
    qualite_flag,
    fichier_source,
    date_insertion
FROM iceberg.rasd.economie_maroc
