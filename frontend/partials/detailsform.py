from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class DetailsForm(QDialog):
    """ Fenêtre affichant les détails d’un candidat """
    def __init__(self, parent=None, candidat=None):
        super().__init__(parent)
        self.setWindowTitle(f"Détails du Candidat N°{candidat[0]}")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()

        labels = [
            "Numéro Table", "Prénom", "Nom", "Date de Naissance", "Lieu de Naissance",
            "Sexe", "Nationalité", "Épreuve Facultative", "Aptitude Sportive"
        ]

        for i, label in enumerate(labels):
            layout.addWidget(QLabel(f"<b>{label} :</b> {candidat[i]}"))

        #? Bouton Fermer stylisé
        self.btn_close = QPushButton("Fermer")
        self.btn_close.setStyleSheet("""
            background-color: #dc3545; 
            color: white; 
            padding: 8px; 
            font-size: 14px; 
            border-radius: 5px;
        """)
        self.btn_close.clicked.connect(self.close)

        layout.addWidget(self.btn_close)
        self.setLayout(layout)
