from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHBoxLayout, QDateEdit
)
from PyQt5.QtCore import Qt, QDate

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des Candidats")
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Barre latérale
        sidebar = QVBoxLayout()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setStyleSheet("background-color: #2C3E50; width: 200px;")
        layout.addWidget(sidebar_widget)

        buttons = ["Liste des candidats", "Ajout/Modification", "Statistiques", "Génération de PDF"]
        for btn_text in buttons:
            button = QPushButton(btn_text)
            button.setStyleSheet("""
                background-color: #34495E; 
                color: white; 
                border: none; 
                padding: 10px; 
                font-size: 16px;
            """)
            sidebar.addWidget(button)

        # Zone principale
        main_area = QVBoxLayout()
        layout.addLayout(main_area)

        # Titre
        title_label = QLabel("Log BFEM")
        title_label.setAlignment(Qt.AlignCenter)
        main_area.addWidget(title_label)

        # Tableau des candidats
        self.table = QTableWidget(10, 6)  # Ajouter une colonne pour l'action
        self.table.setHorizontalHeaderLabels(["Nom", "Prénom", "Numéro de table", "Moyenne", "Statut", "Action"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #BDC3C7;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #2980B9;
                color: white;
                padding: 10px;
            }
        """)
        
        # Remplir le tableau avec des données d'exemple
        for i in range(10):
            self.table.setItem(i, 0, QTableWidgetItem("Nom" + str(i)))
            self.table.setItem(i, 1, QTableWidgetItem("Prénom" + str(i)))
            self.table.setItem(i, 2, QTableWidgetItem(str(i)))
            self.table.setItem(i, 3, QTableWidgetItem(str(15 + i)))
            self.table.setItem(i, 4, QTableWidgetItem("Admis" if i % 2 == 0 else "Recalé"))

            # Ajouter des boutons d'action
            detail_button = QPushButton("Détail")
            detail_button.setStyleSheet("background-color: green; color: white;")
            self.table.setCellWidget(i, 5, detail_button)

            modify_button = QPushButton("Modifier")
            modify_button.setStyleSheet("background-color: yellow; color: black;")
            self.table.setCellWidget(i, 5, modify_button)

            delete_button = QPushButton("Supprimer")
            delete_button.setStyleSheet("background-color: red; color: white;")
            self.table.setCellWidget(i, 5, delete_button)

        main_area.addWidget(self.table)

        # Formulaire
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Ajouter un candidat"))

        name_input = QLineEdit()
        name_input.setPlaceholderText("Nom")
        form_layout.addWidget(name_input)

        surname_input = QLineEdit()
        surname_input.setPlaceholderText("Prénom")
        form_layout.addWidget(surname_input)

        dob_input = QDateEdit()
        dob_input.setCalendarPopup(True)
        dob_input.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("Date de naissance"))
        form_layout.addWidget(dob_input)

        # Style des champs
        name_input.setStyleSheet("padding: 10px; border: 1px solid #BDC3C7; border-radius: 5px;")
        surname_input.setStyleSheet("padding: 10px; border: 1px solid #BDC3C7; border-radius: 5px;")

        main_area.addLayout(form_layout)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()