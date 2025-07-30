"""Test fixtures for GitCo."""

from .analyzers import (
    mock_analysis_request,
    mock_anthropic_response,
    mock_change_analysis,
    mock_openai_response,
)
from .common import (
    mock_config_manager,
    mock_discovery_engine,
    mock_git_repo,
    mock_github_client,
    mock_health_calculator,
    runner,
    sample_config_data,
    temp_config_file,
    temp_log_file,
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
    "mock_analysis_request",
    "mock_change_analysis",
    # Common fixtures
    "temp_log_file",
    "temp_config_file",
    "sample_config_data",
    "runner",
    "mock_config_manager",
    "mock_git_repo",
    "mock_github_client",
    "mock_discovery_engine",
    "mock_health_calculator",
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
