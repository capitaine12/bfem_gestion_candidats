import logging
import os
import sys

# Configuration du logging
log_file = "logs/app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),  # 🔥 Ajout de encoding="utf-8"
        logging.StreamHandler(sys.stdout)  # 🔥 Assurer la sortie console en UTF-8
    ]
)

logger = logging.getLogger(__name__)
logger.info("🚀 Démarrage du script main.py")

from PyQt5.QtWidgets import QApplication
from frontend.views import MainWindow
from backend.function.import_notes import import_notes_from_excel, import_livret_scolaire_from_excel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Fonction pour charger le fichier QSS
def load_stylesheet(app):
    stylesheet_path = os.path.join("frontend", "styles.qss")
    with open(stylesheet_path, "r") as f:
        app.setStyleSheet(f.read())

if __name__ == "__main__":
    logging.info("🚀 Démarrage de l'application")

    app = QApplication(sys.argv)

    try:
        logging.info("📌 Importation des notes et livrets scolaires depuis Excel...")
        import_notes_from_excel("data/bdbfem.xlsx")
        import_livret_scolaire_from_excel("data/bdbfem.xlsx")
        logging.info("✅ Importation terminée.")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'importation : {e}")

    # Charger le fichier de styles
    load_stylesheet(app)

    window = MainWindow()
    window.show()

    logging.info("🖥️ Interface graphique chargée.")
    sys.exit(app.exec_())