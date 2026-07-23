# RASD-Maroc : Observatoire Prdictif Multi-Domaines du Maroc

> Collecte, transformation, prvision et visualisation de donnesconomiques marocaines depuis des sources officielles.

---

## Vue d'ensemble

RASD-Maroc est un pipeline complet qui :
1. **Collecte** les donnes depuis 5 sources officielles marocaines (461 fichiers)
2. **Transforme** les formats htrognes (XLS, XLSX, CSV) en un schma unifi
3. **Prvoit** les sries temporelles via SARIMA, Prophet et baselines
4. **Visualise** via un dashboard Dash interactif (carte + sries + comparateur)
5. **Charge** en BigQuery pour l'analyse et le reporting

### Rsultats actuels

| Source | Lignes | Fichiers | Indicateurs |
|--------|--------|----------|-------------|
| DataGov.ma | 179 477 | 103 | 39 |
| HCP (Haut-Commissariat au Plan) | 28 254 | 40 | 4 |
| Finances Publiques | 20 998 | 15 | 29 |
| BAM (Banque Al-Maghrib) | 13 500 | 2 | 5 |
| Office des Changes | 1 306 | 2 | 1 |
| **TOTAL** | **243 535** | **162** | **78** |

---

## Sources de donnes

### 1. HCP — Haut-Commissariat au Plan
- **URL** : `data.gov.ma`
- **Format** : XLSX (cross-table avec dates en colonnes)
- **Contenu** : PIB trimestriel, IPC, chmage, emploi, indicators macro conomiques
- **Priode** : 2005 — 2023
- **Fichiers** : 40 (i_1.1  i_1.25 + sous-indicateurs)
- **Particularit** : Chaque fichier contient une feuille Metadata avec le nom de l'indicateur, la priodicit et l'unit

### 2. BAM — Banque Al-Maghrib
- **URL** : `data.gov.ma`
- **Format** : XLSX (encodage OLE2 binaire, 225+ colonnes mensuelles)
- **Contenu** : OPCVM (montraires et non-montraires) — encours, actifs, passifs, titres
- **Priode** : Janvier 2005 — Septembre 2023 (225 points mensuels)
- **Fichiers** : 2
- **Particularit** : Format cross-table dtendu, lecture directe via openpyxl

### 3. Finances Publiques
- **URL** : `data.gov.ma`
- **Format** : XLS (BIFF binaire, xlrd requis)
- **Contenu** :
  - Dette publique (exterieure, du trsor, totale)
  - Budget de l'Etat (rpartition par administration, codeconomique, code fonctionnel, rgion)
  - Statistiques conomiques et financires (change, march des capitaux)
- **Priode** : 2006 — 2014
- **Fichiers** : 24
- **Particularit** : Formats multiples — multi-feuilles ADM/REG/CE/CF, format vertical, format OECD

### 4. DataGov.ma
- **URL** : `data.gov.ma`
- **Format** : XLSX/CSV
- **Contenu** : Hydrologie (dbits, prcipitations), emploi, infrastructure
- **Priode** : Variables
- **Fichiers** : 363 (103 avec donnes exploitables)
- **Particularit** : Fichiers HTML dguiss en .xls dtects via magic bytes

### 5. Office des Changes
- **URL** : `data.gov.ma`
- **Format** : XLS/CSV
- **Contenu** : IDE (investissements directs trangers), balance des paiements
- **Priode** : Variables
- **Fichiers** : 5 (2 avec donnes exploitables)

---

## Architecture technique

