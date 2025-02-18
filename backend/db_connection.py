import sqlite3

def get_db_connection():
    """ Établit une connexion à la base de données SQLite """
    conn = sqlite3.connect("data/candidatbfem.db")
    return conn
