from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QHBoxLayout, QGraphicsOpacityEffect, QMessageBox
)
from PyQt5.QtCore import QPropertyAnimation, Qt
from backend.database import add_candidat, update_candidat, candidat_existe
import re, sys, os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class CandidatForm(QDialog):
    """ Fenêtre modale pour ajouter/modifier un candidat """
    
    def __init__(self, parent=None, candidat=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter / Modifier un Candidat")
        self.setFixedSize(400, 600)  # Augmenter la hauteur pour les nouveaux champs
        
        # Effet de fondu progressif
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        self.setStyleSheet(open("frontend/styles.qss").read()) 

        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("""
                           CandidatForm {
                background-color: white;
                color: green;
                
            }

            QPushButton#btn_save {
                background-color: rgb(0, 204, 0);
                color: white;
                padding: 10px;
            }
            QPushButton#btn_save:hover {
                background-color: rgb(33, 145, 80);
            }

            QPushButton#btn_cancel {
                background-color: rgb(255, 51, 0);
                padding: 10px;
            }
            QPushButton#btn_cancel:hover {
                background-color: rgb(192, 57, 43);
            }
        """)
        
        # Mise en page
        layout = QVBoxLayout()

        # Champs du formulaire
        self.num_table_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.nom_input = QLineEdit()
        self.date_naissance_input = QLineEdit()
        self.lieu_naissance_input = QLineEdit()

        # Liste déroulante pour le sexe
        self.sexe_input = QComboBox()
        self.sexe_input.addItems(["M", "F"])

        self.nationalite_input = QLineEdit()

        # Liste déroulante pour l'épreuve facultative
        self.epreuve_facultative_input = QComboBox()
        self.epreuve_facultative_input.addItems(["Neutre", "Dessin", "Musique", "Couture"])

        # Liste déroulante pour l'aptitude sportive
        self.aptitude_sportive_input = QComboBox()
        self.aptitude_sportive_input.addItems(["Apte", "Inapte"])

        # Ajout d'IDs pour le style
        # Noms d'objet pour les QLineEdit
        self.num_table_input.setObjectName("champ_input")
        self.prenom_input.setObjectName("champ_input")
        self.nom_input.setObjectName("champ_input")
        self.date_naissance_input.setObjectName("champ_input")
        self.lieu_naissance_input.setObjectName("champ_input")
        self.nationalite_input.setObjectName("champ_input")

        # Noms d'objet pour les ComboBox
        self.sexe_input.setObjectName("champ_input")
        self.epreuve_facultative_input.setObjectName("champ_input")
        self.aptitude_sportive_input.setObjectName("champ_input")

        # Labels et champs
        layout.addWidget(QLabel("Numéro Table:"))
        layout.addWidget(self.num_table_input)

        layout.addWidget(QLabel("Prénom:"))
        layout.addWidget(self.prenom_input)

        layout.addWidget(QLabel("Nom:"))
        layout.addWidget(self.nom_input)

        layout.addWidget(QLabel("Date de Naissance (YYYY-MM-DD):"))
        layout.addWidget(self.date_naissance_input)

        layout.addWidget(QLabel("Lieu de Naissance:"))
        layout.addWidget(self.lieu_naissance_input)

        layout.addWidget(QLabel("Sexe:"))
        layout.addWidget(self.sexe_input)

        layout.addWidget(QLabel("Nationalité:"))
        layout.addWidget(self.nationalite_input)

        layout.addWidget(QLabel("Épreuve Facultative:"))
        layout.addWidget(self.epreuve_facultative_input)

        layout.addWidget(QLabel("Aptitude Sportive:"))
        layout.addWidget(self.aptitude_sportive_input)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_cancel = QPushButton("Annuler")

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save.setObjectName("btn_save")
        self.btn_cancel.setObjectName("btn_cancel")

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Si on modifie un candidat, remplir les champs
        self.is_editing = False
        if candidat:
            self.is_editing = True
            self.num_table_input.setText(str(candidat[0]))
            self.prenom_input.setText(candidat[1])
            self.nom_input.setText(candidat[2])
            self.date_naissance_input.setText(candidat[3])
            self.lieu_naissance_input.setText(candidat[4])
            self.sexe_input.setCurrentText(candidat[5])
            self.nationalite_input.setText(candidat[6])
            self.epreuve_facultative_input.setCurrentText(candidat[7])
            self.aptitude_sportive_input.setCurrentText(candidat[8])

            self.num_table_input.setDisabled(True)  # Numéro de table ne doit pas être modifié

        # Connexion des boutons
        self.btn_save.clicked.connect(self.save_candidat)
        self.btn_cancel.clicked.connect(self.close)
        
    #  Donner une coloration rouge si un champ est omis ou remplie par des valeur erroner
    def mark_invalid_field(self, field, is_invalid):
        """ Ajoute ou enlève la classe 'invalid' aux champs ayant une erreur """
        if is_invalid:
            field.setStyleSheet("border: 2px solid red; background-color: #ffe6e6;")
        else:
            field.setStyleSheet("")
    
    def save_candidat(self):
        """ Vérifie les champs et empêche les erreurs avant d'enregistrer """
        num_table = self.num_table_input.text().strip()
        prenom = self.prenom_input.text().strip()
        nom = self.nom_input.text().strip()
        date_naissance = self.date_naissance_input.text().strip()
        lieu_naissance = self.lieu_naissance_input.text().strip()
        sexe = self.sexe_input.currentText()
        nationalite = self.nationalite_input.text().strip().upper()
        epreuve_facultative = self.epreuve_facultative_input.currentText()
        aptitude_sportive = self.aptitude_sportive_input.currentText()

        # Vérifier les champs obligatoires et colorer ceux qui sont vides
        champs_invalides = []  # Liste des champs à marquer en rouge

        if not num_table:
            champs_invalides.append(self.num_table_input)
        if not prenom:
            champs_invalides.append(self.prenom_input)
        if not nom:
            champs_invalides.append(self.nom_input)
        if not date_naissance:
            champs_invalides.append(self.date_naissance_input)
        if not lieu_naissance:
            champs_invalides.append(self.lieu_naissance_input)
        if not nationalite:
            champs_invalides.append(self.nationalite_input)

        # Appliquer la coloration rouge aux champs invalides
        for champ in champs_invalides:
            self.mark_invalid_field(champ, True)

        # Vérifier si des champs sont vides et afficher un message
        if champs_invalides:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis.")
            return

        # Vérifier que le numéro de table est un entier
        if not num_table.isdigit():
            self.mark_invalid_field(self.num_table_input, True)
            QMessageBox.warning(self, "Erreur", "Le numéro de table doit être un nombre entier.")
            return
        else:
            self.mark_invalid_field(self.num_table_input, False)

        # Vérification du format du prénom et du nom (lettres uniquement)
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$", prenom):
            self.mark_invalid_field(self.prenom_input, True)
            QMessageBox.warning(self, "Erreur", "Le prénom ne doit contenir que des lettres, espaces ou tirets.")
            return
        else:
            self.mark_invalid_field(self.prenom_input, False)

        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$", nom):
            self.mark_invalid_field(self.nom_input, True)
            QMessageBox.warning(self, "Erreur", "Le nom ne doit contenir que des lettres, espaces ou tirets.")
            return
        else:
            self.mark_invalid_field(self.nom_input, False)

        # Vérification du format du lieu de naissance (lettres uniquement)
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s-]+$", lieu_naissance):
            self.mark_invalid_field(self.lieu_naissance_input, True)
            QMessageBox.warning(self, "Erreur", "Le lieu de naissance ne doit contenir que des lettres.")
            return
        else:
            self.mark_invalid_field(self.lieu_naissance_input, False)

        # Vérification du format de la nationalité (ex: "SEN", "FRA", "MLI", "USA")
        if not re.match(r"^[A-Z]{3}$", nationalite):
            self.mark_invalid_field(self.nationalite_input, True)
            QMessageBox.warning(self, "Erreur", "La nationalité doit être un code de 3 lettres (ex: SEN, FRA, USA).")
            return
        else:
            self.mark_invalid_field(self.nationalite_input, False)

        # Vérification du format de la date de naissance (YYYY-MM-DD)
        if not re.match(r"\d{4}-\d{2}-\d{2}", date_naissance):
            self.mark_invalid_field(self.date_naissance_input, True)
            QMessageBox.warning(self, "Erreur", "La date de naissance doit être au format YYYY-MM-DD.")
            return
        else:
            self.mark_invalid_field(self.date_naissance_input, False)

        # Vérifier que la date de naissance est valide et que l'âge est correct
        try:
            birth_date = datetime.strptime(date_naissance, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if birth_date > today:
                self.mark_invalid_field(self.date_naissance_input, True)
                QMessageBox.warning(self, "Erreur", "La date de naissance ne peut pas être dans le futur.")
                return

            if age < 10 or age > 30:
                self.mark_invalid_field(self.date_naissance_input, True)
                QMessageBox.warning(self, "Erreur", "L'âge du candidat doit être compris entre 10 et 30 ans.")
                return

        except ValueError:
            self.mark_invalid_field(self.date_naissance_input, True)
            QMessageBox.warning(self, "Erreur", "Date invalide.")
            return
        else:
            self.mark_invalid_field(self.date_naissance_input, False)

        # Vérification si un candidat avec ce numéro existe déjà (uniquement pour l'ajout)
        if not self.is_editing and candidat_existe(num_table):
            self.mark_invalid_field(self.num_table_input, True)
            QMessageBox.warning(self, "Erreur", f"Le candidat N° {num_table} existe déjà.")
            return
        else:
            self.mark_invalid_field(self.num_table_input, False)

            # Ajout des boutons personnalisés
        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirmation d'enregistrement")
        confirmation.setText("Voulez-vous vraiment enregistrer ce candidat ?")
        confirmation.setIcon(QMessageBox.Question)

        # Ajout des boutons personnalisés
        btn_yes = confirmation.addButton("Oui", QMessageBox.AcceptRole)
        btn_no = confirmation.addButton("Non", QMessageBox.RejectRole)
        # Affichage de la boîte de dialogue
        confirmation.exec_()

        # si l'utilisateur a cliqué sur "Oui"
        if confirmation.clickedButton() == btn_no:
            return  # Annuler l'enregistrement

        # Enregistrement du candidat (ajout ou modification)
        jury_id = None  # À gérer plus tard

        if self.is_editing:
            update_candidat(num_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, epreuve_facultative, aptitude_sportive, jury_id)
        else:
            add_candidat(num_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, epreuve_facultative, aptitude_sportive, jury_id)

        QMessageBox.information(self, "Succès", "Le candidat a été enregistré avec succès.")
        self.accept()

