from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QHBoxLayout  
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre principale
        self.setWindowTitle("Gestion des Candidats BFEM")
        self.setGeometry(100, 100, 1000, 600)  # Position (x, y) et taille (width, height)

        # Layout principal (horizontal)
        main_layout = QHBoxLayout()

        # Nom du Logiciel
        text_label = QLabel("LOG BFEM")
        text_label.setStyleSheet("""
            font-size: 50px;
            font-family: Arial;
            font-weight: bold;
            color: rgb(93,130,155);                          
        """)
        text_label.setAlignment(Qt.AlignLeft)  # Aligner le texte à gauche

        # ======= Barre de navigation (Menu à gauche) =======
        self.navbar = QWidget()
        self.navbar.setFixedWidth(180)  # Largeur fixe pour la barre latérale
        nav_layout = QVBoxLayout()

        # Boutons du menu
        self.btn_dashboard = QPushButton("🏠 Dashboard")
        self.btn_candidats = QPushButton("📋 Liste des candidats")
        self.btn_deliberation = QPushButton("⚖ Délibération")
        self.btn_statistiques = QPushButton("📊 Statistiques")
        self.btn_quitter = QPushButton("❌ Quitter")

        # Appliquer le style général des boutons
        btn_style = """
            QPushButton {
                padding: 12px;
                font-size: 14px;
                background: transparent;
                color: white;
                text-align: left;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2); /* Effet de survol */
            }
        """
        # Ajout des boutons au layout de navigation
        for btn in [self.btn_dashboard, self.btn_candidats, self.btn_deliberation, self.btn_statistiques, self.btn_quitter]:
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)  # Changer le curseur au survol
            nav_layout.addWidget(btn)

        self.navbar.setLayout(nav_layout)
        self.navbar.setStyleSheet("""
            background-color: #1f3a56;  /* Couleur de fond bleu foncé */
            border-right: 2px solid #1a2e40;  /* Bordure droite */
        """)

        # ======= Contenu principal (Affichage des pages) =======
        self.pages = QStackedWidget()

        # Création des pages (Placeholder pour l'instant)
        self.page_dashboard = QWidget()
        self.page_candidats = QWidget()
        self.page_deliberation = QWidget()
        self.page_statistiques = QWidget()

        # Ajout des pages au QStackedWidget
        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_candidats)
        self.pages.addWidget(self.page_deliberation)
        self.pages.addWidget(self.page_statistiques)

        # Ajout de la barre de navigation et du contenu principal au layout principal
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.pages)

        # Création d'un layout vertical pour inclure le titre et le contenu
        main_container = QVBoxLayout()
        main_container.addWidget(text_label)  # Ajout du texte en haut
        main_container.addLayout(main_layout)  # Ajout du layout principal

        # Création d'un widget central
        central_widget = QWidget()
        central_widget.setLayout(main_container)
        self.setCentralWidget(central_widget)

        # Connexions des boutons aux pages
        self.btn_dashboard.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_dashboard))
        self.btn_candidats.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_candidats))
        self.btn_deliberation.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_deliberation))
        self.btn_statistiques.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_statistiques))
        self.btn_quitter.clicked.connect(self.close)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
