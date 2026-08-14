import logging
import os


# ==========================================================
# DIRETÓRIO DE LOG
# ==========================================================

os.makedirs("logs", exist_ok=True)


# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger("reversa")

logger.setLevel(logging.INFO)


# Evita adicionar handlers duplicados
logger.propagate = False


# ==========================================================
# FORMATTER
# ==========================================================

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)


# ==========================================================
# LOG EM ARQUIVO
# ==========================================================

file_handler = logging.FileHandler(
    "logs/reversa.log",
    encoding="utf-8"
)

file_handler.setLevel(logging.INFO)

file_handler.setFormatter(
    formatter
)


# ==========================================================
# LOG NO CONSOLE
# ==========================================================

console_handler = logging.StreamHandler()

console_handler.setLevel(logging.INFO)

console_handler.setFormatter(
    formatter
)


# ==========================================================
# ADICIONA OS HANDLERS
# ==========================================================

if not logger.handlers:

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )