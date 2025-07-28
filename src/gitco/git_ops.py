"""Git operations and repository management for GitCo."""

import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable, Optional

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

    def validate_upstream_remote(self) -> dict[str, Any]:
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

    def merge_upstream_branch(self, branch: Optional[str] = None) -> dict[str, Any]:
        """Merge upstream branch into current branch.

        Args:
            branch: Branch to merge from upstream. Defaults to default branch.

        Returns:
            Dictionary with merge result information including conflict status.
        """
        try:
            # Get the branch to merge from
            if branch is None:
                branch = self.get_default_branch()
                if branch is None:
                    return {
                        "success": False,
                        "error": "Could not determine default branch",
                        "conflicts": [],
                        "merge_commit": None,
                    }

            # Check if we're on the correct branch
            current_branch = self.get_current_branch()
            if current_branch != branch:
                self.logger.warning(
                    f"Current branch ({current_branch}) differs from target branch ({branch})"
                )

            # Check if there are any uncommitted changes
            if self.has_uncommitted_changes():
                return {
                    "success": False,
                    "error": "Repository has uncommitted changes",
                    "conflicts": [],
                    "merge_commit": None,
                }

            # Check if merge is needed
            upstream_ref = f"upstream/{branch}"
            result = self._run_git_command(
                ["rev-list", "--count", f"HEAD..{upstream_ref}"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to check upstream status: {result.stderr}",
                    "conflicts": [],
                    "merge_commit": None,
                }

            commits_ahead = int(result.stdout.strip())
            if commits_ahead == 0:
                return {
                    "success": True,
                    "message": "Already up to date",
                    "conflicts": [],
                    "merge_commit": None,
                }

            self.logger.info(f"Merging {upstream_ref} into {current_branch}")
            result = self._run_git_command(
                ["merge", "--no-edit", upstream_ref], capture_output=True, text=True
            )

            if result.returncode == 0:
                # Get the merge commit hash
                merge_commit = self._get_last_commit_hash()
                return {
                    "success": True,
                    "message": f"Successfully merged {commits_ahead} commits",
                    "conflicts": [],
                    "merge_commit": merge_commit,
                }
            else:
                # Check for conflicts
                conflicts = self._detect_merge_conflicts()
                return {
                    "success": False,
                    "error": f"Merge failed: {result.stderr}",
                    "conflicts": conflicts,
                    "merge_commit": None,
                }

        except Exception as e:
            self.logger.error(f"Error merging upstream branch for {self.path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "conflicts": [],
                "merge_commit": None,
            }

    def _detect_merge_conflicts(self) -> list[str]:
        """Detect files with merge conflicts.

        Returns:
            List of conflicted file paths.
        """
        try:
            result = self._run_git_command(
                ["diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                return str(result.stdout.strip()).split("\n")
            return []

        except Exception as e:
            self.logger.debug(f"Error detecting merge conflicts for {self.path}: {e}")
            return []

    def _get_last_commit_hash(self) -> Optional[str]:
        """Get the hash of the last commit.

        Returns:
            Commit hash or None if error.
        """
        try:
            result = self._run_git_command(
                ["rev-parse", "HEAD"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return str(result.stdout.strip())
            return None
        except Exception as e:
            self.logger.debug(f"Error getting last commit hash for {self.path}: {e}")
            return None

    def abort_merge(self) -> bool:
        """Abort the current merge operation.

        Returns:
            True if successful, False otherwise.
        """
        try:
            result = self._run_git_command(["merge", "--abort"])
            if result.returncode == 0:
                self.logger.info("Successfully aborted merge")
                return True
            else:
                self.logger.error(f"Failed to abort merge: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Error aborting merge for {self.path}: {e}")
            return False

    def resolve_conflicts(self, strategy: str = "ours") -> bool:
        """Resolve merge conflicts using specified strategy.

        Args:
            strategy: Conflict resolution strategy ('ours', 'theirs', or 'manual').

        Returns:
            True if successful, False otherwise.
        """
        try:
            conflicts = self._detect_merge_conflicts()
            if not conflicts:
                self.logger.info("No conflicts to resolve")
                return True

            self.logger.info(
                f"Resolving {len(conflicts)} conflicts using {strategy} strategy"
            )

            if strategy == "ours":
                result = self._run_git_command(["checkout", "--ours", "--", "."])
            elif strategy == "theirs":
                result = self._run_git_command(["checkout", "--theirs", "--", "."])
            elif strategy == "manual":
                self.logger.info("Manual conflict resolution required")
                return True
            else:
                self.logger.error(f"Unknown conflict resolution strategy: {strategy}")
                return False

            if result.returncode == 0:
                # Add resolved files
                add_result = self._run_git_command(["add", "."])
                if add_result.returncode == 0:
                    self.logger.info("Successfully resolved conflicts")
                    return True
                else:
                    self.logger.error(
                        f"Failed to add resolved files: {add_result.stderr}"
                    )
                    return False
            else:
                self.logger.error(f"Failed to resolve conflicts: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error resolving conflicts for {self.path}: {e}")
            return False

    def get_merge_status(self) -> dict[str, Any]:
        """Get the current merge status.

        Returns:
            Dictionary with merge status information.
        """
        try:
            result = self._run_git_command(
                ["status", "--porcelain"], capture_output=True, text=True
            )

            if result.returncode != 0:
                return {"in_merge": False, "conflicts": [], "status": "unknown"}

            lines = result.stdout.strip().split("\n")
            conflicts = []
            in_merge = False

            for line in lines:
                if (
                    line.startswith("UU")
                    or line.startswith("AA")
                    or line.startswith("DD")
                ):
                    conflicts.append(line[3:])  # Remove status prefix
                    in_merge = True

            if in_merge:
                return {
                    "in_merge": True,
                    "conflicts": conflicts,
                    "status": "conflicted" if conflicts else "in_progress",
                }
            else:
                return {"in_merge": False, "conflicts": [], "status": "clean"}

        except Exception as e:
            self.logger.debug(f"Error getting merge status for {self.path}: {e}")
            return {"in_merge": False, "conflicts": [], "status": "unknown"}

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
                return str(result.stdout.strip())
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
                branch = str(result.stdout.strip()).split("/")[-1]
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

    def get_repository_status(self) -> dict[str, Any]:
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
        """Validate the repository and return any errors.

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
            errors.append(f"Not a valid Git repository: {self.path}")
            return errors

        # Check if repository has any remotes
        remotes = self.get_remote_urls()
        if not remotes:
            errors.append(f"No remotes configured for repository: {self.path}")

        return errors

    def has_uncommitted_changes(self) -> bool:
        """Check if the repository has uncommitted changes.

        Returns:
            True if there are uncommitted changes, False otherwise.
        """
        try:
            result = self._run_git_command(
                ["status", "--porcelain"], capture_output=True, text=True
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception as e:
            self.logger.debug(f"Error checking for uncommitted changes: {e}")
            return False

    def create_stash(
        self, message: str = "GitCo: Auto-stash before sync"
    ) -> Optional[str]:
        """Create a stash of current changes.

        Args:
            message: Stash message

        Returns:
            Stash reference (e.g., "stash@{0}") if successful, None otherwise.
        """
        try:
            if not self.has_uncommitted_changes():
                self.logger.debug(f"No uncommitted changes to stash in {self.path}")
                return None

            self.logger.info(f"Stashing changes in {self.path}")
            result = self._run_git_command(
                ["stash", "push", "-m", message], capture_output=True, text=True
            )

            if result.returncode == 0:
                # Extract stash reference from output
                output_lines = result.stdout.strip().split("\n")
                for line in output_lines:
                    if line.startswith("Saved working directory"):
                        # Extract stash reference like "stash@{0}"
                        match = re.search(r"stash@{(\d+)}", line)
                        if match:
                            stash_ref = f"stash@{{{match.group(1)}}}"
                            self.logger.info(
                                f"Successfully stashed changes: {stash_ref}"
                            )
                            return stash_ref

                # Fallback: return the most recent stash
                return "stash@{0}"
            else:
                self.logger.error(f"Failed to stash changes: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating stash in {self.path}: {e}")
            return None

    def apply_stash(self, stash_ref: str = "stash@{0}") -> bool:
        """Apply a stash to restore changes.

        Args:
            stash_ref: Stash reference to apply (default: most recent)

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.logger.info(f"Applying stash {stash_ref} in {self.path}")
            result = self._run_git_command(
                ["stash", "apply", stash_ref], capture_output=True, text=True
            )

            if result.returncode == 0:
                self.logger.info(f"Successfully applied stash {stash_ref}")
                return True
            else:
                self.logger.error(f"Failed to apply stash {stash_ref}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error applying stash {stash_ref} in {self.path}: {e}")
            return False

    def drop_stash(self, stash_ref: str = "stash@{0}") -> bool:
        """Drop a stash to remove it from the stash list.

        Args:
            stash_ref: Stash reference to drop (default: most recent)

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.logger.info(f"Dropping stash {stash_ref} in {self.path}")
            result = self._run_git_command(
                ["stash", "drop", stash_ref], capture_output=True, text=True
            )

            if result.returncode == 0:
                self.logger.info(f"Successfully dropped stash {stash_ref}")
                return True
            else:
                self.logger.error(f"Failed to drop stash {stash_ref}: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error dropping stash {stash_ref} in {self.path}: {e}")
            return False

    def list_stashes(self) -> list[dict[str, Any]]:
        """List all stashes in the repository.

        Returns:
            List of stash information dictionaries.
        """
        try:
            result = self._run_git_command(
                ["stash", "list", "--format=format:%H %T %s"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return []

            stashes = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(" ", 2)
                    if len(parts) >= 3:
                        stashes.append(
                            {
                                "hash": parts[0],
                                "timestamp": parts[1],
                                "message": parts[2],
                            }
                        )

            return stashes

        except Exception as e:
            self.logger.debug(f"Error listing stashes in {self.path}: {e}")
            return []

    def safe_stash_and_restore(
        self, operation_func: Callable[..., bool], *args: Any, **kwargs: Any
    ) -> tuple[bool, Optional[str]]:
        """Safely stash changes, run an operation, and restore changes.

        Args:
            operation_func: Function to run after stashing
            *args: Arguments to pass to operation_func
            **kwargs: Keyword arguments to pass to operation_func

        Returns:
            Tuple of (operation_success, stash_reference)
        """
        stash_ref = None
        operation_success = False

        try:
            # Check if we need to stash
            if self.has_uncommitted_changes():
                stash_ref = self.create_stash()
                if stash_ref is None:
                    self.logger.error(f"Failed to stash changes in {self.path}")
                    return False, None

            # Run the operation
            operation_success = operation_func(*args, **kwargs)

            # Restore stash if we created one
            if stash_ref and operation_success:
                if not self.apply_stash(stash_ref):
                    self.logger.warning(
                        f"Failed to restore stash {stash_ref} in {self.path}"
                    )
                    # Don't fail the operation if stash restore fails
                    # The changes are still in the stash

            return operation_success, stash_ref

        except Exception as e:
            self.logger.error(f"Error in safe stash and restore operation: {e}")

            # Try to restore stash even if operation failed
            if stash_ref:
                self.logger.info(
                    f"Attempting to restore stash {stash_ref} after operation failure"
                )
                self.apply_stash(stash_ref)

            return False, stash_ref

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

    def __init__(self) -> None:
        """Initialize GitRepositoryManager."""
        self.logger = get_logger()

    def detect_repositories(self, base_path: str) -> list[GitRepository]:
        """Detect Git repositories in a directory tree.

        Args:
            base_path: Base path to search for repositories

        Returns:
            List of GitRepository objects found
        """
        repositories: list[GitRepository] = []
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

    def get_repository_info(self, path: str) -> dict[str, Any]:
        """Get detailed information about a repository.

        Args:
            path: Path to the repository

        Returns:
            Dictionary with repository information
        """
        repository = GitRepository(path)
        return repository.get_repository_status()

    def validate_repository_config(self, config: dict[str, Any]) -> list[str]:
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

    def check_repository_sync_status(self, path: str) -> dict[str, Any]:
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

    def validate_upstream_remote(self, path: str) -> dict[str, Any]:
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

    def safe_stash_changes(
        self, path: str, message: str = "GitCo: Auto-stash before sync"
    ) -> Optional[str]:
        """Safely stash changes in a repository.

        Args:
            path: Path to the repository
            message: Stash message

        Returns:
            Stash reference if successful, None otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return None

            return repository.create_stash(message)

        except Exception as e:
            self.logger.error(f"Error stashing changes in {path}: {e}")
            return None

    def restore_stash(self, path: str, stash_ref: str = "stash@{0}") -> bool:
        """Restore a stash in a repository.

        Args:
            path: Path to the repository
            stash_ref: Stash reference to restore

        Returns:
            True if successful, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.apply_stash(stash_ref)

        except Exception as e:
            self.logger.error(f"Error restoring stash in {path}: {e}")
            return False

    def drop_stash(self, path: str, stash_ref: str = "stash@{0}") -> bool:
        """Drop a stash in a repository.

        Args:
            path: Path to the repository
            stash_ref: Stash reference to drop

        Returns:
            True if successful, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.drop_stash(stash_ref)

        except Exception as e:
            self.logger.error(f"Error dropping stash in {path}: {e}")
            return False

    def list_stashes(self, path: str) -> list[dict[str, Any]]:
        """List all stashes in a repository.

        Args:
            path: Path to the repository

        Returns:
            List of stash information dictionaries.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return []

            return repository.list_stashes()

        except Exception as e:
            self.logger.error(f"Error listing stashes in {path}: {e}")
            return []

    def has_uncommitted_changes(self, path: str) -> bool:
        """Check if a repository has uncommitted changes.

        Args:
            path: Path to the repository

        Returns:
            True if there are uncommitted changes, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.has_uncommitted_changes()

        except Exception as e:
            self.logger.error(f"Error checking for uncommitted changes in {path}: {e}")
            return False

    def safe_stash_and_restore(
        self, path: str, operation_func: Callable[..., bool], *args: Any, **kwargs: Any
    ) -> tuple[bool, Optional[str]]:
        """Safely stash changes, run an operation, and restore changes.

        Args:
            path: Path to the repository
            operation_func: Function to run after stashing
            *args: Arguments to pass to operation_func
            **kwargs: Keyword arguments to pass to operation_func

        Returns:
            Tuple of (operation_success, stash_reference)
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False, None

            return repository.safe_stash_and_restore(operation_func, *args, **kwargs)

        except Exception as e:
            self.logger.error(
                f"Error in safe stash and restore operation for {path}: {e}"
            )
            return False, None

    def fetch_upstream(self, path: str) -> bool:
        """Fetch latest changes from upstream for a repository.

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

            return repository.fetch_upstream()

        except Exception as e:
            self.logger.error(f"Error fetching upstream for {path}: {e}")
            return False

    def merge_upstream_branch(
        self, path: str, branch: Optional[str] = None
    ) -> dict[str, Any]:
        """Merge upstream branch into current branch for a repository.

        Args:
            path: Path to the repository
            branch: Branch to merge from upstream. Defaults to default branch.

        Returns:
            Dictionary with merge result information including conflict status.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return {
                    "success": False,
                    "error": "Not a valid Git repository",
                    "conflicts": [],
                    "merge_commit": None,
                }

            return repository.merge_upstream_branch(branch)

        except Exception as e:
            self.logger.error(f"Error merging upstream branch for {path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "conflicts": [],
                "merge_commit": None,
            }

    def abort_merge(self, path: str) -> bool:
        """Abort the current merge operation for a repository.

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

            return repository.abort_merge()

        except Exception as e:
            self.logger.error(f"Error aborting merge for {path}: {e}")
            return False

    def resolve_conflicts(self, path: str, strategy: str = "ours") -> bool:
        """Resolve merge conflicts using specified strategy for a repository.

        Args:
            path: Path to the repository
            strategy: Conflict resolution strategy ('ours', 'theirs', or 'manual').

        Returns:
            True if successful, False otherwise.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return False

            return repository.resolve_conflicts(strategy)

        except Exception as e:
            self.logger.error(f"Error resolving conflicts for {path}: {e}")
            return False

    def get_merge_status(self, path: str) -> dict[str, Any]:
        """Get the current merge status for a repository.

        Args:
            path: Path to the repository

        Returns:
            Dictionary with merge status information.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return {"in_merge": False, "conflicts": [], "status": "unknown"}

            return repository.get_merge_status()

        except Exception as e:
            self.logger.error(f"Error getting merge status for {path}: {e}")
            return {"in_merge": False, "conflicts": [], "status": "unknown"}

    def sync_repository_with_upstream(
        self, path: str, branch: Optional[str] = None
    ) -> dict[str, Any]:
        """Sync a repository with upstream changes including fetch and merge.

        Args:
            path: Path to the repository
            branch: Branch to sync. Defaults to default branch.

        Returns:
            Dictionary with sync result information.
        """
        try:
            repository = GitRepository(path)

            if not repository.is_git_repository():
                self.logger.error(f"Not a valid Git repository: {path}")
                return {
                    "success": False,
                    "error": "Not a valid Git repository",
                    "fetch_success": False,
                    "merge_success": False,
                    "conflicts": [],
                    "merge_commit": None,
                }

            # Step 1: Fetch from upstream
            self.logger.info(f"Fetching upstream changes for {path}")
            fetch_success = repository.fetch_upstream()

            if not fetch_success:
                return {
                    "success": False,
                    "error": "Failed to fetch from upstream",
                    "fetch_success": False,
                    "merge_success": False,
                    "conflicts": [],
                    "merge_commit": None,
                }

            # Step 2: Merge upstream branch
            self.logger.info(f"Merging upstream changes for {path}")
            merge_result = repository.merge_upstream_branch(branch)

            return {
                "success": merge_result["success"],
                "error": merge_result.get("error"),
                "fetch_success": True,
                "merge_success": merge_result["success"],
                "conflicts": merge_result.get("conflicts", []),
                "merge_commit": merge_result.get("merge_commit"),
                "message": merge_result.get("message"),
            }

        except Exception as e:
            self.logger.error(f"Error syncing repository with upstream for {path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "fetch_success": False,
                "merge_success": False,
                "conflicts": [],
                "merge_commit": None,
            }
