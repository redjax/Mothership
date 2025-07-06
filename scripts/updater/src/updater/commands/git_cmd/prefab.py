import logging

from updater.main import ShellCommandRunner

log = logging.getLogger(__name__)


__all__ = ["update_git_submodules"]


def update_git_submodules(runner: ShellCommandRunner | None  = None):
    if runner is None:
        runner: ShellCommandRunner = ShellCommandRunner()
    
    ## Pull submodule changes
    submodule_pull_cmd = ["git", "pull", "--recurse-submodules"]
    
    log.info("Recursively updating all submodules.")
    try:
        submodule_pull_exit_code = runner.run(submodule_pull_cmd)
        log.info("Updated submodules")
    except Exception as e:
        log.error(f"Failed updating submodules: {e}")
        return False
    
    if submodule_pull_exit_code != 0:
        log.warning(f"Failed executing command: {','.join(submodule_pull_cmd)}")
        
        return False
        
    ## Update submodules
    submodule_update_cmd = ["git", "submodule", "update", "--init", "--recursive", "--remote"]
    
    try:
        submodule_update_exit_code = runner.run(submodule_update_cmd)
        log.info("Updated submodules")
    except Exception as e:
        log.error(f"Failed updating submodules: {e}")
        return False
    
    if submodule_update_exit_code != 0:
        log.warning(f"Failed executing command: {','.join(submodule_update_cmd)}")
        
        return False
        
    return True
