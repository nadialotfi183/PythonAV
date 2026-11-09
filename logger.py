"""Module de logging centralisé du projet Pipeline Log Analyzer.

Tous les modules utilisent get_logger() pour écrire leurs messages
dans la console ET dans le fichier logs/app.log.
"""

import logging
import logging.handlers
import os
import sys

# Racine du projet (le dossier qui contient utils/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger configuré (console + fichier).

    Args:
        name: nom du logger, en général le nom du module (ex: "ingestion").

    Returns:
        Un objet logging.Logger prêt à l'emploi.
    """
    logger = logging.getLogger(name)

    # Évite les doublons de handlers si get_logger est appelé plusieurs fois
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter(LOG_FORMAT)

    # Handler console : niveau INFO
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler fichier : niveau DEBUG, rotation à 1 Mo, 3 sauvegardes
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as error:
        # Si le fichier est impossible à créer, on continue avec la console seule
        print(f"AVERTISSEMENT : logs fichier désactivés ({error})")

    return logger


if __name__ == "__main__":
    test_logger = get_logger("test")
    test_logger.debug("Message DEBUG (visible seulement dans le fichier)")
    test_logger.info("Message INFO")
    test_logger.warning("Message WARNING")
    test_logger.error("Message ERROR")
    try:
        1 / 0
    except ZeroDivisionError:
        test_logger.exception("Exemple d'erreur capturée")
    print(f"Fichier de logs : {LOG_FILE}")