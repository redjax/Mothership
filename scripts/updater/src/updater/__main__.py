from __future__ import annotations

import argparse
import logging

log = logging.getLogger(__name__)

from updater.commands import git_cmd
from updater.libs.setup import setup_package_logging
from updater.main import ShellCommandRunner

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("updater", description="Mothership Repo submodule updater")
    
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    parser.add_argument("--log-file", "-l", type=str, help="Set path to logging file", default="logs/mothership_repo_updater.log")
    parser.add_argument("--update-submodules", "-u", action="store_true", help="Update all submodules")
    
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()
    
    log_level = "DEBUG" if args.debug else "INFO"
    log_file = args.log_file or "mothership_repo_updater.log"
    
    setup_package_logging(log_level=log_level, log_file=log_file)
    log.debug("DEBUG logging enabled")
    
    if args.update_submodules:
        ## Pull & update all submodules
        try:
            submodule_update_success = git_cmd.prefab.update_git_submodules()
        except Exception as exc:
            log.error("Failed updating submodules.", exc)
            exit(1)
            
        log.info("Updated submodules. You may see errors from the shell's stdout stream, but if you're seeing this, the script exited successfully anyway.")
    else:
        log.info("Running git status -v")

        try:
            exit_code = git_cmd.git_status("-v")
        except Exception as exc:
            log.error("Error running shell command", exc)
        
        if exit_code != 0:
            log.warning("Failed checking repo status")
