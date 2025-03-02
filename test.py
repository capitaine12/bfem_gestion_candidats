import logging


try:
    with open("logs/test.txt", "w") as test_file:
        test_file.write("Test d'écriture")
except Exception as e:
    logging.error(f"❌ Échec de l'écriture dans le dossier logs : {e}")