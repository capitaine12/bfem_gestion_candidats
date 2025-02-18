import sys
from PyQt5.QtWidgets import QApplication
from frontend.views import MainWindow

# Fonction pour charger le fichier QSS
def load_stylesheet(app):
    with open("frontend/styles.qss", "r") as f:
        app.setStyleSheet(f.read())
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Charger le fichier de styles
    load_stylesheet(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
