import sqlite3, logging, sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import get_db_connection
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_candidats_second_tour():
    """ Récupère les candidats qui passent au second tour ou qui sont repêchés """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.num_table, c.prenom, c.nom, d.total_points, d.statut
            FROM candidats c
            JOIN deliberation d ON c.id = d.candidat_id 
            WHERE d.statut IN ('Admis Doffice', 'Repêchable au 1er tour', 'Second Tour', 'Repêchable au 2nd tour')
            AND d.total_points >= 153
            ORDER BY d.total_points DESC
        """)

        candidats = cursor.fetchall()
        return candidats

    except sqlite3.Error as e:
        logging.error(f"❌ Erreur lors de la récupération des candidats au second tour : {e}")
        return []
    finally:
        conn.close()