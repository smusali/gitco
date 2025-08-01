"""Tests for configuration management."""

import os
import tempfile
from typing import Any

import pytest
import yaml

from gitco.config import (
    Config,
    ConfigManager,
    ConfigValidator,
    Repository,
    Settings,
    ValidationError,
    create_sample_config,
    get_config_manager,
)


@pytest.fixture
def temp_config_file() -> str:
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(create_sample_config(), f)
        return f.name


@pytest.fixture
def sample_config_data() -> dict[str, Any]:
    """Sample configuration data."""
    return create_sample_config()


def test_repository_dataclass() -> None:
    """Test Repository dataclass."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path/to/repo",
        skills=["python", "web"],
        analysis_enabled=True,
    )
    assert repo.name == "test"
    assert repo.fork == "user/fork"
    assert repo.upstream == "owner/repo"
    assert repo.local_path == "/path/to/repo"
    assert repo.skills == ["python", "web"]
    assert repo.analysis_enabled is True


def test_settings_dataclass() -> None:
    """Test Settings dataclass."""
    settings = Settings(
        llm_provider="openai",
        default_path="~/code",
        analysis_enabled=True,
        max_repos_per_batch=5,
    )
    assert settings.llm_provider == "openai"
    assert settings.default_path == "~/code"
    assert settings.analysis_enabled is True
    assert settings.max_repos_per_batch == 5


def test_config_dataclass() -> None:
    """Test Config dataclass."""
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings()
    config = Config(repositories=[repo], settings=settings)
    assert config.repositories is not None
    assert len(config.repositories) == 1
    assert config.repositories[0].name == "test"
    assert config.settings.llm_provider == "openai"


def test_config_manager_initialization() -> None:
    """Test ConfigManager initialization."""
    manager = ConfigManager()
    assert manager.config_path == os.path.expanduser("~/.gitco/config.yml")
    assert isinstance(manager.config, Config)


def test_create_sample_config() -> None:
    """Test create_sample_config function."""
    config = create_sample_config()
    assert "repositories" in config
    assert "settings" in config
    assert len(config["repositories"]) == 2


def test_config_manager_create_default_config(temp_config_file: str) -> None:
    """Test config_manager create_default_config method."""
    # Remove the existing file first
    if os.path.exists(temp_config_file):
        os.remove(temp_config_file)

    manager = ConfigManager(temp_config_file)
    config = manager.create_default_config()
    assert isinstance(config, Config)
    assert os.path.exists(temp_config_file)


def test_config_manager_create_default_config_force(temp_config_file: str) -> None:
    """Test config_manager create_default_config method with force."""
    manager = ConfigManager(temp_config_file)
    config = manager.create_default_config(force=True)
    assert isinstance(config, Config)


def test_config_manager_create_default_config_exists(temp_config_file: str) -> None:
    """Test config_manager create_default_config method when file exists."""
    manager = ConfigManager(temp_config_file)
    with pytest.raises(FileExistsError):
        manager.create_default_config()


def test_config_manager_load_config(
    temp_config_file: str, sample_config_data: dict[str, Any]
) -> None:
    """Test config_manager load_config method."""
    manager = ConfigManager(temp_config_file)
    config = manager.load_config()
    assert isinstance(config, Config)
    assert config.repositories is not None
    assert len(config.repositories) == 2


def test_config_manager_save_config(temp_config_file: str) -> None:
    """Test config_manager save_config method."""
    manager = ConfigManager(temp_config_file)
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config = Config(repositories=[repo], settings=Settings())

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
    assert manager.config.repositories is not None
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
    assert manager.config.repositories is not None
    assert len(manager.config.repositories) == 1

    # Remove repository
    result = manager.remove_repository("test")
    assert result is True
    assert manager.config.repositories is not None
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
    """Test config_manager _parse_config method with empty data."""
    manager = ConfigManager()
    config = manager._parse_config({})
    assert isinstance(config, Config)
    assert config.repositories is None


def test_config_manager_parse_config_with_repositories() -> None:
    """Test config_manager _parse_config method with repositories."""
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
        ]
    }
    config = manager._parse_config(data)
    assert config.repositories is not None
    assert len(config.repositories) == 1
    assert config.repositories[0].name == "test"
    assert config.repositories[0].skills == ["python"]


def test_config_manager_serialize_config() -> None:
    """Test config_manager _serialize_config method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config = Config(repositories=[repo], settings=Settings())

    data = manager._serialize_config(config)
    assert "repositories" in data
    assert "settings" in data
    assert len(data["repositories"]) == 1


