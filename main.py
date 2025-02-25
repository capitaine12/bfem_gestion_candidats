import logging
import os
import sys
from PyQt5.QtWidgets import QApplication, QDialog
from frontend.views import MainWindow
from backend.loginwindow import LoginWindow
from backend.function.import_notes import import_notes_from_excel, import_livret_scolaire_from_excel

# Configuration du logging
log_file = "logs/app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def load_stylesheet(app):
    stylesheet_path = os.path.join("frontend", "styles.qss")
    with open(stylesheet_path, "r") as f:
        app.setStyleSheet(f.read())

if __name__ == "__main__":
    logging.info("🚀 Démarrage de l'application")

    app = QApplication(sys.argv)

    # Créer une instance de MainWindow avant la connexion
    window = MainWindow()

    try:
        logging.info("📌 Importation des notes et livrets scolaires depuis Excel...")
        import_notes_from_excel("data/bdbfem.xlsx", window)
        import_livret_scolaire_from_excel("data/bdbfem.xlsx")
        logging.info("✅ Importation terminée.")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'importation : {e}")

    # Afficher la fenêtre de connexion
    login_window = LoginWindow()
    
    if login_window.exec_() == QDialog.Accepted:  # Vérifie si la connexion est réussie
        # Charger le fichier de styles
        load_stylesheet(app)

        window.show()
        logging.info("🖥️ Interface graphique chargée.")
        sys.exit(app.exec_())
    else:
        logging.info("❌ Connexion échouée. L'application ne se lance pas.")