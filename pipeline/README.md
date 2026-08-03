# Pipeline — RASD Maroc

Module Python centralisé pour la collecte, transformation, vérification et export des données macroéconomiques et sectorielles du Maroc.

## Structure

```
pipeline/
├── collect/          # Collecteurs officiels (HCP, BAM, Finances, Office des Changes, DataGov)
├── sectors/          # Modules sectoriels métier
│   ├── agriculture/  # 7 cultures : blé, orge, maïs, agrumes, olives, maraîchage, betterave
│   ├── economie/     # PIB, inflation, chômage, SMIG, taux directeur
│   ├── education/    # Effectifs scolaires, universités, taux scolarisation
│   ├── sante/        # Hôpitaux, lits, personnels médicaux par région
│   ├── social/       # Ménages, logement, pauvreté
│   └── sport/        # Fédérations, licenciés, médailles, infrastructures
├── transform/        # Scripts ETL, nettoyage, ingestion, migration Iceberg
├── export/           # Génération Excel, PDF, JSON, push Hugging Face
│   └── imf/          # Module FMI WEO (data_parser, excel_formatter, main)
├── verify/           # Contrôle qualité, audit KPIs, vérification vs sources officielles
└── utils/            # Utilitaires partagés (source_tiers, bigquery, graph_api, etc.)
```

## Commandes rapides

```bash
# Depuis la racine du projet
make pipeline          # Lancer le pipeline complet
make verify            # Vérifier la cohérence des KPIs
make export-imf        # Régénérer les exports FMI WEO

# Depuis ce dossier
python -m collect.hcp           # Collecter données HCP
python -m collect.bam           # Collecter données BAM
python -m verify.verify_kpi_values  # Vérifier les KPIs
```

## Sources de données

| Source | Tier | Fiabilité | Données |
|--------|------|-----------|---------|
| HCP | 1 | ★★★★★ | Emploi, IPC, PIB, comptes nationaux |
| BAM | 1 | ★★★★★ | Taux directeur, réserves, OPCVM |
| Ministère Finances | 1 | ★★★★★ | Budget, déficit, dette publique |
| Office des Changes | 1 | ★★★★★ | IDE, balance commerciale, MRE |
| DataGov.ma | 1 | ★★★★★ | 389 jeux open data |
| FMI WEO | 2 | ★★★☆☆ | Prévisions macro 1980–2029 |
| Banque Mondiale | 2 | ★★★☆☆ | Indicateurs de développement |
