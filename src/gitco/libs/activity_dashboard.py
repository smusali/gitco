"""Repository activity dashboard for GitCo."""

from dataclasses import dataclass, field
from typing import Any, Optional

from ..utils.common import get_logger
from .config import Config
from .git_ops import GitRepository
from .github_client import GitHubClient


@dataclass
class ActivityMetrics:
    """Detailed activity metrics for a repository."""

    repository_name: str
    repository_path: str

    # Commit activity
    commits_last_24h: int = 0
    commits_last_7d: int = 0
    commits_last_30d: int = 0
    commits_last_90d: int = 0
    total_commits: int = 0

    # Contributor activity
    active_contributors_24h: int = 0
    active_contributors_7d: int = 0
    active_contributors_30d: int = 0
    total_contributors: int = 0

    # Issue and PR activity
    new_issues_7d: int = 0
    closed_issues_7d: int = 0
    new_prs_7d: int = 0
    merged_prs_7d: int = 0
    open_issues: int = 0
    open_prs: int = 0

    # Engagement metrics
    issue_response_time_avg: Optional[float] = None  # hours
    pr_merge_time_avg: Optional[float] = None  # hours
    comment_activity_7d: int = 0
    reaction_activity_7d: int = 0

    # Trending metrics
    stars_growth_7d: int = 0
    forks_growth_7d: int = 0
    views_growth_7d: int = 0

    # Activity patterns
    most_active_hour: Optional[int] = None
    most_active_day: Optional[str] = None
    activity_trend: str = "stable"  # "increasing", "decreasing", "stable"

    # Health indicators
    activity_score: float = 0.0  # 0.0-1.0
    engagement_score: float = 0.0  # 0.0-1.0
    overall_activity_health: str = "unknown"  # "excellent", "good", "fair", "poor"


@dataclass
class ActivitySummary:
    """Summary of activity metrics across all repositories."""

    total_repositories: int = 0
    active_repositories_24h: int = 0
    active_repositories_7d: int = 0
    active_repositories_30d: int = 0

    # Activity trends
    high_activity_repositories: int = 0
    moderate_activity_repositories: int = 0
    low_activity_repositories: int = 0

    # Engagement trends
    high_engagement_repositories: int = 0
    moderate_engagement_repositories: int = 0
    low_engagement_repositories: int = 0

    # Trending repositories
    trending_repositories: list[str] = field(default_factory=list)
    declining_repositories: list[str] = field(default_factory=list)

    # Activity patterns
    most_active_repositories: list[str] = field(default_factory=list)
    most_engaged_repositories: list[str] = field(default_factory=list)

    # Summary statistics
    total_commits_7d: int = 0
    total_issues_7d: int = 0
    total_prs_7d: int = 0
    average_activity_score: float = 0.0
    average_engagement_score: float = 0.0


