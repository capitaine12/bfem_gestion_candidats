from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt
from backend.database import add_notes, update_notes, get_all_notes  

class NotesForm(QDialog):
    """ Fenêtre pour ajouter/modifier les notes d’un candidat """
    def __init__(self, parent=None, num_table=None, mode="ajout"):
        super().__init__(parent)
        self.setWindowTitle(f"{'Modifier' if mode == 'modification' else 'Ajouter'} Notes - Candidat {num_table}")
        self.setFixedSize(620, 350)

        self.num_table = num_table
        self.mode = mode  # Stocker le mode (ajout/modification)

        # Appliquer un style
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

            self.fields[key] = field  # Stocke le champ avec sa clé correcte

            col += 2
            if col >= 4:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_cancel = QPushButton("Annuler")
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        self.btn_save.setObjectName("btn_save")
        self.btn_cancel.setObjectName("btn_cancel") 

        layout.addLayout(btn_layout, row + 2, 0, 1, 4)
        self.setLayout(layout)

        # Si on est en mode modification, pré-remplir les champs
        if mode == "modification":
            self.prefill_fields()

        # Connexion des boutons
        self.btn_save.clicked.connect(self.save_notes)
        self.btn_cancel.clicked.connect(self.close)

    def prefill_fields(self):
        """ Pré-remplit les champs avec les notes existantes """
        notes_existantes = get_all_notes(self.num_table)
        if notes_existantes:
            for key, valeur in zip(self.labels.values(), notes_existantes):
                if valeur is not None:
                    self.fields[key].setText(str(valeur))

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

        for key, field in self.fields.items():
            note = field.text().strip()

            # Vérification si le champ est vide → Désormais tous les champs doivent être remplis !
            if not note:
                self.mark_invalid_field(field, True)
                has_error = True
            else:
                # Vérification du format de la note (chiffre entre 0 et 20)
                try:
                    note_float = float(note)
                    if note_float < 0 or note_float > 20:
                        raise ValueError
                    self.mark_invalid_field(field, False)
                    notes[key] = note_float  # Stocker la note validée
                except ValueError:
                    self.mark_invalid_field(field, True)
                    QMessageBox.warning(self, "Erreur", f"La note de {key} doit être un chiffre entre 0 et 20.")
                    has_error = True

        # Empêcher l'enregistrement si tous les champs ne sont pas remplis
        if has_error:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis correctement avant d'enregistrer.")
            return

        # Enregistrement dans la base de données
        if self.mode == "modification":
            update_notes(self.num_table, notes)
        else:
            add_notes(self.num_table, notes)

        QMessageBox.information(self, "Succès", "Les notes ont été enregistrées avec succès.")
        self.accept()