def test_config_manager_parse_config_with_invalid_data() -> None:
    """Test config_manager _parse_config method with invalid data."""
    manager = ConfigManager()
    config = manager._parse_config({"invalid": "data"})
    assert isinstance(config, Config)


def test_config_manager_validate_config_with_empty_repositories() -> None:
    """Test config_manager validate_config with empty repositories."""
    manager = ConfigManager()
    config = Config(repositories=[], settings=Settings())

    errors = manager.validate_config(config)
    assert isinstance(errors, list)


def test_config_manager_validate_config_with_invalid_settings() -> None:
    """Test config_manager validate_config with invalid settings."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(max_repos_per_batch=0)
    config = Config(repositories=[repo], settings=settings)

    errors = manager.validate_config(config)
    assert len(errors) > 0


def test_config_manager_get_repository_not_found() -> None:
    """Test config_manager get_repository method when repository not found."""
    manager = ConfigManager()
    result = manager.get_repository("nonexistent")
    assert result is None


def test_repository_with_all_fields() -> None:
    """Test Repository with all fields set."""
    repo = Repository(
        name="test-repo",
        fork="https://github.com/user/fork",
        upstream="https://github.com/owner/repo",
        local_path="/path/to/repo",
        skills=["python", "web", "api"],
        analysis_enabled=True,
        sync_frequency="0 */6 * * *",
        language="python",
    )
    assert repo.name == "test-repo"
    assert repo.fork == "https://github.com/user/fork"
    assert repo.upstream == "https://github.com/owner/repo"
    assert repo.local_path == "/path/to/repo"
    assert repo.skills == ["python", "web", "api"]
    assert repo.analysis_enabled is True
    assert repo.sync_frequency == "0 */6 * * *"
    assert repo.language == "python"


def test_repository_with_defaults() -> None:
    """Test Repository with default values."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
    )
    assert repo.skills is None
    assert repo.analysis_enabled is True
    assert repo.sync_frequency is None
    assert repo.language is None


def test_repository_with_disabled_analysis() -> None:
    """Test Repository with analysis disabled."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
        analysis_enabled=False,
    )
    assert repo.analysis_enabled is False


def test_repository_with_sync_frequency() -> None:
    """Test Repository with sync frequency."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
        sync_frequency="0 2 * * *",
    )
    assert repo.sync_frequency == "0 2 * * *"


