"""Test fixtures for GitCo."""

from .analyzers import (
    mock_analysis_request,
    mock_anthropic_response,
    mock_change_analysis,
    mock_ollama_response,
    mock_openai_response,
)
from .detectors import (
    sample_breaking_changes,
    sample_commit_messages,
    sample_deprecations,
    sample_diff_content,
    sample_security_updates,
)
from .repositories import (
    mock_config,
    mock_git_repository,
    mock_repository,
)

__all__ = [
    # Analyzer fixtures
    "mock_openai_response",
    "mock_anthropic_response",
    "mock_ollama_response",
    "mock_analysis_request",
    "mock_change_analysis",
    # Detector fixtures
    "sample_diff_content",
    "sample_commit_messages",
    "sample_breaking_changes",
    "sample_security_updates",
    "sample_deprecations",
    # Repository fixtures
    "mock_repository",
    "mock_git_repository",
    "mock_config",
]
