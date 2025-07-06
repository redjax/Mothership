from __future__ import annotations

import logging

from updater.commands import git_cmd
from updater.libs.setup import setup_package_logging
from updater.services.shell_svc import ShellCommandRunner

log = logging.getLogger(__name__)
        

__all__ = ["run_updater"]


def run_updater(
    debug: bool = False,
    log_file: str = "logs/mothership_repo_updater.log",
    update_submodules: bool = False,
):
    log_level = "DEBUG" if debug else "INFO"
    setup_package_logging(log_level=log_level, log_file=log_file)
    log = logging.getLogger(__name__)

    log.debug("DEBUG logging enabled")

    if update_submodules:
        try:
            submodule_update_success = git_cmd.prefab.update_git_submodules()
        except Exception as exc:
            log.error("Failed updating submodules.", exc_info=exc)
            return 1
        log.info("Updated submodules. You may see errors from the shell's stdout stream, but if you're seeing this, the script exited successfully anyway.")
        return 0
    else:
        log.info("Running git status -v")
        try:
            exit_code = git_cmd.git_status("-v")
        except Exception as exc:
            log.error("Error running shell command", exc_info=exc)
            return 1
        if exit_code != 0:
            log.warning("Failed checking repo status")
        return exit_code
    

if __name__ == "__main__":
    setup_package_logging(log_file="logs/mothership_repo_updater.log")
    
    runner = ShellCommandRunner()
    
    exit_code = runner.run(["git", "status"])
    
    exit(exit_code)
