import sqlite3, logging
import pandas as pd

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function.db_connection import get_db_connection

#Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def calculer_statut_candidat(num_table):
    """ Calcule le statut du candidat en fonction de ses notes """
    logging.info(f"📌 Délibération en cours pour le candidat {num_table}")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT n.moy_6e, n.moy_5e, n.moy_4e, n.moy_3e, 
                   n.note_cf, n.note_ort, n.note_tsq, n.note_svt, 
                   n.note_math, n.note_hg, n.note_pc_lv2, n.note_ang1, 
                   n.note_ang2, n.note_eps, n.note_ep_fac, l.nombre_de_fois
            FROM notes n
            JOIN candidats c ON n.candidat_id = c.id
            JOIN livret_scolaire l ON n.candidat_id = l.candidat_id
            WHERE c.num_table = ?
        """, (num_table,))

        data = cursor.fetchone()
        if not data:
            logging.warning(f"❌ Aucune donnée trouvée pour le candidat {num_table} !")
            return "Non délibéré"

        logging.info(f"✅ Données trouvées pour {num_table}: {data}")
        
        # [LOGIQUE DE CALCUL DU STATUT ICI...]
        statut = "Recalé"  # Exemple

        cursor.execute("""
            INSERT INTO deliberation (candidat_id, total_points, statut) 
            VALUES ((SELECT id FROM candidats WHERE num_table = ?), ?, ?)
            ON CONFLICT(candidat_id) DO UPDATE SET total_points = ?, statut = ?
        """, (num_table, 150, statut, 150, statut))

        conn.commit()
        logging.info(f"🎯 Statut final : {statut} pour {num_table}")

    except Exception as e:
        logging.error(f"❌ Erreur lors du calcul du statut pour {num_table} : {e}")
    finally:
        conn.close()

#?::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def recalculer_tous_les_statuts():
    """ Recalcule le statut de tous les candidats et met à jour la table délibération """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("📌 Début du recalcul de tous les statuts...")

    # Récupérer tous les candidats avec notes
    cursor.execute("SELECT num_table FROM candidats")
    candidats = cursor.fetchall()

    for candidat in candidats:
        num_table = candidat[0]
        print(f"🔄 Recalcul du statut pour le candidat {num_table}...")
        statut = calculer_statut_candidat(num_table)
        print(f"🎯 Statut final : {statut} pour {num_table}")

    print("✅ Recalcul des statuts terminé.")
    conn.close()
