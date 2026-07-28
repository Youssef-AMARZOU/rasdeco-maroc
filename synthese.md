# Morocco Data Pipeline — Session Summary

## What was built

**Pipeline data engineering** (`scripts/imf_export/`) pour extraire, structurer et exporter les indicateurs macroeconomiques du Maroc :

| Fichier | Role |
|---|---|
| `data_parser.py` | Parse le JSON brut FMI WEO, filtre MAR (17 indicateurs), clean JSON output |
| `excel_formatter.py` | Excel 4 sheets : time-series matrix, World Bank, definitions, PIB historique |
| `main.py` | Orchestrateur CLI avec mode inline ou fichier |

## Donnees integrees

- **FMI (WEO)** : 17 indicateurs, 1980–2029 (50 ans), dont PIB, inflation, chomage, dette, balance courante, population
- **Banque Mondiale** : esperance de vie, PIB, croissance, chomage, inflation (2024–2025)
- **PIB historique** : Worldometers, 1960–2023

## Livrables generes

| Fichier | Taille | Contenu |
|---|---|---|
| `morocco_imf_data.json` | ~64 KB | JSON clean, hierarchique, pret pour API/DB |
| `morocco_data.xlsx` | ~19 KB | 4 sheets, format pro (headers figes, bandes, color scales, graphique) |

## Points cles Maroc (2024)

| Indicateur | 2024 | 2029 (proj.) |
|---|---|---|
| Croissance PIB | 3.3% | 3.9% |
| PIB (Mds USD) | 152.4 | 258.4 |
| PIB/hab (USD) | 4 763 | 6 493 |
| Inflation | 1.2% | 2.0% |
| Chomage | 12.2% | 12.2% |
| Dette/PIB | 68.2% | 62.3% |
| Balance courante (%PIB) | -2.7% | -4.3% |
| Population (millions) | 32.0 | 32.8 |

## Commandes

```bash
cd scripts/imf_export
python main.py                          # donnees inline
python main.py -i weo.json -o ./out     # depuis fichier brut
```

## Dashboard Update (Frontend)

Fichiers modifies dans le dashboard Next.js :

| Fichier | Changement |
|---|---|
| `src/lib/rasd-data.ts` | Module economie : series temporelles remplacees par donnees FMI WEO 1980-2029. 6 nouveaux indicateurs ajoutes (PIB/hab, balance courante, population, exports, imports, investissement). KPIs recalcules. |
| `src/app/page.tsx` | 6 nouvelles entrees KPI_EXPLANATIONS ajoutees. Valeurs mises a jour pour PIB croissance (4.0%), inflation (2.0%), chomage (12.2%). |

Build Next.js : OK (compiled successfully in 16.7s)

## Data Verification

Validation script (`validate_dashboard.py`) : **11 indicateurs FMI x 7 annees cibles** verifies — correspondance parfaite entre `data_parser.py` et `rasd-data.ts`.

## Tables Excel organizees

`scripts/imf_export/tables/` — 9 fichiers generes automatiquement :

| Fichier | Theme |
|---|---|
| `01-Croissance_PIB.xlsx` | PIB, croissance, PIB/hab, deflateur |
| `02-Inflation_Prix.xlsx` | IPC |
| `03-Emploi.xlsx` | Chomage |
| `04-Finances_Publiques.xlsx` | Recettes, depenses, deficit, dette |
| `05-Commerce_Exterieur.xlsx` | Balance courante, exports, imports |
| `06-Investissement.xlsx` | Investissement total |
| `07-Demographie.xlsx` | Population |
| `09-Tableau_de_Bord.xlsx` | Recap tous indicateurs 2024-2029 |
| `08-Recherche_Macro.bas` | Module VBA (recherche, surlignage) |

Chaque fichier : color scale (rouge/blanc/vert), headers figes, bandes alternees, format professionnel.

Macros VBA incluses :
- `SearchAllTables` — recherche dans toutes les feuilles
- `SearchCurrentSheet` — recherche feuille active
- `HighlightSearchTerm` — surligne en jaune
- `ClearHighlights` — efface surlignage