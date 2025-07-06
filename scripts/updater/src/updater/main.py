import logging.handlers
import subprocess
import logging
from typing import List, Optional

from updater.libs.setup import setup_package_logging

log = logging.getLogger(__name__)

__all__ = ["ShellCommandRunner"]


class ShellCommandRunner:
    def __init__(self, log_level="INFO"):
        self.log = logging.getLogger("ShellCommandRunner")
        
        ## Convert string log level to logging constant
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)

        self.log.setLevel(log_level)
        
        ## Add only a console handler. File logging will be handled by the root logger.
        console_formatter = logging.Formatter(
            "%(asctime)s | [%(levelname)s] :: %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        
        ## Prevent adding multiple handlers if already present
        if not any(isinstance(h, logging.StreamHandler) for h in self.log.handlers):
            self.log.addHandler(console_handler)

    def run(self, command: List[str], cwd: Optional[str] = None) -> int:
        self.log.debug(f"Running command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            self.log.info(f"stdout:\n{result.stdout}")
            
            if result.stderr:
                self.log.error(f"stderr:\n{result.stderr}")
                
            if result.returncode != 0:
                self.log.error(f"Command failed with exit code {result.returncode}")
            else:
                self.log.info("Command completed successfully.")
                
            return result.returncode

        except Exception as e:
            self.log.exception(f"Failed running command '{command}': {e}")
            ## Command probably returned a 0, 1, 2, or other positive integer.
            #  Return a -1 to indicate function failure
            return -1
        

if __name__ == "__main__":
    setup_package_logging(log_file="logs/mothership_repo_updater.log")
    
    runner = ShellCommandRunner()
    
    exit_code = runner.run(["git", "status"])
    
    exit(exit_code)
