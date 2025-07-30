"""Common test fixtures for GitCo."""

import os
import tempfile
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock

import pytest
from click.testing import CliRunner


@pytest.fixture
def temp_log_file() -> Generator[str, None, None]:
    """Create a temporary log file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_config_file() -> Generator[str, None, None]:
    """Create a temporary configuration file."""
    # Create a unique temporary file name
    temp_file = tempfile.mktemp(suffix=".yml")

    # Ensure the file doesn't exist initially
    if os.path.exists(temp_file):
        os.unlink(temp_file)

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_config_data() -> dict[str, Any]:
    """Create sample configuration data."""
    return {
        "repositories": [
            {
                "name": "test-repo",
                "fork": "user/fork",
                "upstream": "upstream/repo",
                "local_path": "/path/to/repo",
                "skills": ["python"],
            }
        ],
        "settings": {
            "llm_provider": "openai",
            "api_key_env": "TEST_API_KEY",
            "default_path": "/path/to/code",
            "analysis_enabled": True,
            "max_repos_per_batch": 5,
        },
    }


@pytest.fixture
def runner() -> CliRunner:
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_config_manager() -> Generator[Mock, None, None]:
    """Mock config manager."""
    from unittest.mock import patch

    with patch("gitco.cli.ConfigManager") as mock:
        yield mock


@pytest.fixture
def mock_git_repo() -> Generator[Mock, None, None]:
    """Mock git repository."""
    from unittest.mock import patch

    with patch("gitco.cli.GitRepository") as mock:
        yield mock


@pytest.fixture
def mock_github_client() -> Generator[Mock, None, None]:
    """Mock GitHub client."""
    from unittest.mock import patch

    with patch("gitco.cli.create_github_client") as mock:
        yield mock


@pytest.fixture
def mock_discovery_engine() -> Generator[Mock, None, None]:
    """Mock discovery engine."""
    from unittest.mock import patch

    with patch("gitco.cli.create_discovery_engine") as mock:
        yield mock


@pytest.fixture
def mock_health_calculator() -> Generator[Mock, None, None]:
    """Mock health calculator."""
    from unittest.mock import patch

    with patch("gitco.cli.create_health_calculator") as mock:
        yield mock
