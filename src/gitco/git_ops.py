"""Git operations and repository management for GitCo."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from .utils import GitOperationError, get_logger


class GitRepository:
    """Represents a Git repository with validation and status information."""

    def __init__(self, path: str):
        """Initialize GitRepository with path.

        Args:
            path: Path to the repository
        """
        self.path = Path(path).resolve()
        self.logger = get_logger()

    def is_git_repository(self) -> bool:
        """Check if the path is a valid Git repository.

        Returns:
            True if it's a Git repository, False otherwise.
        """
        try:
            git_dir = self.path / ".git"
            if not git_dir.exists() or not git_dir.is_dir():
                return False

            # Check if it's a valid Git repository by running git status
            result = self._run_git_command(["status"], capture_output=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"Error checking if {self.path} is a Git repository: {e}")
            return False

    def get_remote_urls(self) -> dict[str, str]:
        """Get all remote URLs for the repository.

        Returns:
            Dictionary mapping remote names to URLs.
        """
        try:
            result = self._run_git_command(
                ["remote", "-v"], capture_output=True, text=True
            )
            if result.returncode != 0:
                return {}

            remotes = {}
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        remote_name = parts[0]
                        remote_url = parts[1]
                        remotes[remote_name] = remote_url

            return remotes
        except Exception as e:
            self.logger.debug(f"Error getting remote URLs for {self.path}: {e}")
            return {}

    def add_upstream_remote(self, upstream_url: str) -> bool:
        """Add or update upstream remote.

        Args:
            upstream_url: URL of the upstream repository

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Check if upstream remote already exists
            remotes = self.get_remote_urls()

            if "upstream" in remotes:
                # Update existing upstream remote
                self.logger.info(f"Updating upstream remote for {self.path}")
                result = self._run_git_command(
                    ["remote", "set-url", "upstream", upstream_url]
                )
            else:
                # Add new upstream remote
                self.logger.info(f"Adding upstream remote for {self.path}")
                result = self._run_git_command(
                    ["remote", "add", "upstream", upstream_url]
                )

            if result.returncode == 0:
                self.logger.info(
                    f"Successfully configured upstream remote: {upstream_url}"
                )
                return True
            else:
                self.logger.error(
                    f"Failed to configure upstream remote: {result.stderr}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error configuring upstream remote for {self.path}: {e}")
            return False

    def remove_upstream_remote(self) -> bool:
        """Remove upstream remote if it exists.

        Returns:
            True if successful or remote doesn't exist, False otherwise.
        """
        try:
            remotes = self.get_remote_urls()

            if "upstream" not in remotes:
                self.logger.info(f"No upstream remote found for {self.path}")
                return True

            self.logger.info(f"Removing upstream remote for {self.path}")
            result = self._run_git_command(["remote", "remove", "upstream"])

            if result.returncode == 0:
                self.logger.info("Successfully removed upstream remote")
                return True
            else:
                self.logger.error(f"Failed to remove upstream remote: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error removing upstream remote for {self.path}: {e}")
            return False

    def update_upstream_remote(self, upstream_url: str) -> bool:
        """Update upstream remote URL.

        Args:
            upstream_url: New URL for the upstream repository

        Returns:
            True if successful, False otherwise.
        """
        try:
            remotes = self.get_remote_urls()

            if "upstream" not in remotes:
                self.logger.warning(
                    f"No upstream remote found for {self.path}, adding new one"
                )
                return self.add_upstream_remote(upstream_url)

            self.logger.info(f"Updating upstream remote URL for {self.path}")
            result = self._run_git_command(
                ["remote", "set-url", "upstream", upstream_url]
            )

            if result.returncode == 0:
                self.logger.info(
                    f"Successfully updated upstream remote: {upstream_url}"
                )
                return True
            else:
                self.logger.error(f"Failed to update upstream remote: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error updating upstream remote for {self.path}: {e}")
            return False

    def validate_upstream_remote(self) -> dict[str, any]:
        """Validate upstream remote configuration.

        Returns:
            Dictionary with validation results.
        """
        try:
            remotes = self.get_remote_urls()

            if "upstream" not in remotes:
                return {
                    "has_upstream": False,
                    "is_valid": False,
                    "error": "No upstream remote configured",
                    "url": None,
                }

            upstream_url = remotes["upstream"]

            # Test if upstream remote is accessible
            result = self._run_git_command(
                ["ls-remote", "--heads", "upstream"], capture_output=True, text=True
            )

            if result.returncode == 0:
                return {
                    "has_upstream": True,
                    "is_valid": True,
                    "url": upstream_url,
                    "accessible": True,
                }
            else:
                return {
                    "has_upstream": True,
                    "is_valid": False,
                    "error": f"Upstream remote not accessible: {result.stderr}",
                    "url": upstream_url,
                    "accessible": False,
                }

        except Exception as e:
            return {
                "has_upstream": "upstream" in self.get_remote_urls(),
                "is_valid": False,
                "error": str(e),
                "url": self.get_remote_urls().get("upstream"),
            }

    def fetch_upstream(self) -> bool:
        """Fetch latest changes from upstream.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Validate upstream remote first
            validation = self.validate_upstream_remote()
            if not validation["has_upstream"]:
                self.logger.error("No upstream remote configured")
                return False

            if not validation["is_valid"]:
                self.logger.error(
                    f"Upstream remote validation failed: {validation['error']}"
                )
                return False

            self.logger.info(f"Fetching from upstream for {self.path}")
            result = self._run_git_command(["fetch", "upstream"])

            if result.returncode == 0:
                self.logger.info("Successfully fetched from upstream")
                return True
            else:
                self.logger.error(f"Failed to fetch from upstream: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error fetching from upstream for {self.path}: {e}")
            return False

    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name.

        Returns:
            Current branch name or None if error.
        """
        try:
            result = self._run_git_command(
                ["branch", "--show-current"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            self.logger.debug(f"Error getting current branch for {self.path}: {e}")
            return None

    def get_default_branch(self) -> Optional[str]:
        """Get the default branch (main/master) of the repository.

        Returns:
            Default branch name or None if error.
        """
        try:
            # Try to get the default branch from origin
            result = self._run_git_command(
                ["symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                # Extract branch name from refs/remotes/origin/main
                branch = result.stdout.strip().split("/")[-1]
                return branch

            # Fallback: try common default branches
            for branch in ["main", "master"]:
                result = self._run_git_command(
                    ["ls-remote", "--heads", "origin", branch],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return branch

            return None
        except Exception as e:
            self.logger.debug(f"Error getting default branch for {self.path}: {e}")
            return None

    def get_repository_status(self) -> dict[str, any]:
        """Get comprehensive repository status.

        Returns:
            Dictionary with repository status information.
        """
        status = {
            "path": str(self.path),
            "is_git_repository": False,
            "current_branch": None,
            "default_branch": None,
            "remotes": {},
            "has_uncommitted_changes": False,
            "has_untracked_files": False,
            "is_clean": False,
            "upstream_status": {},
        }

        if not self.is_git_repository():
            return status

        status["is_git_repository"] = True
        status["current_branch"] = self.get_current_branch()
        status["default_branch"] = self.get_default_branch()
        status["remotes"] = self.get_remote_urls()
        status["upstream_status"] = self.validate_upstream_remote()

        # Check for uncommitted changes
        try:
            result = self._run_git_command(
                ["status", "--porcelain"], capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                status["has_uncommitted_changes"] = any(
                    line and not line.startswith("??") for line in lines
                )
                status["has_untracked_files"] = any(
                    line.startswith("??") for line in lines
                )
                status["is_clean"] = not (
                    status["has_uncommitted_changes"] or status["has_untracked_files"]
                )
        except Exception as e:
            self.logger.debug(f"Error checking repository status for {self.path}: {e}")

        return status

    def validate_repository(self) -> list[str]:
        """Validate the repository and return any issues found.

        Returns:
            List of validation error messages.
        """
        errors = []

        if not self.path.exists():
            errors.append(f"Repository path does not exist: {self.path}")
            return errors

        if not self.path.is_dir():
            errors.append(f"Repository path is not a directory: {self.path}")
            return errors

        if not self.is_git_repository():
            errors.append(f"Path is not a valid Git repository: {self.path}")
            return errors

        # Check if repository has remotes
        remotes = self.get_remote_urls()
        if not remotes:
            errors.append(f"No remotes configured for repository: {self.path}")

        # Check if repository has a default branch
        default_branch = self.get_default_branch()
        if not default_branch:
            errors.append(
                f"Could not determine default branch for repository: {self.path}"
            )

        # Check upstream remote if configured
        upstream_status = self.validate_upstream_remote()
        if upstream_status["has_upstream"] and not upstream_status["is_valid"]:
            errors.append(
                f"Upstream remote validation failed: {upstream_status['error']}"
            )

        return errors

    def _run_git_command(
        self,
        args: list[str],
        capture_output: bool = False,
        text: bool = False,
        cwd: Optional[Path] = None,
    ) -> subprocess.CompletedProcess:
        """Run a Git command in the repository.

        Args:
            args: Git command arguments
            capture_output: Whether to capture output
            text: Whether to return text output
            cwd: Working directory (defaults to repository path)

        Returns:
            CompletedProcess result

        Raises:
            GitOperationError: If Git command fails
        """
        try:
            cmd = ["git"] + args
            working_dir = cwd or self.path

            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=capture_output,
                text=text,
                timeout=30,  # 30 second timeout
            )

            return result
        except subprocess.TimeoutExpired:
            raise GitOperationError(
                f"Git command timed out: {' '.join(args)}"
            ) from None
        except Exception as e:
            raise GitOperationError(
                f"Failed to run Git command {' '.join(args)}: {e}"
            ) from e


class GitRepositoryManager:
    """Manages Git repository operations and validation."""

    def __init__(self):
        """Initialize GitRepositoryManager."""
        self.logger = get_logger()

    def detect_repositories(self, base_path: str) -> list[GitRepository]:
        """Detect Git repositories in a directory tree.

        Args:
            base_path: Base path to search for repositories

        Returns:
            List of GitRepository objects found
        """
        repositories = []
        base_path_obj = Path(base_path).resolve()

        if not base_path_obj.exists():
            self.logger.warning(f"Base path does not exist: {base_path}")
            return repositories

        if not base_path_obj.is_dir():
            self.logger.warning(f"Base path is not a directory: {base_path}")
            return repositories

        # Walk through directory tree looking for .git directories
        for root, dirs, _files in os.walk(base_path_obj):
            if ".git" in dirs:
                repo_path = Path(root)
                repository = GitRepository(str(repo_path))

                if repository.is_git_repository():
                    repositories.append(repository)
                    self.logger.debug(f"Found Git repository: {repo_path}")
                else:
                    self.logger.debug(
                        f"Found .git directory but not valid repository: {repo_path}"
                    )

        return repositories

    def validate_repository_path(self, path: str) -> tuple[bool, list[str]]:
        """Validate a repository path.

        Args:
            path: Path to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        repository = GitRepository(path)
        errors = repository.validate_repository()
        return len(errors) == 0, errors

    def get_repository_info(self, path: str) -> dict[str, any]:
        """Get detailed information about a repository.

        Args:
            path: Path to the repository

        Returns:
            Dictionary with repository information
        """
        repository = GitRepository(path)
        return repository.get_repository_status()

    def validate_repository_config(self, config: dict[str, any]) -> list[str]:
        """Validate repository configuration.

        Args:
            config: Repository configuration dictionary

        Returns:
            List of validation errors
        """
        errors = []

        # Check required fields
        required_fields = ["name", "fork", "upstream", "local_path"]
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f"Missing required field: {field}")

        if errors:
            return errors

        # Validate local path
        local_path = config.get("local_path")
        if local_path:
            is_valid, path_errors = self.validate_repository_path(local_path)
            if not is_valid:
                errors.extend(
                    [
                        f"Repository path validation failed: {error}"
                        for error in path_errors
                    ]
                )

        return errors

    def check_repository_sync_status(self, path: str) -> dict[str, any]:
        """Check if a repository is in sync with upstream.

        Args:
            path: Path to the repository

        Returns:
            Dictionary with sync status information
        """
        repository = GitRepository(path)
        status = repository.get_repository_status()

        if not status["is_git_repository"]:
            return {
                "path": path,
                "is_syncable": False,
                "error": "Not a valid Git repository",
                "behind_upstream": 0,
                "ahead_upstream": 0,
                "diverged": False,
            }

        try:
            # Check if upstream remote exists
            remotes = status["remotes"]
            if "upstream" not in remotes:
                return {
                    "path": path,
                    "is_syncable": False,
                    "error": "No upstream remote configured",
                    "behind_upstream": 0,
                    "ahead_upstream": 0,
                    "diverged": False,
                }

            # Get current branch
            current_branch = status["current_branch"]
            if not current_branch:
                return {
                    "path": path,
                    "is_syncable": False,
                    "error": "Could not determine current branch",
                    "behind_upstream": 0,
                    "ahead_upstream": 0,
                    "diverged": False,
                }

            # Check sync status with upstream
            result = repository._run_git_command(
                ["rev-list", "--count", f"{current_branch}..upstream/{current_branch}"],
                capture_output=True,
                text=True,
            )
            behind_upstream = (
                int(result.stdout.strip()) if result.returncode == 0 else 0
            )

            result = repository._run_git_command(
                ["rev-list", "--count", f"upstream/{current_branch}..{current_branch}"],
                capture_output=True,
                text=True,
            )
            ahead_upstream = int(result.stdout.strip()) if result.returncode == 0 else 0

            return {
                "path": path,
                "is_syncable": True,
                "behind_upstream": behind_upstream,
                "ahead_upstream": ahead_upstream,
                "diverged": behind_upstream > 0 and ahead_upstream > 0,
                "current_branch": current_branch,
                "has_uncommitted_changes": status["has_uncommitted_changes"],
                "has_untracked_files": status["has_untracked_files"],
            }

        except Exception as e:
            return {
                "path": path,
                "is_syncable": False,
                "error": str(e),
                "behind_upstream": 0,
                "ahead_upstream": 0,
                "diverged": False,
            }

    def setup_upstream_remote(self, path: str, upstream_url: str) -> bool:
        """Setup upstream remote for a repository.

        Args:
            path: Path to the repository
            upstream_url: URL of the upstream repository

        Returns:
            True if successful, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.add_upstream_remote(upstream_url)

        except Exception as e:
            self.logger.error(f"Error setting up upstream remote for {path}: {e}")
            return False

    def remove_upstream_remote(self, path: str) -> bool:
        """Remove upstream remote from a repository.

        Args:
            path: Path to the repository

        Returns:
            True if successful, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.remove_upstream_remote()

        except Exception as e:
            self.logger.error(f"Error removing upstream remote for {path}: {e}")
            return False

    def update_upstream_remote(self, path: str, upstream_url: str) -> bool:
        """Update upstream remote URL for a repository.

        Args:
            path: Path to the repository
            upstream_url: New URL for the upstream repository

        Returns:
            True if successful, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.update_upstream_remote(upstream_url)

        except Exception as e:
            self.logger.error(f"Error updating upstream remote for {path}: {e}")
            return False

    def validate_upstream_remote(self, path: str) -> dict[str, any]:
        """Validate upstream remote for a repository.

        Args:
            path: Path to the repository

        Returns:
            Dictionary with validation results.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                return {
                    "has_upstream": False,
                    "is_valid": False,
                    "error": "Not a valid Git repository",
                    "url": None,
                }

            return repository.validate_upstream_remote()

        except Exception as e:
            return {
                "has_upstream": False,
                "is_valid": False,
                "error": str(e),
                "url": None,
            }
