from datetime import datetime
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QLineEdit, QPushButton,QHBoxLayout, QMessageBox, QSizePolicy, QFrame,QComboBox, QGridLayout
    )

import sqlite3
from PyQt5.QtWidgets import QFileDialog
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtGui import QIcon
import os,sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.controllers import NavigationMenu  #? Import du menu de navigation
from backend.database import delete_candidat, get_all_candidats, get_candidats_avec_statut, get_all_jurys  #? Import de la base de données

from frontend.partials.form import CandidatForm  #? Import du formulaire d'ajout / modification
from frontend.partials.ia_data import ia_info  #? Importation des données du fichier ia_data
from frontend.partials.cards import CardsWindow
from frontend.partials.detailsform import DetailsForm
from frontend.partials.notesdialog import NotesDialog


#!::::::::::::::::::::::::::::::::::::::::::::::::::::: fnt de gestion d'effet de survole des btns CRUD ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: fnt de gestion d'effet de survole des btns CRUD ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: fnt de gestion d'effet de survole des btns CRUD ::::::::::::::::::::::::::::::::::::::::

def animate_button(button):
        """ Effet d'animation au survol """
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        animation.setStartValue(button.geometry())
        animation.setEndValue(button.geometry().adjusted(-2, -2, 2, 2))  #? Légère expansion
        animation.start()

#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE ACCUEIL ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE ACCUEIL ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE ACCUEIL ::::::::::::::::::::::::::::::::::::::::

class DashboardPage(QWidget):
    """Page d'accueil du tableau de bord."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        #?label = QLabel("Bienvenue sur le Dashboard")
        self.setObjectName("dashboardPage")
        

        # QLabel pour l'image de fond
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap("frontend/images/img.png"))
        self.background_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        """ self.setStyleSheet(
                           "background-repeat: no-repeat;"
                           "background-position: center bottom;"
                           "background-color: rgba(255, 255, 255, 0.575);"
                           "border-radius: 5px;") """
        layout = QVBoxLayout()
        label = QLabel("Bienvenue sur le Dashboard")
        label.setObjectName("titlePage")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(self.background_label)
        
        # Bouton pour ouvrir la fenêtre des cartes
        button_layout = QHBoxLayout() 
        cards_button = QPushButton("Les Inspections Académiques")
        cards_button.setObjectName("showCardsButton")  # Ajout d'un ID pour le bouton
        cards_button.setFixedSize(300, 40)
        cards_button.clicked.connect(self.open_cards_window)
        button_layout.addWidget(cards_button, alignment=Qt.AlignRight)
        layout.addWidget(cards_button)

        self.setLayout(layout)

    def open_cards_window(self):
        """Ouvre la fenêtre des cartes."""
        cards_window = CardsWindow()
        cards_window.exec_()  # Affiche la fenêtre modale

        #def resizeEvent(self, event):
            #"""Ajuste l'image de fond lorsque la fenêtre est redimensionnée."""
            #self.background_label.setGeometry(0, 0, self.width(), self.height())


#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE CANDIDAT ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE CANDIDAT ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE CANDIDAT ::::::::::::::::::::::::::::::::::::::::

