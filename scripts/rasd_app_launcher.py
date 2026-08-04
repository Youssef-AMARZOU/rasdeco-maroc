import os
import sys
import webbrowser
import subprocess
import time

def print_banner():
    print("=" * 60)
    print("      RASD Maroc — Portail Data & Observatoire Macroéconomique")
    print("      Recherche · Analyse · Synthèse des Données — Maroc")
    print("=" * 60)
    print()

def main():
    print_banner()
    while True:
        print("Menu Principal:")
        print("  [1] 🚀 Démarrer le Dashboard Web (localhost:4000)")
        print("  [2] ⚙️  Lancer le Pipeline Data (Collecte & Mise à jour)")
        print("  [3] 🔍 Vérifier la cohérence des KPIs")
        print("  [4] 📊 Exporter les rapports macroéconomiques (FMI WEO)")
        print("  [5] 🌐 Ouvrir l'Observatoire dans le navigateur")
        print("  [0] ❌ Quitter")
        print()
        choice = input("Votre choix (0-5) : ").strip()
        
        if choice == '1':
            print("\n🚀 Démarrage du serveur web Next.js...")
            dashboard_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard")
            if os.path.exists(dashboard_dir):
                subprocess.Popen(["npm", "run", "dev"], cwd=dashboard_dir, shell=True)
                time.sleep(3)
                webbrowser.open("http://localhost:4000")
            else:
                print("❌ Dossier dashboard non trouvé.")
        elif choice == '2':
            print("\n⚙️ Exécution du pipeline complet...")
            pipeline_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pipeline", "sectors", "economie", "run_all.py")
            if os.path.exists(pipeline_script):
                subprocess.run([sys.executable, pipeline_script])
            else:
                print("❌ Script pipeline introuvable.")
        elif choice == '3':
            print("\n🔍 Vérification des KPIs...")
            verify_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pipeline", "verify", "verify_kpi_values.py")
            if os.path.exists(verify_script):
                subprocess.run([sys.executable, verify_script])
            else:
                print("❌ Script de vérification introuvable.")
        elif choice == '4':
            print("\n📊 Génération des exports FMI WEO...")
            imf_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pipeline", "export", "imf", "main.py")
            if os.path.exists(imf_script):
                subprocess.run([sys.executable, imf_script])
            else:
                print("❌ Script FMI WEO introuvable.")
        elif choice == '5':
            webbrowser.open("http://localhost:4000")
        elif choice == '0':
            print("Au revoir!")
            break
        else:
            print("Choix invalide, veuillez réessayer.\n")

if __name__ == "__main__":
    main()