```
rasdeco-maroc/
├── economie/
│   ├── collect/                    # Scripts de collecte par source
│   │   ├── collect_hcp.py
│   │   ├── collect_bkam.py
│   │   ├── collect_finances.py
│   │   ├── collect_datagov.py
│   │   └── collect_office_des_changes.py
│   ├── transform/                  # Pipeline de transformation
│   │   ├── pipeline.py             # Orchestrateur principal
│   │   ├── schema.py               # Schma fact_indicateurs (13 colonnes)
│   │   ├── regions.py              # Mapping 16 → 12 régions (2015)
│   │   ├── bigquery_loader.py      # Chargement BQ (partitionné + clusterisé)
│   │   └── parsers/
│   │       ├── smart_xls.py        # Lecteur adaptatif (magic bytes: OLE2/ZIP/HTML)
│   │       ├── utils_xls.py        # Cross-table parser (annuel + trimestriel)
│   │       ├── parse_hcp.py        # Parser HCP
│   │       ├── parse_bkam.py       # Parser BAM (openpyxl direct)
│   │       ├── parse_finances.py   # Parser Finances (xlrd legacy)
│   │       ├── parse_datagov.py    # Parser DataGov
│   │       └── parse_office_changes.py
│   ├── forecasting/                # Prvision temporelle
│   │   ├── pipeline.py             # Walk-forward strict
│   │   ├── sarima_model.py         # SARIMA via auto_arima
│   │   ├── prophet_model.py        # Prophet (MCMC, uncertainty_samples=100)
│   │   ├── baselines.py            # Naive saisonnier, Drift, MA
│   │   ├── walk_forward.py         # Validation walk-forward
│   │   ├── metrics.py              # MAE, RMSE, MAPE, coverage IC
│   │   └── forecast_to_bq.py       # Export prvisions → BigQuery
│   ├── dashboard/                  # Dashboard interactif
│   │   ├── app.py                  # Dash (3 onglets: carte, sries, comparateur)
│   │   ├── bq.py                   # Cache TTL BigQuery (cachetools)
│   │   ├── assets/
│   │   │   └── regions_maroc.geojson
│   │   └── requirements.txt
│   └── report/                     # Gnration de rapport
│       └── generate_report.py
├── functions/
│   └── refresh_pipeline/           # Cloud Function (Scheduler)
│       ├── main.py                 # Collecte → Nettoyage → BQ → Prvisions
│       └── requirements.txt
├── Dockerfile                      # Cloud Run (gunicorn, port dynamique)
└── data/raw/economie/              # 461 fichiers bruts collects
```

---

## Schma de donnes

### Table `fact_indicateurs` (BigQuery)

| Colonne | Type | Description |
|---------|------|-------------|
| `date` | DATE | Date de l'observation (clé de partition) |
| `date_label` | STRING | Libell original de la date |
| `region_code` | STRING | Code région (MA00=national, MA01-MA12) |
| `domaine_code` | STRING | Domaine thmatique |
| `code_indicateur` | STRING | Code normalisé de l'indicateur |
| `valeur` | FLOAT64 | Valeur numérique |
| `unite` | STRING | Unité (MAD, %PIB, INDICE, %...) |
| `source_code` | STRING | Source (HCP, BAM, FIN, OC, DATAGOV) |
| `version_serie` | STRING | Version de série (rebasages HCP) |
| `fiabilite` | INT64 | Score de fiabilité (1-5) |
| `qualite_flag` | STRING | Flag qualité (NULL par défaut) |
| `fichier_source` | STRING | Chemin du fichier source |
| `date_insertion` | DATETIME | Horodatage d'insertion |

### Table `previsions` (BigQuery)

| Colonne | Type | Description |
|---------|------|-------------|
| `date` | DATE | Date prévisionnelle |
| `code_indicateur` | STRING | Code indicateur |
| `yhat` | FLOAT64 | Point forecast |
| `yhat_lower` | FLOAT64 | Borne inférieure IC 80% |
| `yhat_upper` | FLOAT64 | Borne supérieure IC 80% |
| `modele` | STRING | Modèle utilisé (SARIMA/Prophet/Naive) |

---

## Indicateurs cles

### Macroconomie
- **PIB.TRIM.VOL** — Produit Intrieur Brut trimestriel (volume, 55 137 points)
- **PIB.ANNUEL.VOL** — PIB annuel (volume, 688 points)
- **PIB.CROISSANCE** — Taux de croissance du PIB (891 points)

### Prix
- **IPC.INDICE** — Indice des Prix  la Consommation (17 813 points)
- **IPC.GLISSEMENT** — IPC glissement (539 points)

### Monnaie et Finance
- **BAM.ACTIF** — Bilan des actifs de la BAM (900 points, Jan 2005 — Sept 2023)
- **BAM.PASSIF** — Bilan des passifs de la BAM (900 points)
- **BAM.TITRES** — Encours de titres (900 points)
- **BAM.OPCVM.ENCOURS** — Encours OPCVM (10 125 points)

