# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "updater",
# ]
#
# [tool.uv.sources]
# updater = { path = "updater" }
# ///

import logging

from updater.libs.setup import setup_package_logging
import updater

log = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s | [%(levelname)s] :: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        update_succces = updater.run_updater(
            debug=False,
            log_file="logs/mothership_repo_updater.log",
            update_submodules=True,
        )
    except Exception as exc:
        log.error("Failed updating project submodules", exc)
        exit(1)

    exit(0)