class CandidatsPage(QWidget):
    """Page de gestion des candidats."""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("candidatsPage")
        layout = QVBoxLayout()

        label = QLabel("📋 Liste des Candidats")
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("titlePage")

        #? ====== Barre de recherche ======
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par numéro de table ou nom ...")
        self.search_button = QPushButton("Rechercher")
        self.search_button.setObjectName("searchButton")
        self.search_button.setCursor(Qt.PointingHandCursor)
        self.search_button.clicked.connect(self.search_candidat)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        #? ====== Création du tableau avec nouvelles colonnes ======
        self.table = QTableWidget()
        self.table.setColumnCount(9) 
        self.table.setHorizontalHeaderLabels([
            "N° Table", "Prénom", "Nom", "Date Naissance", "Lieu Naissance", 
            "Sexe", "Nationalité", "Épreuve Fac.", "Aptitude Sport."
        ])
        self.table.setObjectName("candidatsTable")
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        #? Chargement des candidats depuis SQLite
        self.load_candidats()

        #? ====== Boutons Ajouter / Modifier / Supprimer ======
        btn_layout = QHBoxLayout()
        icon_path = os.path.join(os.path.dirname(__file__), "images")

        self.btn_add = QPushButton(" Ajouter")
        self.btn_add.setIcon(QIcon(os.path.join(icon_path, "add.png")))

        self.btn_edit = QPushButton(" Modifier")
        self.btn_edit.setIcon(QIcon(os.path.join(icon_path, "edit.png")))

        self.btn_delete = QPushButton(" Supprimer")
        self.btn_delete.setIcon(QIcon(os.path.join(icon_path, "delete.png")))

        #? ====== Ajout des nouveaux boutons ======
        self.btn_notes = QPushButton(" Notes")
        self.btn_notes.setIcon(QIcon(os.path.join(icon_path, "notes.png")))  # Icône personnalisée
        self.btn_notes.setEnabled(False)  # Désactivé au départ

        self.btn_details = QPushButton(" Détails")
        self.btn_details.setIcon(QIcon(os.path.join(icon_path, "details.png")))  # Icône personnalisée
        self.btn_details.setEnabled(False)  # Désactivé au départ

        # ID pour le QSS
        self.btn_add.setObjectName("btn_add")
        self.btn_edit.setObjectName("btn_edit")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_notes.setObjectName("btn_notes")
        self.btn_details.setObjectName("btn_details")

        self.btn_add.installEventFilter(self)
        self.btn_edit.installEventFilter(self)
        self.btn_delete.installEventFilter(self)

        
        btn_layout.addWidget(self.btn_notes)  # Ajouter bouton Notes
        btn_layout.addWidget(self.btn_details)  # Ajouter bouton Détails
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)


        layout.addLayout(btn_layout)

        layout.addWidget(label)
        layout.addLayout(search_layout)  # Ajout du champ de recherche
        layout.addWidget(self.table)
        self.setLayout(layout)

        #? Connexions des boutons
        self.btn_add.clicked.connect(self.open_add_form)
        self.btn_edit.clicked.connect(self.open_edit_form)
        self.btn_delete.clicked.connect(self.confirm_delete)
        self.btn_notes.clicked.connect(self.open_notes_form)
        self.btn_details.clicked.connect(self.open_details_window)

        self.table.itemSelectionChanged.connect(self.update_button_states)

    def load_candidats(self, candidats=None):
        """Charge les candidats depuis SQLite et les affiche dans le tableau"""
        if candidats is None:
            candidats = get_all_candidats()

        self.table.setRowCount(len(candidats))
        for row, candidat in enumerate(candidats):
            for col, valeur in enumerate(candidat):
                item = QTableWidgetItem(str(valeur))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

    def search_candidat(self):
        """Recherche un candidat par numéro de table ou nom"""
        search_text = self.search_input.text().strip().lower()
        candidats = [c for c in get_all_candidats() if search_text in str(c[0]).lower() or search_text in c[2].lower()]
        self.load_candidats(candidats)

    def open_add_form(self):
        """ Ouvre la fenêtre pour ajouter un candidat """
        self.form = CandidatForm(self)
        if self.form.exec_():
            self.load_candidats()

    def open_edit_form(self):
        """ Ouvre la fenêtre pour modifier un candidat sélectionné """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un candidat à modifier.")
            return

        #? Récupération des valeurs du tableau
        num_table = self.table.item(selected_row, 0).text()
        prenom = self.table.item(selected_row, 1).text()
        nom = self.table.item(selected_row, 2).text()
        date_naissance = self.table.item(selected_row, 3).text()
        lieu_naissance = self.table.item(selected_row, 4).text()
        sexe = self.table.item(selected_row, 5).text()
        nationalite = self.table.item(selected_row, 6).text()
        epreuve_facultative = self.table.item(selected_row, 7).text()
        aptitude_sportive = self.table.item(selected_row, 8).text()

        candidat_data = (num_table, prenom, nom, date_naissance, lieu_naissance, sexe, 
                         nationalite, epreuve_facultative, aptitude_sportive)

        self.form = CandidatForm(self, candidat_data)
        if self.form.exec_():
            self.load_candidats()

    def confirm_delete(self):
        """ Affiche une confirmation avant de supprimer un candidat """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un candidat à supprimer.")
            return

        num_table = self.table.item(selected_row, 0).text()

        confirmation = QMessageBox(self)
        confirmation.setWindowTitle("Confirmation de suppression")
        confirmation.setText(f"Voulez-vous vraiment supprimer le candidat N° {num_table} ?")

        btn_yes = confirmation.addButton("Oui", QMessageBox.AcceptRole)
        btn_no = confirmation.addButton("Non", QMessageBox.RejectRole)

        confirmation.setIcon(QMessageBox.Warning)
        confirmation.exec_()

        if confirmation.clickedButton() == btn_yes:
            delete_candidat(num_table)
            self.load_candidats()
            QMessageBox.information(self, "Succès", "Le candidat a été supprimé avec succès.")

    def eventFilter(self, obj, event):
        """ Détecte le survol des boutons et applique l’animation """
        if event.type() == event.Enter and isinstance(obj, QPushButton):
            animate_button(obj)
        return super().eventFilter(obj, event)
    
    def update_button_states(self):
        """ Active ou désactive les boutons Notes et Détails selon la sélection """
        selected_row = self.table.currentRow()
        has_selection = selected_row != -1
        self.btn_notes.setEnabled(has_selection)
        self.btn_details.setEnabled(has_selection)


    def open_notes_form(self):
        """ Ouvre la boîte de dialogue pour gérer les notes d'un candidat sélectionné """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un candidat.")
            return  

        num_table = self.table.item(selected_row, 0).text()  # Récupération du numéro de table

        from frontend.partials.notesdialog import NotesDialog
        self.dialog = NotesDialog(self, num_table)
        self.dialog.show()



    def open_details_window(self):
        """ Ouvre une fenêtre affichant tous les détails d'un candidat """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un candidat.")
            return  

        #? Récupération des données du candidat sélectionné
        num_table = self.table.item(selected_row, 0).text()
        prenom = self.table.item(selected_row, 1).text()
        nom = self.table.item(selected_row, 2).text()
        date_naissance = self.table.item(selected_row, 3).text()
        lieu_naissance = self.table.item(selected_row, 4).text()
        sexe = self.table.item(selected_row, 5).text()
        nationalite = self.table.item(selected_row, 6).text()
        epreuve_facultative = self.table.item(selected_row, 7).text()
        aptitude_sportive = self.table.item(selected_row, 8).text()

        candidat_data = (num_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, epreuve_facultative, aptitude_sportive)

        self.details_window = DetailsForm(self, candidat_data)
        self.details_window.show()
    
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE DELIBERATION ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE DELIBERATION ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE DELIBERATION ::::::::::::::::::::::::::::::::::::::::

