from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from backend.database import get_all_jurys  # Assurez-vous d'importer la fonction pour récupérer les jurys
import logging

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion Président du Jury")
        self.setGeometry(100, 100, 1000, 600)  # Positionner et dimensionner la fenêtre

        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # Centrer le contenu verticalement

        # En-tête avec logo et drapeau
        header_layout = QHBoxLayout()

        logo_pixmap = QPixmap("frontend/images/logo.png").scaled(150, 150, Qt.KeepAspectRatio)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)

        # Texte
        title = QLabel("RÉPUBLIQUE DU SÉNÉGAL\nUn Peuple - Un But - Une Foi\nMinistère de l'Éducation nationale")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Drapeau
        flag_pixmap = QPixmap("frontend/images/drapeau.png").scaled(150, 150, Qt.KeepAspectRatio)
        flag_label = QLabel()
        flag_label.setPixmap(flag_pixmap)

        # Ajout des éléments avec un espacement
        header_layout.addWidget(logo_label)
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        header_layout.addWidget(title)
        header_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        header_layout.addWidget(flag_label)

        # Création d'un conteneur pour centrer les formulaires
        form_container = QVBoxLayout()
        form_container.setAlignment(Qt.AlignCenter)

        # Champs de saisie sans labels
        self.input_jury = QLineEdit()
        self.input_jury.setPlaceholderText("Numéro de jury")  # Placeholder pour le numéro de jury
        self.input_jury.setObjectName("champ_input")
        self.input_jury.setFixedWidth(300)  # Définir une largeur fixe

        self.input_cle = QLineEdit()
        self.input_cle.setPlaceholderText("Clé d'accès")  # Placeholder pour la clé d'accès
        self.input_cle.setObjectName("champ_input")
        self.input_cle.setEchoMode(QLineEdit.Password)
        self.input_cle.setFixedWidth(300)  # Définir une largeur fixe
        

        # Bouton de connexion
        self.btn_connexion = QPushButton("Connexion")
        self.btn_connexion.setObjectName("btnConnexion")
        self.btn_connexion.setFixedWidth(230)  # Définir une largeur fixe
        self.btn_connexion.setStyleSheet("background-color: #ff6600; color: white; padding: 10px; border-radius: 5px; font-size: 14px; margin: 5px;")
        self.btn_connexion.clicked.connect(self.check_credentials)

        # Ajout des éléments dans le conteneur
        form_container.addWidget(self.input_jury, alignment=Qt.AlignCenter)
        form_container.addWidget(self.input_cle, alignment=Qt.AlignCenter)
        form_container.addWidget(self.btn_connexion, alignment=Qt.AlignCenter)

        # Espacement en haut et en bas
        layout.addLayout(header_layout)
        layout.addSpacing(180)  # Ajouter un espace avant le formulaire
        layout.addLayout(form_container)
        layout.addStretch()  # Ajouter un espace pour centrer verticalement

        self.setLayout(layout)

        # Feuille de style
        self.setStyleSheet("""
            QLineEdit#champ_input {
                padding: 8px;
                font-size: 14px;
                border-radius: 15px;
                border: 2px solid rgb(255, 123, 0);
            }
                    
            QLineEdit#champ_input:focus,
            QComboBox#champ_input:focus {
            border-color: rgb(255, 123, 0);
            outline: none;
            }

            QPushButton {
                padding: 10px;
            }

             QPushButton#btnConnexion {
                background-color: rgb(255, 123, 0);
                color: white;
                padding: 12px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#btnConnexion:hover {
                background-color: rgb(255, 123, 0);
            }              


        """)

    def check_credentials(self):
        num_jury = self.input_jury.text().strip()
        cle_acces = self.input_cle.text().strip()

        try:
            jurys = get_all_jurys()  # Récupérer les jurys de la base de données
            for jury in jurys:
                if jury[1] == num_jury and jury[9] == cle_acces:  # Comparer avec le numéro de jury et la clé d'accès
                    QMessageBox.information(self, "Bienvenue", f"Bienvenue, {jury[6]} !")  # Afficher le nom du président
                    self.accept()  # Fermer la fenêtre de connexion
                    return

            QMessageBox.warning(self, "Erreur", "Identifiants invalides. Veuillez réessayer.")

        except Exception as e:
            logging.error(f"❌ Erreur lors de la vérification des identifiants : {e}")
            QMessageBox.critical(self, "Erreur", "Une erreur est survenue. Veuillez réessayer plus tard.")