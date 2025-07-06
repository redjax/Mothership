import logging
import argparse

log = logging.getLogger(__name__)

from updater.main import ShellCommandRunner
from updater.libs.setup import setup_package_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("updater", description="Mothership Repo submodule updater")
    
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    parser.add_argument("--log-file", "-l", type=str, help="Set path to logging file", default="logs/mothership_repo_updater.log")
    
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    
    log_level = "DEBUG" if args.debug else "INFO"
    log_file = args.log_file or "mothership_repo_updater.log"
    
    setup_package_logging(log_level=log_level, log_file=log_file)
    log.debug("DEBUG logging enabled")
    
    runner: ShellCommandRunner = ShellCommandRunner(log_level="DEBUG")
    
    try:
        exit_code = runner.run(["git", "status"])
    except Exception as exc:
        log.error("Error running shell command", exc)
    
    exit(exit_code)