def get_resultats():
    """ Récupère les résultats des candidats depuis la base de données """
    try:
        with sqlite3.connect('data/candidatbfem.db') as conn:
            cursor = conn.cursor()

            # Requête avec jointure pour récupérer les résultats
            cursor.execute("""
                SELECT c.num_table, c.prenom, c.nom, d.total_points, d.statut
                FROM candidats c
                JOIN deliberation d ON c.id = d.candidat_id
                ORDER BY CASE d.statut
                    WHEN 'Admis' THEN 1
                    WHEN 'Repêchable au 1er tour' THEN 2
                    WHEN 'Second tour' THEN 3
                    WHEN 'Repêchable au 2nd tour' THEN 4
                    WHEN 'Échoué' THEN 5
                    ELSE 6
                END
            """)

            resultats = cursor.fetchall()
        return resultats

    except sqlite3.Error as e:
        logging.warning(f"❌ Erreur lors de l'accès à la base de données : {e}")
        return []
""" resultats = get_resultats()  # Fonction pour récupérer les résultats
pv = generer_pv(resultats)
print(pv) """
class DeliberationPage(QWidget):
    """ Page pour la délibération """
    def __init__(self):
        super().__init__()
        self.setObjectName("deliberationPage")
        layout = QVBoxLayout()

        # Titre de la page
        label = QLabel("📝 Délibération des candidats")
        label.setObjectName("titlePage")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Conteneur pour les boutons (grille)
        button_layout = QGridLayout()
        button_layout.setAlignment(Qt.AlignCenter)  # Centrer les boutons
        button_layout.setSpacing(10)  # Espacement uniforme

        # Création des boutons d'impression
        self.btn_print_candidats = QPushButton("📄 Imprimer Liste des Candidats")
        self.btn_print_anonymat = QPushButton("🔒 Imprimer Liste Anonyme")
        self.btn_print_resultats = QPushButton("🏆 Imprimer Résultats")
        self.btn_print_pv = QPushButton("📜 Imprimer PV de Délibération")
        self.btn_print_releve_1 = QPushButton("📊 Imprimer Relevé Notes - 1er Tour")
        self.btn_print_releve_2 = QPushButton("📊 Imprimer Relevé Notes - 2nd Tour")

        # Style des boutons
        for button in [self.btn_print_candidats, self.btn_print_anonymat, self.btn_print_resultats,
                       self.btn_print_pv, self.btn_print_releve_1, self.btn_print_releve_2]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(255, 102, 0);
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgb(200, 80, 0);
                }
            """)

        # Ajout des boutons à la grille (2 lignes, 3 colonnes)
        button_layout.addWidget(self.btn_print_candidats, 0, 0)
        button_layout.addWidget(self.btn_print_anonymat, 0, 1)
        button_layout.addWidget(self.btn_print_resultats, 0, 2)
        button_layout.addWidget(self.btn_print_pv, 1, 0)
        button_layout.addWidget(self.btn_print_releve_1, 1, 1)
        button_layout.addWidget(self.btn_print_releve_2, 1, 2)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connexion des boutons aux fonctions
        self.btn_print_candidats.clicked.connect(self.imprimer_liste_candidats)
        self.btn_print_anonymat.clicked.connect(self.imprimer_liste_anonymat)
        self.btn_print_resultats.clicked.connect(self.imprimer_liste_resultats)
        self.btn_print_pv.clicked.connect(self.imprimer_pv_deliberation)
        self.btn_print_releve_1.clicked.connect(self.print_releve_1)
        self.btn_print_releve_2.clicked.connect(self.print_releve_2)

        # Menu déroulant pour filtrer les résultats
        self.filtre_statut = QComboBox()
        self.filtre_statut.addItems(["Tous", "Admis", "Second Tour", "Repêchable au 1er tour",
                                     "Repêchable au 2nd tour", "Échoué"])
        self.filtre_statut.currentTextChanged.connect(self.filtrer_par_statut)
        layout.addWidget(self.filtre_statut)
        self.filtre_statut.setStyleSheet("padding: 5px; border: 1px solid rgb(255, 102, 0); margin-bottom: 5px; font-size: 15px")

        # Création du tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "N° Table", "Prénom", "Nom", "Naissance", "Sexe", "Nationalité", "Points", "Statut"
        ])
        self.table.setObjectName("deliberationTable")
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.setLayout(layout)

        # Charger les résultats
        self.load_deliberation()

    def filtrer_par_statut(self, statut_recherche):
        """ Filtre les candidats selon leur statut sélectionné """
        resultats = get_candidats_avec_statut()  # Assurez-vous que cette fonction est bien importée.

        if statut_recherche != "Tous":
            resultats = [candidat for candidat in resultats if candidat[-1] == statut_recherche]

        self.table.setRowCount(len(resultats))

        for row_idx, candidat in enumerate(resultats):
            for col_idx, data in enumerate(candidat):
                item = QTableWidgetItem(str(data))
                
                # Appliquer une couleur de fond selon le statut
                if col_idx == 7:  # Colonne Statut
                    if data == "Admis":
                        item.setBackground(QColor(0, 255, 0))
                    elif data == "Second Tour":
                        item.setBackground(QColor(255, 255, 0)) 
                    elif data == "Repêchable au 1er tour":
                        item.setBackground(QColor(0, 0, 255))
                    elif data == "Repêchable au 2nd tour":
                        item.setBackground(QColor(255, 165, 0))  
                    elif data == "Échoué":
                        item.setBackground(QColor(255, 0, 0)) 
                
                self.table.setItem(row_idx, col_idx, item)


    def load_deliberation(self):
        """ Charge les résultats des candidats depuis la base de données """
        resultats = get_candidats_avec_statut()

        self.table.setRowCount(len(resultats))
        for row_idx, candidat in enumerate(resultats):
            for col_idx, data in enumerate(candidat):
                item = QTableWidgetItem(str(data))
                # Appliquer le style de fond au statut
                if col_idx == 7:  # Colonne du statut
                    statut = str(data)
                    if statut == "Admis":
                        item.setBackground(QColor(0, 255, 0))
                    elif statut == "Second Tour":
                        item.setBackground(QColor(255, 255, 0)) 
                    elif statut == "Repêchable au 1er tour":
                        item.setBackground(QColor(0, 0, 255))
                    elif statut == "Repêchable au 2nd tour":
                        item.setBackground(QColor(255, 165, 0))  
                    elif statut == "Échoué":
                        item.setBackground(QColor(255, 0, 0)) 

                self.table.setItem(row_idx, col_idx, item)

    def refresh_deliberation(self):
        """ Rafraîchit l'affichage après l'importation des notes """
        self.load_deliberation()

    def imprimer_liste_candidats(self):
        """ Génère un PDF avec la liste des candidats """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la liste des candidats", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )

        if not file_path:
            return  # L'utilisateur a annulé

        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Images : Drapeau et Logo
            drapeau = Image("frontend/images/drapeau.png", width=1.5*cm, height=1*cm)  
            logo = Image("frontend/images/logo.png", width=1.5*cm, height=1*cm) 
            
            # En-tête officiel
            header_text = """<para align=center>
            <b>RÉPUBLIQUE DU SÉNÉGAL</b><br/>
            Un Peuple - Un But - Une Foi<br/>
            <b>Ministère de l'Éducation nationale</b><br/><br/>
            </para>"""

            # Créer un tableau pour le logo, le texte et le drapeau
            logo_table = Table([[logo, Paragraph(header_text, styles['Normal']), drapeau]], colWidths=[2*cm, None, 2*cm])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Alignement du logo à gauche
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),  # Alignement du drapeau à droite
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),  # Alignement vertical du logo
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),  # Alignement vertical du drapeau
            ]))
            
            elements.append(logo_table)
            elements.append(Paragraph("\n", styles['Normal']))  # Saut de ligne

            # Titre
            elements.append(Paragraph("<b>Liste des Candidats</b>", styles['Title']))
            elements.append(Paragraph("\n"))

            # Récupération des candidats depuis la BDD
            candidats = get_all_candidats()

            # Définition du tableau
            data = [["N° Table", "Prénom", "Nom", "Date de Naissance", "Lieu de Naissance", "Sexe", "Nationalité"]]

            for candidat in candidats:
                candidat_formate = [
                    str(candidat[0]),  # Numéro de table
                    candidat[1].capitalize(),  # Prénom
                    candidat[2].upper(),  # Nom
                    str(candidat[3]),  # Date de naissance
                    candidat[4].title(),  # Lieu de naissance
                    candidat[5].upper(),  # Sexe
                    candidat[6].capitalize()  # Nationalité
                ]
                data.append(candidat_formate)

            table = Table(data, colWidths=[3*cm, 3.5*cm, 3.5*cm, 3.5*cm, 4*cm, 1*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
            ]))

            elements.append(table)
            doc.build(elements)

            # Afficher un message de succès
            QMessageBox.information(self, "Succès", "Liste des candidats enregistrée avec succès !")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")

    
    #!::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


    def imprimer_liste_anonymat(self):
        """ Génère un PDF avec la liste d'anonymat """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la liste d'anonymat", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )

        if not file_path:
            return  # L'utilisateur a annulé

        try:
            # Récupérer les candidats depuis la base de données ou une autre source
            candidats = get_candidats_avec_statut()  # Assurez-vous que cette fonction est disponible

            # Générer la liste d'anonymat
            liste_anonymat = self.generer_liste_anonymat(candidats)

            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Images : Drapeau et Logo
            drapeau = Image("frontend/images/drapeau.png", width=1.5 * cm, height=1 * cm)
            logo = Image("frontend/images/logo.png", width=1.5 * cm, height=1 * cm)
           

            # En-tête officiel
            header_text = """<para align=center>
            <b>RÉPUBLIQUE DU SÉNÉGAL</b><br/>
            Un Peuple - Un But - Une Foi<br/>
            <b>Ministère de l'Éducation nationale</b><br/><br/>
            </para>"""

            # Créer un tableau pour le logo, le texte et le drapeau
            logo_table = Table([[logo, Paragraph(header_text, styles['Normal']), drapeau]], colWidths=[2 * cm, None, 2 * cm])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
            ]))

            elements.append(logo_table)
            elements.append(Paragraph("\n", styles['Normal']))  # Saut de ligne

            # Titre
            elements.append(Paragraph("<b>Liste d'Anonymat</b>", styles['Title']))
            elements.append(Paragraph("\n"))

            # Définition du tableau d'anonymat
            data = [["N° Anonymat", "N° Table", "Prénom", "Nom"]]  # Modification ici

            for index, candidat in enumerate(candidats):
                anonymat = f"ANO{index + 1:03d}"  # Générer un numéro d'anonymat
                data.append([anonymat, candidat[0], candidat[1], candidat[2]])  # Ajouter les colonnes séparées

            table = Table(data, colWidths=[4 * cm, 3 * cm, 3.5 * cm, 3.5 * cm])  # Ajustez les largeurs si nécessaire
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
            ]))

            elements.append(table)
            doc.build(elements)

            # Afficher un message de succès
            QMessageBox.information(self, "Succès", "Liste d'anonymat enregistrée avec succès !")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")

    def generer_liste_anonymat(self, candidats):
        """ Génère une liste d'anonymat pour les candidats """
        liste_anonymat = []
        for index, candidat in enumerate(candidats):
            anonymat = f"ANO{index + 1:03d}"  # Générer un numéro d'anonymat
            liste_anonymat.append((anonymat, candidat[0], candidat[1], candidat[2]))  # Inclure N° Table, Prénom, Nom
        return liste_anonymat
                
