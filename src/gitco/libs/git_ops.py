"""Git operations and repository management for GitCo."""

import gc
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Optional

import psutil
from rich import box
from rich.table import Table

from ..utils.common import (
    console,
    create_progress_bar,
    get_logger,
)
from ..utils.exception import GitOperationError


@dataclass
class BatchResult:
    """Result of a batch operation on a repository."""

    repository_name: str
    repository_path: str
    success: bool
    operation: str
    message: str
    details: dict[str, Any]
    duration: float
    error: Optional[Exception] = None


@dataclass
class BatchPerformanceMetrics:
    """Performance metrics for batch processing."""

    total_repositories: int
    successful_operations: int
    failed_operations: int
    total_duration: float
    average_duration: float
    memory_usage_mb: float
    cpu_usage_percent: float
    throughput_repos_per_second: float
    concurrent_workers: int
    batch_size: int


class BatchProcessor:
    """Handles batch processing of multiple repositories with performance optimizations."""

    def __init__(self, max_workers: int = 4, rate_limit_delay: float = 1.0):
        """Initialize batch processor.

        Args:
            max_workers: Maximum number of concurrent workers
            rate_limit_delay: Delay between operations to respect rate limits
        """
        self.max_workers = max_workers
        self.rate_limit_delay = rate_limit_delay
        self.logger = get_logger()

        # Performance optimization attributes
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        self._repository_cache: dict[str, Any] = {}
        self._cache_lock = Lock()
        self._performance_metrics: Optional[BatchPerformanceMetrics] = None

        # Optimize batch size based on system resources
        self._optimal_batch_size = self._calculate_optimal_batch_size()

    def _calculate_optimal_batch_size(self) -> int:
        """Calculate optimal batch size based on system resources."""
        try:
            # Get system memory in GB
            memory_gb = psutil.virtual_memory().total / (1024**3)
            cpu_count = psutil.cpu_count()

            # Calculate optimal batch size based on available resources
            if memory_gb >= 16 and cpu_count >= 8:
                return min(50, self.max_workers * 4)
            elif memory_gb >= 8 and cpu_count >= 4:
                return min(30, self.max_workers * 3)
            else:
                return min(20, self.max_workers * 2)
        except Exception:
            # Fallback to conservative defaults
            return min(20, self.max_workers * 2)

    def _get_or_create_thread_pool(self) -> ThreadPoolExecutor:
        """Get or create a thread pool with connection reuse."""
        if self._thread_pool is None or self._thread_pool._shutdown:
            self._thread_pool = ThreadPoolExecutor(
                max_workers=self.max_workers, thread_name_prefix="gitco-batch"
            )
        return self._thread_pool

    def _get_cached_repository(self, repo_path: str) -> Optional[Any]:
        """Get cached repository object to avoid recreation."""
        with self._cache_lock:
            return self._repository_cache.get(repo_path)

    def _cache_repository(self, repo_path: str, repo_obj: Any) -> None:
        """Cache repository object for reuse."""
        with self._cache_lock:
            # Limit cache size to prevent memory issues
            if len(self._repository_cache) >= self._optimal_batch_size:
                # Remove oldest entries
                oldest_keys = list(self._repository_cache.keys())[:5]
                for key in oldest_keys:
                    del self._repository_cache[key]
            self._repository_cache[repo_path] = repo_obj

    def _clear_cache(self) -> None:
        """Clear the repository cache."""
        with self._cache_lock:
            self._repository_cache.clear()
        gc.collect()  # Force garbage collection

    def _monitor_performance(
        self, start_time: float, results: list[BatchResult]
    ) -> BatchPerformanceMetrics:
        """Monitor and calculate performance metrics."""
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        # Calculate memory usage
        memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)

        # Calculate CPU usage (approximate)
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Calculate throughput
        throughput = len(results) / total_duration if total_duration > 0 else 0

        return BatchPerformanceMetrics(
            total_repositories=len(results),
            successful_operations=successful,
            failed_operations=failed,
            total_duration=total_duration,
            average_duration=total_duration / len(results) if results else 0,
            memory_usage_mb=memory_mb,
            cpu_usage_percent=cpu_percent,
            throughput_repos_per_second=throughput,
            concurrent_workers=self.max_workers,
            batch_size=self._optimal_batch_size,
        )

    def process_repositories(
        self,
        repositories: list[dict[str, Any]],
        operation_func: Callable[[str, dict[str, Any]], dict[str, Any]],
        operation_name: str = "sync",
        show_progress: bool = True,
    ) -> list[BatchResult]:
        """Process multiple repositories in batch with performance optimizations.

        Args:
            repositories: List of repository configurations
            operation_func: Function to execute on each repository
            operation_name: Name of the operation for logging
            show_progress: Whether to show progress indicators

        Returns:
            List of batch results for each repository
        """
        self.logger.info(
            f"Starting optimized batch {operation_name} for {len(repositories)} repositories"
        )

        # Pre-allocate results list for better memory efficiency
        results = []
        start_time = time.time()

        # Handle empty repositories list
        if not repositories:
            self.logger.info(f"No repositories to process for {operation_name}")
            return []

        # Process repositories in optimal batch sizes
        batch_size = min(self._optimal_batch_size, len(repositories))

        if show_progress:
            self._print_batch_header(operation_name, len(repositories))

            # Create progress bar for batch processing
            with create_progress_bar(
                f"Processing {len(repositories)} repositories", len(repositories)
            ) as progress:
                task = progress.add_task(
                    f"[cyan]{operation_name}[/cyan]", total=len(repositories)
                )

                # Process repositories in batches for better memory management
                for i in range(0, len(repositories), batch_size):
                    batch = repositories[i : i + batch_size]

                    # Process current batch with thread pool
                    batch_results = self._process_batch(
                        batch, operation_func, operation_name, progress, task
                    )
                    results.extend(batch_results)

                    # Clear cache between batches to prevent memory buildup
                    if i + batch_size < len(repositories):
                        self._clear_cache()
        else:
            # Process without progress bar (for quiet mode)
            for i in range(0, len(repositories), batch_size):
                batch = repositories[i : i + batch_size]
                batch_results = self._process_batch_quiet(
                    batch, operation_func, operation_name
                )
                results.extend(batch_results)

                # Clear cache between batches
                if i + batch_size < len(repositories):
                    self._clear_cache()

        # Calculate performance metrics
        self._performance_metrics = self._monitor_performance(start_time, results)

        if show_progress:
            self._print_batch_summary(
                results, operation_name, self._performance_metrics.total_duration
            )
            self._print_performance_metrics(self._performance_metrics)

        # Clean up thread pool
        if self._thread_pool:
            self._thread_pool.shutdown(wait=False)
            self._thread_pool = None

        return results

    def _process_batch(
        self,
        batch: list[dict[str, Any]],
        operation_func: Callable[[str, dict[str, Any]], dict[str, Any]],
        operation_name: str,
        progress: Any,
        task: Any,
    ) -> list[BatchResult]:
        """Process a batch of repositories with progress tracking."""
        batch_results = []
        thread_pool = self._get_or_create_thread_pool()

        # Submit all tasks in the batch
        future_to_repo = {
            thread_pool.submit(
                self._process_single_repository,
                repo,
                operation_func,
                operation_name,
            ): repo
            for repo in batch
        }

        # Collect results as they complete
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                result = future.result()
                batch_results.append(result)

                # Update progress bar
                progress.update(task, advance=1)

                # Show result with color coding
                self._print_repository_result(result)

            except Exception as e:
                # Handle unexpected errors in the future
                error_result = BatchResult(
                    repository_name=repo.get("name", "unknown"),
                    repository_path=repo.get("local_path", "unknown"),
                    success=False,
                    operation=operation_name,
                    message=f"Unexpected error: {e}",
                    details={"error": str(e)},
                    duration=0.0,
                    error=e,
                )
                batch_results.append(error_result)

                # Update progress bar
                progress.update(task, advance=1)

                # Show error result
                self._print_repository_result(error_result)

        return batch_results

    def _process_batch_quiet(
        self,
        batch: list[dict[str, Any]],
        operation_func: Callable[[str, dict[str, Any]], dict[str, Any]],
        operation_name: str,
    ) -> list[BatchResult]:
        """Process a batch of repositories without progress tracking."""
        batch_results = []
        thread_pool = self._get_or_create_thread_pool()

        # Submit all tasks in the batch
        future_to_repo = {
            thread_pool.submit(
                self._process_single_repository,
                repo,
                operation_func,
                operation_name,
            ): repo
            for repo in batch
        }

        # Collect results as they complete
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                result = future.result()
                batch_results.append(result)
            except Exception as e:
                error_result = BatchResult(
                    repository_name=repo.get("name", "unknown"),
                    repository_path=repo.get("local_path", "unknown"),
                    success=False,
                    operation=operation_name,
                    message=f"Unexpected error: {e}",
                    details={"error": str(e)},
                    duration=0.0,
                    error=e,
                )
                batch_results.append(error_result)

        return batch_results

    def _process_single_repository(
        self,
        repo_config: dict[str, Any],
        operation_func: Callable[[str, dict[str, Any]], dict[str, Any]],
        operation_name: str,
    ) -> BatchResult:
        """Process a single repository with caching optimization.

        Args:
            repo_config: Repository configuration
            operation_func: Function to execute
            operation_name: Name of the operation

        Returns:
            Batch result for the repository
        """
        repo_name = repo_config.get("name", "unknown")
        repo_path = repo_config.get("local_path", "unknown")

        start_time = time.time()

        try:
            # Check if operation_func is callable
            if not callable(operation_func):
                duration = time.time() - start_time
                return BatchResult(
                    repository_name=repo_name,
                    repository_path=repo_path,
                    success=False,
                    operation=operation_name,
                    message="object is not callable",
                    details={"error": "Operation function is not callable"},
                    duration=duration,
                )

            # Execute the operation
            result = operation_func(repo_path, repo_config)

            duration = time.time() - start_time

            return BatchResult(
                repository_name=repo_name,
                repository_path=repo_path,
                success=result.get("success", False),
                operation=operation_name,
                message=result.get("message", "Operation completed"),
                details=result.get("details", {}),
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time

            return BatchResult(
                repository_name=repo_name,
                repository_path=repo_path,
                success=False,
                operation=operation_name,
                message=f"Operation failed: {e}",
                details={"error": str(e)},
                duration=duration,
                error=e,
            )

    def _print_batch_header(self, operation_name: str, total_repos: int) -> None:
        """Print batch processing header with rich formatting.

        Args:
            operation_name: Name of the operation
            total_repos: Total number of repositories to process
        """
        console.print(f"\n[bold blue]🔄 Batch {operation_name.title()}[/bold blue]")
        console.print(
            f"[dim]Processing {total_repos} repositories with {self.max_workers} workers[/dim]"
        )
        console.print(f"[dim]Optimal batch size: {self._optimal_batch_size}[/dim]\n")

    def _print_repository_result(self, result: BatchResult) -> None:
        """Print individual repository result with color coding.

        Args:
            result: Batch result to display
        """
        if result.success:
            console.print(
                f"✅ [green]{result.repository_name}[/green] - {result.message} "
                f"([dim]{result.duration:.2f}s[/dim])"
            )
        else:
            console.print(
                f"❌ [red]{result.repository_name}[/red] - {result.message} "
                f"([dim]{result.duration:.2f}s[/dim])"
            )

    def _print_batch_summary(
        self, results: list[BatchResult], operation_name: str, total_duration: float
    ) -> None:
        """Print batch processing summary with rich table.

        Args:
            results: List of batch results
            operation_name: Name of the operation
            total_duration: Total duration of the batch operation
        """
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        table = Table(
            title=f"Batch {operation_name.title()} Summary",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Repositories", str(len(results)))
        table.add_row("Successful", f"[green]{successful}[/green]")
        table.add_row("Failed", f"[red]{failed}[/red]")
        table.add_row("Success Rate", f"{(successful / len(results) * 100):.1f}%")
        table.add_row("Total Duration", f"{total_duration:.2f}s")
        table.add_row("Average Duration", f"{total_duration / len(results):.2f}s")

        console.print(table)

    def _print_performance_metrics(self, metrics: BatchPerformanceMetrics) -> None:
        """Print detailed performance metrics.

        Args:
            metrics: Performance metrics to display
        """
        table = Table(
            title="Performance Metrics",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold blue",
        )

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row(
            "Throughput", f"{metrics.throughput_repos_per_second:.2f} repos/sec"
        )
        table.add_row("Memory Usage", f"{metrics.memory_usage_mb:.1f} MB")
        table.add_row("CPU Usage", f"{metrics.cpu_usage_percent:.1f}%")
        table.add_row("Concurrent Workers", str(metrics.concurrent_workers))
        table.add_row("Batch Size", str(metrics.batch_size))

        console.print(table)

    def get_performance_metrics(self) -> Optional[BatchPerformanceMetrics]:
        """Get the last batch processing performance metrics.

        Returns:
            Performance metrics from the last batch operation, or None if no metrics available
        """
        return self._performance_metrics


class GitRepository:
    """Represents a Git repository with validation and status information."""

    def __init__(self, path: str):
        """Initialize GitRepository with path.

        Args:
            path: Path to the repository

        Raises:
            TypeError: If path is None or empty
        """
        if not path:
            raise TypeError("Repository path cannot be None or empty")
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
            # Health metrics fields
            "total_commits": 0,
            "recent_commits_30d": 0,
            "recent_commits_7d": 0,
            "total_contributors": 0,
            "active_contributors_30d": 0,
            "active_contributors_7d": 0,
            "last_commit_days_ago": None,
            "sync_status": "unknown",
            "last_sync": None,
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

        # Calculate health metrics
        try:
            self._calculate_health_metrics(status)
        except Exception as e:
            self.logger.debug(f"Error calculating health metrics for {self.path}: {e}")

        return status

    def _calculate_health_metrics(self, status: dict[str, Any]) -> None:
        """Calculate health metrics for the repository.

        Args:
            status: Status dictionary to update with health metrics
        """
        try:
            # Get total commit count
            result = self._run_git_command(
                ["rev-list", "--count", "HEAD"], capture_output=True, text=True
            )
            if result.returncode == 0:
                status["total_commits"] = int(result.stdout.strip())

            # Get recent commits (30 days)
            result = self._run_git_command(
                ["rev-list", "--count", "HEAD --since='30 days ago'"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                status["recent_commits_30d"] = int(result.stdout.strip())

            # Get recent commits (7 days)
            result = self._run_git_command(
                ["rev-list", "--count", "HEAD --since='7 days ago'"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                status["recent_commits_7d"] = int(result.stdout.strip())

            # Get last commit information
            result = self._run_git_command(
                ["log", "-1", "--format=%H %at"], capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                import time

                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    commit_time = int(parts[1])
                    days_ago = (time.time() - commit_time) / (24 * 3600)
                    status["last_commit_days_ago"] = int(days_ago)

            # Get contributor information (simplified)
            result = self._run_git_command(
                ["shortlog", "-sn", "--all"], capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                status["total_contributors"] = len(lines)

            # Get recent contributors (30 days)
            result = self._run_git_command(
                ["shortlog", "-sn", "--all", "--since='30 days ago'"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                status["active_contributors_30d"] = len(lines)

            # Get recent contributors (7 days)
            result = self._run_git_command(
                ["shortlog", "-sn", "--all", "--since='7 days ago'"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                status["active_contributors_7d"] = len(lines)

            # Determine sync status
            upstream_status = status.get("upstream_status", {})
            if upstream_status.get("valid", False):
                if upstream_status.get("behind", 0) > 0:
                    status["sync_status"] = "behind"
                elif upstream_status.get("ahead", 0) > 0:
                    status["sync_status"] = "ahead"
                elif upstream_status.get("diverged", False):
                    status["sync_status"] = "diverged"
                else:
                    status["sync_status"] = "up_to_date"
            else:
                status["sync_status"] = "unknown"

            # Set last sync time (simplified - use current time if up to date)
            if status["sync_status"] == "up_to_date":
                from datetime import datetime

                status["last_sync"] = datetime.now().isoformat()

        except Exception as e:
            self.logger.debug(f"Error calculating health metrics: {e}")

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

    def get_recent_changes(self, num_commits: int = 10) -> str:
        """Get recent changes as diff content.

        Args:
            num_commits: Number of recent commits to include in diff.

        Returns:
            Diff content as string, or empty string if no changes.
        """
        try:
            # Get the current branch
            current_branch = self.get_current_branch()
            if not current_branch:
                return ""

            # Get the upstream branch
            upstream_branch = self.get_default_branch()
            if not upstream_branch:
                return ""

            # First try to get diff between current branch and upstream
            result = self._run_git_command(
                ["diff", f"origin/{upstream_branch}..HEAD", "--stat"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout and result.stdout.strip():
                # Get detailed diff content for better analysis
                detailed_diff = self._get_detailed_diff(
                    f"origin/{upstream_branch}..HEAD"
                )
                if detailed_diff:
                    return f"{result.stdout}\n\nDetailed Changes:\n{detailed_diff}"
                return str(result.stdout)
            else:
                # Try to get recent commits diff
                result = self._run_git_command(
                    ["log", f"-{num_commits}", "--oneline", "--stat"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout:
                    # Get detailed diff for recent commits
                    detailed_diff = self._get_detailed_commit_diff(num_commits)
                    if detailed_diff:
                        return f"{result.stdout}\n\nDetailed Changes:\n{detailed_diff}"
                    return str(result.stdout)
                return ""

        except Exception as e:
            self.logger.warning(f"Failed to get recent changes: {e}")
            return ""

    def _get_detailed_diff(self, diff_range: str) -> str:
        """Get detailed diff content for analysis.

        Args:
            diff_range: Git diff range (e.g., "origin/main..HEAD").

        Returns:
            Detailed diff content as string.
        """
        try:
            # Get detailed diff with context
            result = self._run_git_command(
                ["diff", diff_range, "--unified=3", "--no-color"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout:
                # Limit the size to avoid overwhelming the AI
                diff_content = str(result.stdout)
                if len(diff_content) > 10000:  # Limit to 10KB
                    diff_content = diff_content[:10000] + "\n... (truncated)"
                return diff_content
            return ""

        except Exception as e:
            self.logger.warning(f"Failed to get detailed diff: {e}")
            return ""

    def _get_detailed_commit_diff(self, num_commits: int) -> str:
        """Get detailed diff for recent commits.

        Args:
            num_commits: Number of recent commits to analyze.

        Returns:
            Detailed diff content as string.
        """
        try:
            # Get the commit hashes for recent commits
            result = self._run_git_command(
                ["log", f"-{num_commits}", "--format=%H", "--no-merges"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0 or not result.stdout:
                return ""

            commit_hashes = [h.strip() for h in result.stdout.splitlines() if h.strip()]
            if not commit_hashes:
                return ""

            # Get detailed diff for each commit
            detailed_diffs = []
            for commit_hash in commit_hashes:
                diff_result = self._run_git_command(
                    ["show", commit_hash, "--unified=3", "--no-color", "--stat"],
                    capture_output=True,
                    text=True,
                )
                if diff_result.returncode == 0 and diff_result.stdout:
                    detailed_diffs.append(diff_result.stdout)

            if detailed_diffs:
                combined_diff = "\n\n".join(detailed_diffs)
                # Limit the size to avoid overwhelming the AI
                if len(combined_diff) > 10000:  # Limit to 10KB
                    combined_diff = combined_diff[:10000] + "\n... (truncated)"
                return combined_diff

            return ""

        except Exception as e:
            self.logger.warning(f"Failed to get detailed commit diff: {e}")
            return ""

    def get_commit_diff_analysis(self, commit_hash: str) -> dict[str, Any]:
        """Get detailed analysis of a specific commit.

        Args:
            commit_hash: Hash of the commit to analyze.

        Returns:
            Dictionary containing commit analysis information.
        """
        try:
            # Get commit information
            commit_info = self._get_commit_info(commit_hash)
            if not commit_info:
                return {}

            # Get detailed diff for the commit
            diff_result = self._run_git_command(
                ["show", commit_hash, "--unified=3", "--no-color", "--stat"],
                capture_output=True,
                text=True,
            )

            diff_content = ""
            if diff_result.returncode == 0 and diff_result.stdout:
                diff_content = diff_result.stdout

            # Get files changed
            files_result = self._run_git_command(
                ["show", "--name-only", "--format=", commit_hash],
                capture_output=True,
                text=True,
            )

            files_changed = []
            if files_result.returncode == 0 and files_result.stdout:
                files_changed = [
                    f.strip() for f in files_result.stdout.splitlines() if f.strip()
                ]

            return {
                "commit_hash": commit_hash,
                "author": commit_info.get("author", ""),
                "date": commit_info.get("date", ""),
                "message": commit_info.get("message", ""),
                "diff_content": diff_content,
                "files_changed": files_changed,
                "insertions": commit_info.get("insertions", 0),
                "deletions": commit_info.get("deletions", 0),
            }

        except Exception as e:
            self.logger.warning(f"Failed to analyze commit {commit_hash}: {e}")
            return {}

    def _get_commit_info(self, commit_hash: str) -> dict[str, Any]:
        """Get detailed information about a commit.

        Args:
            commit_hash: Hash of the commit.

        Returns:
            Dictionary containing commit information.
        """
        try:
            # Get commit details
            result = self._run_git_command(
                [
                    "show",
                    commit_hash,
                    "--format=author:%an%nauthor-date:%ai%nsubject:%s%nbody:%b",
                    "--stat",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0 or not result.stdout:
                return {}

            lines = result.stdout.splitlines()
            info: dict[str, Any] = {}

            for line in lines:
                if line.startswith("author:"):
                    info["author"] = line[7:]
                elif line.startswith("author-date:"):
                    info["date"] = line[12:]
                elif line.startswith("subject:"):
                    info["message"] = line[8:]
                elif "files changed" in line:
                    # Parse stat line like " 2 files changed, 4 insertions(+), 2 deletions(-)"
                    parts = line.split(",")
                    if len(parts) >= 3:
                        try:
                            insertions = int(parts[1].split()[0])
                            deletions = int(parts[2].split()[0])
                            info["insertions"] = insertions
                            info["deletions"] = deletions
                        except (ValueError, IndexError):
                            pass

            return info

        except Exception as e:
            self.logger.warning(f"Failed to get commit info for {commit_hash}: {e}")
            return {}

    def get_recent_commit_messages(self, num_commits: int = 10) -> list[str]:
        """Get recent commit messages.

        Args:
            num_commits: Number of recent commits to retrieve.

        Returns:
            List of commit messages.
        """
        try:
            result = self._run_git_command(
                ["log", f"-{num_commits}", "--oneline", "--no-merges"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                return [
                    line.strip() for line in result.stdout.splitlines() if line.strip()
                ]
            else:
                return []

        except Exception as e:
            self.logger.warning(f"Failed to get recent commit messages: {e}")
            return []

    def get_recent_commits(self, num_commits: int = 10) -> str:
        """Get recent commits information.

        Args:
            num_commits: Number of recent commits to get

        Returns:
            String representation of recent commits
        """
        try:
            result = self._run_git_command(
                ["log", f"-{num_commits}", "--oneline"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()  # type: ignore
            return ""
        except Exception as e:
            self.logger.debug(f"Error getting recent commits: {e}")
            return ""

    def get_commit_diff(self, commit_hash: str) -> str:
        """Get diff for a specific commit.

        Args:
            commit_hash: Commit hash

        Returns:
            Diff content
        """
        try:
            result = self._run_git_command(
                ["show", commit_hash], capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()  # type: ignore
            return ""
        except Exception as e:
            self.logger.debug(f"Error getting commit diff: {e}")
            return ""

    def get_commit_info(self, commit_hash: str) -> dict[str, Any]:
        """Get information about a specific commit.

        Args:
            commit_hash: Commit hash

        Returns:
            Dictionary with commit information
        """
        if not commit_hash:
            return {"hash": None, "info": ""}

        try:
            result = self._run_git_command(
                ["show", "--format=fuller", "--no-patch", commit_hash],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return {"hash": commit_hash, "info": result.stdout.strip()}
            return {"hash": commit_hash, "info": ""}
        except Exception as e:
            self.logger.debug(f"Error getting commit info: {e}")
            return {"hash": commit_hash, "info": ""}

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
                timeout=60,  # 60 second timeout for git operations
            )

            return result
        except subprocess.TimeoutExpired as e:
            raise GitOperationError(
                f"Git command timed out after {e.timeout}s: {' '.join(args)}"
            ) from None
        except Exception as e:
            raise GitOperationError(
                f"Failed to run Git command {' '.join(args)}: {e}"
            ) from e


class GitRepositoryManager:
    """Manages multiple Git repositories."""

    def __init__(self) -> None:
        """Initialize GitRepositoryManager."""
        self.logger = get_logger()
        self.batch_processor = BatchProcessor()

    def batch_sync_repositories(
        self,
        repositories: list[dict[str, Any]],
        max_workers: int = 4,
        show_progress: bool = True,
    ) -> list[BatchResult]:
        """Synchronize multiple repositories in batch.

        Args:
            repositories: List of repository configurations
            max_workers: Maximum number of concurrent workers
            show_progress: Whether to show progress indicators

        Returns:
            List of batch results for each repository
        """
        self.batch_processor.max_workers = max_workers

        return self.batch_processor.process_repositories(
            repositories=repositories,
            operation_func=self._sync_single_repository,
            operation_name="sync",
            show_progress=show_progress,
        )

    def batch_fetch_repositories(
        self,
        repositories: list[dict[str, Any]],
        max_workers: int = 4,
        show_progress: bool = True,
    ) -> list[BatchResult]:
        """Fetch updates for multiple repositories in batch.

        Args:
            repositories: List of repository configurations
            max_workers: Maximum number of concurrent workers
            show_progress: Whether to show progress indicators

        Returns:
            List of batch results for each repository
        """
        self.batch_processor.max_workers = max_workers

        return self.batch_processor.process_repositories(
            repositories=repositories,
            operation_func=self._fetch_single_repository,
            operation_name="fetch",
            show_progress=show_progress,
        )

    def batch_validate_repositories(
        self,
        repositories: list[dict[str, Any]],
        max_workers: int = 4,
        show_progress: bool = True,
    ) -> list[BatchResult]:
        """Validate multiple repositories in batch.

        Args:
            repositories: List of repository configurations
            max_workers: Maximum number of concurrent workers
            show_progress: Whether to show progress indicators

        Returns:
            List of batch results for each repository
        """
        self.batch_processor.max_workers = max_workers

        return self.batch_processor.process_repositories(
            repositories=repositories,
            operation_func=self._validate_single_repository,
            operation_name="validate",
            show_progress=show_progress,
        )

    def _sync_single_repository(
        self, repo_path: str, repo_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Synchronize a single repository with upstream with error recovery.

        Args:
            repo_path: Path to the repository
            repo_config: Repository configuration

        Returns:
            Dictionary with sync result information
        """
        logger = get_logger()
        repo_name = repo_config.get("name", Path(repo_path).name)

        try:
            logger.info(f"Starting sync for repository: {repo_name}")

            # Step 1: Validate repository first
            is_valid, errors = self.validate_repository_path(repo_path)
            if not is_valid:
                logger.error(
                    f"Repository validation failed for {repo_name}: {', '.join(errors)}"
                )
                return {
                    "success": False,
                    "message": f"Repository validation failed: {', '.join(errors)}",
                    "errors": errors,
                    "recovery_attempted": False,
                }

            # Step 2: Check for uncommitted changes and stash if needed
            has_changes = self.has_uncommitted_changes(repo_path)
            stash_ref = None

            if has_changes:
                logger.info(f"Found uncommitted changes in {repo_name}, stashing...")
                stash_ref = self.safe_stash_changes(repo_path)
                if not stash_ref:
                    logger.error(f"Failed to stash changes for {repo_name}")
                    return {
                        "success": False,
                        "message": "Failed to stash uncommitted changes",
                        "recovery_attempted": False,
                    }
                logger.info(f"Successfully stashed changes for {repo_name}")

            # Step 3: Perform sync operation with retry mechanism
            sync_result = self._sync_with_retry(repo_path, repo_name)

            # Step 4: Restore stashed changes if any
            if stash_ref:
                logger.info(f"Restoring stashed changes for {repo_name}")
                restore_success = self.restore_stash(repo_path, stash_ref)
                if not restore_success:
                    logger.warning(f"Failed to restore stashed changes for {repo_name}")
                    # Don't fail the entire operation if stash restore fails
                    sync_result["stash_restore_failed"] = True

            return {
                "success": sync_result.get("success", False),
                "message": sync_result.get("message", "Sync completed"),
                "details": sync_result,
                "stashed_changes": stash_ref is not None,
                "recovery_attempted": sync_result.get("recovery_attempted", False),
                "retry_count": sync_result.get("retry_count", 0),
            }

        except Exception as e:
            logger.error(f"Unexpected error during sync for {repo_name}: {e}")
            return {
                "success": False,
                "message": f"Error during sync: {str(e)}",
                "error": str(e),
                "recovery_attempted": False,
            }

    def _sync_with_retry(
        self, repo_path: str, repo_name: str, max_retries: int = 3
    ) -> dict[str, Any]:
        """Sync repository with retry mechanism for network operations.

        Args:
            repo_path: Path to the repository
            repo_name: Name of the repository
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with sync result information
        """
        logger = get_logger()

        for attempt in range(max_retries + 1):
            try:
                logger.info(
                    f"Sync attempt {attempt + 1}/{max_retries + 1} for {repo_name}"
                )

                # Perform the sync operation
                sync_result = self.sync_repository_with_upstream(repo_path)

                if sync_result["success"]:
                    logger.info(
                        f"Sync successful for {repo_name} on attempt {attempt + 1}"
                    )
                    sync_result["retry_count"] = attempt
                    sync_result["recovery_attempted"] = attempt > 0
                    return sync_result

                # If sync failed, check if it's a recoverable error
                error = sync_result.get("error", "")
                if self._is_recoverable_error(error):
                    if attempt < max_retries:
                        logger.warning(f"Recoverable error for {repo_name}: {error}")
                        logger.info(f"Retrying sync for {repo_name} in 2 seconds...")
                        time.sleep(2)  # Brief delay before retry
                        continue
                    else:
                        logger.error(f"Max retries reached for {repo_name}: {error}")
                        sync_result["retry_count"] = attempt
                        sync_result["recovery_attempted"] = True
                        return sync_result
                else:
                    # Non-recoverable error, don't retry
                    logger.error(f"Non-recoverable error for {repo_name}: {error}")
                    sync_result["retry_count"] = attempt
                    sync_result["recovery_attempted"] = False
                    return sync_result

            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Exception during sync for {repo_name}: {e}")
                    logger.info(f"Retrying sync for {repo_name} in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(
                        f"Max retries reached for {repo_name} due to exception: {e}"
                    )
                    return {
                        "success": False,
                        "error": str(e),
                        "retry_count": attempt,
                        "recovery_attempted": True,
                    }

        # This should never be reached, but just in case
        return {
            "success": False,
            "error": "Max retries exceeded",
            "retry_count": max_retries,
            "recovery_attempted": True,
        }

    def _is_recoverable_error(self, error: str) -> bool:
        """Check if an error is recoverable and should trigger a retry.

        Args:
            error: Error message to check

        Returns:
            True if the error is recoverable, False otherwise
        """
        recoverable_patterns = [
            "network is unreachable",
            "connection refused",
            "timeout",
            "temporary failure",
            "rate limit",
            "too many requests",
            "service unavailable",
            "bad gateway",
            "gateway timeout",
            "internal server error",
        ]

        error_lower = error.lower()
        return any(pattern in error_lower for pattern in recoverable_patterns)

    def _fetch_single_repository(
        self, repo_path: str, repo_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Fetch updates for a single repository.

        Args:
            repo_path: Path to the repository
            repo_config: Repository configuration

        Returns:
            Dictionary with fetch result information
        """
        try:
            # Validate repository first
            is_valid, errors = self.validate_repository_path(repo_path)
            if not is_valid:
                return {
                    "success": False,
                    "message": f"Repository validation failed: {', '.join(errors)}",
                    "errors": errors,
                }

            # Fetch upstream changes
            fetch_success = self.fetch_upstream(repo_path)

            if fetch_success:
                return {
                    "success": True,
                    "message": "Successfully fetched upstream changes",
                }
            else:
                return {"success": False, "message": "Failed to fetch upstream changes"}

        except Exception as e:
            return {
                "success": False,
                "message": f"Error during fetch: {str(e)}",
                "error": str(e),
            }

    def _validate_single_repository(
        self, repo_path: str, repo_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate a single repository.

        Args:
            repo_path: Path to the repository
            repo_config: Repository configuration

        Returns:
            Dictionary with validation result information
        """
        try:
            # Validate repository path
            is_valid, errors = self.validate_repository_path(repo_path)

            if not is_valid:
                return {
                    "success": False,
                    "message": f"Repository validation failed: {', '.join(errors)}",
                    "errors": errors,
                }

            # Get repository info
            repo_info = self.get_repository_info(repo_path)

            return {
                "success": True,
                "message": "Repository validation passed",
                "details": repo_info,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error during validation: {str(e)}",
                "error": str(e),
            }

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

    def sync_repository(self, path: str) -> dict[str, Any]:
        """Sync a single repository.

        Args:
            path: Repository path

        Returns:
            Dictionary with sync results
        """
        try:
            repo = GitRepository(path)
            return repo.merge_upstream_branch()
        except Exception as e:
            self.logger.error(f"Failed to sync repository {path}: {e}")
            return {"success": False, "error": str(e)}

    def fetch_repository(self, path: str) -> dict[str, Any]:
        """Fetch updates for a single repository.

        Args:
            path: Repository path

        Returns:
            Dictionary with fetch results
        """
        try:
            repo = GitRepository(path)
            success = repo.fetch_upstream()
            return {"success": success, "error": None if success else "Fetch failed"}
        except Exception as e:
            self.logger.error(f"Failed to fetch repository {path}: {e}")
            return {"success": False, "error": str(e)}

    def validate_repository(self, path: str) -> dict[str, Any]:
        """Validate a single repository.

        Args:
            path: Repository path

        Returns:
            Dictionary with validation results
        """
        try:
            repo = GitRepository(path)
            return repo.validate_upstream_remote()
        except Exception as e:
            self.logger.error(f"Failed to validate repository {path}: {e}")
            return {"success": False, "error": str(e)}

    def get_repository(self, path: str) -> GitRepository:
        """Get a GitRepository instance for a path.

        Args:
            path: Repository path

        Returns:
            GitRepository instance
        """
        return GitRepository(path)
