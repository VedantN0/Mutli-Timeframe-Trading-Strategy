import logging
import sys
from datetime import datetime, timezone

from config.config import LOG_LEVEL


class UTCFormatter(logging.Formatter):
    """
    Custom logging formatter enforcing UTC timestamps.
    """

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger with UTC timestamps.

    Log level is controlled centrally via config.LOG_LEVEL.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if logger is requested multiple times
    if logger.handlers:
        return logger

    level = _LEVEL_MAP.get(LOG_LEVEL, logging.INFO)

    logger.setLevel(level)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = UTCFormatter(_LOG_FORMAT, _DATE_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
