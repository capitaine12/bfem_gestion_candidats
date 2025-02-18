from PyQt5.QtWidgets import (

    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QHBoxLayout, QGraphicsOpacityEffect,QMessageBox

    )

from PyQt5.QtCore import QPropertyAnimation, Qt
from backend.database import add_candidat, update_candidat, candidat_existe  # Import des fonctions SQLite
import re
from datetime import datetime


class CandidatForm(QDialog):
    """ Fenêtre modale pour ajouter ou modifier un candidat """
    def __init__(self, parent=None, candidat=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter / Modifier un Candidat")
        self.setFixedSize(400, 400)
        
        # Appliquer l'effet de fondu progressif
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(300)  # Durée en ms
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("""
            CandidatForm {
                background-color: white;
            }
            
            QPushButton#btn_save {
                background-color: rgb(0, 204, 0)
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                color: white;
                border: none;
            }
            
            QPushButton#btn_save:hover {
                background-color: rgb(33, 145, 80);
            }
            
            QPushButton#btn_cancel {
                background-color: rgb(255, 51, 0);
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                color: white;
                border: none;
            }
            
            QPushButton#btn_cancel:hover {
                background-color: rgb(192, 57, 43);
            }
        """)

        # fenétre principal
        layout = QVBoxLayout()

        # Champs du formulaire
        self.num_table_input = QLineEdit()
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.date_naissance_input = QLineEdit()
        self.statut_input = QComboBox()
        self.statut_input.addItems(["Admis", "Repêché", "Recalé"])

        # Ajout d'IDs pour le style
        self.num_table_input.setObjectName("champ_input")
        self.prenom_input.setObjectName("champ_input")
        self.nom_input.setObjectName("champ_input")
        self.date_naissance_input.setObjectName("champ_input")
        self.statut_input.setObjectName("champ_input")

        # Labels
        layout.addWidget(QLabel("Numéro Table:"))
        layout.addWidget(self.num_table_input)
        layout.addWidget(QLabel("Prénom:"))
        layout.addWidget(self.prenom_input)
        layout.addWidget(QLabel("Nom:"))
        layout.addWidget(self.nom_input)
        layout.addWidget(QLabel("Date de Naissance (YYYY-MM-DD):"))
        layout.addWidget(self.date_naissance_input)
        layout.addWidget(QLabel("Statut:"))
        layout.addWidget(self.statut_input)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_cancel = QPushButton("Annuler")
        # Ajout d'IDs pour le style
        self.btn_save.setObjectName("btn_save")
        self.btn_cancel.setObjectName("btn_cancel")

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Si on modifie un candidat existant, remplir les champs
        self.is_editing = False
        if candidat:
            self.is_editing = True
            self.num_table_input.setText(str(candidat[0]))
            self.prenom_input.setText(candidat[1])
            self.nom_input.setText(candidat[2])
            self.date_naissance_input.setText(candidat[3])
            self.statut_input.setCurrentText(candidat[4])
            self.num_table_input.setDisabled(True)  # Numéro de table ne doit pas être modifié

        # Connexion des boutons
        self.btn_save.clicked.connect(self.save_candidat)
        self.btn_cancel.clicked.connect(self.close)

    def save_candidat(self):
        """ Vérifie les champs et empêche les erreurs avant d'enregistrer """
        num_table = self.num_table_input.text().strip()
        prenom = self.prenom_input.text().strip()
        nom = self.nom_input.text().strip()
        date_naissance = self.date_naissance_input.text().strip()
        statut = self.statut_input.currentText()

        # Empêcher les champs vides
        if not num_table or not nom or not prenom or not date_naissance:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis avant de valider.")
            return

        # Vérifier que le numéro de table est un entier
        if not num_table.isdigit():
            QMessageBox.warning(self, "Erreur", "Le numéro de table doit être un nombre entier.")
            return
        
       # Vérification du format duprénom et nom  (pas de caractères spéciaux sauf accents et tirets)
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$", prenom):
            QMessageBox.warning(self, "Erreur", "Le prénom ne doit contenir que des lettres, espaces ou tirets.")
            return
        
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$", nom):
            QMessageBox.warning(self, "Erreur", "Le nom ne doit contenir que des lettres, espaces ou tirets.")
            return

        # Vérification du format de la date
        if not re.match(r"\d{4}-\d{2}-\d{2}", date_naissance):
            QMessageBox.warning(self, "Erreur", "La date de naissance doit être au format YYYY-MM-DD.")
            return

        # Vérifier que la date n'est pas future
        try:
            if datetime.strptime(date_naissance, "%Y-%m-%d") > datetime.today():
                QMessageBox.warning(self, "Erreur", "La date de naissance ne peut pas être dans le futur.")
                return
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Date invalide.")
            return

        #  Vérifier si un candidat avec ce numéro existe déjà
        if not self.is_editing and candidat_existe(num_table):
            QMessageBox.warning(self, "Erreur", f"Le candidat N° {num_table} existe déjà.")
            return

        #  Enregistrement sécurisé
        if self.is_editing:
            update_candidat(num_table, prenom, nom, date_naissance, statut)
        else:
            add_candidat(num_table, prenom, nom, date_naissance, statut)

        self.parent().load_candidats()
        QMessageBox.information(self, "Succès", "Le candidat a été enregistré avec succès.")
        self.close()
