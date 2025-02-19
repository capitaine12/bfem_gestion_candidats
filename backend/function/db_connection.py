import sqlite3, logging
import time

def get_db_connection():
    """ Récupère une connexion SQLite avec gestion des erreurs """
    retries = 5  # Nombre de tentatives avant d'abandonner
    for _ in range(retries):
        try:
            conn = sqlite3.connect("data/candidatbfem.db", timeout=5)  # Timeout de 5s
            return conn
        except sqlite3.OperationalError as e:
                logging.warning(f"⚠️ Base de données verrouillée, nouvelle tentative dans 0.1s... ({e})")
                time.sleep(0.1)  # Attendre avant de réessayer
    raise sqlite3.OperationalError("⛔ Impossible d'accéder à la base de données après plusieurs tentatives.")