#!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


    def imprimer_liste_resultats(self):
        """ Génère un PDF avec la liste des résultats """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer la liste des résultats", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )

        if not file_path:
            return  # L'utilisateur a annulé

        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Images : Drapeau et Logo
            drapeau = Image("frontend/images/drapeau.png", width=1.5 * cm, height=1 * cm)
            logo = Image("frontend/images/logo.png", width=1.5 * cm, height=1 * cm)

            # En-tête officiel
            header_text = """<para align=center>
            <b>RÉPUBLIQUE DU SÉNÉGAL</b><br/>
            Un Peuple - Un But - Une Foi<br/>
            <b>Ministère de l'Éducation nationale</b><br/><br/>
            </para>"""

            # Créer un tableau pour le logo, le texte et le drapeau
            logo_table = Table([[logo, Paragraph(header_text, styles['Normal']), drapeau]], colWidths=[2 * cm, None, 2 * cm])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
            ]))

            elements.append(logo_table)
            elements.append(Paragraph("\n", styles['Normal']))  # Saut de ligne

            # Titre
            elements.append(Paragraph("<b>Liste des Résultats</b>", styles['Title']))
            elements.append(Paragraph("\n"))

            # Récupération des résultats depuis la BDD
            resultats = get_resultats()  # Assurez-vous que cette fonction est définie

            # Définition du tableau
            data = [["N° Table", "Prénom", "Nom", "Points", "Statut"]]

            for resultat in resultats:
                resultat_formate = [
                    str(resultat[0]),  # Numéro de table
                    resultat[1].capitalize(),  # Prénom
                    resultat[2].upper(),  # Nom
                    str(resultat[3]),  # Points
                    resultat[4].capitalize()  # Statut
                ]
                data.append(resultat_formate)

            table = Table(data, colWidths=[2 * cm, 4 * cm, 4 * cm, 2 * cm, 6 * cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
            ]))

            elements.append(table)
            doc.build(elements)

            # Afficher un message de succès
            QMessageBox.information(self, "Succès", "Liste des résultats enregistrée avec succès !")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")


   
