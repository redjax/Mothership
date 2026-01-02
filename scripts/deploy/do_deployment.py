import argparse
import json
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


def is_git_available() -> bool:
    """Check if git executable is available in PATH."""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True, timeout=5)

        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


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
    mothership_url: str = "https://github.com/redjax/Mothership.git"

    @classmethod
    def from_json(cls, path: Path) -> "DeployConfig":
        """Load and validate from JSON."""
        config: dict = json.loads(path.read_text())

        repos = [
            RepositoryConfig(**repo_data)
            for repo_data in config.get("repositories", [])
        ]

        mothership_url = config.get("mothership_url", cls.mothership_url)

        return cls(repositories=repos, mothership_url=mothership_url)


@dataclass
class DeployedRepo:
    """Record of a successfully deployed repository."""

    name: str
    target: str
    branch: str
    remote_url: str


class MothershipController:
    """End-to-end Mothership deployment controller."""

    def __init__(self, mothership_dir: Path, config_path: Path, script_cwd: Path):
        self.mothership_dir = mothership_dir.absolute()
        self.config_path = config_path.absolute()
        self.script_cwd = script_cwd.absolute()

        self._ensure_mothership()

        self.config = self._load_config()
        self.deploy_order = self._calculate_deploy_order()
        self.deployed_repos: List[DeployedRepo] = []
        self.failed_repos: List[str] = []
        self.skipped_repos: List[str] = []

    def _ensure_mothership(self) -> None:
        """Clone Mothership repo if it doesn't exist, using config URL."""
        if self.mothership_dir.exists():
            if (self.mothership_dir / ".git").exists():
                print(f"✓ Mothership already exists at {self.mothership_dir}")
                return

            else:
                print(
                    f"[WARN] {self.mothership_dir} exists but is not a git repo. Removing"
                )
                shutil.rmtree(self.mothership_dir)

        default_url = "https://github.com/redjax/Mothership.git"
        mothership_url = default_url

        if self.config_path.exists():
            try:
                config_data = json.loads(self.config_path.read_text())
                mothership_url = config_data.get("mothership_url", default_url)

                if not mothership_url.endswith(".git"):
                    mothership_url += ".git"
            except json.JSONDecodeError:
                pass

        print(f"Cloning Mothership from {mothership_url}")
        self.mothership_dir.parent.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                ["git", "clone", mothership_url, str(self.mothership_dir)], check=True
            )
            print(f"✓ Mothership cloned to {self.mothership_dir}")

            print("Initializing and updating submodules")
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                cwd=self.mothership_dir,
                check=True,
            )
            print("✓ Submodules initialized")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to clone Mothership repo from {mothership_url}: {e}"
            )

    def _load_config(self) -> DeployConfig:
        """Load and validate config."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"deploy.json not found at {self.config_path}")

        return DeployConfig.from_json(self.config_path)

    def _calculate_deploy_order(self) -> List[RepositoryConfig]:
        """Ensure git_dir is cloned first if it's present, preserve order for others."""
        git_dir_repo = None
        other_repos = []

        for repo in self.config.repositories:
            if repo.name == "git_dir":
                git_dir_repo = repo
            else:
                other_repos.append(repo)

        deploy_order = []

        if git_dir_repo:
            deploy_order.append(git_dir_repo)

        deploy_order.extend(other_repos)

        return deploy_order

    def run_git(
        self, *args: str, cwd: Optional[Path] = None, check: bool = True
    ) -> str:
        """Run git command."""
        result = subprocess.run(
            ["git"] + list(args), cwd=cwd, check=check, capture_output=True, text=True
        )

        return result.stdout.strip()

    def get_submodule_remote(self, name: str) -> str:
        """Extract original git remote URL from submodule."""
        submodule_dir: Path = self.mothership_dir / "modules" / name

        if submodule_dir.exists():
            try:
                remote = self.run_git(
                    "config", "--get", "remote.origin.url", cwd=submodule_dir
                )
                if remote:
                    return remote
            except subprocess.CalledProcessError:
                pass

        gitmodules: Path = self.mothership_dir / ".gitmodules"

        if gitmodules.exists():
            try:
                remote = self.run_git(
                    "config",
                    "-f",
                    ".gitmodules",
                    f"submodule.{name}.url",
                    cwd=self.mothership_dir,
                )

                if remote:
                    return remote

            except subprocess.CalledProcessError:
                pass

        raise ValueError(f"No remote found for submodule '{name}'")

    def deploy_repo(self, repo: RepositoryConfig) -> None:
        """Deploy single repository from the Mothership."""
        target = Path(repo.target).expanduser()
        src: Path = self.mothership_dir / "modules" / repo.name

        if not src.exists():
            self.failed_repos.append(f"{repo.name}: Submodule not found at {src}")
            print(f"  [ERROR] Submodule {src} not found")
            return

        print(f"Deploying {repo.name} → {target}")

        if target.exists():
            if target.is_dir() and (target / ".git").exists():
                self.skipped_repos.append(f"{repo.name} (existing git repo)")
                print(
                    f"  Skipping, target '{target}' already exists and is a git repository"
                )
                return

            else:
                self.skipped_repos.append(f"{repo.name} (existing non-git)")
                print(
                    f"  Skipping, target '{target}' already exists but is not a git repository"
                )
                return

        remote_url = ""
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "clone", str(src), str(target)], check=True)

            if repo.mothership_remote:
                remote_url = str(src)
                print(f"  Remote: MOTHERSHIP {remote_url}")
                subprocess.run(
                    ["git", "remote", "set-url", "origin", remote_url],
                    cwd=target,
                    check=True,
                )

            else:
                remote_url = self.get_submodule_remote(repo.name)
                print(f"  Remote: {remote_url}")
                subprocess.run(
                    ["git", "remote", "set-url", "origin", remote_url],
                    cwd=target,
                    check=True,
                )

            subprocess.run(
                ["git", "stash", "push", "-m", "Auto-stash before mothership deploy"],
                cwd=target,
                check=False,
            )

            try:
                subprocess.run(["git", "checkout", repo.branch], cwd=target, check=True)
            except subprocess.CalledProcessError:
                subprocess.run(
                    ["git", "checkout", "-b", repo.branch], cwd=target, check=True
                )

            try:
                subprocess.run(
                    [
                        "git",
                        "branch",
                        "--set-upstream-to",
                        f"origin/{repo.branch}",
                        repo.branch,
                    ],
                    cwd=target,
                )

                subprocess.run(["git", "pull", "--ff-only"], cwd=target, check=True)

            except subprocess.CalledProcessError:
                print(f"  Note: Could not set upstream/pull")

            self.deployed_repos.append(
                DeployedRepo(
                    name=repo.name,
                    target=str(target),
                    branch=repo.branch,
                    remote_url=remote_url,
                )
            )
            print(f"  ✓ {repo.name} deployed")

        except Exception as e:
            self.failed_repos.append(f"{repo.name}: {str(e)[:100]}")
            print(f"  [ERROR] Failed to deploy {repo.name}: {e}")

    def print_deploy_order(self) -> None:
        print("Deploy order:")
        for repo in self.deploy_order:
            print(f"  {repo.name}")

        print()

    def display_report(self) -> None:
        print("\n" + "=" * 80)
        print("DEPLOYMENT REPORT")
        print("=" * 80)
        print(f"  Successfully deployed: {len(self.deployed_repos)}")
        print(f"  Skipped: {len(self.skipped_repos)}")
        print(f"  Failed: {len(self.failed_repos)}")
        print()

        if self.deployed_repos:
            print("SUCCESSFUL DEPLOYS:")
            print(f"{'Name':<20} {'Target':<35} {'Branch':<12} {'Remote'}")
            print("-" * 80)

            for repo in self.deployed_repos:
                print(
                    f"{repo.name:<20} {repo.target:<35} {repo.branch:<12} {repo.remote_url}"
                )

            print()

        if self.skipped_repos:
            print("SKIPPED REPOS:")
            for reason in self.skipped_repos:
                print(f"  {reason}")

            print()

        if self.failed_repos:
            print("FAILED REPOS:")
            for reason in self.failed_repos:
                print(f"  {reason}")

        print("=" * 80)

    def deploy_all(self) -> None:
        self.print_deploy_order()

        for repo in self.deploy_order:
            self.deploy_repo(repo)
            print()

        print("\nDeploy complete")
        self.display_report()


if __name__ == "__main__":
    if not is_git_available():
        print("[ERROR] Git is not installed, or is not available in the PATH")
        sys.exit(1)

    args = parse_args()
    script_cwd = Path.cwd()

    config_path = (
        script_cwd / args.deployment_config
        if not args.deployment_config.is_absolute()
        else args.deployment_config.absolute()
    )

    mothership_dir = args.mothership.absolute()

    try:
        controller = MothershipController(mothership_dir, config_path, script_cwd)
        controller.deploy_all()
    except Exception as exc:
        print(f"[ERROR] ({type(exc).__name__}) Failed to deploy repositories: {exc}")
        sys.exit(1)
