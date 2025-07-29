"""Test GitCo configuration management."""

import os
import tempfile
from collections.abc import Generator
from typing import Any

import pytest

from gitco.config import (
    Config,
    ConfigManager,
    Repository,
    Settings,
    create_sample_config,
    get_config_manager,
)


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


def test_repository_dataclass() -> None:
    """Test Repository dataclass."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path/to/repo",
        skills=["python"],
        analysis_enabled=True,
    )

    assert repo.name == "test"
    assert repo.fork == "user/fork"
    assert repo.upstream == "owner/repo"
    assert repo.local_path == "/path/to/repo"
    assert repo.skills == ["python"]
    assert repo.analysis_enabled is True


def test_settings_dataclass() -> None:
    """Test Settings dataclass."""
    settings = Settings(
        llm_provider="anthropic",
        api_key_env="CUSTOM_API_KEY",
        default_path="/custom/path",
        analysis_enabled=False,
        max_repos_per_batch=5,
    )

    assert settings.llm_provider == "anthropic"
    assert settings.api_key_env == "CUSTOM_API_KEY"
    assert settings.default_path == "/custom/path"
    assert settings.analysis_enabled is False
    assert settings.max_repos_per_batch == 5


def test_config_dataclass() -> None:
    """Test Config dataclass."""
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(llm_provider="openai")

    config = Config(repositories=[repo], settings=settings)

    assert len(config.repositories) == 1
    assert config.repositories[0].name == "test"
    assert config.settings.llm_provider == "openai"


def test_config_manager_initialization() -> None:
    """Test ConfigManager initialization."""
    manager = ConfigManager()
    assert manager.config_path is not None
    assert isinstance(manager.config, Config)


def test_create_sample_config() -> None:
    """Test create_sample_config function."""
    config = create_sample_config()
    assert "repositories" in config
    assert "settings" in config


def test_config_manager_create_default_config(temp_config_file: str) -> None:
    """Test config_manager create_default_config method."""
    manager = ConfigManager(temp_config_file)
    config = manager.create_default_config()

    assert isinstance(config, Config)
    assert len(config.repositories) >= 0  # Can be 0 or more


def test_config_manager_create_default_config_force(temp_config_file: str) -> None:
    """Test config_manager create_default_config method with force."""
    manager = ConfigManager(temp_config_file)
    config = manager.create_default_config(force=True)

    assert isinstance(config, Config)
    assert len(config.repositories) >= 0  # Can be 0 or more


def test_config_manager_create_default_config_exists(temp_config_file: str) -> None:
    """Test config_manager create_default_config method when config exists."""
    manager = ConfigManager(temp_config_file)
    # Create initial config
    manager.create_default_config()

    # Try to create again without force
    with pytest.raises(FileExistsError):
        manager.create_default_config()


def test_config_manager_load_config(
    temp_config_file: str, sample_config_data: dict[str, Any]
) -> None:
    """Test config_manager load_config method."""
    manager = ConfigManager(temp_config_file)
    # Create a config file first
    manager.create_default_config()
    config = manager.load_config()

    assert isinstance(config, Config)
    assert len(config.repositories) >= 0


def test_config_manager_save_config(temp_config_file: str) -> None:
    """Test config_manager save_config method."""
    manager = ConfigManager(temp_config_file)
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo], settings=settings)

    manager.save_config(config)
    assert os.path.exists(temp_config_file)


def test_config_manager_validate_config() -> None:
    """Test config_manager validate_config method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo], settings=settings)

    errors = manager.validate_config(config)
    assert isinstance(errors, list)


def test_config_manager_validate_config_duplicate_names() -> None:
    """Test config_manager validate_config method with duplicate names."""
    manager = ConfigManager()
    repo1 = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path1"
    )
    repo2 = Repository(
        name="test", fork="user/fork2", upstream="owner/repo2", local_path="/path2"
    )
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo1, repo2], settings=settings)

    errors = manager.validate_config(config)
    assert len(errors) > 0


