"""Fixtures for repository and configuration tests."""

from typing import Optional
from unittest.mock import Mock

from gitco.analyzer import GitRepository, Repository


def mock_repository(
    name: str = "test-repo",
    fork: str = "user/fork",
    upstream: str = "upstream/repo",
    skills: Optional[list[str]] = None,
) -> Mock:
    """Create a mock Repository object."""
    if skills is None:
        skills = ["python"]

    mock_repo = Mock(spec=Repository)
    mock_repo.name = name
    mock_repo.fork = fork
    mock_repo.upstream = upstream
    mock_repo.skills = skills

    return mock_repo


def mock_git_repository(
    recent_changes: Optional[str] = None,
    recent_commit_messages: Optional[list[str]] = None,
    specific_commit_diff: Optional[str] = None,
    commit_summary: Optional[str] = None,
) -> Mock:
    """Create a mock GitRepository object."""
    if recent_changes is None:
        recent_changes = """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
-def old_function():
+def new_function(param: str) -> str:
     return "Hello"
"""

    if recent_commit_messages is None:
        recent_commit_messages = ["BREAKING CHANGE: update function"]

    if specific_commit_diff is None:
        specific_commit_diff = """diff --git a/api.py b/api.py
index 1234567..abcdefg 100644
--- a/api.py
+++ b/api.py
@@ -1,3 +1,3 @@
-def process_data(data):
+def new_function(param: str) -> str:
     return "Hello"
"""

    if commit_summary is None:
        commit_summary = "Update API function signature"

    mock_git_repo = Mock(spec=GitRepository)
    mock_git_repo.get_recent_changes.return_value = recent_changes
    mock_git_repo.get_recent_commit_messages.return_value = recent_commit_messages
    mock_git_repo.get_specific_commit_diff.return_value = specific_commit_diff
    mock_git_repo.get_commit_summary.return_value = commit_summary

    return mock_git_repo


def mock_config(
    api_key_env: str = "OPENAI_API_KEY",
    enabled: bool = True,
    max_diff_size: int = 10000,
    max_commit_messages: int = 10,
    ollama_host: str = "http://localhost:11434",
    ollama_model: str = "llama2",
) -> Mock:
    """Create a mock Config object."""
    mock_config = Mock()
    mock_config.settings.api_key_env = api_key_env
    mock_config.settings.enabled = enabled
    mock_config.settings.max_diff_size = max_diff_size
    mock_config.settings.max_commit_messages = max_commit_messages
    mock_config.settings.ollama_host = ollama_host
    mock_config.settings.ollama_model = ollama_model

    return mock_config


def mock_git_result(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> Mock:
    """Create a mock git command result."""
    mock_result = Mock()
    mock_result.returncode = returncode
    mock_result.stdout = stdout
    mock_result.stderr = stderr

    return mock_result


def mock_large_diff_content() -> str:
    """Create a large diff content for testing."""
    lines = []
    lines.append("diff --git a/large_file.py b/large_file.py")
    lines.append("index 1234567..abcdefg 100644")
    lines.append("--- a/large_file.py")
    lines.append("+++ b/large_file.py")
    lines.append("@@ -1,100 +1,100 @@")

    # Add 100 lines of changes
    for i in range(1, 101):
        lines.append(f"-old_line_{i} = 'old value'")
        lines.append(f"+new_line_{i} = 'new value'")

    return "\n".join(lines)


def mock_commit_messages_with_categories() -> list[str]:
    """Create commit messages with different categories."""
    return [
        "feat: add new API endpoint",
        "fix: resolve authentication bug",
        "docs: update README",
        "style: format code",
        "refactor: improve error handling",
        "test: add unit tests",
        "BREAKING CHANGE: update function signature",
        "deprecate: remove old API",
        "security: fix CVE-2023-1234",
    ]