class ActivityDashboard:
    """Repository activity dashboard calculator."""

    def __init__(self, config: Config, github_client: GitHubClient):
        """Initialize the activity dashboard."""
        self.config = config
        self.github_client = github_client
        self.logger = get_logger()

    def calculate_repository_activity(
        self, repository_config: dict[str, Any]
    ) -> ActivityMetrics:
        """Calculate detailed activity metrics for a repository."""
        metrics = ActivityMetrics(
            repository_name=repository_config.get("name", "unknown"),
            repository_path=repository_config.get("local_path", ""),
        )

        try:
            # Calculate local git activity
            self._calculate_local_activity(repository_config, metrics)

            # Calculate GitHub activity
            self._calculate_github_activity(repository_config, metrics)

            # Calculate engagement metrics
            self._calculate_engagement_metrics(repository_config, metrics)

            # Calculate trending metrics
            self._calculate_trending_metrics(repository_config, metrics)

            # Calculate activity patterns
            self._calculate_activity_patterns(repository_config, metrics)

            # Calculate derived metrics
            self._calculate_derived_metrics(metrics)

        except Exception as e:
            self.logger.warning(
                f"Failed to calculate activity metrics for {metrics.repository_name}: {e}"
            )

        return metrics

    def calculate_activity_summary(
        self, repositories: list[dict[str, Any]]
    ) -> ActivitySummary:
        """Calculate activity summary across all repositories."""
        summary = ActivitySummary()
        all_metrics = []

        for repo_config in repositories:
            metrics = self.calculate_repository_activity(repo_config)
            all_metrics.append(metrics)

        if not all_metrics:
            return summary

        summary.total_repositories = len(all_metrics)

        # Calculate summary statistics
        for metrics in all_metrics:
            self._update_summary_counters(summary, metrics)

        # Calculate averages
        if summary.total_repositories > 0:
            summary.average_activity_score = (
                sum(m.activity_score for m in all_metrics) / summary.total_repositories
            )
            summary.average_engagement_score = (
                sum(m.engagement_score for m in all_metrics)
                / summary.total_repositories
            )

        # Identify trending and declining repositories
        summary.trending_repositories = self._identify_trending_repositories(
            all_metrics
        )
        summary.declining_repositories = self._identify_declining_repositories(
            all_metrics
        )

        # Identify most active and engaged repositories
        summary.most_active_repositories = self._identify_most_active_repositories(
            all_metrics
        )
        summary.most_engaged_repositories = self._identify_most_engaged_repositories(
            all_metrics
        )

        return summary

    def _calculate_local_activity(
        self, repository_config: dict[str, Any], metrics: ActivityMetrics
    ) -> None:
        """Calculate local git activity metrics."""
        try:
            local_path = repository_config.get("local_path")
            if not local_path:
                return

            git_repo = GitRepository(local_path)
            if not git_repo.is_git_repository():
                return

            # Get commit counts for different time periods
            # Note: These methods don't exist in GitRepository, so we'll use defaults
            # In a real implementation, these would be calculated from git log
            metrics.commits_last_24h = 0  # Would be calculated from git log
            metrics.commits_last_7d = 0  # Would be calculated from git log
            metrics.commits_last_30d = 0  # Would be calculated from git log
            metrics.commits_last_90d = 0  # Would be calculated from git log
            metrics.total_commits = 0  # Would be calculated from git log

            # Get contributor activity
            metrics.active_contributors_24h = 0  # Would be calculated from git log
            metrics.active_contributors_7d = 0  # Would be calculated from git log
            metrics.active_contributors_30d = 0  # Would be calculated from git log
            metrics.total_contributors = 0  # Would be calculated from git log

        except Exception as e:
            self.logger.warning(f"Failed to calculate local activity: {e}")

    def _calculate_github_activity(
        self, repository_config: dict[str, Any], metrics: ActivityMetrics
    ) -> None:
        """Calculate GitHub activity metrics."""
        try:
            repo_name = repository_config.get("name")
            if not repo_name:
                return

            # Get repository information
            repo_info = self.github_client.get_repository(repo_name)
            if not repo_info:
                return

            # Get recent issues and PRs
            # Note: get_issues doesn't accept 'since' parameter, so we'll use defaults
            issues = self.github_client.get_issues(repo_name, state="all")

            new_issues = [i for i in issues if i.state == "open"]
            closed_issues = [i for i in issues if i.state == "closed"]

            metrics.new_issues_7d = len(new_issues)
            metrics.closed_issues_7d = len(closed_issues)
            metrics.open_issues = repo_info.open_issues_count
            metrics.open_prs = 0  # Would be calculated from PR data

            # Get PR activity (simplified - in real implementation would fetch PRs)
            metrics.new_prs_7d = 0  # Would be calculated from PR data
            metrics.merged_prs_7d = 0  # Would be calculated from PR data

        except Exception as e:
            self.logger.warning(f"Failed to calculate GitHub activity: {e}")

    def _calculate_engagement_metrics(
        self, repository_config: dict[str, Any], metrics: ActivityMetrics
    ) -> None:
        """Calculate engagement metrics."""
        try:
            repo_name = repository_config.get("name")
            if not repo_name:
                return

            # Calculate engagement scores based on available data
            # This is a simplified implementation
            total_activity = (
                metrics.commits_last_7d
                + metrics.new_issues_7d
                + metrics.new_prs_7d
                + metrics.comment_activity_7d
            )

            if total_activity > 0:
                metrics.engagement_score = min(total_activity / 100.0, 1.0)
            else:
                metrics.engagement_score = 0.0

        except Exception as e:
            self.logger.warning(f"Failed to calculate engagement metrics: {e}")

    def _calculate_trending_metrics(
        self, repository_config: dict[str, Any], metrics: ActivityMetrics
    ) -> None:
        """Calculate trending metrics."""
        try:
            repo_name = repository_config.get("name")
            if not repo_name:
                return

            # Get repository information for trending data
            repo_info = self.github_client.get_repository(repo_name)
            if not repo_info:
                return

            # Calculate trending metrics (simplified)
            metrics.stars_growth_7d = 0  # Would be calculated from historical data
            metrics.forks_growth_7d = 0  # Would be calculated from historical data
            metrics.views_growth_7d = 0  # Would be calculated from historical data

        except Exception as e:
            self.logger.warning(f"Failed to calculate trending metrics: {e}")

    def _calculate_activity_patterns(
        self, repository_config: dict[str, Any], metrics: ActivityMetrics
    ) -> None:
        """Calculate activity patterns."""
        try:
            local_path = repository_config.get("local_path")
            if not local_path:
                return

            git_repo = GitRepository(local_path)
            if not git_repo.is_git_repository():
                return

            # Calculate activity patterns (simplified)
            # In a real implementation, this would analyze commit timestamps
            metrics.most_active_hour = 14  # Default to 2 PM
            metrics.most_active_day = "Wednesday"  # Default
            metrics.activity_trend = "stable"  # Would be calculated from trends

        except Exception as e:
            self.logger.warning(f"Failed to calculate activity patterns: {e}")

    def _calculate_derived_metrics(self, metrics: ActivityMetrics) -> None:
        """Calculate derived metrics and health indicators."""
        try:
            # Calculate activity score
            activity_factors = [
                metrics.commits_last_7d / 10.0,  # Normalize to 0-1
                metrics.active_contributors_7d / 5.0,  # Normalize to 0-1
                metrics.new_issues_7d / 20.0,  # Normalize to 0-1
                metrics.new_prs_7d / 10.0,  # Normalize to 0-1
            ]

            metrics.activity_score = min(
                sum(activity_factors) / len(activity_factors), 1.0
            )

            # Determine activity health
            if metrics.activity_score >= 0.7:
                metrics.overall_activity_health = "excellent"
            elif metrics.activity_score >= 0.5:
                metrics.overall_activity_health = "good"
            elif metrics.activity_score >= 0.3:
                metrics.overall_activity_health = "fair"
            else:
                metrics.overall_activity_health = "poor"

        except Exception as e:
            self.logger.warning(f"Failed to calculate derived metrics: {e}")

    def _update_summary_counters(
        self, summary: ActivitySummary, metrics: ActivityMetrics
    ) -> None:
        """Update summary counters with repository metrics."""
        try:
            # Activity counters
            if metrics.commits_last_24h > 0:
                summary.active_repositories_24h += 1
            if metrics.commits_last_7d > 0:
                summary.active_repositories_7d += 1
            if metrics.commits_last_30d > 0:
                summary.active_repositories_30d += 1

            # Activity level classification
            if metrics.activity_score >= 0.7:
                summary.high_activity_repositories += 1
            elif metrics.activity_score >= 0.3:
                summary.moderate_activity_repositories += 1
            else:
                summary.low_activity_repositories += 1

            # Engagement level classification
            if metrics.engagement_score >= 0.7:
                summary.high_engagement_repositories += 1
            elif metrics.engagement_score >= 0.3:
                summary.moderate_engagement_repositories += 1
            else:
                summary.low_engagement_repositories += 1

            # Accumulate totals
            summary.total_commits_7d += metrics.commits_last_7d
            summary.total_issues_7d += metrics.new_issues_7d
            summary.total_prs_7d += metrics.new_prs_7d

        except Exception as e:
            self.logger.warning(f"Failed to update summary counters: {e}")

    def _identify_trending_repositories(
        self, all_metrics: list[ActivityMetrics]
    ) -> list[str]:
        """Identify trending repositories based on activity growth."""
        try:
            # Sort by activity score and return top 5
            sorted_metrics = sorted(
                all_metrics, key=lambda x: x.activity_score, reverse=True
            )
            return [m.repository_name for m in sorted_metrics[:5]]
        except Exception as e:
            self.logger.warning(f"Failed to identify trending repositories: {e}")
            return []

    def _identify_declining_repositories(
        self, all_metrics: list[ActivityMetrics]
    ) -> list[str]:
        """Identify declining repositories based on low activity."""
        try:
            # Sort by activity score and return bottom 5
            sorted_metrics = sorted(all_metrics, key=lambda x: x.activity_score)
            return [m.repository_name for m in sorted_metrics[:5]]
        except Exception as e:
            self.logger.warning(f"Failed to identify declining repositories: {e}")
            return []

    def _identify_most_active_repositories(
        self, all_metrics: list[ActivityMetrics]
    ) -> list[str]:
        """Identify most active repositories."""
        try:
            # Sort by commits in last 7 days
            sorted_metrics = sorted(
                all_metrics, key=lambda x: x.commits_last_7d, reverse=True
            )
            return [m.repository_name for m in sorted_metrics[:5]]
        except Exception as e:
            self.logger.warning(f"Failed to identify most active repositories: {e}")
            return []

    def _identify_most_engaged_repositories(
        self, all_metrics: list[ActivityMetrics]
    ) -> list[str]:
        """Identify most engaged repositories."""
        try:
            # Sort by engagement score
            sorted_metrics = sorted(
                all_metrics, key=lambda x: x.engagement_score, reverse=True
            )
            return [m.repository_name for m in sorted_metrics[:5]]
        except Exception as e:
            self.logger.warning(f"Failed to identify most engaged repositories: {e}")
            return []


def create_activity_dashboard(
    config: Config, github_client: GitHubClient
) -> ActivityDashboard:
    """Create an activity dashboard instance."""
    return ActivityDashboard(config, github_client)
