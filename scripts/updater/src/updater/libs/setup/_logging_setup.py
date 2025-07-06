import logging
import logging.handlers
from pathlib import Path

__all__ = ["setup_package_logging"]


def setup_package_logging(
    log_file: str = "logs/mothership_repo_updater.log",
    log_level: str = "INFO",
    log_file_maxbytes=10 * 1024 * 1024,
    log_file_backup_count=5,
):
    ## root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    file_formatter = logging.Formatter(
        "%(asctime)s | [%(levelname)s] | (%(name)s) > %(module)s.%(funcName)s:%(lineno)s :: %(message)s"
    )

    if not Path(log_file).parent.exists():
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        mode="a",
        maxBytes=log_file_maxbytes,
        backupCount=log_file_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel("DEBUG")

    logger.addHandler(file_handler)