def test_repository_with_skills() -> None:
    """Test Repository with skills."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
        skills=["python", "javascript", "docker"],
    )
    assert repo.skills == ["python", "javascript", "docker"]


def test_settings_with_all_fields() -> None:
    """Test Settings with all fields set."""
    settings = Settings(
        llm_provider="anthropic",
        default_path="~/projects",
        analysis_enabled=False,
        max_repos_per_batch=20,
        git_timeout=600,
        rate_limit_delay=2.0,
        log_level="DEBUG",
        github_token_env="CUSTOM_GITHUB_TOKEN",
        github_username_env="CUSTOM_GITHUB_USERNAME",
        github_password_env="CUSTOM_GITHUB_PASSWORD",
        github_api_url="https://api.github.com",
        github_timeout=60,
        github_max_retries=5,
    )
    assert settings.llm_provider == "anthropic"
    assert settings.default_path == "~/projects"
    assert settings.analysis_enabled is False
    assert settings.max_repos_per_batch == 20
    assert settings.git_timeout == 600
    assert settings.rate_limit_delay == 2.0
    assert settings.log_level == "DEBUG"
    assert settings.github_token_env == "CUSTOM_GITHUB_TOKEN"
    assert settings.github_username_env == "CUSTOM_GITHUB_USERNAME"
    assert settings.github_password_env == "CUSTOM_GITHUB_PASSWORD"
    assert settings.github_api_url == "https://api.github.com"
    assert settings.github_timeout == 60
    assert settings.github_max_retries == 5


def test_settings_with_defaults() -> None:
    """Test Settings with default values."""
    settings = Settings()
    assert settings.llm_provider == "openai"
    assert settings.default_path == "~/code"
    assert settings.analysis_enabled is True
    assert settings.max_repos_per_batch == 10
    assert settings.git_timeout == 300
    assert settings.rate_limit_delay == 1.0
    assert settings.log_level == "INFO"


def test_settings_custom_timeout() -> None:
    """Test Settings with custom timeout."""
    settings = Settings(git_timeout=900)
    assert settings.git_timeout == 900


def test_settings_custom_batch_size() -> None:
    """Test Settings with custom batch size."""
    settings = Settings(max_repos_per_batch=15)
    assert settings.max_repos_per_batch == 15


def test_config_with_repositories() -> None:
    """Test Config with multiple repositories."""
    repo1 = Repository(
        name="repo1", fork="user/repo1", upstream="owner/repo1", local_path="/path1"
    )
    repo2 = Repository(
        name="repo2", fork="user/repo2", upstream="owner/repo2", local_path="/path2"
    )
    config = Config(repositories=[repo1, repo2], settings=Settings())
    assert config.repositories is not None
    assert len(config.repositories) == 2
    assert config.repositories[0].name == "repo1"
    assert config.repositories[1].name == "repo2"


def test_config_with_custom_settings() -> None:
    """Test Config with custom settings."""
    settings = Settings(llm_provider="anthropic", max_repos_per_batch=25)
    config = Config(repositories=[], settings=settings)
    assert config.settings.llm_provider == "anthropic"
    assert config.settings.max_repos_per_batch == 25


def test_config_empty() -> None:
    """Test Config with no repositories."""
    config = Config()
    assert config.repositories is None
    assert isinstance(config.settings, Settings)


def test_config_with_mixed_repositories() -> None:
    """Test Config with repositories having different configurations."""
    repo1 = Repository(
        name="python-repo",
        fork="user/python-repo",
        upstream="owner/python-repo",
        local_path="/path/python",
        skills=["python", "web"],
        analysis_enabled=True,
    )
    repo2 = Repository(
        name="js-repo",
        fork="user/js-repo",
        upstream="owner/js-repo",
        local_path="/path/js",
        skills=["javascript", "frontend"],
        analysis_enabled=False,
    )
    config = Config(repositories=[repo1, repo2], settings=Settings())
    assert config.repositories is not None
    assert len(config.repositories) == 2
    assert config.repositories[0].analysis_enabled is True
    assert config.repositories[1].analysis_enabled is False


def test_config_with_skills_repositories() -> None:
    """Test Config with repositories having skills."""
    repo1 = Repository(
        name="backend",
        fork="user/backend",
        upstream="owner/backend",
        local_path="/path/backend",
        skills=["python", "api", "database"],
    )
    repo2 = Repository(
        name="frontend",
        fork="user/frontend",
        upstream="owner/frontend",
        local_path="/path/frontend",
        skills=["javascript", "react", "css"],
    )
    config = Config(repositories=[repo1, repo2], settings=Settings())
    assert config.repositories is not None
    assert len(config.repositories) == 2
    assert "python" in config.repositories[0].skills
    assert "javascript" in config.repositories[1].skills


def test_config_manager_custom_path() -> None:
    """Test ConfigManager with custom config path."""
    manager = ConfigManager("/custom/path/config.yml")
    assert manager.config_path == "/custom/path/config.yml"


def test_config_manager_default_path() -> None:
    """Test ConfigManager with default config path."""
    manager = ConfigManager()
    assert manager.config_path == os.path.expanduser("~/.gitco/config.yml")


def test_config_manager_initial_config() -> None:
    """Test ConfigManager initial configuration."""
    manager = ConfigManager()
    assert isinstance(manager.config, Config)
    assert manager.config.repositories is None
    assert isinstance(manager.config.settings, Settings)


def test_repository_with_custom_analysis_settings() -> None:
    """Test Repository with custom analysis settings."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
        analysis_enabled=False,
    )
    assert repo.analysis_enabled is False


