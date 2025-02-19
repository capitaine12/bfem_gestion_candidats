import os
import sys
from PyQt5.QtWidgets import QApplication
from frontend.views import MainWindow

# 📌 Ajouter le dossier parent au chemin des modules pour éviter les erreurs d'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 📌 Fonction pour charger le fichier de styles QSS
def load_stylesheet(app):
    """Charge et applique le fichier de styles CSS pour l'application."""
    try:
        with open("frontend/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ Fichier de styles 'frontend/styles.qss' introuvable.")

# 📌 Fonction principale de l'application
def main():
    """Point d'entrée de l'application PyQt5."""
    app = QApplication(sys.argv)

    # 📌 Importation des modules nécessaires pour le traitement des données
    from backend.function.import_notes import import_notes_from_excel, import_livret_scolaire_from_excel
    from backend.function.calculenotes import recalculer_tous_les_statuts

    # 📌 Importation des candidats et de leurs données depuis le fichier Excel
    print("📌 Importation des notes et des livrets scolaires...")
    import_notes_from_excel("data/bdbfem.xlsx")
    import_livret_scolaire_from_excel("data/bdbfem.xlsx")
    print("✅ Importation terminée.")

    # 📌 Recalcul automatique des statuts après importation
    print("📌 Début du calcul automatique des délibérations...")
    recalculer_tous_les_statuts()
    print("✅ Délibérations mises à jour avec succès !")

    # 📌 Charger le fichier de styles pour l'interface
    load_stylesheet(app)

    # 📌 Démarrer l'application avec l'interface principale
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# 📌 Exécuter la fonction principale si ce fichier est lancé directement
if __name__ == "__main__":
    main()
