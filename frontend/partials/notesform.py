from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
from backend.database import update_notes

class NotesForm(QDialog):
    """ Fenêtre pour modifier les notes d’un candidat """
    def __init__(self, parent=None, num_table=None):
        super().__init__(parent)
        self.setWindowTitle(f"Modifier Notes - Candidat {num_table}")
        self.setFixedSize(400, 520)

        self.setStyleSheet("""
        QLineEdit {
            padding: 6px;
        font-size: 14px;
        border: 1px solid rgb(255, 123, 0);
        border-radius: 15px;
        background-color: white;
        }

        QLineEdit:focus {
            border-color: rgb(255, 123, 0);
            outline: none;
        }
    """)

        self.num_table = num_table

        layout = QVBoxLayout()

        self.fields = {}
        self.labels = [
            "Maths", 
            "Français", 
            "SVT", 
            "Histoire-Géo", 
            "EPS", 
            "PC/LV2", 
            "Anglais", 
            "Epreuve Facultative"
        ]

        for label in self.labels:
            layout.addWidget(QLabel(f"{label} :"))
            field = QLineEdit()
            field.setPlaceholderText("Note sur 20")
            layout.addWidget(field)
            self.fields[label] = field  

        

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

        # Connexion des boutons
        self.btn_save.clicked.connect(self.save_notes)
        self.btn_cancel.clicked.connect(self.close)

    def mark_invalid_field(self, field, is_invalid):
        """ Ajoute ou enlève la couleur rouge aux champs ayant une erreur """
        if is_invalid:
            field.setStyleSheet("border: 2px solid red; background-color: #ffe6e6;")
        else:
            field.setStyleSheet("")


    def save_notes(self):
        """ Enregistre les nouvelles notes en vérifiant les valeurs """
        notes = {}
        has_error = False  # Variable pour détecter une erreur
        all_empty = True   # Variable pour vérifier si tous les champs sont vides

        for label, field in self.fields.items():
            note = field.text().strip()

            # Vérification si le champ est vide
            if not note:
                self.mark_invalid_field(field, True)  
                has_error = True
            else:
                all_empty = False  # Au moins un champ est rempli

                # Vérification du format de la note (chiffre entre 0 et 20)
                if not note.isdigit() or int(note) < 0 or int(note) > 20:
                    self.mark_invalid_field(field, True)  
                    QMessageBox.warning(self, "Erreur", f"La note de {label} doit être entre 0 et 20.")  # ✅ Garde cette alerte !
                    has_error = True
                else:
                    self.mark_invalid_field(field, False) 
                    notes[label] = int(note)

        # Empêcher l'enregistrement si tous les champs sont vides
        if all_empty:
            QMessageBox.warning(self, "Erreur", "Vous devez remplir au moins un champ.")
            return

        # Si une erreur est détectée, ne pas enregistrer
        if has_error:
            return

        # Enregistrement dans la base de données
        from backend.database import add_notes, update_notes  
        if self.is_editing:
            update_notes(self.num_table, notes)  
        else:
            add_notes(self.num_table, notes) 

        QMessageBox.information(self, "Succès", "Les notes ont été enregistrées avec succès.")
        self.accept()

