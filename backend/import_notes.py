import sqlite3
import pandas as pd
from backend.db_connection import get_db_connection


def import_notes_from_excel(excel_file):
    """ Importe les notes depuis un fichier Excel et les insère dans la base de données """
    print("🔍 Début de l'importation des notes depuis Excel...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Charger le fichier Excel
        df = pd.read_excel(excel_file)

        # Renommer les colonnes pour correspondre à la base de données
        df.columns = [
            "num_table", "prenom", "nom", "date_naissance", "lieu_naissance", "sexe", "nb_fois",
            "type_candidat", "etablissement", "nationalite", "etat_sportif", "epreuve_facultative",
            "moy_6e", "moy_5e", "moy_4e", "moy_3e", "note_eps", "note_cf", "note_ort",
            "note_tsq", "note_svt", "note_ang1", "note_math", "note_hg", "note_ic",
            "note_pc_lv2", "note_ang2", "note_ep_fac"
        ]


        # Insérer les données dans la base de données
        for _, row in df.iterrows():
            try:
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

                print(f"✅ Notes insérées pour le candidat {row['num_table']}")

            except sqlite3.IntegrityError:
                print(f"❌ Le candidat {row['num_table']} n'existe pas dans la base de données.")

        conn.commit()
        print("✅ Importation des notes terminée avec succès.")

    except Exception as e:
        print(f"❌ Erreur lors de l'importation : {e}")

    conn.close()
