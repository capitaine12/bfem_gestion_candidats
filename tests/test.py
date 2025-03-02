import sqlite3
import os, sys
import pandas as pd


# Ajouter le dossier parent au chemin pour importer backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import QApplication
from frontend.views import CandidatsPage,StatistiquesPage

#from backend.database import get_all_candidats
#from backend.function.calculenotes import calculer_statut_candidat
# Vérifier si des données sont bien récupérées depuis la base de données
#print("recuperation", get_all_candidats())  




""" from backend.function.calculenotes import recalculer_tous_les_statuts
recalculer_tous_les_statuts()
num_table = 101
print(f"📌 Test de la délibération pour le candidat {num_table}")
statut = calculer_statut_candidat(num_table)
print(f"🎯 Statut final : {statut}") """
#calculer_statut_candidat(num_table)


""" from backend.database import get_candidats_avec_statut

candidats = get_candidats_avec_statut()
for c in candidats:
    print(c) """  # Vérifie si les données s'affichent bien en console



""" print("📌 Lancement du recalcul global des statuts...")
recalculer_tous_les_statuts()
print("🎯 Vérifie la table 'deliberation' dans SQLite.") """

 # Définir le chemin du fichier Excel
""" excel_file = "data/bdbfem.xlsx"

if os.path.exists(excel_file):
    print(f"✅ Le fichier existe : {os.path.abspath(excel_file)}")
else:
    print(f"❌ Erreur : Le fichier n'existe pas à cet emplacement : {os.path.abspath(excel_file)}") """


# Charger le fichier Excel
""" df = pd.read_excel(excel_file)

print("✅ Fichier Excel chargé avec succès.")
print(df.head()) """  # Afficher les 5 premières lignes



#df = pd.read_excel(excel_file)
""" print("📊 Colonnes détectées dans Excel :", df.columns.tolist())
print(f"🔢 Nombre de colonnes dans Excel : {len(df.columns)}") """




def main():
    app = QApplication(sys.argv)  # Initialiser l'application Qt
    window = StatistiquesPage()    # Créer une instance de la page statistiques
    window.show()                   # Afficher la fenêtre

    # Appeler des méthodes pour tester
    window.refresh_statistics()     # Rafraîchir les statistiques
    # Vous pouvez appeler d'autres méthodes ici pour les tester

    sys.exit(app.exec_())           # Démarrer l'application

if __name__ == "__main__":
    main()