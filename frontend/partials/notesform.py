from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt
from backend.database import add_notes, update_notes  

class NotesForm(QDialog):
    """ Fenêtre pour modifier les notes d’un candidat """
    def __init__(self, parent=None, num_table=None, notes=None):
        super().__init__(parent)
        self.setWindowTitle(f"Modifier Notes - Candidat {num_table}")
        self.setFixedSize(450, 550)

        self.num_table = num_table
        self.is_editing = notes is not None  # ✅ Vérifie si on modifie une note

        # ✅ Appliquer un style
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

        layout = QGridLayout()

        self.fields = {}
        self.labels = {
            "Moy 6e": "moy_6e", "Moy 5e": "moy_5e", "Moy 4e": "moy_4e", "Moy 3e": "moy_3e",
            "EPS": "note_eps", "Français": "note_cf", "Orthographe": "note_ort", "TSQ": "note_tsq",
            "SVT": "note_svt", "Anglais": "note_ang1", "Maths": "note_math", "Histoire-Géo": "note_hg",
            "IC": "note_ic", "PC/LV2": "note_pc_lv2", "Anglais Oral": "note_ang2", "Epreuve Facultative": "note_ep_fac"
        }

        row, col = 0, 0
        for label, key in self.labels.items():
            lbl = QLabel(f"{label} :")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(lbl, row, col)

            field = QLineEdit()
            field.setPlaceholderText("Note sur 20")
            field.setFixedHeight(30)
            layout.addWidget(field, row, col + 1)

            self.fields[key] = field

            col += 2
            if col >= 4:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)

        # ✅ Boutons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_cancel = QPushButton("Annuler")
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout, row + 2, 0, 1, 4)
        self.setLayout(layout)

        # ✅ Pré-remplir les champs si on modifie une note
        if self.is_editing:
            for key, valeur in notes.items():
                self.fields[key].setText(str(valeur))

        # ✅ Connexion des boutons
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
        has_error = False
        all_empty = True

        for label, field in self.fields.items():
            note = field.text().strip()

            # ✅ Vérification si le champ est vide
            if not note:
                self.mark_invalid_field(field, True)
                has_error = True
            else:
                all_empty = False  # ✅ Au moins un champ est rempli

                # ✅ Vérification du format de la note (chiffre entre 0 et 20)
                if not note.replace('.', '', 1).isdigit() or float(note) < 0 or float(note) > 20:
                    self.mark_invalid_field(field, True)
                    QMessageBox.warning(self, "Erreur", f"La note de {label} doit être entre 0 et 20.")
                    has_error = True
                else:
                    self.mark_invalid_field(field, False)
                    notes[self.labels[label]] = float(note)

        # ✅ Empêcher l'enregistrement si tous les champs sont vides
        if all_empty:
            QMessageBox.warning(self, "Erreur", "Vous devez remplir au moins un champ.")
            return

        # ✅ Si une erreur est détectée, ne pas enregistrer
        if has_error:
            return

        # ✅ Enregistrement dans la base de données
        if self.is_editing:
            update_notes(self.num_table, notes)
        else:
            add_notes(self.num_table, notes)

        QMessageBox.information(self, "Succès", "Les notes ont été enregistrées avec succès.")
        self.accept()
