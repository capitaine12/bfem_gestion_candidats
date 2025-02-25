import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function.db_connection import get_db_connection

# Confi guration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Définition des coefficients des matières
COEFFICIENTS = {
    "note_cf": 2, "note_ort": 1, "note_tsq": 1, "note_svt": 2,
    "note_math": 4, "note_hg": 2, "note_pc_lv2": 2, "note_ang1": 2,
    "note_ang2": 1, "note_eps": 1, "note_ep_fac": 1
}

def calculer_statut_candidat(num_table, conn=None):
    """ Calcule le statut du candidat en fonction de ses notes et de son historique d'examen """
    fermer_connexion = False

    try:
        if conn is None:  # Si aucune connexion n'est fournie, on en ouvre une
            conn = get_db_connection()
            fermer_connexion = True

        cursor = conn.cursor()

        cursor.execute("""
            SELECT n.moy_6e, n.moy_5e, n.moy_4e, n.moy_3e, 
                n.note_cf, n.note_ort, n.note_tsq, n.note_svt, 
                n.note_math, n.note_hg, n.note_pc_lv2, n.note_ang1, 
                n.note_ang2, n.note_eps, n.note_ep_fac, l.nombre_de_fois
            FROM candidats c
            LEFT JOIN notes n ON c.id = n.candidat_id
            LEFT JOIN livret_scolaire l ON c.id = l.candidat_id
            WHERE c.num_table = ?
        """, (num_table,))

        data = cursor.fetchone()
        if not data:
            logging.warning(f"❌ Aucune donnée trouvée pour le candidat {num_table} !")
            return "Non délibéré"
        logging.info(f"✅ Données trouvées pour {num_table}: {data}")

        # Extraction des valeurs
        (moy_6e, moy_5e, moy_4e, moy_3e, 
        note_cf, note_ort, note_tsq, note_svt, 
        note_math, note_hg, note_pc_lv2, note_ang1, 
        note_ang2, note_eps, note_ep_fac, nb_fois) = data

        # Créer une liste de notes
        notes = [
            moy_6e, moy_5e, moy_4e, moy_3e,
            note_cf, note_ort, note_tsq, note_svt,
            note_math, note_hg, note_pc_lv2, note_ang1,
            note_ang2, note_eps, note_ep_fac
        ]

        # Remplacer les None par 0
        notes = [note if note is not None else 0 for note in notes]

        # Calcul du total des points
        total_points = (
            (notes[4] * 2) + (notes[5] * 1) + (notes[6] * 1) + (notes[7] * 2) + 
            (notes[8] * 4) + (notes[9] * 2) + (notes[10] * 2) + (notes[11] * 2) + 
            (notes[12] * 1)
        )

        # Bonus/Malus EPS et épreuve facultative
        bonus_eps = max(0, notes[13] - 10)
        malus_eps = max(0, 10 - notes[13])
        bonus_ef = max(0, notes[14] - 10)

        total_points += bonus_eps + bonus_ef - malus_eps

        # Statut en fonction des règles métiers
        statut = "Recalé"
        if total_points >= 180:
            statut = "Admis Doffice"
        elif total_points >= 153:
            statut = "Second Tour"
        elif total_points < 153:
            statut = "Échoué"

        # Règles de repêchage
        if total_points >= 171 and total_points < 180:
            statut = "Repêchable au 1er tour"
        elif total_points >= 144 and total_points < 153:
            statut = "Repêchable au 2nd tour"

        # Insertion ou mise à jour dans la table de délibération
        cursor.execute("""
                INSERT INTO deliberation (candidat_id, total_points, statut) 
                VALUES ((SELECT id FROM candidats WHERE num_table = ?), ?, ?)
                ON CONFLICT(candidat_id) DO UPDATE SET total_points = ?, statut = ?
            """, (num_table, total_points, statut, total_points, statut))

        conn.commit()
        logging.info(f"🎯 Statut final : {statut} pour {num_table}")

    except Exception as e:
        logging.error(f"❌ Erreur lors du calcul du statut pour {num_table} : {e}")

    finally:
        if fermer_connexion:
            conn.close()
        

def recalculer_tous_les_statuts():
    """ Recalcule le statut de tous les candidats et met à jour la table délibération """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        logging.info("📌 Début du recalcul de tous les statuts...")

        cursor.execute("SELECT num_table FROM candidats")
        candidats = cursor.fetchall()

        for candidat in candidats:
            num_table = candidat[0]
            logging.info(f"🔄 Recalcul du statut pour le candidat {num_table}...")
            calculer_statut_candidat(num_table, conn)  # Utilise la même connexion

        conn.commit()  # Valide toutes les mises à jour en une seule fois
        logging.info("✅ Recalcul des statuts terminé.")

    except Exception as e:
        logging.error(f"❌ Erreur lors du recalcul des statuts : {e}")

    finally:
        conn.close()