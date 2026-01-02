#!/usr/bin/env python3
"""Mothership deploy tool - MothershipController + CLI args."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Mothership repository deployer.")

    parser.add_argument(
        "-c",
        "--deployment-config",
        default="deploy.json",
        type=Path,
        help="Path to JSON file defining Mothership deployment plan. Default: deploy.json",
    )

    parser.add_argument(
        "-m",
        "--mothership",
        default=Path.home() / "Mothership",
        type=Path,
        help="Path to Mothership repo. Default: ~/Mothership",
    )

    return parser.parse_args()


@dataclass
class RepositoryConfig:
    """Container for git repositories loaded from JSON.

    Properties:
        name (str): Name of the repository.
        target (str): Target directory for the repository.
        branch (str): Branch to checkout.
        mothership_remote (bool): Flag to determine whether repo should continue using Mothership as the remote, or if it should use the submodule's origin.
    """

    name: str
    target: str
    branch: str
    mothership_remote: bool = False

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name must be non-empty")

        if not self.target or not self.target.strip():
            raise ValueError("target must be non-empty")

        if not self.branch or not self.branch.strip():
            raise ValueError("branch must be non-empty")

        self.name = self.name.strip()
        self.target = self.target.strip()
        self.branch = self.branch.strip()


@dataclass
class DeployConfig:
    """Mothership deployment configuration loaded from JSON.

    Properties:
        repositories (List[RepositoryConfig]): List of Mothership repositories to deploy.
    """

    repositories: List[RepositoryConfig]

    @classmethod
    def from_json(cls, path: Path) -> "DeployConfig":
        """Load and validate from JSON."""
        config: dict = json.loads(path.read_text())

        ## List to store parsed repositories
        repos = []

        for repo_data in config.get("repositories", []):
            repos.append(RepositoryConfig(**repo_data))

        return cls(repositories=repos)


class MothershipController:
    """End-to-end Mothership deployment controller.

    Attributes:
        mothership_dir (Path): Path to Mothership repo.
        config_path (Path): Path to Mothership deployment config.
        config (DeployConfig): Parsed Mothership deployment config.
        deploy_order (List[RepositoryConfig]): List of repositories to deploy in order.
    """

    def __init__(self, mothership_dir: Path, config_path: Path):
        self.mothership_dir = mothership_dir.absolute()
        self.config_path = config_path.absolute()
        self.config = self._load_config()
        self.deploy_order = self._calculate_deploy_order()

    def _load_config(self) -> DeployConfig:
        """Load and validate config."""
        if not self.mothership_dir.exists():
            raise FileNotFoundError(f"Mothership not found at {self.mothership_dir}")

        if not self.config_path.exists():
            raise FileNotFoundError(f"deploy.json not found at {self.config_path}")

        return DeployConfig.from_json(self.config_path)

    def _calculate_deploy_order(self) -> List[RepositoryConfig]:
        """Ensure git_dir is cloned first if it's present, preserve order for others."""
        ## If git_dir is declared in deployment, this will be overwritten
        git_dir_repo = None
        ## List for non-git_dir repos
        other_repos = []

        ## Split into git_dir and non-git_dir
        for repo in self.config.repositories:
            if repo.name == "git_dir":
                git_dir_repo = repo
            else:
                other_repos.append(repo)

        deploy_order = []

        ## Ensure git_dir is first
        if git_dir_repo:
            deploy_order.append(git_dir_repo)

        deploy_order.extend(other_repos)

        return deploy_order

    def run_git(
        self, *args: str, cwd: Optional[Path] = None, check: bool = True
    ) -> str:
        """Run git command.

        Params:
            args (str): Arguments to pass to git.
            cwd (Path): Working directory to run git in.
            check (bool): Whether to raise an exception on non-zero exit code.
        """
        result = subprocess.run(
            ["git"] + list(args), cwd=cwd, check=check, capture_output=True, text=True
        )

        return result.stdout.strip()

    def get_submodule_remote(self, name: str) -> str:
        """Extract original git remote URL from submodule.

        Params:
            name (str): Name of submodule. Corresponds to a path in the Mothership's modules/ directory.
        """
        ## Set path to submodule
        submodule_dir: Path = self.mothership_dir / "modules" / name

        ## Check if submodule exists
        if submodule_dir.exists():
            ## If submodule exists, check if it has a remote
            remote = self.run_git(
                "config", "--get", "remote.origin.url", cwd=submodule_dir
            )

            if remote:
                return remote

        ## Path to .gitmodules file
        gitmodules: Path = self.mothership_dir / ".gitmodules"

        if gitmodules.exists():
            ## If .gitmodules exists, check if it has a remote
            remote = self.run_git(
                "config",
                "-f",
                ".gitmodules",
                f"submodule.{name}.url",
                cwd=self.mothership_dir,
            )

            if remote:
                return remote

        raise ValueError(f"No remote found for submodule '{name}'")

    def deploy_repo(self, repo: RepositoryConfig) -> None:
        """Deploy single repository from the Mothership.

        Params:
            repo (RepositoryConfig): Repository to deploy.
        """
        ## Get path to deployment target (where repo will be cloned)
        target = Path(repo.target).expanduser()
        ## Get path to submodule in the Mothership
        src: Path = self.mothership_dir / "modules" / repo.name

        if not src.exists():
            raise FileNotFoundError(f"Submodule {src} not found")

        print(f"Deploying {repo.name} → {target}")

        ## Skip if target already exists
        if target.exists():
            if target.is_dir() and (target / ".git").exists():
                print(
                    f"  Skipping, target '{target}' already exists and is a git repository)"
                )
                return

            else:
                print(
                    f"  Skipping, target '{target}' already exists but is not a git repository"
                )
                return

        ## Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)
        ## Clone submodule to target
        subprocess.run(["git", "clone", str(src), str(target)], check=True)

        ## Continue using local Mothership path as remote
        if repo.mothership_remote:
            remote_path = str(src)

            print(f"  Remote: MOTHERSHIP {remote_path}")

            subprocess.run(
                ["git", "remote", "set-url", "origin", remote_path], cwd=target
            )

        ## Extract submodule's original remote origin and set as remote for cloned repository
        else:
            remote = self.get_submodule_remote(repo.name)

            print(f"  Remote: {remote}")

            subprocess.run(["git", "remote", "set-url", "origin", remote], cwd=target)

        os.chdir(target)

        ## Checkout branch
        try:
            subprocess.run(["git", "checkout", repo.branch], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "checkout", "-b", repo.branch], check=True)

        ## Set upstream and pull
        try:
            subprocess.run(
                [
                    "git",
                    "branch",
                    "--set-upstream-to",
                    f"origin/{repo.branch}",
                    repo.branch,
                ]
            )

            subprocess.run(["git", "pull", "--ff-only"], check=True)
        except subprocess.CalledProcessError:
            print(f"  Note: Could not set upstream/pull")

        ## Return to Mothership directory
        os.chdir(self.mothership_dir)
        print(f"  ✓ {repo.name} deployed")

    def print_deploy_order(self) -> None:
        """Show deploy order."""
        print("Deploy order:")

        for repo in self.deploy_order:
            print(f"  {repo.name}")

        print()

    def deploy_all(self) -> None:
        """Deploy all repositories."""
        self.print_deploy_order()

        for repo in self.deploy_order:
            self.deploy_repo(repo)
            print()

        print("\nDeploy complete")


if __name__ == "__main__":
    args = parse_args()

    mothership_dir = args.mothership.absolute()

    config_path = (
        mothership_dir / args.deployment_config
        if not args.deployment_config.is_absolute()
        else args.deployment_config.absolute()
    )

    controller = MothershipController(mothership_dir, config_path)
    controller.deploy_all()