def test_repository_with_minimal_fields() -> None:
    """Test Repository with minimal required fields."""
    repo = Repository(
        name="minimal",
        fork="user/minimal",
        upstream="owner/minimal",
        local_path="/minimal/path",
    )
    assert repo.name == "minimal"
    assert repo.fork == "user/minimal"
    assert repo.upstream == "owner/minimal"
    assert repo.local_path == "/minimal/path"
    assert repo.skills is None
    assert repo.analysis_enabled is True


def test_repository_equality() -> None:
    """Test Repository equality."""
    repo1 = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    repo2 = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    assert repo1 == repo2


def test_repository_inequality() -> None:
    """Test Repository inequality."""
    repo1 = Repository(
        name="test1", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    repo2 = Repository(
        name="test2", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    assert repo1 != repo2


def test_repository_repr() -> None:
    """Test Repository string representation."""
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    repr_str = repr(repo)
    assert "Repository" in repr_str
    assert "test" in repr_str


def test_settings_with_custom_api_keys() -> None:
    """Test Settings with custom API key environment variables."""
    settings = Settings(
        github_token_env="CUSTOM_TOKEN",
        github_username_env="CUSTOM_USERNAME",
        github_password_env="CUSTOM_PASSWORD",
    )
    assert settings.github_token_env == "CUSTOM_TOKEN"
    assert settings.github_username_env == "CUSTOM_USERNAME"
    assert settings.github_password_env == "CUSTOM_PASSWORD"


def test_settings_with_environment_variables() -> None:
    """Test Settings with default environment variable names."""
    settings = Settings()
    assert settings.github_token_env == "GITHUB_TOKEN"
    assert settings.github_username_env == "GITHUB_USERNAME"
    assert settings.github_password_env == "GITHUB_PASSWORD"


def test_settings_equality() -> None:
    """Test Settings equality."""
    settings1 = Settings(llm_provider="openai", max_repos_per_batch=10)
    settings2 = Settings(llm_provider="openai", max_repos_per_batch=10)
    assert settings1 == settings2


def test_settings_inequality() -> None:
    """Test Settings inequality."""
    settings1 = Settings(llm_provider="openai", max_repos_per_batch=10)
    settings2 = Settings(llm_provider="anthropic", max_repos_per_batch=10)
    assert settings1 != settings2


def test_settings_repr() -> None:
    """Test Settings string representation."""
    settings = Settings(llm_provider="openai")
    repr_str = repr(settings)
    assert "Settings" in repr_str
    assert "openai" in repr_str


def test_config_with_custom_settings_and_repositories() -> None:
    """Test Config with both custom settings and repositories."""
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(
        llm_provider="anthropic",
        default_path="~/custom/path",
        analysis_enabled=False,
        max_repos_per_batch=15,
    )
    config = Config(repositories=[repo], settings=settings)
    assert config.repositories is not None
    assert len(config.repositories) == 1
    assert config.settings.llm_provider == "anthropic"
    assert config.settings.default_path == "~/custom/path"
    assert config.settings.analysis_enabled is False
    assert config.settings.max_repos_per_batch == 15


def test_config_with_empty_repositories() -> None:
    """Test Config with empty repositories list."""
    config = Config(repositories=[], settings=Settings())
    assert config.repositories is not None
    assert len(config.repositories) == 0
    assert isinstance(config.settings, Settings)


def test_config_equality() -> None:
    """Test Config equality."""
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config1 = Config(repositories=[repo], settings=Settings())
    config2 = Config(repositories=[repo], settings=Settings())
    assert config1 == config2


def test_config_inequality() -> None:
    """Test Config inequality."""
    repo1 = Repository(
        name="test1", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    repo2 = Repository(
        name="test2", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config1 = Config(repositories=[repo1], settings=Settings())
    config2 = Config(repositories=[repo2], settings=Settings())
    assert config1 != config2


def test_config_repr() -> None:
    """Test Config string representation."""
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    config = Config(repositories=[repo], settings=Settings())
    repr_str = repr(config)
    assert "Config" in repr_str


def test_config_manager_with_custom_config() -> None:
    """Test ConfigManager with custom configuration."""
    manager = ConfigManager()
    repo = Repository(
        name="custom", fork="user/custom", upstream="owner/custom", local_path="/custom"
    )
    settings = Settings(llm_provider="anthropic")
    config = Config(repositories=[repo], settings=settings)
    manager.config = config
    assert manager.config.repositories is not None
    assert len(manager.config.repositories) == 1
    assert manager.config.settings.llm_provider == "anthropic"


def test_config_manager_validate_config_with_valid_data() -> None:
    """Test ConfigManager validate_config with valid data."""
    manager = ConfigManager()
    repo = Repository(
        name="valid-repo",
        fork="https://github.com/user/fork",
        upstream="https://github.com/owner/repo",
        local_path="/valid/path",
        skills=["python"],
    )
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo], settings=settings)

    errors = manager.validate_config(config)
    assert isinstance(errors, list)


def test_config_manager_validate_config_with_invalid_repository() -> None:
    """Test ConfigManager validate_config with invalid repository."""
    manager = ConfigManager()
    repo = Repository(
        name="",  # Invalid: empty name
        fork="",  # Invalid: empty fork
        upstream="",  # Invalid: empty upstream
        local_path="",  # Invalid: empty path
    )
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo], settings=settings)

    errors = manager.validate_config(config)
    assert len(errors) > 0


