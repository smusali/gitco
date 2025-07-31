"""Configuration management for GitCo."""

import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional, Union
from urllib.parse import urlparse

import yaml

from .git_ops import GitRepositoryManager
from .utils.common import (
    get_logger,
    log_configuration_loaded,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    log_validation_result,
)
from .utils.exception import ConfigurationError


@dataclass
class ValidationError:
    """Represents a configuration validation error with context."""

    field: str
    message: str
    severity: str = "error"  # error, warning, info
    context: Optional[dict[str, Any]] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Return formatted error message."""
        msg = f"{self.field}: {self.message}"
        if self.suggestion:
            msg += f" (suggestion: {self.suggestion})"
        return msg


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
    # Rate limiting settings
    github_rate_limit_per_minute: int = 30
    github_rate_limit_per_hour: int = 5000
    github_burst_limit: int = 5
    llm_rate_limit_per_minute: int = 60
    llm_rate_limit_per_hour: int = 1000
    llm_burst_limit: int = 10
    min_request_interval: float = 0.1
    # Cost optimization settings
    enable_cost_tracking: bool = True
    enable_token_optimization: bool = True
    max_tokens_per_request: int = 4000
    max_cost_per_request_usd: float = 0.10
    max_daily_cost_usd: float = 5.0
    max_monthly_cost_usd: float = 50.0
    cost_log_file: str = "~/.gitco/cost_log.json"


@dataclass
class Config:
    """Main configuration class."""

    repositories: list[Repository] = field(default_factory=list)
    settings: Settings = field(default_factory=Settings)


class ConfigValidator:
    """Validates GitCo configuration with detailed error reporting."""

    def __init__(self) -> None:
        """Initialize the validator."""
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []
        self.git_manager = GitRepositoryManager()

    def validate_config(self, config: Config) -> dict[str, list[ValidationError]]:
        """Validate entire configuration with detailed error reporting.

        Args:
            config: Configuration to validate.

        Returns:
            Dictionary with 'errors' and 'warnings' lists.
        """
        self.errors = []
        self.warnings = []

        # Validate settings first
        self._validate_settings(config.settings)

        # Validate repositories
        self._validate_repositories(config.repositories)

        # Validate cross-references and dependencies
        self._validate_cross_references(config)

        return {
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def _validate_settings(self, settings: Settings) -> None:
        """Validate global settings.

        Args:
            settings: Settings to validate.
        """
        # Validate LLM provider
        valid_providers = ["openai", "anthropic", "ollama"]
        if settings.llm_provider not in valid_providers:
            self.errors.append(
                ValidationError(
                    field="settings.llm_provider",
                    message=f"Invalid LLM provider '{settings.llm_provider}'",
                    suggestion=f"Must be one of: {', '.join(valid_providers)}",
                )
            )

        # Validate numeric settings
        if settings.max_repos_per_batch < 1:
            self.errors.append(
                ValidationError(
                    field="settings.max_repos_per_batch",
                    message=f"Value {settings.max_repos_per_batch} is too low",
                    suggestion="Must be at least 1",
                )
            )
        elif settings.max_repos_per_batch > 100:
            self.warnings.append(
                ValidationError(
                    field="settings.max_repos_per_batch",
                    message=f"Value {settings.max_repos_per_batch} is very high",
                    suggestion="Consider using a value between 5-20 for better performance",
                    severity="warning",
                )
            )

        if settings.git_timeout < 30:
            self.errors.append(
                ValidationError(
                    field="settings.git_timeout",
                    message=f"Value {settings.git_timeout} is too low",
                    suggestion="Must be at least 30 seconds",
                )
            )
        elif settings.git_timeout > 1800:
            self.warnings.append(
                ValidationError(
                    field="settings.git_timeout",
                    message=f"Value {settings.git_timeout} is very high",
                    suggestion="Consider using a value between 300-900 seconds",
                    severity="warning",
                )
            )

        if settings.rate_limit_delay < 0.1:
            self.errors.append(
                ValidationError(
                    field="settings.rate_limit_delay",
                    message=f"Value {settings.rate_limit_delay} is too low",
                    suggestion="Must be at least 0.1 seconds",
                )
            )

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if settings.log_level.upper() not in valid_log_levels:
            self.errors.append(
                ValidationError(
                    field="settings.log_level",
                    message=f"Invalid log level '{settings.log_level}'",
                    suggestion=f"Must be one of: {', '.join(valid_log_levels)}",
                )
            )

        # Validate cost optimization settings
        if settings.max_tokens_per_request < 100:
            self.errors.append(
                ValidationError(
                    field="settings.max_tokens_per_request",
                    message=f"Value {settings.max_tokens_per_request} is too low",
                    suggestion="Must be at least 100 tokens",
                )
            )
        elif settings.max_tokens_per_request > 32000:
            self.warnings.append(
                ValidationError(
                    field="settings.max_tokens_per_request",
                    message=f"Value {settings.max_tokens_per_request} is very high",
                    suggestion="Consider using a value between 1000-8000 for cost efficiency",
                    severity="warning",
                )
            )

        if settings.max_cost_per_request_usd < 0:
            self.errors.append(
                ValidationError(
                    field="settings.max_cost_per_request_usd",
                    message=f"Value {settings.max_cost_per_request_usd} is invalid",
                    suggestion="Must be a non-negative number",
                )
            )
        elif settings.max_cost_per_request_usd > 10.0:
            self.warnings.append(
                ValidationError(
                    field="settings.max_cost_per_request_usd",
                    message=f"Value {settings.max_cost_per_request_usd} is very high",
                    suggestion="Consider using a value between 0.01-1.00 for cost control",
                    severity="warning",
                )
            )

        if settings.max_daily_cost_usd < 0:
            self.errors.append(
                ValidationError(
                    field="settings.max_daily_cost_usd",
                    message=f"Value {settings.max_daily_cost_usd} is invalid",
                    suggestion="Must be a non-negative number",
                )
            )

        if settings.max_monthly_cost_usd < 0:
            self.errors.append(
                ValidationError(
                    field="settings.max_monthly_cost_usd",
                    message=f"Value {settings.max_monthly_cost_usd} is invalid",
                    suggestion="Must be a non-negative number",
                )
            )

        # Validate GitHub settings
        self._validate_github_settings(settings)

    def _validate_github_settings(self, settings: Settings) -> None:
        """Validate GitHub-specific settings.

        Args:
            settings: Settings to validate.
        """
        # Validate GitHub API URL
        try:
            parsed_url = urlparse(settings.github_api_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                self.errors.append(
                    ValidationError(
                        field="settings.github_api_url",
                        message=f"Invalid URL format: {settings.github_api_url}",
                        suggestion="Must be a valid HTTP/HTTPS URL",
                    )
                )
        except Exception:
            self.errors.append(
                ValidationError(
                    field="settings.github_api_url",
                    message=f"Invalid URL: {settings.github_api_url}",
                    suggestion="Must be a valid URL",
                )
            )

        # Validate timeout values
        if settings.github_timeout < 5:
            self.errors.append(
                ValidationError(
                    field="settings.github_timeout",
                    message=f"Value {settings.github_timeout} is too low",
                    suggestion="Must be at least 5 seconds",
                )
            )

        if settings.github_max_retries < 1:
            self.errors.append(
                ValidationError(
                    field="settings.github_max_retries",
                    message=f"Value {settings.github_max_retries} is too low",
                    suggestion="Must be at least 1",
                )
            )

    def _validate_repositories(self, repositories: list[Repository]) -> None:
        """Validate repository configurations.

        Args:
            repositories: List of repositories to validate.
        """
        if not repositories:
            self.warnings.append(
                ValidationError(
                    field="repositories",
                    message="No repositories configured",
                    suggestion="Add at least one repository to get started",
                    severity="warning",
                )
            )
            return

        # Check for duplicate names
        repo_names: dict[str, int] = {}
        for i, repo in enumerate(repositories):
            if repo.name in repo_names:
                self.errors.append(
                    ValidationError(
                        field=f"repositories[{i}].name",
                        message=f"Duplicate repository name: {repo.name}",
                        suggestion=f"Repository at index {repo_names[repo.name]} already uses this name",
                        context={"duplicate_index": repo_names[repo.name]},
                    )
                )
            else:
                repo_names[repo.name] = i

        # Validate each repository
        for i, repo in enumerate(repositories):
            self._validate_repository(repo, i)

    def _validate_repository(self, repo: Repository, index: int) -> None:
        """Validate a single repository configuration.

        Args:
            repo: Repository to validate.
            index: Index of the repository in the list.
        """
        prefix = f"repositories[{index}]"

        # Validate name
        if not repo.name:
            self.errors.append(
                ValidationError(
                    field=f"{prefix}.name",
                    message="Repository name is required",
                    suggestion="Provide a unique name for this repository",
                )
            )
        elif not re.match(r"^[a-zA-Z0-9_-]+$", repo.name):
            self.errors.append(
                ValidationError(
                    field=f"{prefix}.name",
                    message=f"Invalid repository name: {repo.name}",
                    suggestion="Use only letters, numbers, underscores, and hyphens",
                )
            )

        # Validate fork URL
        if not repo.fork:
            self.errors.append(
                ValidationError(
                    field=f"{prefix}.fork",
                    message="Fork URL is required",
                    suggestion="Provide the URL of your fork",
                )
            )
        else:
            self._validate_repository_url(repo.fork, f"{prefix}.fork", "fork")

        # Validate upstream URL
        if not repo.upstream:
            self.errors.append(
                ValidationError(
                    field=f"{prefix}.upstream",
                    message="Upstream URL is required",
                    suggestion="Provide the URL of the upstream repository",
                )
            )
        else:
            self._validate_repository_url(
                repo.upstream, f"{prefix}.upstream", "upstream"
            )

        # Validate local path
        if not repo.local_path:
            self.errors.append(
                ValidationError(
                    field=f"{prefix}.local_path",
                    message="Local path is required",
                    suggestion="Provide the local path where the repository should be cloned",
                )
            )
        else:
            self._validate_local_path(repo.local_path, f"{prefix}.local_path")

        # Validate skills
        if repo.skills:
            self._validate_skills(repo.skills, f"{prefix}.skills")

        # Validate sync frequency if provided
        if repo.sync_frequency:
            self._validate_sync_frequency(
                repo.sync_frequency, f"{prefix}.sync_frequency"
            )

        # Validate language if provided
        if repo.language:
            self._validate_language(repo.language, f"{prefix}.language")

    def _validate_repository_url(self, url: str, field: str, url_type: str) -> None:
        """Validate a repository URL.

        Args:
            url: URL to validate.
            field: Field name for error reporting.
            url_type: Type of URL (fork/upstream).
        """
        # Check if it's a valid URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                self.errors.append(
                    ValidationError(
                        field=field,
                        message=f"Invalid {url_type} URL format: {url}",
                        suggestion="Use format: https://github.com/owner/repo",
                    )
                )
                return
        except Exception:
            self.errors.append(
                ValidationError(
                    field=field,
                    message=f"Invalid {url_type} URL: {url}",
                    suggestion="Use a valid HTTP/HTTPS URL",
                )
            )
            return

        # Check for GitHub-specific patterns
        if "github.com" in url:
            if not re.match(r"^https?://github\.com/[^/]+/[^/]+/?$", url):
                self.errors.append(
                    ValidationError(
                        field=field,
                        message=f"Invalid GitHub {url_type} URL: {url}",
                        suggestion="Use format: https://github.com/owner/repo",
                    )
                )

    def _validate_local_path(self, path: str, field: str) -> None:
        """Validate a local repository path.

        Args:
            path: Path to validate.
            field: Field name for error reporting.
        """
        # Check if path is absolute or uses ~
        if not (os.path.isabs(path) or path.startswith("~")):
            self.warnings.append(
                ValidationError(
                    field=field,
                    message=f"Relative path may cause issues: {path}",
                    suggestion="Use absolute path or path starting with ~",
                    severity="warning",
                )
            )

        # Check if path exists and is a git repository
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            if not os.path.isdir(expanded_path):
                self.errors.append(
                    ValidationError(
                        field=field,
                        message=f"Path exists but is not a directory: {path}",
                        suggestion="Provide a directory path",
                    )
                )
            else:
                # Check if it's a git repository
                is_valid, repo_errors = self.git_manager.validate_repository_path(
                    expanded_path
                )
                if not is_valid:
                    for error in repo_errors:
                        self.warnings.append(
                            ValidationError(
                                field=field,
                                message=f"Git repository validation failed: {error}",
                                suggestion="Ensure the directory is a valid git repository",
                                severity="warning",
                            )
                        )

    def _validate_skills(self, skills: list[str], field: str) -> None:
        """Validate skills list.

        Args:
            skills: Skills to validate.
            field: Field name for error reporting.
        """
        for i, skill in enumerate(skills):
            if not skill:
                self.errors.append(
                    ValidationError(
                        field=f"{field}[{i}]",
                        message="Empty skill name",
                        suggestion="Provide a non-empty skill name",
                    )
                )
            elif not re.match(r"^[a-zA-Z0-9_-]+$", skill):
                self.errors.append(
                    ValidationError(
                        field=f"{field}[{i}]",
                        message=f"Invalid skill name: {skill}",
                        suggestion="Use only letters, numbers, underscores, and hyphens",
                    )
                )

    def _validate_sync_frequency(self, frequency: str, field: str) -> None:
        """Validate sync frequency format.

        Args:
            frequency: Frequency string to validate.
            field: Field name for error reporting.
        """
        # Basic cron-like format validation
        if not re.match(
            r"^(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)\s+(\*|[0-9,/-]+)$",
            frequency,
        ):
            self.errors.append(
                ValidationError(
                    field=field,
                    message=f"Invalid sync frequency format: {frequency}",
                    suggestion="Use cron format: minute hour day month weekday",
                )
            )

    def _validate_language(self, language: str, field: str) -> None:
        """Validate programming language.

        Args:
            language: Language to validate.
            field: Field name for error reporting.
        """
        common_languages = [
            "python",
            "javascript",
            "typescript",
            "java",
            "c++",
            "c#",
            "go",
            "rust",
            "php",
            "ruby",
            "swift",
            "kotlin",
            "scala",
            "dart",
            "r",
            "matlab",
        ]

        if language.lower() not in [lang.lower() for lang in common_languages]:
            self.warnings.append(
                ValidationError(
                    field=field,
                    message=f"Unrecognized language: {language}",
                    suggestion=f"Consider using one of: {', '.join(common_languages)}",
                    severity="warning",
                )
            )

    def _validate_cross_references(self, config: Config) -> None:
        """Validate cross-references and dependencies.

        Args:
            config: Configuration to validate.
        """
        # Check if default path exists and is accessible
        default_path = os.path.expanduser(config.settings.default_path)
        if not os.path.exists(default_path):
            self.warnings.append(
                ValidationError(
                    field="settings.default_path",
                    message=f"Default path does not exist: {config.settings.default_path}",
                    suggestion="Create the directory or update the path",
                    severity="warning",
                )
            )

        # Check for repositories using default path
        for i, repo in enumerate(config.repositories):
            if repo.local_path.startswith("~") and "~/code" in repo.local_path:
                self.warnings.append(
                    ValidationError(
                        field=f"repositories[{i}].local_path",
                        message=f"Using default path pattern: {repo.local_path}",
                        suggestion="Consider using a more specific path for better organization",
                        severity="warning",
                    )
                )


class ConfigManager:
    """Manages GitCo configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file. Defaults to 'gitco-config.yml'.
        """
        self.config_path = config_path or "gitco-config.yml"
        self.config = Config()
        self.validator = ConfigValidator()

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
        """Validate configuration with enhanced error reporting.

        Args:
            config: Configuration to validate.

        Returns:
            List of validation error messages.
        """
        get_logger()
        log_operation_start("configuration validation")

        try:
            validation_results = self.validator.validate_config(config)

            # Log validation results
            for error in validation_results["errors"]:
                log_validation_result(error.field, False, error.message)

            for warning in validation_results["warnings"]:
                log_validation_result(
                    warning.field, True, f"Warning: {warning.message}"
                )

            if validation_results["errors"]:
                log_operation_failure(
                    "configuration validation", ConfigurationError("Validation failed")
                )
            else:
                log_operation_success("configuration validation")

            # Return error messages for backward compatibility
            return [str(error) for error in validation_results["errors"]]

        except Exception as e:
            log_operation_failure("configuration validation", e)
            raise

    def get_validation_report(self, config: Config) -> dict[str, Any]:
        """Get detailed validation report.

        Args:
            config: Configuration to validate.

        Returns:
            Detailed validation report with errors and warnings.
        """
        return self.validator.validate_config(config)

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
                # Cost optimization settings
                enable_cost_tracking=settings_data.get("enable_cost_tracking", True),
                enable_token_optimization=settings_data.get(
                    "enable_token_optimization", True
                ),
                max_tokens_per_request=settings_data.get(
                    "max_tokens_per_request", 4000
                ),
                max_cost_per_request_usd=settings_data.get(
                    "max_cost_per_request_usd", 0.10
                ),
                max_daily_cost_usd=settings_data.get("max_daily_cost_usd", 5.0),
                max_monthly_cost_usd=settings_data.get("max_monthly_cost_usd", 50.0),
                cost_log_file=settings_data.get(
                    "cost_log_file", "~/.gitco/cost_log.json"
                ),
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
                # Cost optimization settings
                "enable_cost_tracking": config.settings.enable_cost_tracking,
                "enable_token_optimization": config.settings.enable_token_optimization,
                "max_tokens_per_request": config.settings.max_tokens_per_request,
                "max_cost_per_request_usd": config.settings.max_cost_per_request_usd,
                "max_daily_cost_usd": config.settings.max_daily_cost_usd,
                "max_monthly_cost_usd": config.settings.max_monthly_cost_usd,
                "cost_log_file": config.settings.cost_log_file,
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