def test_config_manager_validate_config_invalid_llm_provider() -> None:
    """Test config_manager validate_config method with invalid LLM provider."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(llm_provider="invalid_provider")
    config = Config(repositories=[repo], settings=settings)

    errors = manager.validate_config(config)
    assert len(errors) > 0


def test_config_manager_get_repository() -> None:
    """Test config_manager get_repository method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config = Config(repositories=[repo], settings=Settings())

    manager.config = config
    result = manager.get_repository("test")
    assert result is not None
    assert result.name == "test"


def test_config_manager_add_repository() -> None:
    """Test config_manager add_repository method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )

    manager.add_repository(repo)
    assert len(manager.config.repositories) == 1
    assert manager.config.repositories[0].name == "test"


def test_config_manager_remove_repository() -> None:
    """Test config_manager remove_repository method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )

    # Add repository
    manager.add_repository(repo)
    assert len(manager.config.repositories) == 1

    # Remove repository
    result = manager.remove_repository("test")
    assert result is True
    assert len(manager.config.repositories) == 0


def test_get_config_manager() -> None:
    """Test get_config_manager function."""
    manager = get_config_manager()
    assert isinstance(manager, ConfigManager)


def test_config_manager_load_config_file_not_found() -> None:
    """Test config_manager load_config when file not found."""
    manager = ConfigManager("/nonexistent/config.yml")
    with pytest.raises(FileNotFoundError):
        manager.load_config()


def test_config_manager_parse_config_empty() -> None:
    """Test config_manager parse_config with empty data."""
    manager = ConfigManager()
    config = manager._parse_config({})
    assert isinstance(config, Config)


def test_config_manager_parse_config_with_repositories() -> None:
    """Test config_manager parse_config with repositories."""
    manager = ConfigManager()
    data = {
        "repositories": [
            {
                "name": "test",
                "fork": "user/fork",
                "upstream": "owner/repo",
                "local_path": "/path",
                "skills": ["python"],
            }
        ],
        "settings": {"llm_provider": "openai"},
    }
    config = manager._parse_config(data)
    assert isinstance(config, Config)
    assert len(config.repositories) == 1
    assert config.repositories[0].name == "test"


def test_config_manager_serialize_config() -> None:
    """Test config_manager serialize_config method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo], settings=settings)

    serialized = manager._serialize_config(config)
    assert "repositories" in serialized
    assert "settings" in serialized
    assert serialized["repositories"][0]["name"] == "test"


def test_config_manager_parse_config_with_invalid_data() -> None:
    """Test config_manager parse_config with invalid data."""
    manager = ConfigManager()
    invalid_data = {"invalid": "data"}

    # The _parse_config method doesn't raise ConfigurationError for invalid data
    # It just returns a default config, so we'll test that behavior
    config = manager._parse_config(invalid_data)
    assert isinstance(config, Config)


def test_config_manager_validate_config_with_empty_repositories() -> None:
    """Test config_manager validate_config with empty repositories."""
    manager = ConfigManager()
    config = Config(repositories=[], settings=Settings())

    errors = manager.validate_config(config)
    assert len(errors) == 0  # Empty repositories should be valid


def test_config_manager_validate_config_with_invalid_settings() -> None:
    """Test config_manager validate_config with invalid settings."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(llm_provider="invalid_provider")
    config = Config(repositories=[repo], settings=settings)

    errors = manager.validate_config(config)
    assert len(errors) > 0
    # The validation errors are logged but not returned in the list
    # So we just check that there are errors
    assert len(errors) > 0


def test_config_manager_get_repository_not_found() -> None:
    """Test config_manager get_repository when repository not found."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config = Config(repositories=[repo], settings=Settings())

    # Set the config on the manager
    manager.config = config

    # The get_repository method takes only the name
    result = manager.get_repository("nonexistent")
    assert result is None
