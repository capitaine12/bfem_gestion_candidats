import sqlite3
import pandas as pd
import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.function.db_connection import get_db_connection
from backend.function.calculenotes import calculer_statut_candidat
from frontend.views import DeliberationPage
from frontend.views import MainWindow
# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")



def import_notes_from_excel(excel_file,main_window):
    """ Importe les notes depuis un fichier Excel et met à jour le statut des candidats """
    logging.info("🔍 Début de l'importation des notes depuis Excel...")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return

    try:
        df = pd.read_excel(excel_file)

        df.columns = [
            "num_table", "prenom", "nom", "date_naissance", "lieu_naissance", "sexe", "nb_fois",
            "type_candidat", "etablissement", "nationalite", "etat_sportif", "epreuve_facultative",
            "moy_6e", "moy_5e", "moy_4e", "moy_3e", "note_eps", "note_cf", "note_ort",
            "note_tsq", "note_svt", "note_ang1", "note_math", "note_hg", "note_ic",
            "note_pc_lv2", "note_ang2", "note_ep_fac"
        ]

        df.fillna(0, inplace=True)

        for _, row in df.iterrows():
            cursor.execute("SELECT id FROM candidats WHERE num_table = ?", (row["num_table"],))
            candidat_id = cursor.fetchone()

            if candidat_id:
                cursor.execute("SELECT 1 FROM notes WHERE candidat_id = ?", (candidat_id[0],))
                exists = cursor.fetchone()

                if exists:
                    cursor.execute("""
                        UPDATE notes SET 
                            moy_6e=?, moy_5e=?, moy_4e=?, moy_3e=?, note_eps=?, note_cf=?, note_ort=?, 
                            note_tsq=?, note_svt=?, note_ang1=?, note_math=?, note_hg=?, note_ic=?, 
                            note_pc_lv2=?, note_ang2=?, note_ep_fac=?
                        WHERE candidat_id=?
                    """, (row["moy_6e"], row["moy_5e"], row["moy_4e"], row["moy_3e"], 
                          row["note_eps"], row["note_cf"], row["note_ort"], row["note_tsq"], 
                          row["note_svt"], row["note_ang1"], row["note_math"], row["note_hg"], 
                          row["note_ic"], row["note_pc_lv2"], row["note_ang2"], row["note_ep_fac"], 
                          candidat_id[0]))
                    
                    logging.info(f"🔄 Notes mises à jour pour le candidat {row['num_table']}")

                else:
                    cursor.execute("""
                        INSERT INTO notes (candidat_id, moy_6e, moy_5e, moy_4e, moy_3e, note_eps, note_cf, 
                                           note_ort, note_tsq, note_svt, note_ang1, note_math, note_hg, 
                                           note_ic, note_pc_lv2, note_ang2, note_ep_fac)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (candidat_id[0], row["moy_6e"], row["moy_5e"], row["moy_4e"], row["moy_3e"], 
                          row["note_eps"], row["note_cf"], row["note_ort"], row["note_tsq"], 
                          row["note_svt"], row["note_ang1"], row["note_math"], row["note_hg"], 
                          row["note_ic"], row["note_pc_lv2"], row["note_ang2"], row["note_ep_fac"]))
                    logging.info(f"✅ Notes insérées pour le candidat {row['num_table']}")

        conn.commit()
        #Calcul des statuts après l'importation pour éviter les accès concurrents
        logging.info("🔄 Mise à jour des statuts des candidats...")
        cursor.execute("SELECT num_table FROM candidats")
        candidats = cursor.fetchall()

        for candidat in candidats:
                calculer_statut_candidat(candidat[0], conn)

        conn.commit()
        logging.info("✅ Importation des notes terminée avec succès.")
        main_window.refresh_deliberation_signal.emit()

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'importation des notes : {e}")

    finally:
        conn.close()


def import_livret_scolaire_from_excel(excel_file):
    """ Importe les livrets scolaires depuis un fichier Excel """
    logging.info("📌 Début de l'importation du livret scolaire...")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return

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
                VALUES ((SELECT id FROM candidats WHERE num_table = ?), ?, ?, ?, ?, ?, ?)
                ON CONFLICT(candidat_id) DO UPDATE SET 
                    nombre_de_fois=excluded.nombre_de_fois, 
                    moyenne_6e=excluded.moyenne_6e, 
                    moyenne_5e=excluded.moyenne_5e, 
                    moyenne_4e=excluded.moyenne_4e, 
                    moyenne_3e=excluded.moyenne_3e, 
                    moyenne_cycle=excluded.moyenne_cycle
            """, (row["num_table"], row["nb_fois"], row["moy_6e"], row["moy_5e"], row["moy_4e"], row["moy_3e"], row["moyenne_cycle"]))
        
        conn.commit()
        logging.info("✅ Importation des livrets scolaires terminée avec succès.")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'importation du livret scolaire : {e}")
    
    finally:
        conn.close()
