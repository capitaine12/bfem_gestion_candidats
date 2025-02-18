from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

class NotesDialog(QDialog):
    """ Fenêtre pour choisir entre Ajouter et Modifier une note """
    def __init__(self, parent=None, num_table=None):
        super().__init__(parent)
        self.setWindowTitle(f"Gestion des Notes - Candidat N°{num_table}")
        self.setFixedSize(450, 200)

        self.num_table = num_table  

        layout = QVBoxLayout()

        #? Texte principal
        self.label = QLabel(f"Voulez-vous ajouter ou modifier la note du candidat N° {num_table} ?")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label)

        #? Boutons Ajouter / Modifier
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Ajouter Note")
        self.btn_modify = QPushButton("Modifier Note")
        self.btn_close = QPushButton("Fermer")

        #? Styliser les boutons
        self.btn_add.setStyleSheet("background-color: #28a745; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")
        self.btn_modify.setStyleSheet("background-color: #ffc107; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")
        self.btn_close.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; font-size: 14px; border-radius: 5px;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_modify)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        #? Connexion des boutons
        self.btn_add.clicked.connect(self.open_add_notes)
        self.btn_modify.clicked.connect(self.open_modify_notes)
        self.btn_close.clicked.connect(self.close)

    def open_add_notes(self):
        """ Ouvre le formulaire pour ajouter des notes """
        from frontend.partials.notesform import NotesForm 
        self.form = NotesForm(self, self.num_table)  # Utilisation correcte de num_table
        self.form.show()

    def open_modify_notes(self):
        """ Ouvre le formulaire de modification des notes """
        from frontend.partials.notesform import NotesForm
        self.form = NotesForm(self, self.num_table)  # Utilisation correcte de num_table
        self.form.show()
