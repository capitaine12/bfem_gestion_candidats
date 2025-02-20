import sqlite3, logging
import pandas as pd
from datetime import datetime

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.function.calculenotes import calculer_statut_candidat
from backend.function.db_connection import get_db_connection

#Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect("data/candidatbfem.db", timeout=10)  # Attente max de 10s
    conn.execute("PRAGMA foreign_keys = ON")  
    return conn

# Fonction pour créer la table des candidats et les autres tables
def create_tables():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

    # Table Jury
    
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jury (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ia_region TEXT NOT NULL,
                ief_departement TEXT NOT NULL,
                localite TEXT NOT NULL,
                centre_examen TEXT NOT NULL,
                president_jury TEXT NOT NULL,
                telephone TEXT NOT NULL
            )
        """)

        # Table Candidat
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                num_table INTEGER UNIQUE NOT NULL,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                date_naissance TEXT NOT NULL,
                lieu_naissance TEXT,
                sexe CHAR(1) NOT NULL,
                nationalite TEXT NOT NULL,
                epreuve_facultative TEXT,
                aptitude_sportive BOOLEAN NOT NULL,
                jury_id INTEGER,
                FOREIGN KEY (jury_id) REFERENCES jury(id) ON DELETE SET NULL
            )
        """)

        # Table Notes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidat_id INTEGER UNIQUE NOT NULL,
                moy_6e FLOAT,
                moy_5e FLOAT,
                moy_4e FLOAT,
                moy_3e FLOAT,
                note_eps FLOAT,
                note_cf FLOAT,
                note_ort FLOAT,
                note_tsq FLOAT,
                note_svt FLOAT,
                note_ang1 FLOAT,
                note_math FLOAT,
                note_hg FLOAT,
                note_ic FLOAT,
                note_pc_lv2 FLOAT,
                note_ang2 FLOAT,
                note_ep_fac FLOAT,
                FOREIGN KEY (candidat_id) REFERENCES candidats(id) ON DELETE CASCADE
            )
        """)


        # Table Livret Scolaire
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livret_scolaire (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidat_id INTEGER UNIQUE NOT NULL,
                nombre_de_fois INTEGER NOT NULL,
                moyenne_6e FLOAT,
                moyenne_5e FLOAT,
                moyenne_4e FLOAT,
                moyenne_3e FLOAT,
                moyenne_cycle FLOAT,
                FOREIGN KEY (candidat_id) REFERENCES candidats(id) ON DELETE CASCADE
            )
        """)

        # Table Délibération
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deliberation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidat_id INTEGER UNIQUE NOT NULL,
                total_points INTEGER NOT NULL,
                statut TEXT NOT NULL,
                FOREIGN KEY (candidat_id) REFERENCES candidats(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        logging.info("✅ Tables créées avec succès.")
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de la création des tables : {e}")

    finally:
        conn.close()

# Fonction pour importer des candidats depuis un fichier Excel

def import_candidats_from_excel(excel_file="data/bdbfem.xlsx"):
    logging.info(" Début de l'importation des candidats depuis Excel...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return

    try:
        # Chargement du fichier Excel
        df = pd.read_excel(excel_file)

        # Renommer les colonnes pour correspondre à la base SQLite
        df.columns = [
            "num_table", "prenom", "nom", "date_naissance", "lieu_naissance",
            "sexe", "nb_fois", "type_candidat", "etablissement", "nationalite",
            "etat_sportif", "epreuve_facultative", "moy_6e", "moy_5e", "moy_4e", "moy_3e",
            "note_eps", "note_cf", "note_ort", "note_tsq", "note_svt", "note_ang1",
            "note_math", "note_hg", "note_ic", "note_pc_lv2", "note_ang2", "note_ep_fac",
            
        ]

        # Convertir la colonne date_naissance au format pour SQLite
        df['date_naissance'] = pd.to_datetime(df['date_naissance']).dt.strftime('%Y-%m-%d')
        # Insérer les données dans la base de données
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                               INSERT INTO candidats (num_table, prenom, nom, date_naissance, lieu_naissance, sexe,
                               nationalite, epreuve_facultative, aptitude_sportive)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                               """, (row["num_table"], row["prenom"], row["nom"], row["date_naissance"], row["lieu_naissance"],
                                     row["sexe"], row["nationalite"], row["epreuve_facultative"], row["etat_sportif"]))
                
                
                logging.info(f"✅ Candidat inséré : {row['num_table']} - {row['prenom']} {row['nom']}")
                
            except sqlite3.IntegrityError:
                logging.error(f"❌ Le candidat avec num_table {row['num_table']} existe déjà.")

        # Sauvegarder et fermer la connexion
        conn.commit()
        logging.info("Les candidats ont été importés avec succès depuis Excel.")
        
    except Exception as e:
       logging.error(f"❌ Erreur lors de l'importation : {e}")
    finally:
        conn.close()

# Vérification si un candidat existe déjà
def candidat_existe(num_table):
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return

    try:
        cursor.execute("SELECT COUNT(*) FROM candidats WHERE num_table = ?", (num_table,))
        result = cursor.fetchone()[0]
    
    finally:
        conn.close()

    return result > 0  # Retourne True si le numéro de table existe déjà

#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE RECUPERATION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE RECUPERATION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE RECUPERATION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
# Fonction pour récupérer tous les candidats
def get_all_candidats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return
    
    try:
        cursor.execute("""
        SELECT c.num_table, c.prenom, c.nom, c.date_naissance, c.lieu_naissance, 
               c.sexe, c.nationalite, c.epreuve_facultative, 
               c.aptitude_sportive, COALESCE(d.statut, 'Non délibéré') AS statut
        FROM candidats c
        LEFT JOIN deliberation d ON c.id = d.candidat_id 
        ORDER BY c.nom, c.date_naissance, c.sexe ASC
        """)

        candidats = cursor.fetchall()
    finally:
        conn.close()
    return candidats

# recuperation de candidat avec son status
def get_candidats_avec_statut():
    """ Récupère tous les candidats avec leur statut de délibération """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.num_table, c.prenom, c.nom, c.date_naissance, c.sexe, 
               c.nationalite, d.total_points, COALESCE(d.statut, 'Non délibéré')
        FROM candidats c
        LEFT JOIN deliberation d ON c.id = d.candidat_id 
        ORDER BY c.nom, c.date_naissance
    """)
    
    candidats = cursor.fetchall()
    conn.close()
    return candidats


# recuperation des notes des candidats
def get_all_notes():
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return
    
    cursor.execute("""
        SELECT c.num_table, n.moy_6e, n.moy_5e, n.moy_4e, n.moy_3e, n.note_eps,
               n.note_cf, n.note_ort, n.note_tsq, n.note_svt, n.note_ang1, 
               n.note_math, n.note_hg, n.note_ic, n.note_pc_lv2, n.note_ang2, 
               n.note_ep_fac,
               (n.moy_6e + n.moy_5e + n.moy_4e + n.moy_3e + n.note_eps +
                n.note_cf + n.note_ort + n.note_tsq + n.note_svt +
                n.note_ang1 + n.note_math + n.note_hg + n.note_ic + 
                n.note_pc_lv2 + n.note_ang2 + n.note_ep_fac) AS total_points
        FROM candidats c
        LEFT JOIN notes n ON c.id = n.candidat_id
    """)
    
    notes = cursor.fetchall()
    conn.close()
    return notes


#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS D'AJOUT BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS D'AJOUT BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS D'AJOUT BD :::::::::::::::::::::::::::::::::::::::::::::::::::

# Fonction pour ajouter un candidat
def add_candidat(num_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, 
                 epreuve_facultative, aptitude_sportive, jury_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO candidats (
                       num_table,
                       prenom,
                       nom,
                       date_naissance,
                       lieu_naissance,
                       sexe,
                       nationalite,
                       epreuve_facultative,
                       aptitude_sportive,
                       jury_id
                       ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (num_table, prenom, nom, date_naissance, lieu_naissance, sexe, 
              nationalite, epreuve_facultative, aptitude_sportive, jury_id))
        
        conn.commit()
        
        return True  # Succès
    except sqlite3.IntegrityError:
        return False  # Échec : Doublon détecté
    finally:
        conn.close()

def add_notes(num_table, notes):
    """ Ajoute les notes d'un candidat dans la base de données """
    logging.info(f"📌 Ajout des notes pour le candidat {num_table}")
   
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notes (candidat_id, moy_6e, moy_5e, moy_4e, moy_3e, note_eps, 
                               note_cf, note_ort, note_tsq, note_svt, note_ang1, note_math, 
                               note_hg, note_ic, note_pc_lv2, note_ang2, note_ep_fac) 
            VALUES ((SELECT id FROM candidats WHERE num_table = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (num_table, notes["moy_6e"], notes["moy_5e"], notes["moy_4e"], notes["moy_3e"], notes["note_eps"], 
              notes["note_cf"], notes["note_ort"], notes["note_tsq"], notes["note_svt"], notes["note_ang1"], 
              notes["note_math"], notes["note_hg"], notes["note_ic"], notes["note_pc_lv2"], notes["note_ang2"], notes["note_ep_fac"]))

        conn.commit()
        logging.info(f"✅ Notes ajoutées pour {num_table}, recalcul du statut...")
        calculer_statut_candidat(num_table)
        
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'ajout des notes pour {num_table} : {e}")
    finally:
        conn.close()


#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE MODIFICATION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE MODIFICATION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE MODIFICATION BD :::::::::::::::::::::::::::::::::::::::::::::::::::


# Fonction pour modifier un candidat existant
def update_candidat(num_table, prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, 
                     epreuve_facultative, aptitude_sportive, jury_id=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return
    
    try: 
        cursor.execute("""
            UPDATE candidats 
            SET prenom = ?, nom = ?, date_naissance = ?, lieu_naissance = ?, sexe = ?, nationalite = ?, 
                epreuve_facultative = ?, aptitude_sportive = ?, jury_id = ? 
            WHERE num_table = ?
        """, (prenom, nom, date_naissance, lieu_naissance, sexe, nationalite, 
            epreuve_facultative, aptitude_sportive, jury_id, num_table))
        conn.commit()
    finally:
        conn.close()

def update_notes(num_table, notes):
    """ Met à jour les notes d'un candidat existant """
    logging.info(f"📌 Mise à jour des notes pour {num_table}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return

    cursor.execute("""
        UPDATE notes
        SET moy_6e = ?, moy_5e = ?, moy_4e = ?, moy_3e = ?, note_eps = ?, 
            note_cf = ?, note_ort = ?, note_tsq = ?, note_svt = ?, note_ang1 = ?, 
            note_math = ?, note_hg = ?, note_ic = ?, note_pc_lv2 = ?, note_ang2 = ?, note_ep_fac = ?
        WHERE candidat_id = (SELECT id FROM candidats WHERE num_table = ?)
    """, (notes["moy_6e"], notes["moy_5e"], notes["moy_4e"], notes["moy_3e"], notes["note_eps"], 
          notes["note_cf"], notes["note_ort"], notes["note_tsq"], notes["note_svt"], notes["note_ang1"], 
          notes["note_math"], notes["note_hg"], notes["note_ic"], notes["note_pc_lv2"], notes["note_ang2"], notes["note_ep_fac"], num_table))

    
    conn.commit()
    logging.infot(f"✅ Notes mises à jour pour {num_table}, recalcul du statut...")
    calculer_statut_candidat(num_table)
    conn.close()



#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE SUPPRESSION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE SUPPRESSION BD :::::::::::::::::::::::::::::::::::::::::::::::::::
#?::::::::::::::::::::::::::::::::::::::::::::::::::: LES FONCTIONS DE SUPPRESSION BD :::::::::::::::::::::::::::::::::::::::::::::::::::

# Fonction pour supprimer un candidat
def delete_candidat(num_table):
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except sqlite3.OperationalError as e:
        logging.error(f"⚠️ Base de données verrouillée : {e}")
        return
    
    cursor.execute("DELETE FROM candidats WHERE num_table = ?", (num_table,))
    
    conn.commit()
    conn.close()



# Création des tables au lancement & importaion des données dans la BDD
create_tables()

import_candidats_from_excel()


