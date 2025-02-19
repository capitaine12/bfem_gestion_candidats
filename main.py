import logging
import os
import sys
from PyQt5.QtWidgets import QApplication
from frontend.views import MainWindow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configuration du logging
log_file = "logs/app.log"
logging.basicConfig(
    level=logging.INFO,  # Niveau INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w"),  # Mode "w" écrase le fichier à chaque lancement
        logging.StreamHandler()  # Affiche aussi les logs dans la console
    ]
)

logger = logging.getLogger(__name__)  # Création du logger


# Fonction pour charger le fichier QSS
def load_stylesheet(app):
    with open("frontend/styles.qss", "r") as f:
        app.setStyleSheet(f.read())

if __name__ == "__main__":
    logging.info("🚀 Démarrage de l'application")

    app = QApplication(sys.argv)
    
    #from backend.function.import_notes import import_notes_from_excel, import_livret_scolaire_from_excel

    """ logging.info("📌 Importation des notes et livrets scolaires depuis Excel...")
    import_notes_from_excel("data/bdbfem.xlsx")
    import_livret_scolaire_from_excel("data/bdbfem.xlsx")
    logging.info("✅ Importation terminée.") """

    # Charger le fichier de styles
    #load_stylesheet(app)

    """ window = MainWindow()
    window.show() """

    #logging.info("🖥️ Interface graphique chargée.")
    #sys.exit(app.exec_())
print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
logging.info("✅ Avant import des notes")
from backend.function.import_notes import import_notes_from_excel, import_livret_scolaire_from_excel
logging.info("✅ Après import des notes")

logging.info("✅ Avant importation des notes")
import_notes_from_excel("data/bdbfem.xlsx")
logging.info("✅ Après importation des notes")

logging.info("✅ Avant importation du livret scolaire")
import_livret_scolaire_from_excel("data/bdbfem.xlsx")
logging.info("✅ Après importation du livret scolaire")

logging.info("✅ Avant lancement de l'interface graphique")
from frontend.views import MainWindow
logging.info("✅ Après lancement de l'interface graphique")

load_stylesheet(app)

window = MainWindow()
window.show()
logging.info("✅ Interface graphique démarrée")

sys.exit(app.exec_())
