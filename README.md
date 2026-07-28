# RASD-Maroc : Observatoire Prédictif Multi-Domaines du Maroc

> Collecte, transformation, prévision et visualisation de données économiques marocaines — 243 535 observations, 17 indicateurs FMI WEO, 50 ans (1980–2029).

---

## 📊 Plateformes

| Plateforme | Lien | Usage |
|---|---|---|
| **GitHub** | https://github.com/Youssef-AMARZOU/rasdeco-maroc | Code source, Releases, Packages |
| **GitLab** | https://gitlab.com/Youssef-AMARZOU/radar-maroc | Miroir CI/CD |
| **Hugging Face Space** | https://ysfmo98-economie-maroc-rasd.static.hf.space | Dashboard Next.js interactif |
| **Hugging Face Dataset** | https://huggingface.co/datasets/YsfMO98/economie-maroc-rasd | Données économiques + FMI WEO |
| **Kaggle Dataset** | https://www.kaggle.com/datasets/amarzouyoussef/economie-maroc-rasd | Datasets + Notebook R |

---

## 📦 Datasets disponibles

### 🇲🇦 Données économiques marocaines (243 535 obs.)
Collectées depuis 5 sources officielles :

| Source | Lignes | Indicateurs | Période |
|--------|--------|-------------|---------|
| DataGov.ma (open data) | 179 477 | 39 | 1967–2026 |
| HCP (Haut-Commissariat au Plan) | 28 254 | 4 | 2005–2026 |
| Finances Publiques | 20 998 | 29 | 2006–2014 |
| BAM (Bank Al-Maghrib) | 13 500 | 5 | 2005–2026 |
| Office des Changes | 1 306 | 1 | 2006–2026 |
| **TOTAL** | **243 535** | **78** | **1967–2026** |

### 🌍 FMI World Economic Outlook (17 indicateurs, 1980–2029)
Données macroéconomiques du Maroc issues du WEO Avril 2026 :

| Indicateur | Code FMI | Période |
|---|---|---|
| Croissance du PIB (%) | NGDP_RPCH | 1980–2029 |
| PIB constant (Mds MAD) | NGDP | 1980–2029 |
| PIB courant (M USD) | NGDPD | 1980–2029 |
| PIB par habitant (USD) | NGDPDPC | 1980–2029 |
| Déflateur PIB (Index) | NGDP_D | 1980–2029 |
| Inflation IPC (%) | PCPIEPCH | 1980–2029 |
| Taux de chômage (%) | LUR | 1980–2029 |
| Investissement (% PIB) | NID_NGDP | 1980–2029 |
| Exportations (var. %) | TX_RPCH | 1980–2029 |
| Importations (var. %) | TM_RPCH | 1980–2029 |
| Recettes publiques (% PIB) | GGR | 1990–2029 |
| Dépenses publiques (% PIB) | GGX | 1990–2029 |
| Déficit (% PIB) | GGXCNL | 1990–2029 |
| Dette publique (% PIB) | GGXWDG | 1990–2029 |
| Balance courante (M USD) | BCA | 1980–2029 |
| Balance courante (% PIB) | BCA_NGDPD | 1980–2029 |
| Population (millions) | LP | 1980–2029 |

Formats disponibles : **CSV, Parquet, JSON, SQLite, Excel (.xlsx)**

---

## 🖥️ Dashboard Next.js

Un tableau de bord interactif accessible sur **Hugging Face Spaces** :

**https://ysfmo98-economie-maroc-rasd.static.hf.space**

Pages :
- `/` — Accueil : KPIs macroéconomiques, carte interactive, graphiques d'évolution
- `/kpi` — Liste détaillée de tous les indicateurs avec définitions

Technos : **Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Recharts**

---

## 📑 Livrables (scripts/imf_export/)

| Livrable | Description |
|---|---|
| `pdf_report/Maroc_Rapport_Macro.pdf` | Rapport PDF complet (7 sections, 17 indicateurs, 50 ans) |
| `tables/01-09_*.xlsx` | 8 fichiers Excel thématiques + tableau de bord |
| `powerpoint/Maroc_Macro_Indicateurs.pptx` | Présentation PowerPoint (9 slides) |
| `dashboard/index.html` | Dashboard HTML statique (Chart.js) |
| `api/main.py` | API REST FastAPI (6 endpoints, CORS) |
| `exports/morocco_imf.{json,db,parquet}` | Export multi-format |
| `comparison/comparaison_regionale.txt` | Comparaison Maroc vs Algérie/Tunisie/Égypte |

---

## 🔧 Scripts ETL (Python)

```bash
# Pipeline principal
python scripts/imf_export/main.py

# Générer le rapport PDF
python scripts/imf_export/pdf_report/generate_pdf.py

# Générer les tables Excel
python scripts/imf_export/generate_tables.py

# API REST locale
cd scripts/imf_export/api && uvicorn main:app --reload
```

---

## 📈 Analyse Kaggle (R)

Un notebook R complet est disponible sur Kaggle pour :
- Charger les datasets (Parquet/CSV)
- Calculer les KPIs clés par source et par indicateur
- Visualiser les tendances (ggplot2)
- Exporter les tables récapitulatives

→ https://www.kaggle.com/datasets/amarzouyoussef/economie-maroc-rasd

---

## 🔐 Sécurité

Aucun token, clé API ou secret n'est hardcodé dans le dépôt.
Toutes les authentifications passent par des variables d'environnement :
- `HF_TOKEN` — Token Hugging Face
- `GOOGLE_APPLICATION_CREDENTIALS` — BigQuery
- Fichier `~/.kaggle/kaggle.json` — Kaggle API

---

## 🏗️ Architecture

```
rasdeco-maroc/
├── economie/                   # Pipeline ETL principal (Python)
│   ├── collect/                # Collecte par source
│   ├── transform/              # Parsing, nettyage, normalisation
│   ├── forecasting/            # SARIMA, Prophet, baselines
│   └── dashboard/              # Dash/Plotly (legacy)
├── scripts/imf_export/         # Pipeline FMI WEO
│   ├── data_parser.py          # 17 indicateurs inline 1980–2029
│   ├── excel_formatter.py      # Excel 4 sheets pro
│   ├── generate_tables.py      # 8 fichiers thématiques + VBA
│   ├── generate_pdf.py         # Rapport PDF 12 pages
│   ├── api/main.py             # FastAPI REST
│   └── exports/                # Parquet, JSON, SQLite
├── src/                        # Dashboard Next.js
│   ├── app/                    # Pages (/, /kpi)
│   └── components/ui/          # shadcn/ui components
├── hf_space/                   # Déploiement Hugging Face Space
├── kaggle_dataset/             # Dataset Kaggle + notebook R
├── data/                       # Données brutes & export
├── functions/                  # Cloud Function (scheduler)
└── Dockerfile                  # Cloud Run (legacy)
```

---

## 📜 Licence

- **Données sources** : Open Data Maroc (data.gov.ma) — Licence Ouverte
- **Données FMI WEO** : FMI World Economic Outlook — Terms of Use
- **Code** : MIT

---

## 👤 Auteur

**Youssef Amarzou** — RASD-Maroc Project

[LinkedIn](https://www.linkedin.com/in/youssef-amarzou-8b18413a7/) | [GitHub](https://github.com/Youssef-AMARZOU) | [GitLab](https://gitlab.com/Youssef-AMARZOU) | [Kaggle](https://www.kaggle.com/amarzouyoussef)