#!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    def imprimer_pv_deliberation(self):
        """ Génère un PDF avec le Procès-Verbal de Délibération """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le PV de Délibération", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )

        if not file_path:
            return  # L'utilisateur a annulé

        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Images : Drapeau et Logo
            drapeau = Image("frontend/images/drapeau.png", width=1.5*cm, height=1*cm)  
            logo = Image("frontend/images/logo.png", width=1.5*cm, height=1*cm) 
            
            # En-tête officiel
            header_text = """<para align=center>
            <b>RÉPUBLIQUE DU SÉNÉGAL</b><br/>
            Un Peuple - Un But - Une Foi<br/>
            <b>Ministère de l'Éducation nationale</b><br/><br/>
            </para>"""

            # Tableau pour le logo, le texte et le drapeau
            logo_table = Table([[logo, Paragraph(header_text, styles['Normal']), drapeau]], colWidths=[2*cm, None, 2*cm])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('VALIGN', (2, 0), (2, 0), 'MIDDLE'),
            ]))
            
            elements.append(logo_table)
            elements.append(Spacer(1, 10))  # Espace entre l'en-tête et le contenu

            # Titre du PV
            elements.append(Paragraph("<b>PROCÈS-VERBAL DE DÉLIBÉRATION</b>", styles['Title']))
            elements.append(Spacer(1, 10)) 

            # Date actuelle
            date_str = datetime.now().strftime("%d/%m/%Y")
            elements.append(Paragraph(f"Date : {date_str}", styles['Normal']))

            # Récupération des informations du jury
            jury_info = get_all_jurys()
            if jury_info:
                jury = jury_info[0]  # On prend le premier jury
                jury_text = f"""
                    <b>IA :</b> {jury[1]}<br/>
                    <b>Localité :</b> {jury[3]}<br/>
                    <b>Centre d'examen :</b> {jury[4]}<br/>
                    <b>Saison :</b> 2024/2025<br/>
                    <b>Président du Jury :</b> {jury[5]}<br/>
                    <b>N° Jury :</b> {jury[0]}<br/>
                    <b>Examinateurs :</b> M. Diallo, Mme Ba, M. Ndiaye
                """
                elements.append(Paragraph(jury_text, styles['Normal']))
                elements.append(Spacer(1, 10))

            # Récupération des résultats depuis la BDD
            candidats = get_candidats_avec_statut()

            # Vérification si des candidats existent
            if not candidats:
                QMessageBox.warning(self, "Avertissement", "Aucun candidat trouvé dans la base de données.")
                return

            # Tri des candidats par total de points (du plus élevé au plus bas)
            candidats.sort(key=lambda x: x[6], reverse=True)

            # Remplacement des statuts "Repêchable au 1er tour" -> "Admis" et "Repêchable au 2nd tour" -> "Second Tour"
            for i in range(len(candidats)):
                if candidats[i][7] == "Repêchable au 1er tour":
                    candidats[i] = (*candidats[i][:7], "Admis Doffice")
                elif candidats[i][7] == "Repêchable au 2nd tour":
                    candidats[i] = (*candidats[i][:7], "Second Tour")

            # Définition du tableau des candidats
            data = [["N° Table", "Prénom", "Nom", "Sexe", "Points", "Statut"]]
            for candidat in candidats:
                data.append([
                    str(candidat[0]), 
                    candidat[1].capitalize(), 
                    candidat[2].upper(),
                    candidat[4].upper(), 
                    str(candidat[6]), 
                    candidat[7]
                ])
            
            # Création du tableau
            table = Table(data, colWidths=[3*cm, 4*cm, 4*cm, 2*cm, 3*cm, 4*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))  # Espace après le tableau

            # Signatures (placées en bas de la page à gauche)
            elements.append(Spacer(1, 50))  # Espace pour descendre les signatures
            elements.append(Paragraph("<b>Signature du Président du Jury :</b> ______________________", styles['Normal']))
            elements.append(Paragraph("<b>Signature de l'Inspecteur :</b> ______________________", styles['Normal']))

            # Génération du PDF
            doc.build(elements)

            # Afficher un message de succès
            QMessageBox.information(self, "Succès", "PV de Délibération enregistré avec succès !")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")
            
