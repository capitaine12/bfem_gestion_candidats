import sqlite3
import os, sys
import pandas as pd

# Ajouter le dossier parent au chemin pour importer backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import get_all_candidats

""" # Définir le chemin du fichier Excel
excel_file = "E:/labo/code/bfem_gestion_candidats/backend/bdbfem.xlsx"

if os.path.exists(excel_file):
    print(f"✅ Le fichier existe : {os.path.abspath(excel_file)}")
else:
    print(f"❌ Erreur : Le fichier n'existe pas à cet emplacement : {os.path.abspath(excel_file)}")

# Vérifier si des données sont bien récupérées depuis la base de données
print("recuperation", get_all_candidats())  

# Charger le fichier Excel
df = pd.read_excel(excel_file)

print("✅ Fichier Excel chargé avec succès.")
print(df.head())  # Afficher les 5 premières lignes

#df = pd.read_excel(excel_file)
print("📊 Colonnes détectées dans Excel :", df.columns.tolist())
print(f"🔢 Nombre de colonnes dans Excel : {len(df.columns)}") """

