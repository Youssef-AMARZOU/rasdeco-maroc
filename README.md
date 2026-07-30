---
title: Economie Maroc - RASD
colorFrom: blue
colorTo: green
sdk: static
pinned: false
license: mit
datasets:
  - YsfMO98/economie-maroc-rasd
---

# Dashboard Économie Maroc — RASD

> **R**echerche, **A**nalyse et **S**ynthèse des **D**onnées — Portail macroéconomique du Maroc

Tableau de bord interactif avec pipeline data hybride (MongoDB + Neo4j), ingestion temps réel (CDC Kafka), orchestration Airflow, et déploiement multi-cible (HF Spaces, Electron).

```mermaid
%%{init: {"flowchart": {"htmlLabels": true, "curve": "basis"}, "theme": "neutral"} }%%
flowchart TB
    subgraph Sources["📡 SOURCES DE DONNÉES"]
        direction TB
        HCP["HCP<br/>Emploi, IPC, PIB"]
        IMF["IMF WEO<br/>Macro prévisions"]
        BAM["Bank Al-Maghrib<br/>Taux, Réserves"]
        DG["DataGov.ma<br/>389 jeux ouverts"]
        OC["Office des Changes<br/>IDE, Balance"]
        FIN["Ministère Finances<br/>Budget, Dette"]
        WEB["Web Scraping<br/>Worldometer, etc."]
    end

    subgraph Ingestion["⬇️ INGESTION & STREAMING"]
        direction TB
        AIRFLOW["Airflow DAGs<br/>- collect<br/>- parse<br/>- transform"]
        CDC["Debezium CDC<br/>PostgreSQL → Kafka"]
        KAFKA["Kafka<br/>Topics partitionnés"]
        DLQ["DLQ<br/>Poison-pill isolation"]
    end

    subgraph Storage["💾 STOCKAGE HYBRIDE"]
        direction TB
        MONGO["MongoDB<br/>Données brutes & agrégées"]
        NEO4J["Neo4j<br/>Relations indic-teurs ↔ sources"]
        ICEBERG["Apache Iceberg<br/>Données historiques"]
        TRINO["Trino<br/>Requêtes跨-moteur"]
        REDIS["Redis<br/>Cache SSE temps réel"]
    end

    subgraph API["🔌 API & ENRICHISSEMENT"]
        direction TB
        GRAPHQL["GraphQL<br/>Requêtes unifiées"]
        REST["REST API<br/>/api/data<br/>/api/stream"]
        ENRICH["Enrich Layer<br/>IMF→ts_data→hardcode<br/>3 tiers de fiabilité"]
        SSE["Server-Sent Events<br/>Mises à jour temps réel"]
    end

    subgraph Dashboard["🖥️ DASHBOARD"]
        direction TB
        NEXT["Next.js 16 App<br/>Static SSG"]
        NX["Next.js API Server"]
        HF["Hugging Face Spaces<br/>sdk: static"]
        ELECTRON["Electron<br/>Desktop app"]
        D3["D3.js / Recharts<br/>Graphiques interactifs"]
        MAP["Leaflet<br/>Cartes régions"]
    end

    subgraph Pipeline["🔁 PIPELINE DATA"]
        AGRI["Agriculture<br/>7 cultures"]
        SOCIAL["Social<br/>Ménages, Logement"]
        SANTE["Santé<br/>Hôpitaux, Lits"]
        EDU["Éducation<br/>Écoles, Université"]
        SPORT["Sport<br/>Infrastructures"]
    end

    Sources -->|Collect| AIRFLOW
    Sources -->|API directe| REST
    Sources -->|Webhook| CDC
    
    AIRFLOW -->|Parse & Transform| MONGO
    AIRFLOW -->|Graph| NEO4J
    AIRFLOW -->|Archive| ICEBERG
    CDC --> KAFKA -->|Consume| MONGO
    KAFKA --> DLQ

    MONGO --> TRINO
    ICEBERG --> TRINO
    NEO4J --> GRAPHQL

    API -->|enrichModule| ENRICH
    ENRICH -->|IMF priority → ts_data → fallback| NEXT
    MONGO -->|REST| NEXT
    REDIS --> SSE --> NEXT

    NEXT -->|Build| HF
    NEXT -->|Electron| ELECTRON
    NEXT --> D3
    NEXT --> MAP

    Pipeline -->|Données sectorielles| MONGO

    subgraph Tiers["🎯 TIERS DE FIABILITÉ"]
        T1["Tier 1 (fiab 5)<br/>HCP, BAM, DataGov, Finances, OC"]
        T2["Tier 2 (fiab 3)<br/>IMF, World Bank, UN"]
        T3["Tier 3 (fiab 1)<br/>Worldometer, Web"]
    end

    Sources --> Tiers
    Tiers --> ENRICH
```

