"""Contribution history tracking for GitCo."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import Config
from .github_client import GitHubClient, GitHubIssue
from .utils import (
    APIError,
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)


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


class ContributionTrackerError(APIError):
    """Raised when contribution tracking operations fail."""

    pass


class ContributionTracker:
    """Tracks user contributions across repositories."""

    def __init__(self, config: Config, github_client: GitHubClient):
        """Initialize contribution tracker.

        Args:
            config: GitCo configuration
            github_client: GitHub API client
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
    config: Config, github_client: GitHubClient
) -> ContributionTracker:
    """Create a contribution tracker instance.

    Args:
        config: GitCo configuration
        github_client: GitHub API client

    Returns:
        Contribution tracker instance
    """
    return ContributionTracker(config, github_client)
