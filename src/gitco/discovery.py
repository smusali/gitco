"""Issue discovery and skill-based matching for GitCo."""

import re
from dataclasses import dataclass
from typing import Optional

from .config import Config, Repository
from .github_client import GitHubClient, GitHubIssue
from .patterns.constants import DIFFICULTY_INDICATORS, SKILL_SYNONYMS, TIME_PATTERNS
from .utils import (
    APIError,
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)


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


class DiscoveryError(APIError):
    """Raised when discovery operations fail."""

    pass


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

    def discover_opportunities(
        self,
        skill_filter: Optional[str] = None,
        label_filter: Optional[str] = None,
        limit: Optional[int] = None,
        min_confidence: float = 0.1,
    ) -> list[IssueRecommendation]:
        """Discover contribution opportunities across configured repositories.

        Args:
            skill_filter: Filter by specific skill
            label_filter: Filter by GitHub labels
            limit: Maximum number of recommendations
            min_confidence: Minimum confidence score for recommendations

        Returns:
            List of issue recommendations sorted by score
        """
        log_operation_start(
            "issue discovery", skill_filter=skill_filter, label_filter=label_filter
        )

        try:
            recommendations = []

            for repo in self.config.repositories:
                # Skip if skill filter doesn't match repository skills
                if skill_filter and skill_filter.lower() not in [
                    s.lower() for s in repo.skills
                ]:
                    continue

                repo_recommendations = self._discover_for_repository(
                    repo, skill_filter, label_filter, min_confidence
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

                # Calculate overall score
                overall_score = self._calculate_overall_score(skill_matches, issue)

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
        self, skill_matches: list[SkillMatch], issue: GitHubIssue
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

        total_score = (
            skill_score
            + diversity_bonus
            + high_confidence_bonus
            + beginner_bonus
            + recency_bonus
        )

        return min(total_score, 1.0)  # Cap at 1.0

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
