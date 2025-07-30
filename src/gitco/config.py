"""Configuration management for GitCo."""

import os
from dataclasses import dataclass, field
from typing import Any, Optional, Union

import yaml

from .git_ops import GitRepositoryManager
from .utils import (
    ConfigurationError,
    get_logger,
    log_configuration_loaded,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    log_validation_result,
)


@dataclass
class Repository:
    """Repository configuration."""

    name: str
    fork: str
    upstream: str
    local_path: str
    skills: list[str] = field(default_factory=list)
    analysis_enabled: bool = True
    sync_frequency: Optional[str] = None
    language: Optional[str] = None


@dataclass
class Settings:
    """Global settings configuration."""

    llm_provider: str = "openai"
    default_path: str = "~/code"
    analysis_enabled: bool = True
    max_repos_per_batch: int = 10
    git_timeout: int = 300
    rate_limit_delay: float = 1.0
    log_level: str = "INFO"
    # GitHub API settings
    github_token_env: str = "GITHUB_TOKEN"
    github_username_env: str = "GITHUB_USERNAME"
    github_password_env: str = "GITHUB_PASSWORD"
    github_api_url: str = "https://api.github.com"
    github_timeout: int = 30
    github_max_retries: int = 3


@dataclass
class Config:
    """Main configuration class."""

    repositories: list[Repository] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)


