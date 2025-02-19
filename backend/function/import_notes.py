import sqlite3
import pandas as pd
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function.db_connection import get_db_connection


def import_notes_from_excel(excel_file):
    """ Importe les notes depuis un fichier Excel et gère les valeurs NULL """
    print("🔍 Début de l'importation des notes depuis Excel...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        df = pd.read_excel(excel_file)

        # Renommer les colonnes
        df.columns = [
            "num_table", "prenom", "nom", "date_naissance", "lieu_naissance", "sexe", "nb_fois",
            "type_candidat", "etablissement", "nationalite", "etat_sportif", "epreuve_facultative",
            "moy_6e", "moy_5e", "moy_4e", "moy_3e", "note_eps", "note_cf", "note_ort",
            "note_tsq", "note_svt", "note_ang1", "note_math", "note_hg", "note_ic",
            "note_pc_lv2", "note_ang2", "note_ep_fac"
        ]

        # Remplace les valeurs NaN (vides) par 0 pour éviter les erreurs
        df.fillna({"note_eps": 0, "note_ep_fac": 0}, inplace=True)

        # Insérer les notes
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO notes (candidat_id, moy_6e, moy_5e, moy_4e, moy_3e, note_eps, note_cf, 
                                   note_ort, note_tsq, note_svt, note_ang1, note_math, note_hg, 
                                   note_ic, note_pc_lv2, note_ang2, note_ep_fac)
                VALUES (
                    (SELECT id FROM candidats WHERE num_table = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (row["num_table"], row["moy_6e"], row["moy_5e"], row["moy_4e"], row["moy_3e"], 
                  row["note_eps"], row["note_cf"], row["note_ort"], row["note_tsq"], row["note_svt"], 
                  row["note_ang1"], row["note_math"], row["note_hg"], row["note_ic"], row["note_pc_lv2"], 
                  row["note_ang2"], row["note_ep_fac"]))

        conn.commit()
        print("✅ Importation des notes terminée avec succès.")

    except Exception as e:
        print(f"❌ Erreur lors de l'importation : {e}")

    conn.close()


#?:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def import_livret_scolaire_from_excel(excel_file):
    """ Importe les livrets scolaires depuis un fichier Excel """
    print("📌 Début de l'importation du livret scolaire...")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        df = pd.read_excel(excel_file)

        # Vérifie si les colonnes existent
        required_columns = ["num_table", "nb_fois", "moy_6e", "moy_5e", "moy_4e", "moy_3e"]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"❌ La colonne '{col}' est absente du fichier Excel.")

        # Calcul de la moyenne du cycle
        df["moyenne_cycle"] = df[["moy_6e", "moy_5e", "moy_4e", "moy_3e"]].mean(axis=1)

        # Insérer les données
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO livret_scolaire (candidat_id, nombre_de_fois, moyenne_6e, moyenne_5e, moyenne_4e, moyenne_3e, moyenne_cycle)
                VALUES (
                    (SELECT id FROM candidats WHERE num_table = ?), ?, ?, ?, ?, ?, ?
                )
            """, (row["num_table"], row["nb_fois"], row["moy_6e"], row["moy_5e"], row["moy_4e"], row["moy_3e"], row["moyenne_cycle"]))

        conn.commit()
        print("✅ Importation des livrets scolaires terminée avec succès.")

    except Exception as e:
        print(f"❌ Erreur lors de l'importation du livret scolaire : {e}")

    conn.close()
