import logging

from updater.main import ShellCommandRunner

log = logging.getLogger(__name__)


__all__ = ["git_status", "git_list_remotes"]


def git_status(*args):
    runner = ShellCommandRunner()
    
    command = ["git", "status"] + list(args)
    
    return runner.run(command)


def git_list_remotes(*args):
    runner = ShellCommandRunner()
        
    command = ["git", "remote"] + list(args)
    
    return runner.run(command)