class ConfigManager:
    """Manages GitCo configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file. Defaults to 'gitco-config.yml'.
        """
        self.config_path = config_path or "gitco-config.yml"
        self.config = Config()

    def load_config(self) -> Config:
        """Load configuration from file.

        Returns:
            Loaded configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            yaml.YAMLError: If configuration file has invalid YAML.
        """
        get_logger()
        log_operation_start("configuration loading", config_path=self.config_path)

        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(
                    f"Configuration file not found: {self.config_path}"
                )

            with open(self.config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            config = self._parse_config(data)
            self.config = config  # Update the instance config
            log_operation_success("configuration loading", config_path=self.config_path)
            log_configuration_loaded(self.config_path, len(config.repositories))

            return config

        except Exception as e:
            log_operation_failure(
                "configuration loading", e, config_path=self.config_path
            )
            raise

    def save_config(self, config: Config) -> None:
        """Save configuration to file.

        Args:
            config: Configuration to save.
        """
        get_logger()
        log_operation_start("configuration saving", config_path=self.config_path)

        try:
            data = self._serialize_config(config)

            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)

            log_operation_success("configuration saving", config_path=self.config_path)

        except Exception as e:
            log_operation_failure(
                "configuration saving", e, config_path=self.config_path
            )
            raise

    def create_default_config(self, force: bool = False) -> Config:
        """Create default configuration file.

        Args:
            force: Whether to overwrite existing file.

        Returns:
            Default configuration.
        """
        if os.path.exists(self.config_path) and not force:
            raise FileExistsError(
                f"Configuration file already exists: {self.config_path}"
            )

        config = Config()
        self.save_config(config)
        return config

    def validate_config(self, config: Config) -> list[str]:
        """Validate configuration.

        Args:
            config: Configuration to validate.

        Returns:
            List of validation errors.
        """
        get_logger()
        log_operation_start("configuration validation")

        errors = []

        # Validate repositories
        repo_names = set()
        git_manager = GitRepositoryManager()

        for repo in config.repositories:
            if not repo.name:
                errors.append("Repository name is required")
                log_validation_result(
                    "repository name", False, f"Repository {repo.name} missing name"
                )
            elif repo.name in repo_names:
                errors.append(f"Duplicate repository name: {repo.name}")
                log_validation_result(
                    "repository name uniqueness", False, f"Duplicate name: {repo.name}"
                )
            else:
                repo_names.add(repo.name)
                log_validation_result(
                    "repository name", True, f"Repository {repo.name}"
                )

            if not repo.fork:
                errors.append(f"Fork URL is required for repository: {repo.name}")
                log_validation_result(
                    "repository fork", False, f"Repository {repo.name} missing fork URL"
                )
            else:
                log_validation_result(
                    "repository fork", True, f"Repository {repo.name}"
                )

            if not repo.upstream:
                errors.append(f"Upstream URL is required for repository: {repo.name}")
                log_validation_result(
                    "repository upstream",
                    False,
                    f"Repository {repo.name} missing upstream URL",
                )
            else:
                log_validation_result(
                    "repository upstream", True, f"Repository {repo.name}"
                )

            if not repo.local_path:
                errors.append(f"Local path is required for repository: {repo.name}")
                log_validation_result(
                    "repository local_path",
                    False,
                    f"Repository {repo.name} missing local path",
                )
            else:
                # Validate git repository at local path
                is_valid, repo_errors = git_manager.validate_repository_path(
                    repo.local_path
                )
                if not is_valid:
                    errors.extend(
                        [f"Repository {repo.name}: {error}" for error in repo_errors]
                    )
                    log_validation_result(
                        "repository git validation",
                        False,
                        f"Repository {repo.name} at {repo.local_path}",
                    )
                else:
                    log_validation_result(
                        "repository git validation",
                        True,
                        f"Repository {repo.name} at {repo.local_path}",
                    )
                    log_validation_result(
                        "repository local_path", True, f"Repository {repo.name}"
                    )

        # Validate settings
        if config.settings.llm_provider not in [
            "openai",
            "anthropic",
        ]:
            errors.append("Invalid LLM provider. Must be one of: openai, anthropic")
            log_validation_result(
                "settings llm_provider",
                False,
                f"Invalid provider: {config.settings.llm_provider}",
            )
        else:
            log_validation_result(
                "settings llm_provider",
                True,
                f"Provider: {config.settings.llm_provider}",
            )

        if config.settings.max_repos_per_batch < 1:
            errors.append("max_repos_per_batch must be at least 1")
            log_validation_result(
                "settings max_repos_per_batch",
                False,
                f"Value: {config.settings.max_repos_per_batch}",
            )
        else:
            log_validation_result(
                "settings max_repos_per_batch",
                True,
                f"Value: {config.settings.max_repos_per_batch}",
            )

        if config.settings.git_timeout < 30:
            errors.append("git_timeout must be at least 30 seconds")
            log_validation_result(
                "settings git_timeout", False, f"Value: {config.settings.git_timeout}"
            )
        else:
            log_validation_result(
                "settings git_timeout", True, f"Value: {config.settings.git_timeout}"
            )

        if errors:
            log_operation_failure(
                "configuration validation", ConfigurationError("Validation failed")
            )
        else:
            log_operation_success("configuration validation")

        return errors

    def get_repository(self, name: str) -> Optional[Repository]:
        """Get repository by name.

        Args:
            name: Repository name.

        Returns:
            Repository configuration or None if not found.
        """
        for repo in self.config.repositories:
            if repo.name == name:
                return repo
        return None

    def add_repository(self, repo: Repository) -> None:
        """Add repository to configuration.

        Args:
            repo: Repository to add.
        """
        # Remove existing repository with same name
        self.config.repositories = [
            r for r in self.config.repositories if r.name != repo.name
        ]
        self.config.repositories.append(repo)

    def remove_repository(self, name: str) -> bool:
        """Remove repository from configuration.

        Args:
            name: Repository name to remove.

        Returns:
            True if repository was removed, False if not found.
        """
        initial_count = len(self.config.repositories)
        self.config.repositories = [
            r for r in self.config.repositories if r.name != name
        ]
        return len(self.config.repositories) < initial_count

    def get_github_credentials(self) -> dict[str, Union[Optional[str], int]]:
        """Get GitHub credentials from environment variables.

        Returns:
            Dictionary with GitHub credentials.
        """
        settings = self.config.settings

        return {
            "token": os.getenv(settings.github_token_env),
            "username": os.getenv(settings.github_username_env),
            "password": os.getenv(settings.github_password_env),
            "base_url": settings.github_api_url,
            "timeout": settings.github_timeout,
            "max_retries": settings.github_max_retries,
        }

    def _parse_config(self, data: dict[str, Any]) -> Config:
        """Parse configuration from dictionary.

        Args:
            data: Configuration data.

        Returns:
            Parsed configuration.
        """
        config = Config()

        # Parse repositories
        if "repositories" in data:
            for repo_data in data["repositories"]:
                repo = Repository(
                    name=repo_data.get("name", ""),
                    fork=repo_data.get("fork", ""),
                    upstream=repo_data.get("upstream", ""),
                    local_path=repo_data.get("local_path", ""),
                    skills=repo_data.get("skills", []),
                    analysis_enabled=repo_data.get("analysis_enabled", True),
                    sync_frequency=repo_data.get("sync_frequency"),
                )
                config.repositories.append(repo)

        # Parse settings
        if "settings" in data:
            settings_data = data["settings"]
            config.settings = Settings(
                llm_provider=settings_data.get("llm_provider", "openai"),
                default_path=settings_data.get("default_path", "~/code"),
                analysis_enabled=settings_data.get("analysis_enabled", True),
                max_repos_per_batch=settings_data.get("max_repos_per_batch", 10),
                git_timeout=settings_data.get("git_timeout", 300),
                rate_limit_delay=settings_data.get("rate_limit_delay", 1.0),
                log_level=settings_data.get("log_level", "INFO"),
                # GitHub settings
                github_token_env=settings_data.get("github_token_env", "GITHUB_TOKEN"),
                github_username_env=settings_data.get(
                    "github_username_env", "GITHUB_USERNAME"
                ),
                github_password_env=settings_data.get(
                    "github_password_env", "GITHUB_PASSWORD"
                ),
                github_api_url=settings_data.get(
                    "github_api_url", "https://api.github.com"
                ),
                github_timeout=settings_data.get("github_timeout", 30),
                github_max_retries=settings_data.get("github_max_retries", 3),
            )

        return config

    def _serialize_config(self, config: Config) -> dict[str, Any]:
        """Serialize configuration to dictionary.

        Args:
            config: Configuration to serialize.

        Returns:
            Serialized configuration.
        """
        data: dict[str, Any] = {
            "repositories": [],
            "settings": {
                "llm_provider": config.settings.llm_provider,
                "default_path": config.settings.default_path,
                "analysis_enabled": config.settings.analysis_enabled,
                "max_repos_per_batch": config.settings.max_repos_per_batch,
                "git_timeout": config.settings.git_timeout,
                "rate_limit_delay": config.settings.rate_limit_delay,
                "log_level": config.settings.log_level,
                # GitHub settings
                "github_token_env": config.settings.github_token_env,
                "github_username_env": config.settings.github_username_env,
                "github_password_env": config.settings.github_password_env,
                "github_api_url": config.settings.github_api_url,
                "github_timeout": config.settings.github_timeout,
                "github_max_retries": config.settings.github_max_retries,
            },
        }

        for repo in config.repositories:
            repo_data = {
                "name": repo.name,
                "fork": repo.fork,
                "upstream": repo.upstream,
                "local_path": repo.local_path,
                "skills": repo.skills,
                "analysis_enabled": repo.analysis_enabled,
            }
            if repo.sync_frequency:
                repo_data["sync_frequency"] = repo.sync_frequency
            data["repositories"].append(repo_data)

        return data


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get configuration manager instance.

    Args:
        config_path: Path to configuration file.

    Returns:
        Configuration manager.
    """
    return ConfigManager(config_path)


def create_sample_config() -> dict[str, Any]:
    """Create sample configuration data.

    Returns:
        Sample configuration dictionary.
    """
    return {
        "repositories": [
            {
                "name": "django",
                "fork": "username/django",
                "upstream": "django/django",
                "local_path": "~/code/django",
                "skills": ["python", "web", "orm"],
            },
            {
                "name": "fastapi",
                "fork": "username/fastapi",
                "upstream": "tiangolo/fastapi",
                "local_path": "~/code/fastapi",
                "skills": ["python", "api", "async"],
            },
        ],
        "settings": {
            "llm_provider": "openai",
            "default_path": "~/code",
            "analysis_enabled": True,
            "max_repos_per_batch": 10,
            "git_timeout": 300,
            "rate_limit_delay": 1.0,
            "log_level": "INFO",
        },
    }
