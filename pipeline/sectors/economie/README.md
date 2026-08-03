# RASD-Maroc — Pipeline de Collecte Économie

Collecte automatisée des données économiques du Maroc depuis les sources officielles.

## Sources couvertes

| Script | Organisme | Données | Source |
|--------|-----------|---------|--------|
| `collect_hcp.py` | HCP | PIB, IPC, chômage, comptes nationaux | CKAN + BDS |
| `collect_bkam.py` | Bank Al-Maghrib | Taux directeur, stats monétaires, change | CKAN + API REST + scraping |
| `collect_finances.py` | Ministère des Finances | Dette publique, budget | CKAN + téléchargements directs |
| `collect_office_des_changes.py` | Office des Changes | Réserves de change, IDE | CKAN + scraping |
| `collect_datagov.py` | data.gov.ma | Groupe Économie & Finance (exhaustif) | CKAN |

## Prérequis

```bash
pip install requests beautifulsoup4
```

## Utilisation

### Collecte complète (recommandé)

```bash
cd economie
python run_all.py
```

### Collecte sélective

```bash
python run_all.py --sources hcp bkam
```

### Forcer la re-collecte

```bash
python run_all.py --force
```

### Script individuel

```bash
python collect_hcp.py
```

## Arborescence de sortie

```
data/raw/economie/
├── hcp/
│   ├── meta.json
│   ├── collect.log
│   ├── 2020/
│   │   └── pib_trimestriel.xlsx
│   ├── 2021/
│   │   └── ipc_base2017.xlsx
│   └── undated/
│       └── ...
├── bkam/
│   ├── meta.json
│   ├── collect.log
│   └── ...
├── finances/
│   ├── meta.json
│   ├── collect.log
│   └── ...
├── office_des_changes/
│   ├── meta.json
│   ├── collect.log
│   └── ...
├── datagov/
│   ├── meta.json
│   ├── collect.log
│   └── ...
└── pipeline_report.json
```

## Format meta.json

Chaque source produit un `meta.json` :

```json
{
  "source": "Haut-Commissariat au Plan (HCP)",
  "date_recuperation": "2026-07-23T17:30:00+00:00",
  "organisme": "HCP",
  "periodicite": "Trimestrielle / Annuelle",
  "granularite_geographique": "Nationale, régionale",
  "date_debut_reelle_donnees": "1955",
  "jeux_telecharges": [
    {
      "url": "https://...",
      "format": "XLSX",
      "description": "PIB trimestriel",
      "fichier": "hcp/2020/pib.xlsx"
    }
  ]
}
```

## Variables d'environnement

| Variable | Requis | Description |
|----------|--------|-------------|
| `BAM_API_KEY` | Non | Clé API Bank Al-Maghrib (gratuite sur apihelpdesk.centralbankofmorocco.ma) |

## Reprise automatique

- `run_all.py` vérifie l'existence de `meta.json` pour chaque source
- Si le fichier existe et n'est pas vide, la source est **automatiquement skipée**
- Utilisez `--force` pour tout re-télécharger
- Les fichiers individuels déjà téléchargés sont aussi skippés (vérification taille > 0)

## Notes techniques

### Endpoints API propres
- **CKAN data.gov.ma** : `https://www.data.gov.ma/data/api/3/action/package_search`
  - Pas d'authentification requise
  - Pagination par `rows` + `start`
  - Filtrage par organisation : `fq=organization:nom-org`

### Scraping fragile (sections marquées)
- Les scripts contiennent des sections `>>> FRAGILE <<<` isolant le code de scraping HTML
- Ces sections utilisent BeautifulSoup avec des sélecteurs CSS
- **À adapter** si les sites sont refondus
- Ne cassent pas le reste du pipeline si elles échouent

## Développement

### Ajouter une nouvelle source

1. Créer `collect_<source>.py` dans `economie/`
2. Implémenter une fonction `main()` retournant la liste des téléchargements
3. Ajouter la source dans `SOURCES` dans `run_all.py`
4. Tester : `python collect_<source>.py`

### Structure du code

- `utils.py` : fonctions partagées (session HTTP, retry, logging, meta.json)
- `collect_*.py` : un script par organisme source
- `run_all.py` : orchestrateur avec reprise automatique
