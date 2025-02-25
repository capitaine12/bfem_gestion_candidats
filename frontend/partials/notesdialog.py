from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from backend.database import get_all_notes

class NotesDialog(QDialog):
    """ Fenêtre pour choisir entre Ajouter et Modifier une note """
    def __init__(self, parent=None, num_table=None):
        super().__init__(parent)
        self.setWindowTitle(f"Gestion des Notes - Candidat N°{num_table}")
        self.setFixedSize(450, 200)

        self.num_table = num_table  
        self.notes_existantes = get_all_notes(num_table)  # Récupération des notes

        # Vérifier si le candidat a déjà des notes
        self.has_notes = self.notes_existantes is not None and any(self.notes_existantes)

        layout = QVBoxLayout()

        # Texte principal
        self.label = QLabel(f"Voulez-vous ajouter ou modifier la note du candidat N° {num_table} ?")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label)

        # Boutons Ajouter / Modifier
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter Note")
        self.btn_modify = QPushButton("Modifier Note")
        self.btn_close = QPushButton("Fermer")

        # Styliser les boutons
        self.btn_add.setStyleSheet("background-color: #28a745; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")
        self.btn_modify.setStyleSheet("background-color: #ffc107; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")
        self.btn_close.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_modify)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        # Connexion des boutons
        self.btn_add.clicked.connect(self.handle_add_notes)
        self.btn_modify.clicked.connect(self.handle_modify_notes)
        self.btn_close.clicked.connect(self.close)

        self.setLayout(layout)

        # Désactiver les boutons en fonction des données
        self.update_buttons()

    def update_buttons(self):
        """ Active/désactive les boutons en fonction des notes existantes """
        if self.has_notes:
            self.btn_add.setEnabled(False)  # Désactive "Ajouter Note"
            self.btn_modify.setEnabled(True)  # Active "Modifier Note"
        else:
            self.btn_add.setEnabled(True)  # Active "Ajouter Note"
            self.btn_modify.setEnabled(False)  # Désactive "Modifier Note"

    def handle_add_notes(self):
        """ Vérifie avant d'ouvrir le formulaire d'ajout """
        if self.has_notes:
            QMessageBox.warning(self, "Ajout Impossible", "❌ Ce candidat a déjà des notes. Veuillez les modifier.")
        else:
            self.open_add_notes()

    def handle_modify_notes(self):
        """ Vérifie avant d'ouvrir le formulaire de modification """
        if not self.has_notes:
            QMessageBox.warning(self, "Modification Impossible", "⚠️ Ce candidat n'a pas encore de notes. Veuillez les ajouter.")
        else:
            self.open_modify_notes()

    def open_add_notes(self):
        """ Ouvre le formulaire pour ajouter des notes """
        from frontend.partials.notesform import NotesForm
        self.form = NotesForm(self, self.num_table, mode="ajout")
        self.form.exec_()

    def open_modify_notes(self):
        """ Ouvre le formulaire pour modifier les notes """
        from frontend.partials.notesform import NotesForm
        self.form = NotesForm(self, self.num_table, mode="modification")
        self.form.exec_()