def test_config_manager_get_repository_by_name() -> None:
    """Test ConfigManager get_repository by name."""
    manager = ConfigManager()
    repo = Repository(
        name="test-repo", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    manager.add_repository(repo)
    result = manager.get_repository("test-repo")
    assert result is not None
    assert result.name == "test-repo"


def test_config_manager_remove_repository_by_name() -> None:
    """Test ConfigManager remove_repository by name."""
    manager = ConfigManager()
    repo = Repository(
        name="test-repo", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    manager.add_repository(repo)
    assert manager.config.repositories is not None
    assert len(manager.config.repositories) == 1

    result = manager.remove_repository("test-repo")
    assert result is True
    assert manager.config.repositories is not None
    assert len(manager.config.repositories) == 0


def test_config_manager_load_config_exception_handling() -> None:
    """Test ConfigManager load_config exception handling."""
    manager = ConfigManager("/nonexistent/file.yml")
    with pytest.raises(FileNotFoundError):
        manager.load_config()


def test_config_manager_save_config_exception_handling() -> None:
    """Test ConfigManager save_config exception handling."""
    manager = ConfigManager("/invalid/path/config.yml")
    config = Config()
    # This should raise an exception due to invalid path
    with pytest.raises((OSError, PermissionError)):
        manager.save_config(config)


def test_config_manager_validate_config_edge_cases() -> None:
    """Test validate_config with edge cases (lines 209-210, 230-235, 258-259, 272-273)."""
    manager = ConfigManager()

    # Test with None config
    with pytest.raises((TypeError, AttributeError)):
        manager.validate_config(None)  # type: ignore

    # Test with empty config
    config = Config()
    errors = manager.validate_config(config)
    assert isinstance(errors, list)


def test_config_manager_get_github_credentials() -> None:
    """Test ConfigManager get_github_credentials method."""
    manager = ConfigManager()
    repo = Repository(
        name="test", fork="user/fork", upstream="owner/repo", local_path="/path"
    )
    settings = Settings(
        github_token_env="TEST_GITHUB_TOKEN",
        github_username_env="TEST_GITHUB_USERNAME",
        github_password_env="TEST_GITHUB_PASSWORD",
        github_api_url="https://api.github.com",
        github_timeout=30,
        github_max_retries=3,
    )
    config = Config(repositories=[repo], settings=settings)
    manager.config = config

    credentials = manager.get_github_credentials()
    assert "token" in credentials
    assert "username" in credentials
    assert "password" in credentials
    assert "base_url" in credentials
    assert "timeout" in credentials
    assert "max_retries" in credentials


def test_config_manager_get_github_credentials_missing_env() -> None:
    """Test ConfigManager get_github_credentials with missing environment variables."""
    manager = ConfigManager()
    config = Config(repositories=[], settings=Settings())
    manager.config = config

    credentials = manager.get_github_credentials()
    assert credentials["token"] is None
    assert credentials["username"] is None
    assert credentials["password"] is None


# New tests for enhanced validation functionality


def test_validation_error_dataclass() -> None:
    """Test ValidationError dataclass."""
    error = ValidationError(
        field="test.field",
        message="Test error message",
        severity="error",
        context={"key": "value"},
        suggestion="Test suggestion",
    )
    assert error.field == "test.field"
    assert error.message == "Test error message"
    assert error.severity == "error"
    assert error.context == {"key": "value"}
    assert error.suggestion == "Test suggestion"


def test_validation_error_str_representation() -> None:
    """Test ValidationError string representation."""
    error = ValidationError(
        field="test.field", message="Test error message", suggestion="Test suggestion"
    )
    error_str = str(error)
    assert "test.field: Test error message" in error_str
    assert "(suggestion: Test suggestion)" in error_str


def test_config_validator_initialization() -> None:
    """Test ConfigValidator initialization."""
    validator = ConfigValidator()
    assert isinstance(validator.errors, list)
    assert isinstance(validator.warnings, list)
    assert len(validator.errors) == 0
    assert len(validator.warnings) == 0


def test_config_validator_validate_settings_valid() -> None:
    """Test ConfigValidator _validate_settings with valid settings."""
    validator = ConfigValidator()
    settings = Settings(
        llm_provider="openai",
        max_repos_per_batch=10,
        git_timeout=300,
        rate_limit_delay=1.0,
        log_level="INFO",
    )

    validator._validate_settings(settings)
    assert len(validator.errors) == 0


def test_config_validator_validate_settings_invalid_llm_provider() -> None:
    """Test ConfigValidator _validate_settings with invalid LLM provider."""
    validator = ConfigValidator()
    settings = Settings(llm_provider="invalid_provider")

    validator._validate_settings(settings)
    assert len(validator.errors) > 0
    assert any("llm_provider" in error.field for error in validator.errors)


def test_config_validator_validate_settings_invalid_batch_size() -> None:
    """Test ConfigValidator _validate_settings with invalid batch size."""
    validator = ConfigValidator()
    settings = Settings(max_repos_per_batch=0)

    validator._validate_settings(settings)
    assert len(validator.errors) > 0
    assert any("max_repos_per_batch" in error.field for error in validator.errors)


def test_config_validator_validate_settings_invalid_timeout() -> None:
    """Test ConfigValidator _validate_settings with invalid timeout."""
    validator = ConfigValidator()
    settings = Settings(git_timeout=10)  # Too low

    validator._validate_settings(settings)
    assert len(validator.errors) > 0
    assert any("git_timeout" in error.field for error in validator.errors)


def test_config_validator_validate_github_settings_valid() -> None:
    """Test ConfigValidator _validate_github_settings with valid settings."""
    validator = ConfigValidator()
    settings = Settings(
        github_api_url="https://api.github.com", github_timeout=30, github_max_retries=3
    )

    validator._validate_github_settings(settings)
    assert len(validator.errors) == 0


def test_config_validator_validate_github_settings_invalid_url() -> None:
    """Test ConfigValidator _validate_github_settings with invalid URL."""
    validator = ConfigValidator()
    settings = Settings(github_api_url="invalid-url")

    validator._validate_github_settings(settings)
    assert len(validator.errors) > 0
    assert any("github_api_url" in error.field for error in validator.errors)


def test_config_validator_validate_repositories_empty() -> None:
    """Test ConfigValidator _validate_repositories with empty list."""
    validator = ConfigValidator()

    validator._validate_repositories([])
    assert len(validator.warnings) > 0
    assert any("repositories" in warning.field for warning in validator.warnings)


def test_config_validator_validate_repositories_duplicate_names() -> None:
    """Test ConfigValidator _validate_repositories with duplicate names."""
    validator = ConfigValidator()
    repos = [
        Repository(
            name="test", fork="user/fork1", upstream="owner/repo1", local_path="/path1"
        ),
        Repository(
            name="test", fork="user/fork2", upstream="owner/repo2", local_path="/path2"
        ),
    ]

    validator._validate_repositories(repos)
    assert len(validator.errors) > 0
    assert any(
        "Duplicate repository name" in error.message for error in validator.errors
    )


def test_config_validator_validate_repository_valid() -> None:
    """Test ConfigValidator _validate_repository with valid repository."""
    validator = ConfigValidator()
    repo = Repository(
        name="test-repo",
        fork="https://github.com/user/fork",
        upstream="https://github.com/owner/repo",
        local_path="/valid/path",
    )

    validator._validate_repository(repo, 0)
    assert len(validator.errors) == 0


def test_config_validator_validate_repository_invalid_name() -> None:
    """Test ConfigValidator _validate_repository with invalid name."""
    validator = ConfigValidator()
    repo = Repository(
        name="",  # Empty name
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
    )

    validator._validate_repository(repo, 0)
    assert len(validator.errors) > 0
    assert any("name" in error.field for error in validator.errors)


def test_config_validator_validate_repository_invalid_name_format() -> None:
    """Test ConfigValidator _validate_repository with invalid name format."""
    validator = ConfigValidator()
    repo = Repository(
        name="invalid name with spaces",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path",
    )

    validator._validate_repository(repo, 0)
    assert len(validator.errors) > 0
    assert any("name" in error.field for error in validator.errors)


def test_config_validator_validate_repository_url_valid() -> None:
    """Test ConfigValidator _validate_repository_url with valid URL."""
    validator = ConfigValidator()

    validator._validate_repository_url(
        "https://github.com/user/repo", "test.field", "fork"
    )
    assert len(validator.errors) == 0


def test_config_validator_validate_repository_url_invalid() -> None:
    """Test ConfigValidator _validate_repository_url with invalid URL."""
    validator = ConfigValidator()

    validator._validate_repository_url("invalid-url", "test.field", "fork")
    assert len(validator.errors) > 0
    assert any("test.field" in error.field for error in validator.errors)


def test_config_validator_validate_skills_valid() -> None:
    """Test ConfigValidator _validate_skills with valid skills."""
    validator = ConfigValidator()
    skills = ["python", "javascript", "docker"]

    validator._validate_skills(skills, "test.field")
    assert len(validator.errors) == 0


def test_config_validator_validate_skills_invalid() -> None:
    """Test ConfigValidator _validate_skills with invalid skills."""
    validator = ConfigValidator()
    skills = ["python", "", "invalid skill with spaces"]

    validator._validate_skills(skills, "test.field")
    assert len(validator.errors) > 0


def test_config_validator_validate_sync_frequency_valid() -> None:
    """Test ConfigValidator _validate_sync_frequency with valid format."""
    validator = ConfigValidator()

    validator._validate_sync_frequency("0 2 * * *", "test.field")
    assert len(validator.errors) == 0


def test_config_validator_validate_sync_frequency_invalid() -> None:
    """Test ConfigValidator _validate_sync_frequency with invalid format."""
    validator = ConfigValidator()

    validator._validate_sync_frequency("invalid-cron", "test.field")
    assert len(validator.errors) > 0


def test_config_validator_validate_language_valid() -> None:
    """Test ConfigValidator _validate_language with valid language."""
    validator = ConfigValidator()

    validator._validate_language("python", "test.field")
    assert len(validator.errors) == 0
    assert len(validator.warnings) == 0


def test_config_validator_validate_language_unknown() -> None:
    """Test ConfigValidator _validate_language with unknown language."""
    validator = ConfigValidator()

    validator._validate_language("unknown_language", "test.field")
    assert len(validator.warnings) > 0
    assert any("test.field" in warning.field for warning in validator.warnings)


def test_config_validator_validate_cross_references() -> None:
    """Test ConfigValidator _validate_cross_references."""
    validator = ConfigValidator()
    config = Config(
        repositories=[
            Repository(
                name="test",
                fork="user/fork",
                upstream="owner/repo",
                local_path="~/code/test",
            )
        ],
        settings=Settings(default_path="~/code"),
    )

    validator._validate_cross_references(config)
    # Should generate warnings for default path usage
    assert len(validator.warnings) > 0


def test_config_manager_get_validation_report() -> None:
    """Test ConfigManager get_validation_report method."""
    manager = ConfigManager()
    repo = Repository(
        name="test",
        fork="https://github.com/user/fork",
        upstream="https://github.com/owner/repo",
        local_path="/path",
    )
    config = Config(repositories=[repo], settings=Settings())

    report = manager.get_validation_report(config)
    assert "errors" in report
    assert "warnings" in report
    assert isinstance(report["errors"], list)
    assert isinstance(report["warnings"], list)


def test_config_validator_validate_config_comprehensive() -> None:
    """Test ConfigValidator validate_config with comprehensive validation."""
    validator = ConfigValidator()

    # Valid config
    repo = Repository(
        name="test-repo",
        fork="https://github.com/user/fork",
        upstream="https://github.com/owner/repo",
        local_path="/valid/path",
        skills=["python", "web"],
    )
    settings = Settings(llm_provider="openai", max_repos_per_batch=10, git_timeout=300)
    config = Config(repositories=[repo], settings=settings)

    result = validator.validate_config(config)
    assert "errors" in result
    assert "warnings" in result
    assert isinstance(result["errors"], list)
    assert isinstance(result["warnings"], list)


def test_config_manager_with_none_values() -> None:
    """Test ConfigManager with None values in config."""
    # Test with None repositories
    config = Config(repositories=None, settings=Settings())

    # Should handle None values gracefully
    assert config.repositories is None
    assert config.settings is not None


def test_repository_with_none_skills() -> None:
    """Test Repository with None skills field."""
    repo = Repository(
        name="test-repo",
        fork="https://github.com/user/fork",
        upstream="https://github.com/owner/repo",
        local_path="/path/to/repo",
        skills=None,
    )

    assert repo.name == "test-repo"
    assert repo.skills is None


def test_settings_with_none_values() -> None:
    """Test Settings with None values."""
    settings = Settings()

    # Test default values
    assert settings.llm_provider == "openai"
    assert settings.github_token_env == "GITHUB_TOKEN"
    assert settings.max_repos_per_batch == 10
    assert settings.git_timeout == 300


def test_config_validator_with_empty_config() -> None:
    """Test ConfigValidator with completely empty config."""
    validator = ConfigValidator()

    # Create minimal config with None values
    config = Config(repositories=None, settings=Settings())

    result = validator.validate_config(config)

    # Should handle None values gracefully
    assert "errors" in result
    assert "warnings" in result
    assert isinstance(result["errors"], list)
    assert isinstance(result["warnings"], list)


def test_config_manager_serialization_with_none_values() -> None:
    """Test ConfigManager serialization with None values."""
    manager = ConfigManager()

    # Create config with None values
    config = Config(
        repositories=None,
        settings=Settings(llm_provider="openai", github_token_env="GITHUB_TOKEN"),
    )

    # Should serialize without errors
    serialized = manager._serialize_config(config)
    assert isinstance(serialized, dict)

    # Should deserialize without errors
    deserialized = manager._parse_config(serialized)
    assert deserialized.repositories is None
    assert deserialized.settings.llm_provider == "openai"
