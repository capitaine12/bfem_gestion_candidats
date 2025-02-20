import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
class StatistiquesPage(QWidget):
    """Page des statistiques avec un graphique."""
    def __init__(self):
        super().__init__()
        self.setObjectName("statistiquesPage")
        
        # Layout principal
        layout = QVBoxLayout()

        # Titre de la page
        label = QLabel("Statistiques des Candidats")
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Création du tableau
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)  # Ajustez selon vos besoins
        self.stats_table.setHorizontalHeaderLabels(["Statistique", "Valeur", "Description"])
        layout.addWidget(self.stats_table)

        # Création du graphique
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Charger des données initiales
        self.load_initial_statistics()
        self.plot_graph()

        self.setLayout(layout)

    def load_initial_statistics(self):
        """Charge les statistiques initiales dans le tableau."""
        data = [
            ["Taux de réussite", "85%", "Pourcentage d'admis"],
            ["Moyenne générale", "14.5", "Moyenne des notes"],
        ]
        
        self.stats_table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.stats_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def plot_graph(self):
        """Dessine un graphique simple avec Matplotlib."""
        ax = self.figure.add_subplot(111)
        ax.clear()  # Efface l'ancien graphique

        # Exemple de données pour le graphique
        labels = ['Admis', 'Échoué', 'Second Tour']
        sizes = [70, 20, 10]

        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title('Répartition des Statuts')
        
        self.canvas.draw()  # Met à jour le canvas

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StatistiquesPage()
    window.show()
    sys.exit(app.exec_())