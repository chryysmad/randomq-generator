# Utility class for common functions/utilities

from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")