"""
core/logger.py — Structured logging system.
Log files: ~/.adm/logs/adm_YYYY-MM-DD.log
"""
import logging
import os
from datetime import datetime

_LOG_DIR = os.path.join(os.path.expanduser("~"), ".adm", "logs")
_loggers: dict = {}


def get_logger(name: str) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]

    os.makedirs(_LOG_DIR, exist_ok=True)
    logger = logging.getLogger(f"adm.{name}")

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        log_file = os.path.join(_LOG_DIR, f"adm_{datetime.now():%Y-%m-%d}.log")
        try:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            ))
            logger.addHandler(fh)
        except OSError:
            pass

        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(ch)

    _loggers[name] = logger
    return logger
