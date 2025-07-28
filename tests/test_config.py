"""Test GitCo configuration management."""

import pytest
import tempfile
import os
from pathlib import Path

from gitco.config import (
    ConfigManager, Config, Repository, Settings,
    create_sample_config, get_config_manager
)


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file path."""
    with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as f:
        temp_path = f.name
        f.close()
        os.unlink(temp_path)  # Remove the file immediately
        yield temp_path


@pytest.fixture
def sample_config_data():
    """Sample configuration data."""
    return {
        "repositories": [
            {
                "name": "django",
                "fork": "username/django",
                "upstream": "django/django",
                "local_path": "~/code/django",
                "skills": ["python", "web", "orm"]
            }
        ],
        "settings": {
            "llm_provider": "openai",
            "api_key_env": "AETHERIUM_API_KEY",
            "default_path": "~/code",
            "analysis_enabled": True,
            "max_repos_per_batch": 10
        }
    }


def test_repository_dataclass():
    """Test Repository dataclass."""
    repo = Repository(
        name="test",
        fork="user/fork",
        upstream="owner/repo",
        local_path="/path/to/repo",
        skills=["python"],
        analysis_enabled=True
    )
    
    assert repo.name == "test"
    assert repo.fork == "user/fork"
    assert repo.upstream == "owner/repo"
    assert repo.local_path == "/path/to/repo"
    assert repo.skills == ["python"]
    assert repo.analysis_enabled is True


def test_settings_dataclass():
    """Test Settings dataclass."""
    settings = Settings(
        llm_provider="anthropic",
        api_key_env="CUSTOM_API_KEY",
        default_path="/custom/path",
        analysis_enabled=False,
        max_repos_per_batch=5
    )
    
    assert settings.llm_provider == "anthropic"
    assert settings.api_key_env == "CUSTOM_API_KEY"
    assert settings.default_path == "/custom/path"
    assert settings.analysis_enabled is False
    assert settings.max_repos_per_batch == 5


def test_config_dataclass():
    """Test Config dataclass."""
    repo = Repository(name="test", fork="user/fork", upstream="owner/repo", local_path="/path")
    settings = Settings(llm_provider="openai")
    
    config = Config(repositories=[repo], settings=settings)
    
    assert len(config.repositories) == 1
    assert config.repositories[0].name == "test"
    assert config.settings.llm_provider == "openai"


def test_config_manager_initialization():
    """Test ConfigManager initialization."""
    manager = ConfigManager()
    assert manager.config_path == "gitco-config.yml"
    
    manager = ConfigManager("custom.yml")
    assert manager.config_path == "custom.yml"


def test_create_sample_config():
    """Test create_sample_config function."""
    sample = create_sample_config()
    
    assert "repositories" in sample
    assert "settings" in sample
    assert len(sample["repositories"]) == 2
    assert sample["settings"]["llm_provider"] == "openai"


def test_config_manager_create_default_config(temp_config_file):
    """Test creating default configuration."""
    manager = ConfigManager(temp_config_file)
    config = manager.create_default_config()
    
    assert isinstance(config, Config)
    assert len(config.repositories) == 0
    assert config.settings.llm_provider == "openai"
    
    # Check that file was created
    assert os.path.exists(temp_config_file)


def test_config_manager_create_default_config_force(temp_config_file):
    """Test creating default configuration with force."""
    manager = ConfigManager(temp_config_file)
    
    # Create first config
    config1 = manager.create_default_config()
    
    # Create second config with force
    config2 = manager.create_default_config(force=True)
    
    assert isinstance(config2, Config)


def test_config_manager_create_default_config_exists(temp_config_file):
    """Test creating default configuration when file exists."""
    manager = ConfigManager(temp_config_file)
    manager.create_default_config()
    
    # Try to create again without force
    with pytest.raises(FileExistsError):
        manager.create_default_config()


def test_config_manager_load_config(temp_config_file, sample_config_data):
    """Test loading configuration from file."""
    import yaml
    
    # Write sample config to file
    with open(temp_config_file, 'w') as f:
        yaml.dump(sample_config_data, f)
    
    manager = ConfigManager(temp_config_file)
    config = manager.load_config()
    
    assert len(config.repositories) == 1
    assert config.repositories[0].name == "django"
    assert config.settings.llm_provider == "openai"


def test_config_manager_save_config(temp_config_file):
    """Test saving configuration to file."""
    manager = ConfigManager(temp_config_file)
    
    repo = Repository(name="test", fork="user/fork", upstream="owner/repo", local_path="/path")
    settings = Settings(llm_provider="anthropic")
    config = Config(repositories=[repo], settings=settings)
    
    manager.save_config(config)
    
    # Verify file was created
    assert os.path.exists(temp_config_file)
    
    # Load and verify
    loaded_config = manager.load_config()
    assert len(loaded_config.repositories) == 1
    assert loaded_config.repositories[0].name == "test"
    assert loaded_config.settings.llm_provider == "anthropic"


def test_config_manager_validate_config():
    """Test configuration validation."""
    manager = ConfigManager()
    
    # Valid config
    repo = Repository(name="test", fork="user/fork", upstream="owner/repo", local_path="/path")
    settings = Settings(llm_provider="openai")
    config = Config(repositories=[repo], settings=settings)
    
    errors = manager.validate_config(config)
    assert len(errors) == 0
    
    # Invalid config - missing name
    invalid_repo = Repository(name="", fork="user/fork", upstream="owner/repo", local_path="/path")
    invalid_config = Config(repositories=[invalid_repo], settings=settings)
    
    errors = manager.validate_config(invalid_config)
    assert len(errors) > 0
    assert "Repository name is required" in errors[0]


def test_config_manager_validate_config_duplicate_names():
    """Test configuration validation with duplicate repository names."""
    manager = ConfigManager()
    
    repo1 = Repository(name="test", fork="user/fork1", upstream="owner/repo1", local_path="/path1")
    repo2 = Repository(name="test", fork="user/fork2", upstream="owner/repo2", local_path="/path2")
    settings = Settings()
    config = Config(repositories=[repo1, repo2], settings=settings)
    
    errors = manager.validate_config(config)
    assert len(errors) > 0
    assert "Duplicate repository name: test" in errors[0]


def test_config_manager_validate_config_invalid_llm_provider():
    """Test configuration validation with invalid LLM provider."""
    manager = ConfigManager()
    
    repo = Repository(name="test", fork="user/fork", upstream="owner/repo", local_path="/path")
    settings = Settings(llm_provider="invalid_provider")
    config = Config(repositories=[repo], settings=settings)
    
    errors = manager.validate_config(config)
    assert len(errors) > 0
    assert "Invalid LLM provider" in errors[0]


def test_config_manager_get_repository():
    """Test getting repository by name."""
    manager = ConfigManager()
    
    repo1 = Repository(name="repo1", fork="user/fork1", upstream="owner/repo1", local_path="/path1")
    repo2 = Repository(name="repo2", fork="user/fork2", upstream="owner/repo2", local_path="/path2")
    config = Config(repositories=[repo1, repo2])
    manager.config = config
    
    found_repo = manager.get_repository("repo1")
    assert found_repo is not None
    assert found_repo.name == "repo1"
    
    not_found = manager.get_repository("nonexistent")
    assert not_found is None


def test_config_manager_add_repository():
    """Test adding repository to configuration."""
    manager = ConfigManager()
    
    repo1 = Repository(name="repo1", fork="user/fork1", upstream="owner/repo1", local_path="/path1")
    repo2 = Repository(name="repo2", fork="user/fork2", upstream="owner/repo2", local_path="/path2")
    
    manager.add_repository(repo1)
    assert len(manager.config.repositories) == 1
    
    manager.add_repository(repo2)
    assert len(manager.config.repositories) == 2
    
    # Add repository with same name (should replace)
    repo1_updated = Repository(name="repo1", fork="user/fork1_updated", upstream="owner/repo1", local_path="/path1")
    manager.add_repository(repo1_updated)
    assert len(manager.config.repositories) == 2
    assert manager.get_repository("repo1").fork == "user/fork1_updated"


def test_config_manager_remove_repository():
    """Test removing repository from configuration."""
    manager = ConfigManager()
    
    repo1 = Repository(name="repo1", fork="user/fork1", upstream="owner/repo1", local_path="/path1")
    repo2 = Repository(name="repo2", fork="user/fork2", upstream="owner/repo2", local_path="/path2")
    config = Config(repositories=[repo1, repo2])
    manager.config = config
    
    # Remove existing repository
    removed = manager.remove_repository("repo1")
    assert removed is True
    assert len(manager.config.repositories) == 1
    assert manager.config.repositories[0].name == "repo2"
    
    # Try to remove non-existent repository
    removed = manager.remove_repository("nonexistent")
    assert removed is False
    assert len(manager.config.repositories) == 1


def test_get_config_manager():
    """Test get_config_manager function."""
    manager = get_config_manager()
    assert isinstance(manager, ConfigManager)
    assert manager.config_path == "gitco-config.yml"
    
    manager = get_config_manager("custom.yml")
    assert manager.config_path == "custom.yml"


def test_config_manager_load_config_file_not_found():
    """Test loading configuration when file doesn't exist."""
    manager = ConfigManager("nonexistent.yml")
    
    with pytest.raises(FileNotFoundError):
        manager.load_config()