### Commerce extrieur
- **EXPORTATIONS** — Exportations (1 070 points)
- **IDE.FLUX** — Investissements Directs Etrangers (675 points)
- **CHANGE.USD** — Taux de change USD/MAD (1 451 points)

### Finances publiques
- **DETTE.PUBLIQUE** — Dette publique (4 279 points)
- **DEFICIT.BUDGET** — Déficit budgétaire (10 788 points)
- **DEPENSES.TOTAL** — Dépenses totales (324 points)

### Emploi
- **EMPLOI.VOLUME** — Volume de l'emploi (3 597 points)

---

## Dmarrage rapide

### Collecte + Transformation
```bash
# Installer les dpendances
pip install polars openpyxl xlrd requests tqdm

# Collecter les donnes (461 fichiers)
python -m economie.run_all

# Transformer + parser
python -m economie.transform.pipeline --load
```

### Dashboard local
```bash
cd economie/dashboard
pip install -r requirements.txt
python app.py
# → http://localhost:8050
```

### Prvisions
```bash
python -m economie.forecasting.forecast_to_bq
```

### Docker (Cloud Run)
```bash
docker build -t dashboard-eco .
docker run -p 8080:8080 dashboard-eco
```

---

## Dploiement Cloud

### Cloud Run (Dashboard)
```bash
gcloud builds submit --tag europe-west1-docker.pkg.dev/rasd-maroc/apps/dashboard-eco:latest .
gcloud run deploy dashboard-eco \
  --image europe-west1-docker.pkg.dev/rasd-maroc/apps/dashboard-eco:latest \
  --region europe-west1 --allow-unauthenticated \
  --memory 1Gi --cpu 1 --min-instances 0 --max-instances 3
```

### Cloud Function (Rafraichissement)
```bash
gcloud functions deploy refresh-pipeline \
  --gen2 --runtime python312 --region europe-west1 \
  --source functions/refresh_pipeline --entry-point refresh \
  --trigger-http --timeout 540s --memory 1Gi
```

### Cloud Scheduler
```bash
# Hebdomadaire : lundi 06:00 UTC
gcloud scheduler jobs create http refresh-eco-weekly \
  --location europe-west1 --schedule "0 6 * * 1" \
  --uri "$(gcloud functions describe refresh-pipeline --gen2 --region europe-west1 --format 'value(serviceConfig.uri)')"
```

---

## Limites connues

- **Pas de donnes rgionales** : 100% des observations sont au niveau national (MA00). Les indicateurs rgionaux n'ont pas encore t intgrs.
- **Dates htrognes** : Certains fichiers DatGov utilisent des formats de date non standard (texte arabe), resulting des dates invalides dans la colonne `date`.
- **Indicateurs en arabe** : Les noms d'indicateurs DataGov ne sont pas encore normalis en franais.
- **Fiabilit uniforme** : Le score de fiabilit est fixe  2 pour toutes les donnes (calibration en cours).
- **Priode Finance limite** : Les donnes budgétaires couvrent 2006-2014 uniquement.

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Collecte | Python, requests, retry/backoff |
| Parsing | Polars, openpyxl, xlrd, smart_xls (magic bytes) |
| Transformation | Polars pipeline (dedup, imputation, 16→12 régions) |
| Prvision | SARIMA (auto_arima), Prophet, baselines saisonnieres |
| Validation | Walk-forward strict (pas de split aléatoire) |
| Dashboard | Dash/Plotly (choroplèthe, séries, comparateur double axe) |
| Stockage | BigQuery (partitionné par date, clusterisé par région+indicateur) |
| Infra | Cloud Run, Cloud Function, Cloud Scheduler |
| CI/CD | Docker multi-stage, gunicorn |

---

## Licence

Données sources : Open Data Maroc (data.gov.ma) — Licence Ouverte.
Code : MIT

---

## Auteurs

**Youssef Amarzou** — [LinkedIn](https://linkedin.com/in/youssef-amarzou) | [GitLab](https://gitlab.com/Youssef-AMARZOU)

Projet de recherche : Observatoire Prdictif Multi-Domaines du Maroc
