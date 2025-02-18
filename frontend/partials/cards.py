from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QDialog
from PyQt5.QtCore import Qt
from frontend.partials.ia_data import ia_info  #? Importation des données du fichier ia_data


def create_ia_cards(layout):
    """Crée des cartes pour les inspections académiques."""
    card_layout = QVBoxLayout()  # Layout vertical pour les lignes de cartes

    # Créer une ligne de cartes
    for i, ia in enumerate(ia_info):
        card = create_ia_card(ia)
        
        # Si c'est le début d'une nouvelle ligne, ajouter un layout horizontal
        if i % 3 == 0:
            row_layout = QHBoxLayout()
            card_layout.addLayout(row_layout)
        
        row_layout.addWidget(card)  # Ajouter la carte à la ligne actuelle

    layout.addLayout(card_layout)

def create_ia_card(ia):
    """Crée une carte pour une inspection académique."""
    card = QFrame()
    card.setObjectName("iaCard")  # Ajout d'un ID pour la carte
    card.setFrameShape(QFrame.StyledPanel)
    card.setFixedSize(220, 200)  # Taille fixe pour les cartes
    card_layout = QVBoxLayout()

    # Ajout des informations de l'IA
    name_label = QLabel(ia["nom"])
    name_label.setObjectName("iaNameLabel")
    card_layout.addWidget(name_label, alignment=Qt.AlignCenter)
    
    address_label = QLabel(f"Adresse: {ia['adresse']}")
    address_label.setObjectName("iaAddressLabel")
    card_layout.addWidget(address_label, alignment=Qt.AlignLeft)

    tel_label = QLabel(f"Tél: {ia['tel']}")
    tel_label.setObjectName("iaTelLabel")
    card_layout.addWidget(tel_label, alignment=Qt.AlignLeft)

    if "email" in ia:
        email_label = QLabel(f"Email: {ia['email']}")
        email_label.setObjectName("iaEmailLabel")
        card_layout.addWidget(email_label, alignment=Qt.AlignLeft)

    site_label = QLabel(f"Site Web: {ia['site']}")
    site_label.setObjectName("iaSiteLabel")
    card_layout.addWidget(site_label, alignment=Qt.AlignLeft)

    
    card.setLayout(card_layout)
    return card

class CardsWindow(QDialog):
    """Fenêtre pour afficher les cartes des inspections académiques."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inspections Académiques")
        layout = QVBoxLayout()
        create_ia_cards(layout)  # Ajoutez les cartes au layout

        # Bouton de fermeture avec ID
        button_layout = QHBoxLayout()
        close_button = QPushButton("Fermer")
        close_button.setObjectName("closeButton")  # Ajout d'un ID pour le bouton
        close_button.setFixedSize(150, 40)
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button, alignment=Qt.AlignRight)
        layout.addWidget(close_button)

        self.setLayout(layout)