"""Issue discovery and skill-based matching for GitCo."""

import re
from dataclasses import dataclass
from typing import Optional, Union

from rich.panel import Panel
from rich.text import Text

from ..patterns.constants import DIFFICULTY_INDICATORS, SKILL_SYNONYMS, TIME_PATTERNS
from ..utils.common import (
    console,
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)
from ..utils.exception import DiscoveryError
from .config import Config, Repository
from .github_client import GitHubClient, GitHubIssue


@dataclass
class SkillMatch:
    """Represents a skill match between an issue and user skills."""

    skill: str
    confidence: float
    match_type: str  # 'exact', 'partial', 'related', 'language'
    evidence: list[str]


@dataclass
class IssueRecommendation:
    """Represents a recommended issue with matching details."""

    issue: GitHubIssue
    repository: Repository
    skill_matches: list[SkillMatch]
    overall_score: float
    difficulty_level: str  # 'beginner', 'intermediate', 'advanced'
    estimated_time: str  # 'quick', 'medium', 'long'
    tags: list[str]


class SkillMatcher:
    """Matches user skills to GitHub issues."""

    def __init__(self) -> None:
        """Initialize skill matcher."""
        self.logger = get_logger()

        # Use constants from patterns module
        self.skill_synonyms = SKILL_SYNONYMS
        self.difficulty_indicators = DIFFICULTY_INDICATORS
        self.time_patterns = TIME_PATTERNS

    def match_skills_to_issue(
        self, user_skills: list[str], issue: GitHubIssue, repository: Repository
    ) -> list[SkillMatch]:
        """Match user skills to a GitHub issue.

        Args:
            user_skills: List of user's skills
            issue: GitHub issue to match against
            repository: Repository containing the issue

        Returns:
            List of skill matches with confidence scores
        """
        matches = []
        issue_text = self._get_issue_text(issue, repository)

        for skill in user_skills:
            skill_lower = skill.lower()

            # Check for exact matches
            if self._exact_match(skill_lower, issue_text):
                matches.append(
                    SkillMatch(
                        skill=skill,
                        confidence=1.0,
                        match_type="exact",
                        evidence=self._find_evidence(skill_lower, issue_text),
                    )
                )
                continue

            # Check for partial matches
            partial_confidence = self._partial_match(skill_lower, issue_text)
            if partial_confidence > 0.3:
                matches.append(
                    SkillMatch(
                        skill=skill,
                        confidence=partial_confidence,
                        match_type="partial",
                        evidence=self._find_evidence(skill_lower, issue_text),
                    )
                )
                continue

            # Check for related terms
            related_confidence = self._related_match(skill_lower, issue_text)
            if related_confidence > 0.2:
                matches.append(
                    SkillMatch(
                        skill=skill,
                        confidence=related_confidence,
                        match_type="related",
                        evidence=self._find_evidence(skill_lower, issue_text),
                    )
                )
                continue

            # Check for language matches
            language_confidence = self._language_match(skill_lower, repository)
            if language_confidence > 0.1:
                matches.append(
                    SkillMatch(
                        skill=skill,
                        confidence=language_confidence,
                        match_type="language",
                        evidence=[
                            f"Repository language: {repository.language or 'unknown'}"
                        ],
                    )
                )

        return matches

    def _get_issue_text(self, issue: GitHubIssue, repository: Repository) -> str:
        """Extract all text content from an issue for analysis."""
        text_parts = []

        # Title
        if issue.title:
            text_parts.append(issue.title.lower())

        # Body
        if issue.body:
            text_parts.append(issue.body.lower())

        # Labels
        if issue.labels:
            text_parts.extend([label.lower() for label in issue.labels])

        # Repository name and description
        if repository.name:
            text_parts.append(repository.name.lower())

        return " ".join(text_parts)

    def _exact_match(self, skill: str, text: str) -> bool:
        """Check for exact skill matches in text."""
        # Direct skill match
        if skill in text:
            return True

        # Check synonyms
        if skill in self.skill_synonyms:
            for synonym in self.skill_synonyms[skill]:
                if synonym in text:
                    return True

        return False

    def _partial_match(self, skill: str, text: str) -> float:
        """Calculate partial match confidence."""
        if skill in self.skill_synonyms:
            synonyms = self.skill_synonyms[skill]
        else:
            synonyms = [skill]

        max_confidence = 0.0
        for synonym in synonyms:
            # Check for word boundaries
            pattern = r"\b" + re.escape(synonym) + r"\b"
            if re.search(pattern, text):
                max_confidence = max(max_confidence, 0.8)

            # Check for partial matches
            if synonym in text:
                max_confidence = max(max_confidence, 0.6)

        return max_confidence

    def _related_match(self, skill: str, text: str) -> float:
        """Calculate related term match confidence."""
        if skill not in self.skill_synonyms:
            return 0.0

        related_terms = self.skill_synonyms[skill]
        max_confidence = 0.0

        for term in related_terms:
            if term in text:
                max_confidence = max(max_confidence, 0.4)

        return max_confidence

    def _language_match(self, skill: str, repository: Repository) -> float:
        """Calculate language-based match confidence."""
        if not repository.language:
            return 0.0

        repo_language = repository.language.lower()

        # Direct language match
        if skill == repo_language:
            return 0.3

        # Check if skill is related to repository language
        if skill in self.skill_synonyms:
            synonyms = self.skill_synonyms[skill]
            if repo_language in synonyms:
                return 0.2

        return 0.0

    def _find_evidence(self, skill: str, text: str) -> list[str]:
        """Find evidence of skill matches in text."""
        evidence = []

        if skill in self.skill_synonyms:
            synonyms = self.skill_synonyms[skill]
        else:
            synonyms = [skill]

        for synonym in synonyms:
            if synonym in text:
                # Find context around the match
                words = text.split()
                for i, word in enumerate(words):
                    if synonym in word:
                        start = max(0, i - 3)
                        end = min(len(words), i + 4)
                        context = " ".join(words[start:end])
                        evidence.append(f"...{context}...")
                        break

        return evidence[:3]  # Limit to 3 pieces of evidence

    def determine_difficulty(self, issue: GitHubIssue) -> str:
        """Determine the difficulty level of an issue."""
        issue_text = self._get_issue_text(issue, Repository("", "", "", ""))

        for difficulty, indicators in self.difficulty_indicators.items():
            for indicator in indicators:
                if indicator in issue_text:
                    return difficulty

        return "intermediate"  # Default difficulty

    def estimate_time(self, issue: GitHubIssue) -> str:
        """Estimate the time required for an issue."""
        issue_text = self._get_issue_text(issue, Repository("", "", "", ""))

        for time_level, patterns in self.time_patterns.items():
            for pattern in patterns:
                if pattern in issue_text:
                    return time_level

        return "medium"  # Default time estimate


