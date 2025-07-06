import logging

from updater.services.shell_svc import ShellCommandRunner
from updater.libs.setup import setup_package_logging

log = logging.getLogger(__name__)
        

if __name__ == "__main__":
    setup_package_logging(log_file="logs/mothership_repo_updater.log")
    
    runner = ShellCommandRunner()
    
    exit_code = runner.run(["git", "status"])
    
    exit(exit_code)