#!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

    def print_candidats(self):
        QMessageBox.information(None, "Info", "Impression de la liste des candidats.")

    def print_anonymat(self):
        QMessageBox.information(None, "Info", "Impression de la liste anonyme.")

    def print_resultats(self):
        QMessageBox.information(None, "Info", "Impression des résultats.")

    def print_pv(self):
        QMessageBox.information(None, "Info", "Impression du PV de délibération.")

    def print_releve_1(self):
        QMessageBox.information(None, "Info", "Impression du relevé des notes - 1er Tour.")

    def print_releve_2(self):
        QMessageBox.information(None, "Info", "Impression du relevé des notes - 2nd Tour.")


    
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE STATISTIQUE ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE STATISTIQUE ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: PAGE STATISTIQUE ::::::::::::::::::::::::::::::::::::::::

class StatistiquesPage(QWidget):
    """Page des statistiques."""
    def __init__(self):
        super().__init__()
        self.setObjectName("statistiquesPage")
        
        # Layout principal
        layout = QVBoxLayout()

        # Titre de la page
        label = QLabel("Statistiques des Candidats")
        label.setObjectName("titlePage")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: LABO DU FENETRE PRINCIPALE ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: LABO DU FENETRE PRINCIPALE ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: LABO DU FENETRE PRINCIPALE ::::::::::::::::::::::::::::::::::::::::

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    # Déclaration du signal
    refresh_deliberation_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des Candidats BFEM")
        self.setGeometry(100, 100, 1000, 600)

        #? Layout principal (horizontal)
        main_layout = QHBoxLayout()
        
        text_label = QLabel("LOG.BFEM") #? Nom du logiciel
        text_label.setObjectName("appTitle")  #? Ajout du nom d'objet
        text_label.setAlignment(Qt.AlignLeft)

        #? Barre de navigation
        self.navbar = NavigationMenu()
                
        #? Contenu principal (Pages)
        self.pages = QStackedWidget()
        self.page_dashboard = DashboardPage()
        self.page_candidats = CandidatsPage()
        self.page_deliberation = DeliberationPage()
        self.page_statistiques = StatistiquesPage()

        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_candidats)
        self.pages.addWidget(self.page_deliberation)
        self.pages.addWidget(self.page_statistiques)

        #? Ajout au layout principal
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.pages)

        #? Layout global
        main_container = QVBoxLayout()
        main_container.addWidget(text_label)
        main_container.addLayout(main_layout)

        #? Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_container)
        self.setCentralWidget(central_widget)

        #? Connexions des boutons aux pages
        self.navbar.btn_dashboard.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_dashboard))
        self.navbar.btn_candidats.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_candidats))
        self.navbar.btn_deliberation.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_deliberation))
        self.navbar.btn_statistiques.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_statistiques))
        self.navbar.btn_quitter.clicked.connect(self.close)

        #Connexion du signal pour mettre à jour la page délibération
        self.refresh_deliberation_signal.connect(self.page_deliberation.refresh_deliberation)
                            