class IssueDiscovery:
    """Discovers and matches GitHub issues for contribution opportunities."""

    def __init__(self, github_client: GitHubClient, config: Config):
        """Initialize issue discovery.

        Args:
            github_client: GitHub API client
            config: GitCo configuration
        """
        self.github_client = github_client
        self.config = config
        self.skill_matcher = SkillMatcher()
        self.logger = get_logger()

        # Initialize contribution tracker
        from .contribution_tracker import create_contribution_tracker

        self.contribution_tracker = create_contribution_tracker(config, github_client)

    def discover_opportunities(
        self,
        skill_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        limit: Optional[int] = None,
        min_confidence: float = 0.1,
        include_personalization: bool = False,
    ) -> list[IssueRecommendation]:
        """Discover contribution opportunities across configured repositories.

        Args:
            skill_filter: Filter by specific skill
            label_filter: Filter by GitHub labels
            limit: Maximum number of recommendations
            min_confidence: Minimum confidence score for recommendations
            include_personalization: Include personalized scoring based on contribution history

        Returns:
            List of issue recommendations sorted by score
        """
        log_operation_start(
            "issue discovery",
            skill_filter=skill_filter,
            label_filter=label_filter,
            personalized=include_personalization,
        )

        try:
            recommendations = []

            if self.config.repositories is not None:
                for repo in self.config.repositories:
                    # Skip if skill filter doesn't match repository skills
                    if skill_filter and skill_filter.lower() not in [
                        s.lower() for s in repo.skills
                    ]:
                        continue

                    repo_recommendations = self._discover_for_repository(
                        repo,
                        skill_filter,
                        label_filter,
                        min_confidence,
                        include_personalization,
                    )
                    recommendations.extend(repo_recommendations)

            # Sort by overall score (descending)
            recommendations.sort(key=lambda x: x.overall_score, reverse=True)

            # Apply limit
            if limit:
                recommendations = recommendations[:limit]

            log_operation_success(
                "issue discovery", recommendations_count=len(recommendations)
            )

            return recommendations

        except Exception as e:
            log_operation_failure("issue discovery", error=e)
            raise DiscoveryError(f"Failed to discover opportunities: {e}") from e

    def _discover_for_repository(
        self,
        repository: Repository,
        skill_filter: Optional[str],
        label_filter: Optional[str],
        min_confidence: float,
        include_personalization: bool = False,
    ) -> list[IssueRecommendation]:
        """Discover opportunities for a specific repository."""
        try:
            # Get issues from repository
            labels = None
            if label_filter:
                labels = [label_filter]

            issues = self.github_client.get_issues(
                repo_name=repository.fork,
                state="open",
                labels=labels,
                limit=50,  # Reasonable limit per repository
            )

            recommendations = []

            for issue in issues:
                # Get user skills (from repository configuration)
                user_skills = repository.skills

                # Apply skill filter if specified
                if skill_filter:
                    if skill_filter.lower() not in [s.lower() for s in user_skills]:
                        continue
                    user_skills = [skill_filter]

                # Match skills to issue
                skill_matches = self.skill_matcher.match_skills_to_issue(
                    user_skills, issue, repository
                )

                # Calculate overall score with personalization if enabled
                if include_personalization:
                    overall_score = self._calculate_personalized_score(
                        skill_matches, issue, repository
                    )
                else:
                    overall_score = self._calculate_overall_score(
                        skill_matches, issue, repository
                    )

                # Skip if below minimum confidence
                if overall_score < min_confidence:
                    continue

                # Determine difficulty and time estimate
                difficulty = self.skill_matcher.determine_difficulty(issue)
                estimated_time = self.skill_matcher.estimate_time(issue)

                # Generate tags
                tags = self._generate_tags(issue, repository, skill_matches)

                recommendation = IssueRecommendation(
                    issue=issue,
                    repository=repository,
                    skill_matches=skill_matches,
                    overall_score=overall_score,
                    difficulty_level=difficulty,
                    estimated_time=estimated_time,
                    tags=tags,
                )

                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            self.logger.warning(
                f"Failed to discover opportunities for {repository.name}: {e}"
            )
            return []

    def _calculate_overall_score(
        self,
        skill_matches: list[SkillMatch],
        issue: GitHubIssue,
        repository: Repository,
    ) -> float:
        """Calculate overall recommendation score."""
        if not skill_matches:
            return 0.0

        # Base score from skill matches
        skill_score = sum(match.confidence for match in skill_matches) / len(
            skill_matches
        )

        # Bonus for multiple skill matches
        diversity_bonus = min(len(skill_matches) * 0.1, 0.3)

        # Bonus for high-confidence matches
        high_confidence_bonus = sum(
            0.1 for match in skill_matches if match.confidence > 0.8
        )

        # Bonus for "good first issue" labels
        beginner_bonus = (
            0.2
            if any("good first issue" in label.lower() for label in issue.labels)
            else 0.0
        )

        # Bonus for recent issues
        recency_bonus = 0.1  # Could be enhanced with actual date logic

        # Contribution history bonus
        history_bonus = self._calculate_history_bonus(issue, repository)

        total_score = (
            skill_score
            + diversity_bonus
            + high_confidence_bonus
            + beginner_bonus
            + recency_bonus
            + history_bonus
        )

        return min(total_score, 1.0)  # Cap at 1.0

    def _calculate_personalized_score(
        self,
        skill_matches: list[SkillMatch],
        issue: GitHubIssue,
        repository: Repository,
    ) -> float:
        """Calculate personalized score based on contribution history and patterns."""
        try:
            # Start with base score calculation
            base_score = self._calculate_overall_score(skill_matches, issue, repository)

            # Get contribution history
            contributions = self.contribution_tracker.load_contribution_history()

            if not contributions:
                return base_score  # No history available

            # Calculate personalized bonuses
            personalization_bonus = 0.0

            # Repository familiarity bonus
            repo_contributions = [
                c for c in contributions if c.repository == repository.fork
            ]
            if repo_contributions:
                # Higher bonus for repositories with successful contributions
                successful_contributions = [
                    c
                    for c in repo_contributions
                    if c.status in ["closed", "merged"] and c.impact_score > 0.5
                ]
                familiarity_bonus = min(len(successful_contributions) * 0.08, 0.25)
                personalization_bonus += familiarity_bonus

            # Skill development pattern bonus
            user_skills = set(repository.skills)
            skill_usage_pattern: dict[str, int] = {}

            for contribution in contributions:
                for skill in contribution.skills_used:
                    if skill in user_skills:
                        skill_usage_pattern[skill] = (
                            skill_usage_pattern.get(skill, 0) + 1
                        )

            # Bonus for skills that have been successfully used
            for match in skill_matches:
                if match.skill in skill_usage_pattern:
                    # Higher bonus for skills with successful usage
                    usage_count = skill_usage_pattern[match.skill]
                    skill_bonus = min(usage_count * 0.03, 0.15)
                    personalization_bonus += skill_bonus

            # Issue type preference bonus
            issue_type_bonus = self._calculate_issue_type_bonus(issue, contributions)
            personalization_bonus += issue_type_bonus

            # Difficulty preference bonus
            difficulty_bonus = self._calculate_difficulty_preference_bonus(
                issue, contributions
            )
            personalization_bonus += difficulty_bonus

            # Repository activity bonus
            activity_bonus = self._calculate_repository_activity_bonus(
                repository, contributions
            )
            personalization_bonus += activity_bonus

            # Combine base score with personalization
            final_score = base_score + personalization_bonus

            return min(final_score, 1.0)  # Cap at 1.0

        except Exception as e:
            self.logger.warning(f"Failed to calculate personalized score: {e}")
            return self._calculate_overall_score(skill_matches, issue, repository)

    def _calculate_issue_type_bonus(
        self, issue: GitHubIssue, contributions: list
    ) -> float:
        """Calculate bonus based on preferred issue types."""
        try:
            # Analyze past contribution types
            pr_count = sum(1 for c in contributions if c.contribution_type == "pr")
            issue_count = sum(
                1 for c in contributions if c.contribution_type == "issue"
            )

            current_type = "pr" if "pull_request" in issue.html_url else "issue"

            # Bonus for preferred type
            if pr_count > issue_count and current_type == "pr":
                return 0.1
            elif issue_count > pr_count and current_type == "issue":
                return 0.1

            return 0.0

        except Exception as e:
            self.logger.warning(f"Failed to calculate issue type bonus: {e}")
            return 0.0

    def _calculate_difficulty_preference_bonus(
        self, issue: GitHubIssue, contributions: list
    ) -> float:
        """Calculate bonus based on difficulty preferences."""
        try:
            # Analyze past contribution difficulties
            difficulty = self.skill_matcher.determine_difficulty(issue)

            # Count successful contributions by difficulty
            successful_contributions = [
                c
                for c in contributions
                if c.status in ["closed", "merged"] and c.impact_score > 0.5
            ]

            difficulty_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}

            for contribution in successful_contributions:
                # Estimate difficulty from impact score and labels
                if contribution.impact_score > 0.8:
                    difficulty_counts["advanced"] += 1
                elif contribution.impact_score > 0.5:
                    difficulty_counts["intermediate"] += 1
                else:
                    difficulty_counts["beginner"] += 1

            # Bonus for preferred difficulty level
            preferred_difficulty = max(
                difficulty_counts, key=lambda k: difficulty_counts[k]
            )
            if (
                difficulty == preferred_difficulty
                and difficulty_counts[preferred_difficulty] > 0
            ):
                return 0.05

            return 0.0

        except Exception as e:
            self.logger.warning(f"Failed to calculate difficulty preference bonus: {e}")
            return 0.0

    def _calculate_repository_activity_bonus(
        self, repository: Repository, contributions: list
    ) -> float:
        """Calculate bonus based on repository activity patterns."""
        try:
            # Analyze activity in similar repositories
            repo_contributions = [
                c
                for c in contributions
                if any(skill in c.skills_used for skill in repository.skills)
            ]

            if not repo_contributions:
                return 0.0

            # Bonus for repositories with good engagement
            recent_contributions = [
                c
                for c in repo_contributions
                if c.status in ["closed", "merged"] and c.impact_score > 0.6
            ]

            if recent_contributions:
                return 0.05

            return 0.0

        except Exception as e:
            self.logger.warning(f"Failed to calculate repository activity bonus: {e}")
            return 0.0

    def _calculate_history_bonus(
        self, issue: GitHubIssue, repository: Repository
    ) -> float:
        """Calculate bonus score based on contribution history."""
        try:
            # Get contribution history for this repository
            contributions = self.contribution_tracker.load_contribution_history()
            repo_contributions = [
                c for c in contributions if c.repository == repository.fork
            ]

            if not repo_contributions:
                return 0.0  # No history, no bonus

            # Calculate repository familiarity bonus
            repo_contribution_count = len(repo_contributions)
            familiarity_bonus = min(repo_contribution_count * 0.05, 0.2)

            # Calculate skill development bonus
            user_skills = set(repository.skills)
            developed_skills = set()
            for contribution in repo_contributions:
                developed_skills.update(contribution.skills_used)

            # Bonus for skills that have been successfully used in this repo
            skill_bonus = 0.0
            for skill in user_skills:
                if skill in developed_skills:
                    skill_bonus += 0.05

            # Bonus for high-impact contributions in this repo
            high_impact_contributions = [
                c for c in repo_contributions if c.impact_score > 0.7
            ]
            impact_bonus = min(len(high_impact_contributions) * 0.03, 0.15)

            return min(familiarity_bonus + skill_bonus + impact_bonus, 0.3)

        except Exception as e:
            self.logger.warning(f"Failed to calculate history bonus: {e}")
            return 0.0

    def _generate_tags(
        self,
        issue: GitHubIssue,
        repository: Repository,
        skill_matches: list[SkillMatch],
    ) -> list[str]:
        """Generate tags for the recommendation."""
        tags = []

        # Add skill tags
        for match in skill_matches:
            if match.confidence > 0.5:
                tags.append(match.skill)

        # Add difficulty tag
        difficulty = self.skill_matcher.determine_difficulty(issue)
        tags.append(difficulty)

        # Add time estimate tag
        estimated_time = self.skill_matcher.estimate_time(issue)
        tags.append(estimated_time)

        # Add language tag
        if repository.language:
            tags.append(repository.language)

        # Add special tags
        if any("good first issue" in label.lower() for label in issue.labels):
            tags.append("beginner-friendly")

        if any("help wanted" in label.lower() for label in issue.labels):
            tags.append("help-wanted")

        return list(set(tags))  # Remove duplicates


