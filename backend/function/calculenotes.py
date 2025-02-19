import sqlite3
import pandas as pd

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function.db_connection import get_db_connection


def calculer_statut_candidat(num_table):
    """ Calcule le statut du candidat en fonction de ses notes et de son historique d'examen """
    print(f"📌 Délibération en cours pour {num_table}...")
    conn = get_db_connection()
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
        print(f"❌ Aucune donnée trouvée pour le candidat {num_table} !")
        return "Non délibéré"

    # Extraction des valeurs et gestion des NULL
    (moy_6e, moy_5e, moy_4e, moy_3e, 
     note_cf, note_ort, note_tsq, note_svt, 
     note_math, note_hg, note_pc_lv2, note_ang1, 
     note_ang2, note_eps, note_ep_fac, nb_fois) = data

    note_ep_fac = note_ep_fac if note_ep_fac is not None else 0
    note_eps = note_eps if note_eps is not None else 0

    # Calcul du total des points
    total_points = (
        (note_cf * 2) + (note_ort * 1) + (note_tsq * 1) + (note_svt * 2) + 
        (note_math * 4) + (note_hg * 2) + (note_pc_lv2 * 2) + (note_ang1 * 2) + 
        (note_ang2 * 1)
    )

    # Bonus/Malus EPS et épreuve facultative
    bonus_eps = max(0, note_eps - 10)
    malus_eps = max(0, 10 - note_eps)
    bonus_ef = max(0, note_ep_fac - 10)

    total_points += bonus_eps + bonus_ef - malus_eps

    statut = "Recalé"
    if total_points >= 180:
        statut = "Admis d'office"
    elif total_points >= 153:
        statut = "Second Tour"

    cursor.execute("""
        INSERT INTO deliberation (candidat_id, total_points, statut) 
        VALUES ((SELECT id FROM candidats WHERE num_table = ?), ?, ?)
        ON CONFLICT(candidat_id) DO UPDATE SET total_points = ?, statut = ?
    """, (num_table, total_points, statut, total_points, statut))

    conn.commit()
    print(f"📌 Insertion du statut {statut} pour {num_table} avec {total_points} points")
    conn.close()

    return statut

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
