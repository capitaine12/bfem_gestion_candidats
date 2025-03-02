from datetime import datetime
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QTableWidget, QScrollArea, QSpacerItem,
    QTableWidgetItem, QLineEdit, QPushButton,QHBoxLayout, QMessageBox, QSizePolicy, QFrame,QComboBox, QGridLayout
    )

import sqlite3
from PyQt5.QtWidgets import QFileDialog
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QFont,  QIcon

import os,sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from backend.function.calculenotes import calculer_statut_candidat, recalculer_tous_les_statuts
from frontend.controllers import NavigationMenu  #? Import du menu de navigation
from backend.database import delete_candidat, get_all_candidats, get_candidats_avec_statut, get_all_jurys, get_all_notes #? Import de la base de données


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

        # Définir l'objet de la page
        self.setObjectName("dashboardPage")

        # Création du QLabel pour l'image de fond
        self.background_label = QLabel(self)
        self.background_label.setObjectName("backgroundImage")
        self.background_label.setScaledContents(True)  # Permet au QLabel de s'étendre automatiquement
        self.background_label.setPixmap(QPixmap("frontend/images/logbfem.png"))
        self.background_label.setAlignment(Qt.AlignCenter)

        # Création du layout principal
        layout = QVBoxLayout(self)

        # Message de bienvenue en haut
        welcome_label = QLabel("BIENVENUE SUR LA PLATFORME")
        welcome_label.setObjectName("welcomeTitle")
        welcome_label.setAlignment(Qt.AlignCenter)

        # Bouton pour ouvrir la fenêtre des cartes
        cards_button = QPushButton("Les Inspections Académiques")
        cards_button.setObjectName("showCardsButton")
        cards_button.setFixedSize(400, 120)
        cards_button.clicked.connect(self.open_cards_window)

        # Ajout des widgets au layout
        layout.addWidget(welcome_label, alignment=Qt.AlignTop)  # Texte en haut
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Espace flexible
        layout.addWidget(cards_button, alignment=Qt.AlignCenter)  # Bouton en bas

        # Appliquer le layout à la page
        self.setLayout(layout)

        # Appliquer le style (y compris image de fond couvrant la page)
        self.setStyleSheet("""
            #dashboardPage {
                border-radius: 10px;
            }
            #backgroundImage {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                
            }
            #welcomeTitle {
                font-size: 30px;
                font-weight: bold;
                color: #fff;
                margin: 20px 0;
                
            }
            #showCardsButton {
                background-color: white;
                color: rgb(2, 10, 122);
                font-size: 16px;
                border: none;
                border-radius: 5px;
                padding: 10px;
                
            }
            #showCardsButton:hover {
                background-color: #2980B9;
            }
        """)

    def resizeEvent(self, event):
        """Réajuste l'image de fond lorsque la fenêtre est redimensionnée."""
        self.background_label.resize(self.size())  # Étendre l'image à toute la fenêtre

    def open_cards_window(self):
        """Ouvre la fenêtre des cartes."""
        cards_window = CardsWindow()
        cards_window.exec_()  # Affiche la fenêtre modale

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
        """Charge les candidats depuis SQLite et les affiche dans le tableau."""
        if candidats is None:
            candidats = get_all_candidats()

        if candidats is None:  # Vérifie si get_all_candidats() a échoué
            logging.error("❌ Erreur : Impossible de récupérer les candidats (get_all_candidats() a retourné None).")
            QMessageBox.critical(self, "Erreur", "Impossible de charger les candidats. Vérifiez la base de données.")
            candidats = []  # Empêche le plantage

        self.table.setRowCount(len(candidats))  # Évite l'erreur si candidats est None

        for row, candidat in enumerate(candidats):
            for col, valeur in enumerate(candidat):
                item = QTableWidgetItem(str(valeur))
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(row, col, item)

        logging.info(f"📌 Chargement des candidats terminé. {len(candidats)} candidats affichés.")


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
        self.btn_print_releve_1.clicked.connect(self.imprimer_releve_notes_pt)
        self.btn_print_releve_2.clicked.connect(self.imprimer_releve_notes)

        # Menu déroulant pour filtrer les résultats
        self.filtre_statut = QComboBox()
        self.filtre_statut.addItems(["Tous", "Admis Doffice", "Second Tour", "Repêchable au 1er tour",
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
                    if data == "Admis Doffice":
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
                    if statut == "Admis Doffice":
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
            elements.append(Paragraph("<b>PROCÈS-VERBAL DE DÉLIBÉRATION 1er TOUR </b>", styles['Title']))
            elements.append(Spacer(1, 10)) 

            # Date actuelle
            date_str = datetime.now().strftime("%d/%m/%Y")
            elements.append(Paragraph(f"Date : {date_str}", styles['Normal']))

            # Récupération des informations du jury
            jury_info = get_all_jurys()
            if jury_info:
                jury = jury_info[0]  # On prend le premier jury
                jury_text = f"""
                    <b>IA :</b> {jury[2]}<br/>
                    <b>IEF :</b> {jury[3]}<br/>
                    <b>Localité :</b> {jury[4]}<br/>
                    <b>Centre d'examen :</b> {jury[5]}<br/>
                    <b>Saison :</b> 2024/2025<br/>
                    <b>Président du Jury :</b> {jury[6]}<br/>
                    <b>N° Jury :</b> {jury[1]}<br/>
                    <b>Examinateurs :</b> Mlle. Diagne, Mlle Diarisso, M. Diop
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
            
#?:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


    def imprimer_releve_notes_pt(self):
        """ Imprime le relevé de notes du candidat sélectionné """
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un candidat.")
            return  
        
        num_table = self.table.item(selected_row, 0).text()
        candidats = get_all_candidats()
        notes = get_all_notes(num_table)  # Passer num_table pour récupérer les notes
        jurys = get_all_jurys()
        
        # Trouver les informations du candidat

        candidat_info = next((c for c in candidats if str(c[0]) == num_table), None)

        if not candidat_info or notes is None or len(notes) == 0:
            QMessageBox.critical(self, "Erreur", "Impossible de récupérer les informations du candidat ou ses notes.")
            return  
        
        statut = candidat_info[-1]  # Dernière colonne contient le statut
        if statut not in ["Admis Doffice", "Repêchable au 1er tour"]:
            QMessageBox.warning(self, "Accès refusé", "Ce candidat n'est pas admis ou repêché au 1er tour.")
            return
         
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le relevé de notes", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )

        if not file_path:
            return  
        
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

            # Titre du Relevé
            elements.append(Paragraph("<b>RELEVÉ DE NOTES - 1er TOUR</b>", styles['Title']))
            elements.append(Spacer(1, 10)) 

            # Récupération des informations du jury
            jury_info = get_all_jurys()
            if jury_info:
                jury = jury_info[0]  # On prend le premier jury
                jury_text = f"""
                    <b>Centre d'examen :</b> {jury[5]}<br/>
                    <b>Localité :</b> {jury[4]}<br/>
                    <b>Saison :</b> 2024/2025<br/>
                """
                elements.append(Paragraph(jury_text, styles['Normal']))
                elements.append(Spacer(1, 10))

            # Infos candidat
            date_naissance_formatee = datetime.strptime(candidat_info[3], "%Y-%m-%d").strftime("%d/%m/%Y")
            elements.append(Paragraph(f"Numéro de table : {candidat_info[0]}", styles['Normal']))
            elements.append(Paragraph(f"Nom & Prénom : {candidat_info[2].upper()} {candidat_info[1].capitalize()}", styles['Normal']))
            elements.append(Paragraph(f"Sexe : {candidat_info[5]}", styles['Normal']))
            elements.append(Paragraph(f"Né(e) : Le {date_naissance_formatee} à {candidat_info[4]}", styles['Normal']))
            elements.append(Paragraph("\n"))
            
            # Récupération et affichage du statut
            statut = candidat_info[-1]  # Dernière colonne contient le statut
            elements.append(Paragraph(f"<b>Statut :</b> {statut}", styles['Normal']))
            elements.append(Paragraph("\n"))

            elements.append(Spacer(1, 20)) 
            # Tableau des notes
            data = [["Matières", "Coef", "Note Obtenue"]]
            coefficients = {
                "note_cf": 2, "note_ort": 1, "note_tsq": 1, "note_svt": 2,
                "note_math": 4, "note_hg": 2, "note_pc_lv2": 2, "note_ang1": 2,
                "note_ang2": 1, "note_eps": 1, "note_ep_fac": 1
            }
            
            total_points = 0
            total_coef = 0
            
            for matiere, coef in coefficients.items():
                note = notes[list(coefficients.keys()).index(matiere)]  # Récupérer la note par rapport à la clé
                data.append([matiere, coef, note if note is not None else "-"])  # Afficher "-" si la note est None
                if note is not None:
                    total_points += note * coef
                    total_coef += coef
            
            moyenne = round(total_points / 20, 2) if total_coef > 0 else 0  # Calcul de la moyenne générale
            
            table = Table(data, colWidths=[6*cm, 2*cm, 4*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20)) 
            elements.append(Paragraph("\n"))
            elements.append(Paragraph(f"Total des points : {total_points} / {total_coef * 20}", styles['Normal']))
            elements.append(Paragraph(f"Moyenne Générale : {moyenne} / 20", styles['Normal']))
            
            # Décision finale
            elements.append(Paragraph(f"<b>Décision :</b> <b>{statut}</b>", styles['Normal']))
            elements.append(Spacer(1, 1*cm))
            elements.append(Paragraph("Signature du Président du Jury: ______________________", styles['Normal']))
            elements.append(Paragraph("Signature de l'Inspecteur: ______________________", styles['Normal']))
            
            doc.build(elements)
            QMessageBox.information(self, "Succès", "Relevé de notes enregistré avec succès !")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")
            
            
#!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    def imprimer_releve_notes(self):
            """ Imprime le relevé de notes du candidat sélectionné """
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Avertissement", "Veuillez sélectionner un candidat.")
                return  
            
            num_table = self.table.item(selected_row, 0).text()
            candidats = get_all_candidats()
            notes = get_all_notes(num_table)  # Passer num_table pour récupérer les notes
            jurys = get_all_jurys()
            
            # Trouver les informations du candidat

            candidat_info = next((c for c in candidats if str(c[0]) == num_table), None)

            if not candidat_info or notes is None or len(notes) == 0:
                QMessageBox.critical(self, "Erreur", "Impossible de récupérer les informations du candidat ou ses notes.")
                return  
            
            statut = candidat_info[-1]  # Dernière colonne contient le statut
            if statut not in ["Second Tour", "Repêchable au 2nd tour"]:
                QMessageBox.warning(self, "Accès refusé", "Ce candidat n'est pas admis ou repêché au 2nd tour.")
                return
            
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le relevé de notes", "", "PDF Files (*.pdf);;All Files (*)", options=options
            )

            if not file_path:
                return  
            
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

                # Titre du Relevé
                elements.append(Paragraph("<b>RELEVÉ DE NOTES - 1er TOUR</b>", styles['Title']))
                elements.append(Spacer(1, 10)) 

                # Récupération des informations du jury
                jury_info = get_all_jurys()
                if jury_info:
                    jury = jury_info[0]  # On prend le premier jury
                    jury_text = f"""
                        <b>Centre d'examen :</b> {jury[4]}<br/>
                        <b>Localité :</b> {jury[3]}<br/>
                        <b>Saison :</b> 2024/2025<br/>
                    """
                    elements.append(Paragraph(jury_text, styles['Normal']))
                    elements.append(Spacer(1, 10))

                # Infos candidat
                date_naissance_formatee = datetime.strptime(candidat_info[3], "%Y-%m-%d").strftime("%d/%m/%Y")
                elements.append(Paragraph(f"Numéro de table : {candidat_info[0]}", styles['Normal']))
                elements.append(Paragraph(f"Nom & Prénom : {candidat_info[2].upper()} {candidat_info[1].capitalize()}", styles['Normal']))
                elements.append(Paragraph(f"Sexe : {candidat_info[5]}", styles['Normal']))
                elements.append(Paragraph(f"Né(e) : Le {date_naissance_formatee} à {candidat_info[4]}", styles['Normal']))
                elements.append(Paragraph("\n"))
                
                # Récupération et affichage du statut
                statut = candidat_info[-1]  # Dernière colonne contient le statut
                elements.append(Paragraph(f"<b>Statut :</b> {statut}", styles['Normal']))
                elements.append(Paragraph("\n"))

                elements.append(Spacer(1, 20)) 
                # Tableau des notes
                data = [["Matières", "Coef", "Note Obtenue"]]
                coefficients = {
                    "note_cf": 2, "note_ort": 1, "note_tsq": 1, "note_svt": 2,
                    "note_math": 4, "note_hg": 2, "note_pc_lv2": 2, "note_ang1": 2,
                    "note_ang2": 1, "note_eps": 1, "note_ep_fac": 1
                }
                
                total_points = 0
                total_coef = 0
                
                for matiere, coef in coefficients.items():
                    note = notes[list(coefficients.keys()).index(matiere)]  # Récupérer la note par rapport à la clé
                    data.append([matiere, coef, note if note is not None else "-"])  # Afficher "-" si la note est None
                    if note is not None:
                        total_points += note * coef
                        total_coef += coef
                
                moyenne = round(total_points / 20, 2) if total_coef > 0 else 0  # Calcul de la moyenne générale
                
                table = Table(data, colWidths=[6*cm, 2*cm, 4*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 20)) 
                elements.append(Paragraph("\n"))
                elements.append(Paragraph(f"Total des points : {total_points} / {total_coef * 20}", styles['Normal']))
                elements.append(Paragraph(f"Moyenne Générale : {moyenne} / 20", styles['Normal']))
                
                # Décision finale
                elements.append(Paragraph(f"<b>Décision :</b> <b>{statut}</b>", styles['Normal']))
                elements.append(Spacer(1, 1*cm))
                elements.append(Paragraph("Signature du Président du Jury: ______________________", styles['Normal']))
                elements.append(Paragraph("Signature de l'Inspecteur: ______________________", styles['Normal']))
                
                doc.build(elements)
                QMessageBox.information(self, "Succès", "Relevé de notes enregistré avec succès !")

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
    def __init__(self):
        super().__init__()
        self.setObjectName("statistiquesPage")
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Ajout d'espacement global
        
        # Titre principal
        title = QLabel("📊 Statistiques des Candidats")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Conteneur pour les cartes statistiques
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)  # Espacement entre les cartes
        
        # Traiter les candidats et récupérer les données de la BDD
        self.traiter_candidats(cards_layout)
        
        layout.addLayout(cards_layout)
        
        # Zone scrollable pour les graphiques
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)  # Espacement entre les graphiques
        
        # Ajout des graphiques
        self.add_graph(content_layout, "Répartition des Candidats par Statuts", self.plot_pie_chart)
        self.add_graph(content_layout, "Répartition des Candidats par Sexe", self.plot_bar_chart)
        self.add_graph(content_layout, "Histogramme des Notes par Matière", self.plot_histogram)
        self.add_graph(content_layout, "Nombre de Sexe par Statut", self.plot_sexe_par_statut)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)


    def traiter_candidats(self, cards_layout):
        """Traite tous les candidats : calcule les notes, met à jour les statuts et calcule la moyenne générale."""
        candidats = get_all_candidats()  # Récupérer tous les candidats

        # Étape 1 : Calculer et stocker les notes
        for candidat in candidats:
            num_table = candidat[0]
            calculer_statut_candidat(num_table)  # Calcule et stocke les notes
            

        # Étape 2 : Recalculer tous les statuts
        recalculer_tous_les_statuts()  # Met à jour tous les statuts après le calcul des notes
        #candidats = get_all_candidats()  # Récupérer tous les candidats


        # Étape 3 : Calculer les statistiques
        total_candidats = len(candidats)
        moyenne_generale = self.calculer_moyenne_generale(candidats)
        taux_reussite = self.calculer_taux_reussite(candidats)
        
        self.add_stat_card(cards_layout, "📌 Candidats", str(total_candidats))
        self.add_stat_card(cards_layout, "🎓 Moyenne Générale", f"{moyenne_generale:.2f}/20")
        self.add_stat_card(cards_layout, "✅ Taux de Réussite", f"{taux_reussite:.2f}%")

    def add_stat_card(self, layout, title, value):
        """Ajoute une carte statistique avec icône et animation légère"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                border: 2px solid #ff6600;
                border-radius: 10px;
                padding: 15px;
                background-color: #fff;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)
        
        label_title = QLabel(title)
        label_title.setFont(QFont("Arial", 12, QFont.Bold))
        label_title.setAlignment(Qt.AlignCenter)
        
        label_value = QLabel(value)
        label_value.setFont(QFont("Arial", 22, QFont.Bold))  # Taille augmentée
        label_value.setAlignment(Qt.AlignCenter)
        
        card_layout.addWidget(label_title)
        card_layout.addWidget(label_value)
        card.setLayout(card_layout)
        layout.addWidget(card)
    

    def add_graph(self, layout, title, plot_function):
        """Ajoute un graphique avec un titre souligné"""
        title_label = QLabel(f"<u>{title}</u>")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        figure = plt.figure(figsize=(6, 4))  # Agrandissement du graphique
        canvas = FigureCanvas(figure)
        canvas.setFixedHeight(350)  # Fixe la hauteur des graphiques
        
        plot_function(figure)
        layout.addWidget(canvas)


    def calculer_moyenne_generale(self, candidats):
        """Calcule la moyenne générale des candidats."""
        total_moyenne = 0
        total_candidats = len(candidats)
        
        for candidat in candidats:
            notes = get_all_notes(candidat[0])  # Utilise le numéro de table pour récupérer les notes
            if notes:
                # Filtrer les notes non nulles
                notes_valides = [note for note in notes if note is not None]
                if notes_valides:  # Vérifie que la liste n'est pas vide
                    moyenne = sum(notes_valides) / len(notes_valides)
                    total_moyenne += moyenne
        
        return total_moyenne / total_candidats if total_candidats > 0 else 0

    def calculer_taux_reussite(self, candidats):
        """Calcule le taux de réussite des candidats."""
        admis_count = sum(1 for candidat in candidats if candidat[-1] == "Admis Doffice")  # Assurez-vous que le statut est le bon
        total_count = len(candidats)
        return (admis_count / total_count * 100) if total_count > 0 else 0

    def plot_pie_chart(self, figure):
        """Diagramme circulaire pour la répartition des statuts"""
        candidats_statut = get_candidats_avec_statut()
        labels = ["Admis Doffice", "Repêchable au 1er tour", "Second Tour", "Repêchable au 2nd tour", "Échoué"]
        
        # Compter le nombre de candidats par statut
        sizes = [
            sum(1 for c in candidats_statut if c[-1] == "Admis Doffice"),
            sum(1 for c in candidats_statut if c[-1] == "Repêchable au 1er tour"),
            sum(1 for c in candidats_statut if c[-1] == "Second Tour"),
            sum(1 for c in candidats_statut if c[-1] == "Repêchable au 2nd tour"),
            sum(1 for c in candidats_statut if c[-1] == "Échoué")
        ]

        # Éviter les erreurs si toutes les tailles sont à zéro
        if sum(sizes) == 0:
            sizes = [1] * len(labels)  # Éviter la division par zéro
            labels = ["Aucun candidat"] * len(labels)

        colors = ['#4CAF50', '#16028a', '#FFC107', '#8b038b', '#F44336']

        ax = figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)

        # Équilibrer le graphique
        ax.axis('equal')  
        # Titre du graphique
       # ax.set_title("Répartition des Statuts des Candidats", fontsize=12)

        # Améliorer la lisibilité des étiquettes
        for text in texts:
            text.set_fontsize(12)
            text.set_color('black')

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color('white')

        # Ajouter une légende à gauche
        ax.legend(wedges, labels, title="Statuts", loc="center left", bbox_to_anchor=(-0.15, 0, 0.5, 1), fontsize=10)  
    
    def plot_bar_chart(self, figure):
        """Diagramme en barres pour la répartition des sexes"""
        candidats_statut = get_all_candidats()
        labels = ['Hommes', 'Femmes']
        values = [
            sum(1 for c in candidats_statut if c[5] == 'M'),  # Compte des hommes
            sum(1 for c in candidats_statut if c[5] == 'F')   # Compte des femmes
        ]
        
        ax = figure.add_subplot(111)
        ax.bar(labels, values, color=['#1E88E5', '#D81B60'])
        ax.set_ylabel("Nombre de candidats")
        ax.set_title("Répartition Hommes/Femmes", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)  # Ajout d'une grille
    
    def plot_histogram(self, figure):
        """Histogramme des moyennes par matière"""
        sujets = ['Français', 'TSQ','Dictée', 'Maths', 'SVT', 'Histoire', 'Anglais', 'Ang-Oral', 'PC / LV2', 'EPS', 'Ép-Facultative']
        moyennes = [self.calculer_moyenne_par_matiere(sujet) for sujet in sujets]
        
        ax = figure.add_subplot(111)
        bars = ax.bar(sujets, moyennes, color=['#3F51B5', '#FF9800', '#009688', '#E91E63', '#8BC34A', '#ff0000', '#01441bde', '#66625ece', '#fd80ba', '#1a3e44', '#030e70'])
        
        ax.set_ylabel("Moyenne des candidats")
        ax.set_title("Moyenne par Matière", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)  # Ajout d'une grille

        # Affichage des valeurs sur chaque barre
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.3, f"{yval:.1f}", ha='center', fontsize=10, fontweight='bold')


    def plot_sexe_par_statut(self, figure):
        """Diagramme en barres pour la répartition des sexes par statut"""
        candidats_statut = get_all_candidats()  # Récupérer les candidats
        statuts = ['Admis Doffice', 'Repêchable au 1er tour', 'Second Tour', 'Repêchable au 2nd tour', 'Échoué']  # Exemple de statuts
        hommes = [sum(1 for c in candidats_statut if c[5] == 'M' and c[-1] == statut) for statut in statuts]
        femmes = [sum(1 for c in candidats_statut if c[5] == 'F' and c[-1] == statut) for statut in statuts]

        ax = figure.add_subplot(111)
        bar_width = 0.35
        index = range(len(statuts))

        bars1 = ax.bar(index, hommes, bar_width, label='Hommes', color='#1E88E5')
        bars2 = ax.bar([i + bar_width for i in index], femmes, bar_width, label='Femmes', color='#D81B60')

        ax.set_xlabel('Statuts')
        ax.set_ylabel('Nombre de Candidats')
        ax.set_title('Répartition des Sexes par Statut')
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(statuts)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Affichage des valeurs sur chaque barre
        for bar in bars1 + bars2:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.3, f"{yval}", ha='center', fontsize=10, fontweight='bold')


    def calculer_moyenne_par_matiere(self, sujet):
        """Calcule la moyenne pour une matière donnée."""
        candidats = get_all_candidats()
        total = 0
        count = 0
        
        # Mappage des matières aux notes dans la base de données
        note_mapping = {
            "Français": "note_cf",
            "TSQ": "note_tsq",
            "Dictée": "note_ort",
            "Maths": "note_math",
            "SVT": "note_svt",
            "Histoire": "note_hg",
            "Anglais": "note_ang1",
            "Ang-Oral": "note_ang2",
            "EPS": "note_eps",
            "Ép-Facultative": "note_ep_fac",
            "PC / LV2": "note_pc_lv2"
        }
        
        if sujet not in note_mapping:
            logging.warning(f"❌ Matière non trouvée : {sujet}")
            return 0  # Retourne 0 si la matière n'est pas reconnue

        for candidat in candidats:
            notes = get_all_notes(candidat[0])  # Utilise le numéro de table
            if notes:
                # Récupère le nom de la note correspondant à la matière
                note_column = note_mapping[sujet]
                index = ["note_cf", "note_ort", "note_tsq", "note_svt", "note_math", "note_hg", "note_pc_lv2", "note_ang1", "note_ang2", "note_eps", "note_ep_fac"].index(note_column)
                note = notes[index]
                if note is not None:
                    total += note
                    count += 1
        
        return total / count if count > 0 else 0

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
                            