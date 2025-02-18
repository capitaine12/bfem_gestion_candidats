from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
#from frontend.controllers import open_add_form, open_edit_form



class NavigationMenu(QWidget):
    """Classe représentant le menu de navigation."""
    def __init__(self):
        super().__init__()
        self.setObjectName("navigationMenu")
        self.setFixedWidth(200)
        
        nav_layout = QVBoxLayout()

        # Création des boutons avec un ID unique pour le QSS
        self.btn_dashboard = QPushButton("🏠 Accueil")
        self.btn_dashboard.setObjectName("menuButton")

        self.btn_candidats = QPushButton("📋 Liste des candidats")
        self.btn_candidats.setObjectName("menuButton")

        self.btn_deliberation = QPushButton("⚖ Délibération")
        self.btn_deliberation.setObjectName("menuButton")

        self.btn_statistiques = QPushButton("📊 Statistiques")
        self.btn_statistiques.setObjectName("menuButton")

        self.btn_quitter = QPushButton("❌ Quitter")
        self.btn_quitter.setObjectName("menuButton")

        for btn in [self.btn_dashboard, self.btn_candidats, self.btn_deliberation, self.btn_statistiques, self.btn_quitter]:
            btn.setCursor(Qt.PointingHandCursor)
            nav_layout.addWidget(btn)
        self.setLayout(nav_layout)

        
