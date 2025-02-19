import logging
import os

# Vérifier et créer le dossier logs
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("✅ Test : Ceci est un message de test dans app.log")