def test_config_manager_parse_config_empty():
    """Test parsing empty configuration."""
    manager = ConfigManager()
    config = manager._parse_config({})
    
    assert isinstance(config, Config)
    assert len(config.repositories) == 0
    assert config.settings.llm_provider == "openai"


def test_config_manager_parse_config_with_repositories():
    """Test parsing configuration with repositories."""
    manager = ConfigManager()
    data = {
        "repositories": [
            {
                "name": "test",
                "fork": "user/fork",
                "upstream": "owner/repo",
                "local_path": "/path",
                "skills": ["python"],
                "analysis_enabled": False
            }
        ]
    }
    
    config = manager._parse_config(data)
    
    assert len(config.repositories) == 1
    repo = config.repositories[0]
    assert repo.name == "test"
    assert repo.fork == "user/fork"
    assert repo.upstream == "owner/repo"
    assert repo.local_path == "/path"
    assert repo.skills == ["python"]
    assert repo.analysis_enabled is False


def test_config_manager_serialize_config():
    """Test serializing configuration."""
    manager = ConfigManager()
    
    repo = Repository(name="test", fork="user/fork", upstream="owner/repo", local_path="/path")
    settings = Settings(llm_provider="anthropic", max_repos_per_batch=5)
    config = Config(repositories=[repo], settings=settings)
    
    data = manager._serialize_config(config)
    
    assert "repositories" in data
    assert "settings" in data
    assert len(data["repositories"]) == 1
    assert data["repositories"][0]["name"] == "test"
    assert data["settings"]["llm_provider"] == "anthropic"
    assert data["settings"]["max_repos_per_batch"] == 5 
