# ============================================================
#  RASD Maroc — Makefile
#  Commandes unifiées pour l'ensemble du projet
# ============================================================

.PHONY: help dev build pipeline verify export clean infra desktop

# Afficher l'aide par défaut
help:
	@echo ""
	@echo "  ██████╗  █████╗ ███████╗██████╗     ███╗   ███╗ █████╗ ██████╗  ██████╗  ██████╗"
	@echo "  ██╔══██╗██╔══██╗██╔════╝██╔══██╗    ████╗ ████║██╔══██╗██╔══██╗██╔═══██╗██╔════╝"
	@echo "  ██████╔╝███████║███████╗██║  ██║    ██╔████╔██║███████║██████╔╝██║   ██║██║"
	@echo "  ██╔══██╗██╔══██║╚════██║██║  ██║    ██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║██║"
	@echo "  ██║  ██║██║  ██║███████║██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██║╚██████╔╝╚██████╗"
	@echo ""
	@echo "  Portail Data Macroéconomique du Maroc"
	@echo ""
	@echo "  Usage: make <commande>"
	@echo ""
	@echo "  DASHBOARD"
	@echo "    dev           Démarrer le serveur Next.js (http://localhost:3000)"
	@echo "    build         Build statique Next.js -> dashboard/out/"
	@echo "    desktop       Lancer l'application desktop Electron (RASD Desktop)"
	@echo "    deploy        Build + push vers Hugging Face Spaces"
	@echo ""
	@echo "  PIPELINE"
	@echo "    pipeline      Lancer le pipeline data complet"
	@echo "    collect-hcp   Collecter les données HCP"
	@echo "    collect-bam   Collecter les données Bank Al-Maghrib"
	@echo "    export-imf    Régénérer exports FMI WEO (JSON + Excel)"
	@echo ""
	@echo "  QUALITÉ"
	@echo "    verify        Vérifier la cohérence des KPIs"
	@echo "    audit         Audit complet des sources et indicateurs"
	@echo ""
	@echo "  INFRA"
	@echo "    up            docker-compose up -d (tous les services)"
	@echo "    down          docker-compose down"
	@echo "    logs          Logs des conteneurs"
	@echo ""
	@echo "  UTILITAIRES"
	@echo "    clean         Nettoyer les caches (.next, __pycache__)"
	@echo "    install       Installer toutes les dépendances"
	@echo ""

# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────

dev:
	@echo "🚀 Démarrage du dashboard Next.js → http://localhost:4000"
	cd dashboard && npm run dev

build:
	@echo "📦 Build statique..."
	cd dashboard && npm run build

desktop: build
	@echo "🖥️  Lancement de l'application desktop Electron..."
	cd dashboard && npm run desktop

deploy: build
	@echo "🚢 Déploiement vers Hugging Face Spaces..."
	python pipeline/export/push_to_hf.py

# ─────────────────────────────────────────────
#  PIPELINE DATA
# ─────────────────────────────────────────────

pipeline:
	@echo "⚙️  Lancement du pipeline complet..."
	python pipeline/sectors/economie/run_all.py

collect-hcp:
	python pipeline/collect/collect_hcp.py

collect-bam:
	python pipeline/collect/collect_bkam.py

collect-all:
	python pipeline/collect/collect_hcp.py
	python pipeline/collect/collect_bkam.py
	python pipeline/collect/collect_finances.py
	python pipeline/collect/collect_office_des_changes.py
	python pipeline/collect/collect_datagov.py

export-imf:
	@echo "📊 Export FMI WEO..."
	cd pipeline/export/imf && python main.py

# ─────────────────────────────────────────────
#  QUALITÉ & VÉRIFICATION
# ─────────────────────────────────────────────

verify:
	@echo "🔍 Vérification des KPIs..."
	cd dashboard && python ../pipeline/verify/verify_kpi_values.py

audit:
	@echo "🔎 Audit complet des indicateurs..."
	python pipeline/verify/audit_kpi_codes.py
	python pipeline/verify/audit_kpi_resolution.py
	python pipeline/verify/audit_imf.py

# ─────────────────────────────────────────────
#  INFRASTRUCTURE DOCKER
# ─────────────────────────────────────────────

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# ─────────────────────────────────────────────
#  UTILITAIRES
# ─────────────────────────────────────────────

install:
	@echo "📥 Installation des dépendances..."
	cd dashboard && npm install
	pip install -r requirements.txt

clean:
	@echo "🧹 Nettoyage des caches..."
	rd /s /q dashboard\.next 2>nul || true
	for /r pipeline %%d in (__pycache__) do rd /s /q "%%d" 2>nul || true
	@echo "✅ Nettoyage terminé"
