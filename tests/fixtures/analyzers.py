"""Fixtures for analyzer tests."""

from typing import Optional
from unittest.mock import Mock

from gitco.analyzer import AnalysisRequest, ChangeAnalysis, GitRepository, Repository


def mock_openai_response() -> Mock:
    """Create a mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[
        0
    ].message.content = """{
        "summary": "Test summary",
        "breaking_changes": ["Change 1", "Change 2"],
        "new_features": ["Feature 1"],
        "bug_fixes": ["Fix 1"],
        "security_updates": ["Security 1"],
        "deprecations": ["Deprecation 1"],
        "recommendations": ["Recommendation 1"],
        "confidence": 0.85
    }"""
    return mock_response


def mock_anthropic_response() -> Mock:
    """Create a mock Anthropic API response."""
    mock_response = Mock()
    mock_content = Mock()
    mock_content.text = """{
        "summary": "Test summary",
        "breaking_changes": ["Change 1", "Change 2"],
        "new_features": ["Feature 1"],
        "bug_fixes": ["Fix 1"],
        "security_updates": ["Security 1"],
        "deprecations": ["Deprecation 1"],
        "recommendations": ["Recommendation 1"],
        "confidence": 0.85
    }"""
    mock_response.content = [mock_content]
    return mock_response


def mock_analysis_request(
    repository_name: str = "test-repo",
    repository_fork: str = "user/fork",
    repository_upstream: str = "upstream/repo",
    repository_skills: Optional[list[str]] = None,
    diff_content: str = "test diff",
    commit_messages: Optional[list[str]] = None,
    custom_prompt: Optional[str] = None,
) -> AnalysisRequest:
    """Create a mock AnalysisRequest."""
    if repository_skills is None:
        repository_skills = ["python"]

    if commit_messages is None:
        commit_messages = ["test commit"]

    mock_repo = Mock(spec=Repository)
    mock_repo.name = repository_name
    mock_repo.fork = repository_fork
    mock_repo.upstream = repository_upstream
    mock_repo.skills = repository_skills

    mock_git_repo = Mock(spec=GitRepository)

    return AnalysisRequest(
        repository=mock_repo,
        git_repo=mock_git_repo,
        diff_content=diff_content,
        commit_messages=commit_messages,
        custom_prompt=custom_prompt,
    )


def mock_change_analysis(
    summary: str = "Test summary",
    breaking_changes: Optional[list[str]] = None,
    new_features: Optional[list[str]] = None,
    bug_fixes: Optional[list[str]] = None,
    security_updates: Optional[list[str]] = None,
    deprecations: Optional[list[str]] = None,
    recommendations: Optional[list[str]] = None,
    confidence: float = 0.85,
) -> ChangeAnalysis:
    """Create a mock ChangeAnalysis."""
    if breaking_changes is None:
        breaking_changes = ["Change 1", "Change 2"]

    if new_features is None:
        new_features = ["Feature 1"]

    if bug_fixes is None:
        bug_fixes = ["Fix 1"]

    if security_updates is None:
        security_updates = ["Security 1"]

    if deprecations is None:
        deprecations = ["Deprecation 1"]

    if recommendations is None:
        recommendations = ["Recommendation 1"]

    return ChangeAnalysis(
        summary=summary,
        breaking_changes=breaking_changes,
        new_features=new_features,
        bug_fixes=bug_fixes,
        security_updates=security_updates,
        deprecations=deprecations,
        recommendations=recommendations,
        confidence=confidence,
    )