def create_discovery_engine(
    github_client: GitHubClient, config: Config
) -> IssueDiscovery:
    """Create an issue discovery engine.

    Args:
        github_client: GitHub API client
        config: GitCo configuration

    Returns:
        Configured issue discovery engine
    """
    return IssueDiscovery(github_client, config)


def print_issue_recommendation(
    recommendation: "IssueRecommendation", index: int
) -> None:
    """Print a formatted issue recommendation.

    Args:
        recommendation: The issue recommendation to display
        index: The recommendation number/index
    """
    if not isinstance(recommendation, IssueRecommendation):
        return

    # Build the content
    content: list[Union[Text, str]] = []

    # Issue title and URL
    title_text = Text(f"#{recommendation.issue.number}: {recommendation.issue.title}")
    title_text.stylize("bold blue")
    content.append(title_text)
    content.append(f"🔗 {recommendation.issue.html_url}")
    content.append("")

    # Repository info
    content.append(f"📁 Repository: {recommendation.repository.name}")
    if recommendation.repository.language:
        content.append(f"💻 Language: {recommendation.repository.language}")
    content.append("")

    # Score and difficulty with enhanced information
    score_text = f"Score: {recommendation.overall_score:.2f}"
    difficulty_text = f"Difficulty: {recommendation.difficulty_level.title()}"
    time_text = f"Time: {recommendation.estimated_time.title()}"

    # Add confidence indicator
    if recommendation.overall_score > 0.8:
        confidence_indicator = "🎯 Excellent Match"
    elif recommendation.overall_score > 0.6:
        confidence_indicator = "⭐ Good Match"
    elif recommendation.overall_score > 0.4:
        confidence_indicator = "💡 Good Opportunity"
    else:
        confidence_indicator = "🔍 Exploration"

    content.append(
        f"{confidence_indicator} | {score_text} | 🎯 {difficulty_text} | ⏱️ {time_text}"
    )
    content.append("")

    # Skill matches with enhanced details
    if recommendation.skill_matches:
        content.append("🎯 Skill Matches:")
        for match in recommendation.skill_matches:
            confidence_text = f"({match.confidence:.1%})"
            match_type_emoji = {
                "exact": "🎯",
                "partial": "📝",
                "related": "🔗",
                "language": "💻",
            }.get(match.match_type, "📌")

            match_text = f"  {match_type_emoji} {match.skill} {confidence_text} [{match.match_type}]"
            content.append(match_text)

            # Show evidence for high-confidence matches
            if match.confidence > 0.7 and match.evidence:
                evidence_text = f"    Evidence: {match.evidence[0][:60]}..."
                content.append(f"    {evidence_text}")
        content.append("")

    # Tags with categorization
    if recommendation.tags:
        # Categorize tags
        skill_tags: list[str] = [
            tag
            for tag in recommendation.tags
            if tag
            in [
                "python",
                "javascript",
                "java",
                "go",
                "rust",
                "react",
                "vue",
                "angular",
                "api",
                "database",
                "testing",
                "devops",
            ]
        ]
        difficulty_tags: list[str] = [
            tag
            for tag in recommendation.tags
            if tag in ["beginner", "intermediate", "advanced"]
        ]
        time_tags: list[str] = [
            tag for tag in recommendation.tags if tag in ["quick", "medium", "long"]
        ]
        special_tags: list[str] = [
            tag
            for tag in recommendation.tags
            if tag not in skill_tags + difficulty_tags + time_tags
        ]

        if skill_tags:
            content.append(f"💻 Skills: {', '.join(skill_tags)}")
        if difficulty_tags:
            content.append(f"🎯 Level: {', '.join(difficulty_tags)}")
        if time_tags:
            content.append(f"⏱️ Time: {', '.join(time_tags)}")
        if special_tags:
            content.append(f"🏷️ Tags: {', '.join(special_tags)}")
        content.append("")

    # Personalized insights (if available)
    if hasattr(recommendation, "personalized_insights"):
        content.append("💡 Personalized Insights:")
        for insight in recommendation.personalized_insights[:2]:  # Show top 2 insights
            content.append(f"  • {insight}")
        content.append("")

    # Create the panel with dynamic styling
    border_style = (
        "green"
        if recommendation.overall_score > 0.7
        else "yellow"
        if recommendation.overall_score > 0.4
        else "blue"
    )

    panel = Panel(
        "\n".join(str(item) for item in content),
        title=f"Recommendation #{index}",
        border_style=border_style,
    )

    console.print(panel)
    console.print()  # Add spacing
