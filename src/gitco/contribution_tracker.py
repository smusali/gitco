"""Contribution history tracking for GitCo."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import Config
from .github_client import GitHubClient, GitHubIssue
from .utils.common import (
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)
from .utils.exception import ContributionTrackerError


@dataclass
class Contribution:
    """Represents a single contribution."""

    repository: str
    issue_number: int
    issue_title: str
    issue_url: str
    contribution_type: str  # 'issue', 'pr', 'comment', 'review'
    status: str  # 'open', 'closed', 'merged', 'draft'
    created_at: str
    updated_at: str
    skills_used: list[str] = field(default_factory=list)
    impact_score: float = 0.0
    labels: list[str] = field(default_factory=list)
    milestone: Optional[str] = None
    assignees: list[str] = field(default_factory=list)
    comments_count: int = 0
    reactions_count: int = 0


@dataclass
class ContributionStats:
    """Statistics about user contributions."""

    total_contributions: int = 0
    open_contributions: int = 0
    closed_contributions: int = 0
    merged_contributions: int = 0
    repositories_contributed_to: int = 0
    skills_developed: set[str] = field(default_factory=set)
    total_impact_score: float = 0.0
    average_impact_score: float = 0.0
    contribution_timeline: dict[str, int] = field(default_factory=dict)
    recent_activity: list[Contribution] = field(default_factory=list)

    # Enhanced impact metrics
    impact_trend_30d: float = 0.0  # Impact score trend over 30 days
    impact_trend_7d: float = 0.0  # Impact score trend over 7 days
    high_impact_contributions: int = 0  # Contributions with impact score > 0.7
    critical_contributions: int = 0  # Contributions with impact score > 0.9
    skill_impact_scores: dict[str, float] = field(
        default_factory=dict
    )  # Impact by skill
    repository_impact_scores: dict[str, float] = field(
        default_factory=dict
    )  # Impact by repo

    # Trending analysis
    contribution_velocity: float = 0.0  # Contributions per day over last 30 days
    skill_growth_rate: dict[str, float] = field(
        default_factory=dict
    )  # Skill development rate
    repository_engagement_trend: dict[str, float] = field(
        default_factory=dict
    )  # Repo engagement trend
    trending_skills: list[str] = field(
        default_factory=list
    )  # Skills with growing usage
    declining_skills: list[str] = field(
        default_factory=list
    )  # Skills with declining usage

    # Advanced metrics
    collaboration_score: float = 0.0  # How much collaboration with others
    recognition_score: float = 0.0  # Recognition from community (reactions, comments)
    influence_score: float = 0.0  # Overall influence in projects
    sustainability_score: float = 0.0  # Long-term contribution sustainability


class ContributionTracker:
    """Tracks user contributions across repositories."""

    def __init__(self, config: Config, github_client: Optional[GitHubClient]):
        """Initialize contribution tracker.

        Args:
            config: GitCo configuration
            github_client: GitHub API client (can be None if no credentials)
        """
        self.config = config
        self.github_client = github_client
        self.logger = get_logger()
        self.history_file = Path("~/.gitco/contribution_history.json").expanduser()
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load_contribution_history(self) -> list[Contribution]:
        """Load contribution history from file.

        Returns:
            List of contributions
        """
        log_operation_start(
            "loading contribution history", file_path=str(self.history_file)
        )

        try:
            if not self.history_file.exists():
                log_operation_success(
                    "loading contribution history", contributions_count=0
                )
                return []

            with open(self.history_file, encoding="utf-8") as f:
                data = json.load(f)

            contributions = []
            for item in data.get("contributions", []):
                contribution = Contribution(
                    repository=item["repository"],
                    issue_number=item["issue_number"],
                    issue_title=item["issue_title"],
                    issue_url=item["issue_url"],
                    contribution_type=item["contribution_type"],
                    status=item["status"],
                    created_at=item["created_at"],
                    updated_at=item["updated_at"],
                    skills_used=item.get("skills_used", []),
                    impact_score=item.get("impact_score", 0.0),
                    labels=item.get("labels", []),
                    milestone=item.get("milestone"),
                    assignees=item.get("assignees", []),
                    comments_count=item.get("comments_count", 0),
                    reactions_count=item.get("reactions_count", 0),
                )
                contributions.append(contribution)

            log_operation_success(
                "loading contribution history", contributions_count=len(contributions)
            )
            return contributions

        except Exception as e:
            log_operation_failure("loading contribution history", e)
            raise ContributionTrackerError(
                f"Failed to load contribution history: {e}"
            ) from e

    def save_contribution_history(self, contributions: list[Contribution]) -> None:
        """Save contribution history to file.

        Args:
            contributions: List of contributions to save
        """
        log_operation_start(
            "saving contribution history", contributions_count=len(contributions)
        )

        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "contributions": [
                    {
                        "repository": c.repository,
                        "issue_number": c.issue_number,
                        "issue_title": c.issue_title,
                        "issue_url": c.issue_url,
                        "contribution_type": c.contribution_type,
                        "status": c.status,
                        "created_at": c.created_at,
                        "updated_at": c.updated_at,
                        "skills_used": c.skills_used,
                        "impact_score": c.impact_score,
                        "labels": c.labels,
                        "milestone": c.milestone,
                        "assignees": c.assignees,
                        "comments_count": c.comments_count,
                        "reactions_count": c.reactions_count,
                    }
                    for c in contributions
                ],
            }

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_operation_success(
                "saving contribution history", contributions_count=len(contributions)
            )

        except Exception as e:
            log_operation_failure("saving contribution history", e)
            raise ContributionTrackerError(
                f"Failed to save contribution history: {e}"
            ) from e

    def add_contribution(self, contribution: Contribution) -> None:
        """Add a new contribution to history.

        Args:
            contribution: Contribution to add
        """
        log_operation_start(
            "adding contribution",
            repository=contribution.repository,
            issue=contribution.issue_number,
        )

        try:
            contributions = self.load_contribution_history()

            # Check if contribution already exists
            existing = next(
                (
                    c
                    for c in contributions
                    if c.repository == contribution.repository
                    and c.issue_number == contribution.issue_number
                ),
                None,
            )

            if existing:
                # Update existing contribution
                existing.updated_at = contribution.updated_at
                existing.status = contribution.status
                existing.skills_used = contribution.skills_used
                existing.impact_score = contribution.impact_score
                existing.labels = contribution.labels
                existing.comments_count = contribution.comments_count
                existing.reactions_count = contribution.reactions_count
            else:
                # Add new contribution
                contributions.append(contribution)

            self.save_contribution_history(contributions)
            log_operation_success(
                "adding contribution",
                repository=contribution.repository,
                issue=contribution.issue_number,
            )

        except Exception as e:
            log_operation_failure("adding contribution", e)
            raise ContributionTrackerError(f"Failed to add contribution: {e}") from e

    def get_contribution_stats(self, days: Optional[int] = None) -> ContributionStats:
        """Get contribution statistics.

        Args:
            days: Number of days to look back (None for all time)

        Returns:
            Contribution statistics
        """
        log_operation_start("calculating contribution stats", days=days)

        try:
            contributions = self.load_contribution_history()

            if days:
                cutoff_date = datetime.now() - timedelta(days=days)
                contributions = [
                    c
                    for c in contributions
                    if datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                    > cutoff_date
                ]

            stats = ContributionStats()
            stats.total_contributions = len(contributions)

            # Count by status
            for contribution in contributions:
                if contribution.status == "open":
                    stats.open_contributions += 1
                elif contribution.status == "closed":
                    stats.closed_contributions += 1
                elif contribution.status == "merged":
                    stats.merged_contributions += 1

            # Get unique repositories
            repositories = {c.repository for c in contributions}
            stats.repositories_contributed_to = len(repositories)

            # Collect skills
            for contribution in contributions:
                stats.skills_developed.update(contribution.skills_used)
                stats.total_impact_score += contribution.impact_score

            # Calculate averages
            if stats.total_contributions > 0:
                stats.average_impact_score = (
                    stats.total_impact_score / stats.total_contributions
                )

            # Build timeline (last 12 months)
            timeline = {}
            for i in range(12):
                date = datetime.now() - timedelta(days=30 * i)
                month_key = date.strftime("%Y-%m")
                timeline[month_key] = 0

            for contribution in contributions:
                try:
                    date = datetime.fromisoformat(
                        contribution.created_at.replace("Z", "+00:00")
                    )
                    month_key = date.strftime("%Y-%m")
                    if month_key in timeline:
                        timeline[month_key] += 1
                except ValueError:
                    continue

            stats.contribution_timeline = timeline

            # Get recent activity (last 10 contributions)
            sorted_contributions = sorted(
                contributions,
                key=lambda x: datetime.fromisoformat(
                    x.updated_at.replace("Z", "+00:00")
                ),
                reverse=True,
            )
            stats.recent_activity = sorted_contributions[:10]

            # Calculate enhanced impact metrics and trending analysis
            self._calculate_enhanced_impact_metrics(contributions, stats)

            log_operation_success(
                "calculating contribution stats",
                total_contributions=stats.total_contributions,
            )
            return stats

        except Exception as e:
            log_operation_failure("calculating contribution stats", e)
            raise ContributionTrackerError(
                f"Failed to calculate contribution stats: {e}"
            ) from e

    def sync_contributions_from_github(self, username: str) -> None:
        """Sync contributions from GitHub API.

        Args:
            username: GitHub username to sync contributions for
        """
        log_operation_start("syncing contributions from GitHub", username=username)

        if not self.github_client:
            raise ContributionTrackerError(
                "GitHub client not available. Please configure GitHub credentials."
            )

        try:
            # Get user's issues and PRs
            issues = self.github_client.search_issues(
                query=f"author:{username}", state="all", limit=100
            )

            contributions = []
            for issue in issues:
                # Determine contribution type
                contribution_type = (
                    "pr" if "pull_request" in issue.html_url else "issue"
                )

                # Calculate impact score based on various factors
                impact_score = self._calculate_impact_score(issue)

                # Extract skills from labels and content
                skills_used = self._extract_skills_from_issue(issue)

                contribution = Contribution(
                    repository=issue.html_url.split("/")[-4]
                    + "/"
                    + issue.html_url.split("/")[-3],
                    issue_number=issue.number,
                    issue_title=issue.title,
                    issue_url=issue.html_url,
                    contribution_type=contribution_type,
                    status=issue.state,
                    created_at=issue.created_at,
                    updated_at=issue.updated_at,
                    skills_used=skills_used,
                    impact_score=impact_score,
                    labels=issue.labels,
                    milestone=issue.milestone,
                    assignees=issue.assignees,
                    comments_count=issue.comments_count,
                    reactions_count=issue.reactions_count,
                )
                contributions.append(contribution)

            # Save all contributions
            for contribution in contributions:
                self.add_contribution(contribution)

            log_operation_success(
                "syncing contributions from GitHub",
                contributions_synced=len(contributions),
            )

        except Exception as e:
            log_operation_failure("syncing contributions from GitHub", e)
            raise ContributionTrackerError(
                f"Failed to sync contributions from GitHub: {e}"
            ) from e

    def _calculate_impact_score(self, issue: GitHubIssue) -> float:
        """Calculate impact score for an issue.

        Args:
            issue: GitHub issue

        Returns:
            Impact score (0.0 to 1.0)
        """
        score = 0.0

        # Base score for different types
        if "pull_request" in issue.html_url:
            score += 0.3  # PRs are more impactful than issues
        else:
            score += 0.1  # Base score for issues

        # Engagement score
        score += min(issue.comments_count * 0.02, 0.2)  # Comments
        score += min(issue.reactions_count * 0.01, 0.1)  # Reactions

        # Label-based scoring
        high_impact_labels = [
            "bug",
            "enhancement",
            "feature",
            "security",
            "performance",
        ]
        for label in issue.labels:
            if label.lower() in high_impact_labels:
                score += 0.1
                break

        # Status-based scoring
        if issue.state == "closed":
            score += 0.2  # Completed work is more impactful

        return min(score, 1.0)  # Cap at 1.0

    def _calculate_enhanced_impact_metrics(
        self, contributions: list[Contribution], stats: ContributionStats
    ) -> None:
        """Calculate enhanced impact metrics and trending analysis.

        Args:
            contributions: List of contributions
            stats: Stats object to update
        """
        try:
            if not contributions:
                return

            # Calculate impact trends
            self._calculate_impact_trends(contributions, stats)

            # Calculate skill-based impact scores
            self._calculate_skill_impact_scores(contributions, stats)

            # Calculate repository-based impact scores
            self._calculate_repository_impact_scores(contributions, stats)

            # Calculate trending analysis
            self._calculate_trending_analysis(contributions, stats)

            # Calculate advanced metrics
            self._calculate_advanced_metrics(contributions, stats)

        except Exception as e:
            self.logger.warning(f"Failed to calculate enhanced impact metrics: {e}")

    def _calculate_impact_trends(
        self, contributions: list[Contribution], stats: ContributionStats
    ) -> None:
        """Calculate impact score trends over time.

        Args:
            contributions: List of contributions
            stats: Stats object to update
        """
        try:
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)
            seven_days_ago = now - timedelta(days=7)

            # Filter contributions by time periods
            recent_30d = [
                c
                for c in contributions
                if datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                >= thirty_days_ago
            ]
            recent_7d = [
                c
                for c in contributions
                if datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                >= seven_days_ago
            ]

            # Calculate trends (comparing recent vs older periods)
            if recent_30d:
                avg_recent_30d = sum(c.impact_score for c in recent_30d) / len(
                    recent_30d
                )
                older_30d = [c for c in contributions if c not in recent_30d]
                if older_30d:
                    avg_older_30d = sum(c.impact_score for c in older_30d) / len(
                        older_30d
                    )
                    stats.impact_trend_30d = avg_recent_30d - avg_older_30d
                else:
                    stats.impact_trend_30d = avg_recent_30d

            if recent_7d:
                avg_recent_7d = sum(c.impact_score for c in recent_7d) / len(recent_7d)
                older_7d = [c for c in contributions if c not in recent_7d]
                if older_7d:
                    avg_older_7d = sum(c.impact_score for c in older_7d) / len(older_7d)
                    stats.impact_trend_7d = avg_recent_7d - avg_older_7d
                else:
                    stats.impact_trend_7d = avg_recent_7d

            # Count high impact contributions
            stats.high_impact_contributions = len(
                [c for c in contributions if c.impact_score > 0.7]
            )
            stats.critical_contributions = len(
                [c for c in contributions if c.impact_score > 0.9]
            )

        except Exception as e:
            self.logger.warning(f"Failed to calculate impact trends: {e}")

    def _calculate_skill_impact_scores(
        self, contributions: list[Contribution], stats: ContributionStats
    ) -> None:
        """Calculate impact scores by skill.

        Args:
            contributions: List of contributions
            stats: Stats object to update
        """
        try:
            skill_contributions: dict[str, list[Contribution]] = {}

            for contribution in contributions:
                for skill in contribution.skills_used:
                    if skill not in skill_contributions:
                        skill_contributions[skill] = []
                    skill_contributions[skill].append(contribution)

            for skill, skill_contribs in skill_contributions.items():
                if skill_contribs:
                    avg_impact = sum(c.impact_score for c in skill_contribs) / len(
                        skill_contribs
                    )
                    stats.skill_impact_scores[skill] = avg_impact

        except Exception as e:
            self.logger.warning(f"Failed to calculate skill impact scores: {e}")

    def _calculate_repository_impact_scores(
        self, contributions: list[Contribution], stats: ContributionStats
    ) -> None:
        """Calculate impact scores by repository.

        Args:
            contributions: List of contributions
            stats: Stats object to update
        """
        try:
            repo_contributions: dict[str, list[Contribution]] = {}

            for contribution in contributions:
                repo = contribution.repository
                if repo not in repo_contributions:
                    repo_contributions[repo] = []
                repo_contributions[repo].append(contribution)

            for repo, repo_contribs in repo_contributions.items():
                if repo_contribs:
                    avg_impact = sum(c.impact_score for c in repo_contribs) / len(
                        repo_contribs
                    )
                    stats.repository_impact_scores[repo] = avg_impact

        except Exception as e:
            self.logger.warning(f"Failed to calculate repository impact scores: {e}")

    def _calculate_trending_analysis(
        self, contributions: list[Contribution], stats: ContributionStats
    ) -> None:
        """Calculate trending analysis for skills and repositories.

        Args:
            contributions: List of contributions
            stats: Stats object to update
        """
        try:
            now = datetime.now()
            thirty_days_ago = now - timedelta(days=30)
            sixty_days_ago = now - timedelta(days=60)

            # Calculate contribution velocity (contributions per day over last 30 days)
            recent_30d = [
                c
                for c in contributions
                if datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                >= thirty_days_ago
            ]
            stats.contribution_velocity = len(recent_30d) / 30.0

            # Calculate skill growth rates
            self._calculate_skill_growth_rates(
                contributions, stats, thirty_days_ago, sixty_days_ago
            )

            # Calculate repository engagement trends
            self._calculate_repository_engagement_trends(
                contributions, stats, thirty_days_ago, sixty_days_ago
            )

            # Identify trending and declining skills
            self._identify_trending_skills(stats)

        except Exception as e:
            self.logger.warning(f"Failed to calculate trending analysis: {e}")

    def _calculate_skill_growth_rates(
        self,
        contributions: list[Contribution],
        stats: ContributionStats,
        thirty_days_ago: datetime,
        sixty_days_ago: datetime,
    ) -> None:
        """Calculate growth rates for skills.

        Args:
            contributions: List of contributions
            stats: Stats object to update
            thirty_days_ago: 30 days ago timestamp
            sixty_days_ago: 60 days ago timestamp
        """
        try:
            # Group contributions by skill and time period
            skill_periods = {}

            for contribution in contributions:
                contrib_date = datetime.fromisoformat(
                    contribution.updated_at.replace("Z", "+00:00")
                )

                for skill in contribution.skills_used:
                    if skill not in skill_periods:
                        skill_periods[skill] = {"recent": 0, "older": 0}

                    if contrib_date >= thirty_days_ago:
                        skill_periods[skill]["recent"] += 1
                    elif contrib_date >= sixty_days_ago:
                        skill_periods[skill]["older"] += 1

            # Calculate growth rates
            for skill, periods in skill_periods.items():
                if periods["older"] > 0:
                    growth_rate = (periods["recent"] - periods["older"]) / periods[
                        "older"
                    ]
                    stats.skill_growth_rate[skill] = growth_rate
                elif periods["recent"] > 0:
                    stats.skill_growth_rate[skill] = 1.0  # New skill
                else:
                    stats.skill_growth_rate[skill] = 0.0

        except Exception as e:
            self.logger.warning(f"Failed to calculate skill growth rates: {e}")

    def _calculate_repository_engagement_trends(
        self,
        contributions: list[Contribution],
        stats: ContributionStats,
        thirty_days_ago: datetime,
        sixty_days_ago: datetime,
    ) -> None:
        """Calculate engagement trends for repositories.

        Args:
            contributions: List of contributions
            stats: Stats object to update
            thirty_days_ago: 30 days ago timestamp
            sixty_days_ago: 60 days ago timestamp
        """
        try:
            # Group contributions by repository and time period
            repo_periods = {}

            for contribution in contributions:
                contrib_date = datetime.fromisoformat(
                    contribution.updated_at.replace("Z", "+00:00")
                )
                repo = contribution.repository

                if repo not in repo_periods:
                    repo_periods[repo] = {"recent": 0, "older": 0}

                if contrib_date >= thirty_days_ago:
                    repo_periods[repo]["recent"] += 1
                elif contrib_date >= sixty_days_ago:
                    repo_periods[repo]["older"] += 1

            # Calculate engagement trends
            for repo, periods in repo_periods.items():
                if periods["older"] > 0:
                    trend = (periods["recent"] - periods["older"]) / periods["older"]
                    stats.repository_engagement_trend[repo] = trend
                elif periods["recent"] > 0:
                    stats.repository_engagement_trend[repo] = 1.0  # New engagement
                else:
                    stats.repository_engagement_trend[repo] = 0.0

        except Exception as e:
            self.logger.warning(
                f"Failed to calculate repository engagement trends: {e}"
            )

    def _identify_trending_skills(self, stats: ContributionStats) -> None:
        """Identify trending and declining skills.

        Args:
            stats: Stats object to update
        """
        try:
            trending_threshold = 0.2  # 20% growth
            declining_threshold = -0.2  # 20% decline

            for skill, growth_rate in stats.skill_growth_rate.items():
                if growth_rate >= trending_threshold:
                    stats.trending_skills.append(skill)
                elif growth_rate <= declining_threshold:
                    stats.declining_skills.append(skill)

            # Sort by growth rate
            stats.trending_skills.sort(
                key=lambda s: stats.skill_growth_rate.get(s, 0), reverse=True
            )
            stats.declining_skills.sort(key=lambda s: stats.skill_growth_rate.get(s, 0))

        except Exception as e:
            self.logger.warning(f"Failed to identify trending skills: {e}")

    def _calculate_advanced_metrics(
        self, contributions: list[Contribution], stats: ContributionStats
    ) -> None:
        """Calculate advanced contribution metrics.

        Args:
            contributions: List of contributions
            stats: Stats object to update
        """
        try:
            if not contributions:
                return

            # Collaboration score (based on assignees, comments, reactions)
            collaboration_scores = []
            for contrib in contributions:
                collab_score = 0.0
                if contrib.assignees:
                    collab_score += 0.3
                if contrib.comments_count > 0:
                    collab_score += min(contrib.comments_count * 0.05, 0.4)
                if contrib.reactions_count > 0:
                    collab_score += min(contrib.reactions_count * 0.1, 0.3)
                collaboration_scores.append(collab_score)

            if collaboration_scores:
                stats.collaboration_score = sum(collaboration_scores) / len(
                    collaboration_scores
                )

            # Recognition score (based on reactions and comments)
            recognition_scores = []
            for contrib in contributions:
                recog_score = 0.0
                recog_score += min(contrib.reactions_count * 0.2, 0.6)
                recog_score += min(contrib.comments_count * 0.1, 0.4)
                recognition_scores.append(recog_score)

            if recognition_scores:
                stats.recognition_score = sum(recognition_scores) / len(
                    recognition_scores
                )

            # Influence score (combination of impact, collaboration, and recognition)
            influence_factors = [
                stats.average_impact_score * 0.4,
                stats.collaboration_score * 0.3,
                stats.recognition_score * 0.3,
            ]
            stats.influence_score = sum(influence_factors)

            # Sustainability score (based on consistent contribution over time)
            if len(contributions) > 1:
                # Calculate consistency over time
                dates = [
                    datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                    for c in contributions
                ]
                dates.sort()

                if len(dates) > 1:
                    time_spans = []
                    for i in range(1, len(dates)):
                        span = (dates[i] - dates[i - 1]).days
                        time_spans.append(span)

                    avg_span = sum(time_spans) / len(time_spans)
                    # Lower average span = more sustainable (consistent contributions)
                    sustainability = max(0, 1 - (avg_span / 30))  # Normalize to 30 days
                    stats.sustainability_score = sustainability

        except Exception as e:
            self.logger.warning(f"Failed to calculate advanced metrics: {e}")

    def _extract_skills_from_issue(self, issue: GitHubIssue) -> list[str]:
        """Extract skills from issue labels and content.

        Args:
            issue: GitHub issue

        Returns:
            List of skills identified
        """
        skills = set()

        # Extract from labels
        skill_labels = [
            "python",
            "javascript",
            "typescript",
            "java",
            "c++",
            "go",
            "rust",
            "react",
            "vue",
            "angular",
            "node",
            "django",
            "flask",
            "fastapi",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "database",
            "api",
            "frontend",
            "backend",
            "devops",
            "testing",
            "documentation",
        ]

        for label in issue.labels:
            if label.lower() in skill_labels:
                skills.add(label.lower())

        # Extract from title and body
        text = (issue.title + " " + (issue.body or "")).lower()

        # Language detection
        if any(lang in text for lang in ["python", "py"]):
            skills.add("python")
        if any(lang in text for lang in ["javascript", "js", "node"]):
            skills.add("javascript")
        if any(lang in text for lang in ["typescript", "ts"]):
            skills.add("typescript")
        if any(lang in text for lang in ["java"]):
            skills.add("java")
        if any(lang in text for lang in ["react", "vue", "angular"]):
            skills.add("frontend")
        if any(lang in text for lang in ["api", "rest", "graphql"]):
            skills.add("api")
        if any(lang in text for lang in ["docker", "kubernetes", "k8s"]):
            skills.add("devops")

        return list(skills)

    def get_contribution_recommendations(
        self, user_skills: list[str]
    ) -> list[Contribution]:
        """Get personalized contribution recommendations based on history.

        Args:
            user_skills: User's current skills

        Returns:
            List of recommended contributions
        """
        log_operation_start(
            "generating contribution recommendations", skills_count=len(user_skills)
        )

        try:
            contributions = self.load_contribution_history()

            # Analyze past contributions to understand patterns
            skill_frequency: dict[str, int] = {}
            repository_frequency: dict[str, int] = {}

            for contribution in contributions:
                for skill in contribution.skills_used:
                    skill_frequency[skill] = skill_frequency.get(skill, 0) + 1

                repository_frequency[contribution.repository] = (
                    repository_frequency.get(contribution.repository, 0) + 1
                )

            # Find most successful skills and repositories
            top_skills = sorted(
                skill_frequency.items(), key=lambda x: x[1], reverse=True
            )[:5]

            # Create recommendations based on patterns
            recommendations = []

            # Recommend continuing in successful areas
            for skill, _ in top_skills:
                if skill in user_skills:
                    # Find recent high-impact contributions in this skill
                    skill_contributions = [
                        c
                        for c in contributions
                        if skill in c.skills_used and c.impact_score > 0.5
                    ]
                    if skill_contributions:
                        recommendations.extend(skill_contributions[:2])

            # Recommend exploring new skills
            for skill in user_skills:
                if skill not in skill_frequency:
                    # User has this skill but hasn't used it much
                    # This could be a growth opportunity
                    pass

            log_operation_success(
                "generating contribution recommendations",
                recommendations_count=len(recommendations),
            )
            return recommendations

        except Exception as e:
            log_operation_failure("generating contribution recommendations", e)
            raise ContributionTrackerError(
                f"Failed to generate contribution recommendations: {e}"
            ) from e


def create_contribution_tracker(
    config: Config, github_client: Optional[GitHubClient]
) -> ContributionTracker:
    """Create a contribution tracker instance.

    Args:
        config: GitCo configuration
        github_client: GitHub API client (can be None if no credentials)

    Returns:
        Contribution tracker instance
    """
    return ContributionTracker(config, github_client)
