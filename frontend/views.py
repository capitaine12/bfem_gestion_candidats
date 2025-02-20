from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QStackedWidget, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QLineEdit, QPushButton,QHBoxLayout, QMessageBox, QSizePolicy, QFrame,QComboBox
    )

from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtGui import QIcon
import os,sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.controllers import NavigationMenu  #? Import du menu de navigation
from backend.database import delete_candidat, get_all_candidats  #? Import de la base de données

from frontend.partials.form import CandidatForm  #? Import du formulaire d'ajout / modification
from frontend.partials.ia_data import ia_info  #? Importation des données du fichier ia_data
from frontend.partials.cards import CardsWindow
from frontend.partials.detailsform import DetailsForm
from frontend.partials.notesdialog import NotesDialog

from backend.database import get_candidats_avec_statut

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

class DeliberationPage(QWidget):
    """ Page pour la délibération """
    def __init__(self):
        super().__init__()
        self.setObjectName("deliberationPage")
        layout = QVBoxLayout()

        label = QLabel("📝 Délibération des candidats")
        label.setObjectName("titlePage")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


         # Conteneur pour les boutons
        button_layout = QVBoxLayout()

        # Création des boutons d'impression
        self.btn_print_candidats = QPushButton("📄 Imprimer Liste des Candidats")
        self.btn_print_anonymat = QPushButton("🔒 Imprimer Liste Anonyme")
        self.btn_print_resultats = QPushButton("🏆 Imprimer Résultats")
        self.btn_print_pv = QPushButton("📜 Imprimer PV de Délibération")
        self.btn_print_releve_1 = QPushButton("📊 Imprimer Relevé Notes - 1er Tour")
        self.btn_print_releve_2 = QPushButton("📊 Imprimer Relevé Notes - 2nd Tour")


         # Ajout des boutons à la mise en page
        button_layout.addWidget(self.btn_print_candidats)
        button_layout.addWidget(self.btn_print_anonymat)
        button_layout.addWidget(self.btn_print_resultats)
        button_layout.addWidget(self.btn_print_pv)
        button_layout.addWidget(self.btn_print_releve_1)
        button_layout.addWidget(self.btn_print_releve_2)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connexion des boutons aux fonctions (à implémenter plus tard)
        self.btn_print_candidats.clicked.connect(self.print_candidats)
        self.btn_print_anonymat.clicked.connect(self.print_anonymat)
        self.btn_print_resultats.clicked.connect(self.print_resultats)
        self.btn_print_pv.clicked.connect(self.print_pv)
        self.btn_print_releve_1.clicked.connect(self.print_releve_1)
        self.btn_print_releve_2.clicked.connect(self.print_releve_2)

        # Menu déroulant pour filtrer les résultats
        self.filtre_statut = QComboBox()
        self.filtre_statut.addItems(["Tous", "Admis", "Second Tour", "Repêchable au 1er tour", 
                                      "Repêchable au 2nd tour", "Échoué"])
        self.filtre_statut.currentTextChanged.connect(self.filtrer_par_statut)
        layout.addWidget(self.filtre_statut)
        self.filtre_statut.setStyleSheet("padding: 5px; border: 1px solid rgb(255, 102, 0); margin-bottom: 5px; font-size: 15px ")

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
                        item.setBackground(QColor(0, 255, 0))  # Vert
                    elif statut == "Second Tour":
                        item.setBackground(QColor(255, 255, 0))  # Jaune
                    elif statut == "Repêchable au 1er tour":
                        item.setBackground(QColor(0, 0, 255))  # Bleu
                    elif statut == "Repêchable au 2nd tour":
                        item.setBackground(QColor(255, 165, 0))  # Orange
                    elif statut == "Échoué":
                        item.setBackground(QColor(255, 0, 0))  # Rouge

                self.table.setItem(row_idx, col_idx, item)

    def refresh_deliberation(self):
        """ Rafraîchit l'affichage après l'importation des notes """
        self.load_deliberation()
    
    def filtrer_par_statut(self, statut_recherche):
        """ Filtre l'affichage des candidats selon leur statut """
        resultats = get_candidats_avec_statut()
        
        if statut_recherche != "Tous":
            resultats = [c for c in resultats if c[-1] == statut_recherche]

        self.table.setRowCount(len(resultats))
        
        for row_idx, candidat in enumerate(resultats):
            for col_idx, data in enumerate(candidat):
                item = QTableWidgetItem(str(data))
                # Appliquer le style de fond au statut
                if col_idx == 7:  # Colonne du statut
                    statut = str(data)
                    if statut == "Admis":
                        item.setBackground(QColor(0, 255, 0))  # Vert
                    elif statut == "Second Tour":
                        item.setBackground(QColor(255, 255, 0))  # Jaune
                    elif statut == "Repêchable au 1er tour":
                        item.setBackground(QColor(0, 0, 255))  # Bleu
                    elif statut == "Repêchable au 2nd tour":
                        item.setBackground(QColor(255, 165, 0))  # Orange
                    elif statut == "Échoué":
                        item.setBackground(QColor(255, 0, 0))  # Rouge
                self.table.setItem(row_idx, col_idx, item)
                
    
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

        # Menu déroulant pour sélectionner les statistiques
        self.statistiques_selection = QComboBox()
        self.statistiques_selection.addItems(["Sélectionnez une statistique", "Taux de réussite", "Moyennes par matière", "Répartition des statuts"])
        self.statistiques_selection.currentTextChanged.connect(self.update_statistics)
        layout.addWidget(self.statistiques_selection)

        # Bouton pour rafraîchir les statistiques
        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.clicked.connect(self.refresh_statistics)
        layout.addWidget(self.refresh_button)

        # Tableau pour afficher les statistiques
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)  # Ajustez selon vos besoins
        self.stats_table.setHorizontalHeaderLabels(["Statistique", "Valeur", "Description", "Date", "Commentaires"])
        layout.addWidget(self.stats_table)

        # Configuration du layout
        self.setLayout(layout)

        # Chargement initial des statistiques
        self.load_initial_statistics()

    def load_initial_statistics(self):
        """Charge les statistiques initiales dans le tableau."""
        # Exemple de données, remplacez par vos données réelles
        data = [
            ["Taux de réussite", "85%", "Pourcentage d'admis", "2025", "Bon résultat"],
            ["Moyenne générale", "14.5", "Moyenne des notes", "2025", "À améliorer"],
        ]
        
        self.stats_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.stats_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def update_statistics(self):
        """Met à jour les statistiques selon la sélection."""
        selected_stat = self.statistiques_selection.currentText()
        # Logique pour mettre à jour le tableau en fonction de la sélection
        # Exemple : filtrer ou charger de nouvelles données
        print(f"Selected statistic: {selected_stat}")
    
    def refresh_statistics(self):
        """Rafraîchit les données des statistiques."""
        # Logique pour rafraîchir les données
        print("Refreshing statistics...")
        self.load_initial_statistics()  # Recharge les données initiales

#!::::::::::::::::::::::::::::::::::::::::::::::::::::: LABO DU FENETRE PRINCIPALE ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: LABO DU FENETRE PRINCIPALE ::::::::::::::::::::::::::::::::::::::::
#!::::::::::::::::::::::::::::::::::::::::::::::::::::: LABO DU FENETRE PRINCIPALE ::::::::::::::::::::::::::::::::::::::::

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    refresh_deliberation_signal = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des Candidats BFEM")
        self.setGeometry(100, 100, 1000, 600)

        #? Layout principal (horizontal)
        main_layout = QHBoxLayout()
        
        text_label = QLabel("LOG BFEM") #? Nom du logiciel
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
                            