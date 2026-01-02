import json
import os
import subprocess
import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class RepositoryConfig:
    """Container for git repositories loaded from JSON."""

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
    """Mothership deployment configuration loaded from JSON."""

    repositories: List[RepositoryConfig]

    @classmethod
    def from_json(cls, path: Path) -> "DeployConfig":
        """Load and validate from JSON."""
        config = json.loads(path.read_text())

        ## List to store repositories loaded from JSON
        repos = []

        for repo_data in config.get("repositories", []):
            repos.append(RepositoryConfig(**repo_data))

        return cls(repositories=repos)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mothership repository deployer.")

    parser.add_argument(
        "-c",
        "--deployment-config",
        default="deploy.json",
        type=Path,
        help="Path to JSON file defining Mothership deployment plan. Default: deploy.json",
    )

    return parser.parse_args()


def run_git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    """Run a git command using host CLI and return the output."""
    result = subprocess.run(
        ["git"] + list(args), cwd=cwd, check=check, capture_output=True, text=True
    )

    return result.stdout.strip()


def get_submodule_remote(mothership_dir: Path, name: str) -> str:
    """Extract original git remote URL from submodule."""
    submodule_dir = mothership_dir / "modules" / name

    if submodule_dir.exists():
        remote = run_git("config", "--get", "remote.origin.url", cwd=submodule_dir)

        if remote:
            return remote

    gitmodules = mothership_dir / ".gitmodules"

    if gitmodules.exists():
        remote = run_git(
            "config", "-f", ".gitmodules", f"submodule.{name}.url", cwd=mothership_dir
        )

        if remote:
            return remote

    raise ValueError(f"No remote found for submodule '{name}'")


def deploy_repo(repo: RepositoryConfig, mothership_dir: Path) -> None:
    """Deploy a git repository from the Mothership."""
    target = Path(repo.target).expanduser()
    src = mothership_dir / "modules" / repo.name

    if not src.exists():
        raise FileNotFoundError(f"Submodule {src} not found")

    print(f"Deploying {repo.name} → {target}")

    if target.exists():
        if target.is_dir() and (target / ".git").exists():
            print(f"  Skipping - already exists (git repo detected)")
            return
        else:
            print(f"  Target exists but not a git repo - removing")
            import shutil

            shutil.rmtree(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", str(src), str(target)], check=True)

    if repo.mothership_remote:
        remote_path = str(src)
        print(f"  Remote: MOTHERSHIP {remote_path}")

        subprocess.run(["git", "remote", "set-url", "origin", remote_path], cwd=target)
    else:
        remote = get_submodule_remote(mothership_dir, repo.name)
        print(f"  Remote: {remote}")

        subprocess.run(["git", "remote", "set-url", "origin", remote], cwd=target)

    ## cd to path where command should run
    os.chdir(target)

    try:
        subprocess.run(["git", "checkout", repo.branch], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["git", "checkout", "-b", repo.branch], check=True)

    try:
        subprocess.run(
            ["git", "branch", "--set-upstream-to", f"origin/{repo.branch}", repo.branch]
        )

        subprocess.run(["git", "pull", "--ff-only"], check=True)
    except subprocess.CalledProcessError:
        print(f"  Note: Could not set upstream/pull")

    os.chdir(mothership_dir)

    print(f"  ✓ {repo.name} deployed")


if __name__ == "__main__":
    args = parse_args()

    mothership_dir = Path.home() / "Mothership"
    if not mothership_dir.exists():
        print(f"Error: Mothership not found at {mothership_dir}")
        sys.exit(1)

    config_path = mothership_dir / "deploy.json"
    if not config_path.exists():
        print(f"Error: deploy.json not found at {config_path}")
        sys.exit(1)

    config = DeployConfig.from_json(config_path)

    ## Prioritize git_dir first, preserve order for others
    git_dir_repo = None
    other_repos = []

    for repo in config.repositories:
        if repo.name == "git_dir":
            git_dir_repo = repo
        else:
            other_repos.append(repo)

    deploy_order = []

    if git_dir_repo:
        deploy_order.append(git_dir_repo)
    deploy_order.extend(other_repos)

    print("Deploy order:")
    for repo in deploy_order:
        print(f"  {repo.name}")
    print()

    for repo in deploy_order:
        deploy_repo(repo, mothership_dir)

    print("\nDeploy complete")