## Architecture

### Pipeline Data

| Étape | Technologie | Rôle |
|-------|-------------|------|
| **Collecte** | Airflow + API | Récupération depuis 6+ sources (HCP, IMF, BAM...) |
| **Streaming** | Debezium → Kafka → CDC | Mises à jour temps réel, poison-pill DLQ |
| **Stockage** | MongoDB + Neo4j + Iceberg | Brute → Relationnel → Historique |
| **Requêtes** | Trino | Requêtes跨-moteur MongoDB ↔ Iceberg |
| **Orchestration** | Airflow + DBT | Transformations, nettoyage, audits |

### Dashboard (Next.js 16)

| Couche | Technologie |
|--------|-------------|
| **Rendu** | Static SSG + API Routes |
| **Graphiques** | Recharts (KPIs), Leaflet (cartes régions) |
| **Temps réel** | SSE (Server-Sent Events) |
| **Déploiement** | HF Spaces (static) + Electron (desktop) |
| **Design** | Tailwind CSS, responsive |

### Enrichissement des KPIs

Les KPIs suivent une résolution par priorité :

1. **IMF WEO** — données macro-économiques officielles (croissance PIB, inflation, dette)
2. **ts_data** — séries temporelles internes (chômage HCP, SMIG, taux directeur BAM)
3. **Valeur hardcodée** — fallback dans `rasd-data.ts`

La fiabilité est pondérée par source (Tier 1 = 5, Tier 2 = 3, Tier 3 = 1).

## Modules sectoriels

- **Économie** — PIB, inflation, chômage, monnaie, finances publiques
- **Agriculture** — 7 cultures (blé, orge, maïs, agrumes, olives, maraîchage, betterave)
- **Social** — Revenus ménages, conditions de logement, pauvreté
- **Santé** — Capacité hospitalière, lits, personnel médical par région
- **Éducation** — Scolarisation, effectifs, universités
- **Sport** — Infrastructures sportives et clubs

## Pages

- `/` — Accueil avec KPIs macroéconomiques et carte interactive des régions
- `/kpi` — Liste détaillée de tous les indicateurs avec séries temporelles

## Déploiement

| Cible | URL |
|-------|-----|
| **HF Spaces** | https://ysfmo98-economie-maroc-rasd.static.hf.space |
| **Dataset** | https://huggingface.co/datasets/YsfMO98/economie-maroc-rasd |
| **Desktop** | `C:\Users\youss\Desktop\RASD-Maroc-Desktop\` |

## Développement

```bash
npm install
npm run dev     # dev server
npm run build   # static export → out/
python push_to_hf.py   # deploy to HF Spaces
```

## Sources

| Source | Données | Fréquence |
|--------|---------|-----------|
| **FMI WEO** — Avril 2026 | PIB, inflation, dette, balance courante | Semestriel |
| **HCP** | Comptes nationaux, IPC, emploi, population | Mensuel/Trimestriel |
| **Bank Al-Maghrib** | Taux directeur, réserves de change | Mensuel |
| **Ministère des Finances** | Budget, déficit, dette | Annuel |
| **Office des Changes** | IDE, balance commerciale, transferts MRE | Mensuel |
| **DataGov.ma** | 389 jeux de données open data | Variable |
