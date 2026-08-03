# Dashboard — RASD Maroc

Application **Next.js** statique — Portail macroéconomique et sectoriel du Maroc.

## Démarrage rapide

```bash
cd dashboard
npm install       # Une seule fois
npm run dev       # Serveur de développement → http://localhost:3000
npm run build     # Build statique → out/
```

## Structure

```
dashboard/
├── src/
│   ├── app/            # Routes Next.js App Router
│   │   ├── page.tsx    # Accueil (KPIs + carte interactive)
│   │   ├── kpi/        # Page liste des indicateurs
│   │   └── layout.tsx  # Layout global
│   ├── components/     # Composants réutilisables
│   │   ├── morocco-map.tsx       # Carte Leaflet par région
│   │   ├── kpi-detail-dialog.tsx # Dialogue détail KPI
│   │   └── ui/                   # ShadcN UI components
│   ├── hooks/          # React hooks
│   └── lib/            # Données et utilitaires
│       ├── rasd-data.ts     # 🔑 Modèle de données principal (268 KB)
│       ├── data.json        # Données brutes (42 MB)
│       ├── data-service.ts  # Service d'accès aux données
│       └── data-client.ts   # Client API
├── public/             # Assets statiques + JSON publics
│   └── data/           # imf.json, ts_*.json
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Accueil — KPIs macroéco + carte régions Maroc |
| `/kpi` | Liste complète des indicateurs avec séries temporelles |

## Déploiement

```bash
npm run build                    # Génère out/
python ../pipeline/export/push_to_hf.py   # → Hugging Face Spaces
```

| Cible | URL |
|-------|-----|
| HF Spaces | https://ysfmo98-economie-maroc-rasd.static.hf.space |
| Dataset HF | https://huggingface.co/datasets/YsfMO98/economie-maroc-rasd |
| Desktop | Electron (`../infra/`) |
