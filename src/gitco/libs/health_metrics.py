"""Repository health metrics calculation for GitCo."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..utils.common import (
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)
from ..utils.exception import HealthMetricsError
from .config import Config
from .git_ops import GitRepository
from .github_client import GitHubClient


@dataclass
class RepositoryHealthMetrics:
    """Health metrics for a single repository."""

    repository_name: str
    repository_path: str
    upstream_url: Optional[str] = None

    # Activity metrics
    last_commit_days_ago: Optional[int] = None
    total_commits: int = 0
    recent_commits_30d: int = 0
    recent_commits_7d: int = 0

    # Contributor metrics
    total_contributors: int = 0
    active_contributors_30d: int = 0
    active_contributors_7d: int = 0

    # GitHub metrics
    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    open_prs_count: int = 0

    # Sync health
    days_since_last_sync: Optional[int] = None
    sync_status: str = "unknown"  # "up_to_date", "behind", "ahead", "diverged"
    uncommitted_changes: bool = False

    # Engagement metrics
    issue_response_time_avg: Optional[float] = None  # hours
    pr_merge_time_avg: Optional[float] = None  # hours
    contributor_engagement_score: float = 0.0  # 0.0-1.0

    # Trending metrics
    stars_growth_30d: int = 0
    forks_growth_30d: int = 0
    issues_growth_30d: int = 0

    # Health score
    overall_health_score: float = 0.0  # 0.0-1.0
    health_status: str = "unknown"  # "excellent", "good", "fair", "poor", "critical"

    # Additional metadata
    language: Optional[str] = None
    topics: list[str] = field(default_factory=list)
    archived: bool = False
    disabled: bool = False


@dataclass
class HealthSummary:
    """Summary of health metrics across all repositories."""

    total_repositories: int = 0
    healthy_repositories: int = 0
    needs_attention_repositories: int = 0
    critical_repositories: int = 0

    # Activity summary
    active_repositories_7d: int = 0
    active_repositories_30d: int = 0
    average_activity_score: float = 0.0

    # Trending repositories
    trending_repositories: list[str] = field(default_factory=list)
    declining_repositories: list[str] = field(default_factory=list)

    # Sync status summary
    up_to_date_repositories: int = 0
    behind_repositories: int = 0
    diverged_repositories: int = 0

    # Engagement summary
    high_engagement_repositories: int = 0
    low_engagement_repositories: int = 0

    # Repository metrics
    total_stars: int = 0
    total_forks: int = 0
    total_open_issues: int = 0


class RepositoryHealthCalculator:
    """Calculates comprehensive health metrics for repositories."""

    def __init__(self, config: Config, github_client: GitHubClient):
        """Initialize health calculator.

        Args:
            config: GitCo configuration
            github_client: GitHub API client
        """
        self.config = config
        self.github_client = github_client
        self.logger = get_logger()

    def calculate_repository_health(
        self, repository_config: dict[str, Any]
    ) -> RepositoryHealthMetrics:
        """Calculate health metrics for a single repository.

        Args:
            repository_config: Repository configuration

        Returns:
            Repository health metrics
        """
        repo_name = repository_config.get("name", "unknown")
        repo_path = repository_config.get("local_path", "")

        log_operation_start("calculating repository health", repository=repo_name)

        try:
            metrics = RepositoryHealthMetrics(
                repository_name=repo_name,
                repository_path=repo_path,
                upstream_url=repository_config.get("upstream"),
            )

            # Get local repository information
            if repo_path and Path(repo_path).exists():
                git_repo = GitRepository(repo_path)
                self._calculate_local_metrics(git_repo, metrics)

            # Get GitHub repository information
            if repository_config.get("upstream"):
                self._calculate_github_metrics(repository_config, metrics)

            # Calculate derived metrics
            self._calculate_derived_metrics(metrics)

            log_operation_success(
                "calculating repository health",
                repository=repo_name,
                health_score=metrics.overall_health_score,
            )

            return metrics

        except Exception as e:
            log_operation_failure(
                "calculating repository health",
                repository=repo_name,
                error=e,
            )
            raise HealthMetricsError(
                f"Failed to calculate health for {repo_name}: {e}"
            ) from e

    def calculate_health_summary(
        self, repositories: list[dict[str, Any]]
    ) -> HealthSummary:
        """Calculate health summary across all repositories.

        Args:
            repositories: List of repository configurations

        Returns:
            Health summary
        """
        log_operation_start(
            "calculating health summary", repositories_count=len(repositories)
        )

        try:
            summary = HealthSummary(total_repositories=len(repositories))
            repository_metrics = []

            # Calculate metrics for each repository
            for repo_config in repositories:
                metrics = self.calculate_repository_health(repo_config)
                repository_metrics.append(metrics)

                # Update summary counters
                self._update_summary_counters(summary, metrics)

            # Calculate trending repositories
            summary.trending_repositories = self._identify_trending_repositories(
                repository_metrics
            )
            summary.declining_repositories = self._identify_declining_repositories(
                repository_metrics
            )

            # Calculate averages
            if repository_metrics:
                summary.average_activity_score = sum(
                    m.overall_health_score for m in repository_metrics
                ) / len(repository_metrics)

            log_operation_success(
                "calculating health summary",
                healthy_repositories=summary.healthy_repositories,
                needs_attention=summary.needs_attention_repositories,
            )

            return summary

        except Exception as e:
            log_operation_failure("calculating health summary", error=e)
            raise HealthMetricsError(f"Failed to calculate health summary: {e}") from e

    def _calculate_local_metrics(
        self, git_repo: GitRepository, metrics: RepositoryHealthMetrics
    ) -> None:
        """Calculate metrics from local git repository.

        Args:
            git_repo: Git repository instance
            metrics: Metrics object to update
        """
        try:
            # Get repository status
            status = git_repo.get_repository_status()

            # Calculate sync status
            if "last_sync" in status:
                last_sync = datetime.fromisoformat(status["last_sync"])
                metrics.days_since_last_sync = (datetime.now() - last_sync).days

            # Determine sync status
            if "sync_status" in status:
                metrics.sync_status = status["sync_status"]

            # Check for uncommitted changes
            metrics.uncommitted_changes = git_repo.has_uncommitted_changes()

            # Get commit statistics
            if "total_commits" in status:
                metrics.total_commits = status["total_commits"]

            if "recent_commits_30d" in status:
                metrics.recent_commits_30d = status["recent_commits_30d"]

            if "recent_commits_7d" in status:
                metrics.recent_commits_7d = status["recent_commits_7d"]

            # Get contributor information
            if "total_contributors" in status:
                metrics.total_contributors = status["total_contributors"]

            if "active_contributors_30d" in status:
                metrics.active_contributors_30d = status["active_contributors_30d"]

            if "active_contributors_7d" in status:
                metrics.active_contributors_7d = status["active_contributors_7d"]

            # Get last commit information
            if "last_commit_days_ago" in status:
                metrics.last_commit_days_ago = status["last_commit_days_ago"]

        except Exception as e:
            self.logger.warning(f"Failed to calculate local metrics: {e}")

    def _calculate_github_metrics(
        self, repository_config: dict[str, Any], metrics: RepositoryHealthMetrics
    ) -> None:
        """Calculate metrics from GitHub API.

        Args:
            repository_config: Repository configuration
            metrics: Metrics object to update
        """
        try:
            upstream_url = repository_config.get("upstream")
            if not upstream_url:
                return

            # Extract repository name from upstream URL
            repo_name = self._extract_repo_name_from_url(upstream_url)
            if not repo_name:
                return

            # Get repository information from GitHub
            github_repo = self.github_client.get_repository(repo_name)
            if not github_repo:
                return

            # Update metrics with GitHub data
            metrics.stars_count = github_repo.stargazers_count
            metrics.forks_count = github_repo.forks_count
            metrics.open_issues_count = github_repo.open_issues_count
            metrics.language = github_repo.language
            metrics.topics = github_repo.topics or []
            metrics.archived = github_repo.archived
            metrics.disabled = github_repo.disabled

            # Calculate engagement metrics
            self._calculate_engagement_metrics(repo_name, metrics)

            # Calculate trending metrics
            self._calculate_trending_metrics(repo_name, metrics)

        except Exception as e:
            self.logger.warning(f"Failed to calculate GitHub metrics: {e}")

    def _calculate_engagement_metrics(
        self, repo_name: str, metrics: RepositoryHealthMetrics
    ) -> None:
        """Calculate engagement metrics for a repository.

        Args:
            repo_name: Repository name
            metrics: Metrics object to update
        """
        try:
            # Get recent issues for response time calculation
            recent_issues = self.github_client.get_issues(
                repo_name, state="all", limit=50
            )

            if recent_issues:
                response_times = []
                for issue in recent_issues:
                    if issue.comments_count > 0:
                        # Calculate time to first response
                        # This is a simplified calculation
                        response_times.append(issue.comments_count)

                if response_times:
                    metrics.issue_response_time_avg = sum(response_times) / len(
                        response_times
                    )

            # Calculate contributor engagement score
            engagement_factors = []

            # Factor 1: Recent activity
            if metrics.recent_commits_7d > 0:
                engagement_factors.append(min(metrics.recent_commits_7d / 10.0, 1.0))

            # Factor 2: Active contributors
            if metrics.total_contributors > 0:
                active_ratio = (
                    metrics.active_contributors_7d / metrics.total_contributors
                )
                engagement_factors.append(min(active_ratio, 1.0))

            # Factor 3: Issue engagement
            if metrics.open_issues_count > 0:
                engagement_factors.append(min(metrics.open_issues_count / 100.0, 1.0))

            # Factor 4: Star growth
            if metrics.stars_growth_30d > 0:
                engagement_factors.append(min(metrics.stars_growth_30d / 50.0, 1.0))

            if engagement_factors:
                metrics.contributor_engagement_score = sum(engagement_factors) / len(
                    engagement_factors
                )

        except Exception as e:
            self.logger.warning(f"Failed to calculate engagement metrics: {e}")

    def _calculate_trending_metrics(
        self, repo_name: str, metrics: RepositoryHealthMetrics
    ) -> None:
        """Calculate trending metrics for a repository.

        Args:
            repo_name: Repository name
            metrics: Metrics object to update
        """
        try:
            # This is a simplified calculation
            # In a real implementation, you would fetch historical data
            # For now, we'll use current metrics as trending indicators

            # Stars growth (simplified)
            metrics.stars_growth_30d = max(0, metrics.stars_count // 100)

            # Forks growth (simplified)
            metrics.forks_growth_30d = max(0, metrics.forks_count // 50)

            # Issues growth (simplified)
            metrics.issues_growth_30d = max(0, metrics.open_issues_count // 10)

        except Exception as e:
            self.logger.warning(f"Failed to calculate trending metrics: {e}")

    def _calculate_derived_metrics(self, metrics: RepositoryHealthMetrics) -> None:
        """Calculate derived metrics and health score.

        Args:
            metrics: Metrics object to update
        """
        try:
            health_factors = []

            # Factor 1: Recent activity (30%)
            if metrics.recent_commits_30d > 0:
                activity_score = min(metrics.recent_commits_30d / 20.0, 1.0)
                health_factors.append(("activity", activity_score, 0.3))

            # Factor 2: Sync status (25%)
            sync_score = 1.0
            if metrics.sync_status == "up_to_date":
                sync_score = 1.0
            elif metrics.sync_status == "behind":
                sync_score = 0.7
            elif metrics.sync_status == "ahead":
                sync_score = 0.8
            elif metrics.sync_status == "diverged":
                sync_score = 0.3
            else:
                sync_score = 0.5

            health_factors.append(("sync", sync_score, 0.25))

            # Factor 3: Contributor engagement (20%)
            health_factors.append(
                ("engagement", metrics.contributor_engagement_score, 0.2)
            )

            # Factor 4: GitHub metrics (15%)
            github_score = 0.0
            if metrics.stars_count > 0:
                github_score += min(metrics.stars_count / 1000.0, 1.0) * 0.5
            if metrics.forks_count > 0:
                github_score += min(metrics.forks_count / 500.0, 1.0) * 0.5
            health_factors.append(("github", github_score, 0.15))

            # Factor 5: Repository age and stability (10%)
            stability_score = 1.0
            if metrics.last_commit_days_ago is not None:
                if metrics.last_commit_days_ago <= 7:
                    stability_score = 1.0
                elif metrics.last_commit_days_ago <= 30:
                    stability_score = 0.8
                elif metrics.last_commit_days_ago <= 90:
                    stability_score = 0.6
                else:
                    stability_score = 0.3
            health_factors.append(("stability", stability_score, 0.1))

            # Calculate weighted overall health score
            total_score = 0.0
            total_weight = 0.0

            for _factor_name, score, weight in health_factors:
                total_score += score * weight
                total_weight += weight

            if total_weight > 0:
                metrics.overall_health_score = total_score / total_weight
            else:
                metrics.overall_health_score = 0.0

            # Determine health status
            if metrics.overall_health_score >= 0.8:
                metrics.health_status = "excellent"
            elif metrics.overall_health_score >= 0.6:
                metrics.health_status = "good"
            elif metrics.overall_health_score >= 0.4:
                metrics.health_status = "fair"
            elif metrics.overall_health_score >= 0.2:
                metrics.health_status = "poor"
            else:
                metrics.health_status = "critical"

        except Exception as e:
            self.logger.warning(f"Failed to calculate derived metrics: {e}")

    def _update_summary_counters(
        self, summary: HealthSummary, metrics: RepositoryHealthMetrics
    ) -> None:
        """Update summary counters with repository metrics.

        Args:
            summary: Health summary to update
            metrics: Repository metrics
        """
        # Health status counters
        if metrics.health_status == "excellent" or metrics.health_status == "good":
            summary.healthy_repositories += 1
        elif metrics.health_status == "fair":
            summary.needs_attention_repositories += 1
        elif metrics.health_status == "poor" or metrics.health_status == "critical":
            summary.critical_repositories += 1

        # Activity counters
        if metrics.recent_commits_7d > 0:
            summary.active_repositories_7d += 1
        if metrics.recent_commits_30d > 0:
            summary.active_repositories_30d += 1

        # Sync status counters
        if metrics.sync_status == "up_to_date":
            summary.up_to_date_repositories += 1
        elif metrics.sync_status == "behind":
            summary.behind_repositories += 1
        elif metrics.sync_status == "diverged":
            summary.diverged_repositories += 1

        # Engagement counters
        if metrics.contributor_engagement_score >= 0.7:
            summary.high_engagement_repositories += 1
        elif metrics.contributor_engagement_score <= 0.3:
            summary.low_engagement_repositories += 1

        # Repository metrics
        summary.total_stars += metrics.stars_count
        summary.total_forks += metrics.forks_count
        summary.total_open_issues += metrics.open_issues_count

    def _identify_trending_repositories(
        self, repository_metrics: list[RepositoryHealthMetrics]
    ) -> list[str]:
        """Identify trending repositories based on growth metrics.

        Args:
            repository_metrics: List of repository metrics

        Returns:
            List of trending repository names
        """
        trending = []

        for metrics in repository_metrics:
            # Simple trending criteria
            trending_score = 0

            if metrics.stars_growth_30d > 10:
                trending_score += 1
            if metrics.forks_growth_30d > 5:
                trending_score += 1
            if metrics.recent_commits_7d > 5:
                trending_score += 1
            if metrics.contributor_engagement_score > 0.7:
                trending_score += 1

            if trending_score >= 2:
                trending.append(metrics.repository_name)

        return trending

    def _identify_declining_repositories(
        self, repository_metrics: list[RepositoryHealthMetrics]
    ) -> list[str]:
        """Identify declining repositories based on activity metrics.

        Args:
            repository_metrics: List of repository metrics

        Returns:
            List of declining repository names
        """
        declining = []

        for metrics in repository_metrics:
            # Simple declining criteria
            declining_score = 0

            if metrics.last_commit_days_ago and metrics.last_commit_days_ago > 90:
                declining_score += 1
            if metrics.recent_commits_30d == 0:
                declining_score += 1
            if metrics.contributor_engagement_score < 0.3:
                declining_score += 1
            if metrics.sync_status == "diverged":
                declining_score += 1

            if declining_score >= 2:
                declining.append(metrics.repository_name)

        return declining

    def _extract_repo_name_from_url(self, url: str) -> Optional[str]:
        """Extract repository name from GitHub URL.

        Args:
            url: GitHub repository URL

        Returns:
            Repository name in format "owner/repo" or None
        """
        try:
            # Handle different URL formats
            if url.startswith("https://github.com/"):
                parts = url.replace("https://github.com/", "").split("/")
                if len(parts) >= 2:
                    return f"{parts[0]}/{parts[1]}"
            elif url.startswith("git@github.com:"):
                parts = url.replace("git@github.com:", "").split("/")
                if len(parts) >= 2:
                    return f"{parts[0]}/{parts[1].replace('.git', '')}"

            return None
        except Exception:
            return None


def create_health_calculator(
    config: Config, github_client: GitHubClient
) -> RepositoryHealthCalculator:
    """Create a repository health calculator.

    Args:
        config: GitCo configuration
        github_client: GitHub API client

    Returns:
        Repository health calculator
    """
    return RepositoryHealthCalculator(config, github_client)
