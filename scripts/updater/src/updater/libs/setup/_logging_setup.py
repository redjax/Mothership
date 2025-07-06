from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

__all__ = ["setup_package_logging"]


def setup_package_logging(
    log_file: str = "logs/mothership_repo_updater.log",
    log_level: str = "INFO",
    log_file_maxbytes: int = 10 * 1024 * 1024,
    log_file_backup_count: int = 5,
):
    # Convert log_level string to logging constant if needed
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove all existing handlers (for testing, to avoid conflicts)
    logger.handlers.clear()

    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        mode="a",
        maxBytes=log_file_maxbytes,
        backupCount=log_file_backup_count,
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        "%(asctime)s | [%(levelname)s] | (%(name)s) > %(module)s.%(funcName)s:%(lineno)s :: %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Console handler
    console_fmt_str = (
        "%(asctime)s | [%(levelname)s] | %(name)s.%(funcName)s:%(lineno)d :: %(message)s"
        if log_level == logging.DEBUG
        else "%(asctime)s | [%(levelname)s] :: %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(console_fmt_str))
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)
