from __future__ import annotations

import logging
import logging.handlers
import subprocess
from typing import List, Optional

from updater.libs.setup import setup_package_logging

log = logging.getLogger(__name__)

__all__ = ["ShellCommandRunner"]


class ShellCommandRunner:
    def __init__(self, log_level="INFO"):
        self.log = logging.getLogger("ShellCommandRunner")
        self.log.setLevel(log_level)

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
