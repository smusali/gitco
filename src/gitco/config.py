"""Configuration management for GitCo."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Repository:
    """Repository configuration."""
    name: str
    fork: str
    upstream: str
    local_path: str
    skills: List[str] = field(default_factory=list)
    analysis_enabled: bool = True
    sync_frequency: Optional[str] = None


@dataclass
class Settings:
    """Global settings configuration."""
    llm_provider: str = "openai"
    api_key_env: str = "AETHERIUM_API_KEY"
    default_path: str = "~/code"
    analysis_enabled: bool = True
    max_repos_per_batch: int = 10
    git_timeout: int = 300
    rate_limit_delay: float = 1.0
    log_level: str = "INFO"


@dataclass
class Config:
    """Main configuration class."""
    repositories: List[Repository] = field(default_factory=list)
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
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._parse_config(data)
    
    def save_config(self, config: Config) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save.
        """
        data = self._serialize_config(config)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
    
    def create_default_config(self, force: bool = False) -> Config:
        """Create default configuration file.
        
        Args:
            force: Whether to overwrite existing file.
            
        Returns:
            Default configuration.
        """
        if os.path.exists(self.config_path) and not force:
            raise FileExistsError(f"Configuration file already exists: {self.config_path}")
        
        config = Config()
        self.save_config(config)
        return config
    
    def validate_config(self, config: Config) -> List[str]:
        """Validate configuration.
        
        Args:
            config: Configuration to validate.
            
        Returns:
            List of validation errors.
        """
        errors = []
        
        # Validate repositories
        repo_names = set()
        for repo in config.repositories:
            if not repo.name:
                errors.append("Repository name is required")
            elif repo.name in repo_names:
                errors.append(f"Duplicate repository name: {repo.name}")
            else:
                repo_names.add(repo.name)
            
            if not repo.fork:
                errors.append(f"Fork URL is required for repository: {repo.name}")
            
            if not repo.upstream:
                errors.append(f"Upstream URL is required for repository: {repo.name}")
            
            if not repo.local_path:
                errors.append(f"Local path is required for repository: {repo.name}")
        
        # Validate settings
        if config.settings.llm_provider not in ["openai", "anthropic", "local", "custom"]:
            errors.append("Invalid LLM provider. Must be one of: openai, anthropic, local, custom")
        
        if config.settings.max_repos_per_batch < 1:
            errors.append("max_repos_per_batch must be at least 1")
        
        if config.settings.git_timeout < 30:
            errors.append("git_timeout must be at least 30 seconds")
        
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
        self.config.repositories = [r for r in self.config.repositories if r.name != repo.name]
        self.config.repositories.append(repo)
    
    def remove_repository(self, name: str) -> bool:
        """Remove repository from configuration.
        
        Args:
            name: Repository name to remove.
            
        Returns:
            True if repository was removed, False if not found.
        """
        initial_count = len(self.config.repositories)
        self.config.repositories = [r for r in self.config.repositories if r.name != name]
        return len(self.config.repositories) < initial_count
    
    def _parse_config(self, data: Dict[str, Any]) -> Config:
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
                    sync_frequency=repo_data.get("sync_frequency")
                )
                config.repositories.append(repo)
        
        # Parse settings
        if "settings" in data:
            settings_data = data["settings"]
            config.settings = Settings(
                llm_provider=settings_data.get("llm_provider", "openai"),
                api_key_env=settings_data.get("api_key_env", "AETHERIUM_API_KEY"),
                default_path=settings_data.get("default_path", "~/code"),
                analysis_enabled=settings_data.get("analysis_enabled", True),
                max_repos_per_batch=settings_data.get("max_repos_per_batch", 10),
                git_timeout=settings_data.get("git_timeout", 300),
                rate_limit_delay=settings_data.get("rate_limit_delay", 1.0),
                log_level=settings_data.get("log_level", "INFO")
            )
        
        return config
    
    def _serialize_config(self, config: Config) -> Dict[str, Any]:
        """Serialize configuration to dictionary.
        
        Args:
            config: Configuration to serialize.
            
        Returns:
            Serialized configuration.
        """
        data = {
            "repositories": [],
            "settings": {
                "llm_provider": config.settings.llm_provider,
                "api_key_env": config.settings.api_key_env,
                "default_path": config.settings.default_path,
                "analysis_enabled": config.settings.analysis_enabled,
                "max_repos_per_batch": config.settings.max_repos_per_batch,
                "git_timeout": config.settings.git_timeout,
                "rate_limit_delay": config.settings.rate_limit_delay,
                "log_level": config.settings.log_level
            }
        }
        
        for repo in config.repositories:
            repo_data = {
                "name": repo.name,
                "fork": repo.fork,
                "upstream": repo.upstream,
                "local_path": repo.local_path,
                "skills": repo.skills,
                "analysis_enabled": repo.analysis_enabled
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


def create_sample_config() -> Dict[str, Any]:
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
                "skills": ["python", "web", "orm"]
            },
            {
                "name": "fastapi",
                "fork": "username/fastapi",
                "upstream": "tiangolo/fastapi",
                "local_path": "~/code/fastapi",
                "skills": ["python", "api", "async"]
            }
        ],
        "settings": {
            "llm_provider": "openai",
            "api_key_env": "AETHERIUM_API_KEY",
            "default_path": "~/code",
            "analysis_enabled": True,
            "max_repos_per_batch": 10,
            "git_timeout": 300,
            "rate_limit_delay": 1.0,
            "log_level": "INFO"
        }
    } 
