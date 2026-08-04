from loguru import logger
import os

os.makedirs("logs", exist_ok=True)

logger.add(
    "logs/reversa_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="15 days",
    compression="zip",
    level="INFO",
    encoding="utf-8"
)