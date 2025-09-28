"""Interactive prompts for GitCo CLI."""

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from .common import console

# Global console instance
_console = Console()

__all__ = [
    "prompt_text",
    "prompt_choice",
    "prompt_confirm",
    "prompt_list",
    "prompt_path",
    "prompt_repository_info",
    "prompt_llm_settings",
    "prompt_github_settings",
    "prompt_general_settings",
    "prompt_repositories",
    "show_configuration_summary",
    "prompt_save_configuration",
]


@dataclass
class PromptConfig:
    """Configuration for prompt functionality."""

    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0


@dataclass
class PromptTemplate:
    """Template for prompts."""

    name: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[list[str]] = None


class PromptManager:
    """Manager for prompt functionality."""

    def __init__(self, config: Optional[PromptConfig] = None):
        """Initialize the prompt manager.

        Args:
            config: Configuration for prompts
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.templates: dict[str, PromptTemplate] = {}

    def get_prompt_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name.

        Args:
            template_name: Name of the template

        Returns:
            Prompt template or None if not found
        """
        return self.templates.get(template_name)

    def format_prompt(
        self,
        template: Optional[Union[str, PromptTemplate]],
        variables: Optional[dict[str, str]],
    ) -> str:
        """Format a prompt with variables.

        Args:
            template: Prompt template name or PromptTemplate object
            variables: Variables to substitute

        Returns:
            Formatted prompt
        """
        # Handle string template names
        if isinstance(template, str):
            template = self.get_prompt_template(template)

        if not template or not template.content:
            return ""

        if not variables:
            return template.content

        # Simple variable substitution
        result = template.content
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result


# Global prompt manager instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get the global prompt manager instance.

    Returns:
        Global prompt manager
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


def reset_prompt_manager() -> None:
    """Reset the global prompt manager instance."""
    global _prompt_manager
    _prompt_manager = None


def prompt_text(
    message: str,
    default: Optional[str] = None,
    required: bool = True,
    validator: Optional[Callable[[str], None]] = None,
) -> str:
    """Prompt for text input.

    Args:
        message: Prompt message
        default: Default value
        required: Whether input is required
        validator: Optional validation function

    Returns:
        User input
    """
    while True:
        value = Prompt.ask(message, default=default)

        if not value and required:
            console.print("[red]This field is required. Please enter a value.[/red]")
            continue

        if value and validator:
            try:
                validator(value)
            except ValueError as e:
                console.print(f"[red]Invalid input: {e}[/red]")
                continue

        return str(value or "")


def prompt_choice(
    message: str,
    choices: list[str],
    default: Optional[str] = None,
) -> str:
    """Prompt for choice selection.

    Args:
        message: Prompt message
        choices: List of available choices
        default: Default choice

    Returns:
        Selected choice
    """
    console.print(f"\n{message}")

    for i, choice in enumerate(choices, 1):
        marker = "→" if choice == default else " "
        console.print(f"  {marker} {i}. {choice}")

    while True:
        try:
            choice_input = Prompt.ask(
                f"\nSelect option (1-{len(choices)})",
                default=str(choices.index(default) + 1) if default else None,
            )
            if not choice_input:
                console.print("[red]Please enter a valid number[/red]")
                continue
            choice_index = int(choice_input) - 1

            if 0 <= choice_index < len(choices):
                return choices[choice_index]
            else:
                console.print(
                    f"[red]Please select a number between 1 and {len(choices)}[/red]"
                )
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def prompt_confirm(
    message: str,
    default: bool = True,
) -> bool:
    """Prompt for confirmation.

    Args:
        message: Prompt message
        default: Default value

    Returns:
        User confirmation
    """
    result = Confirm.ask(message, default=default)
    return bool(result)


def prompt_list(
    message: str,
    default: Optional[list[str]] = None,
    allow_empty: bool = False,
) -> list[str]:
    """Prompt for a list of values.

    Args:
        message: Prompt message
        default: Default list
        allow_empty: Whether empty list is allowed

    Returns:
        List of values
    """
    console.print(f"\n{message}")
    console.print("Enter values separated by commas (or press Enter to finish)")

    if default:
        console.print(f"Default: {', '.join(default)}")

    while True:
        input_str = Prompt.ask("Values", default=",".join(default) if default else "")

        if not input_str and not allow_empty:
            console.print("[red]At least one value is required[/red]")
            continue

        if not input_str:
            return []

        # Split by comma and clean up
        values = [v.strip() for v in input_str.split(",") if v.strip()]

        if not values and not allow_empty:
            console.print("[red]At least one value is required[/red]")
            continue

        return values


def prompt_path(
    message: str,
    default: Optional[str] = None,
    must_exist: bool = False,
    create_if_missing: bool = False,
) -> str:
    """Prompt for a file path.

    Args:
        message: Prompt message
        default: Default path
        must_exist: Whether path must exist
        create_if_missing: Whether to create directory if missing

    Returns:
        File path
    """
    while True:
        path_input = Prompt.ask(message, default=default)

        if not path_input:
            console.print("[red]Path is required. Please enter a value.[/red]")
            continue

        path = str(path_input)

        # Expand user path
        path = os.path.expanduser(path)

        if must_exist and not os.path.exists(path):
            console.print(f"[red]Path does not exist: {path}[/red]")
            continue

        if create_if_missing and not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                console.print(f"[green]Created directory: {path}[/green]")
            except OSError as e:
                console.print(f"[red]Failed to create directory: {e}[/red]")
                continue

        return path


def prompt_repository_info() -> dict[str, Any]:
    """Prompt for repository information.

    Returns:
        Repository configuration dictionary
    """
    console.print("\n[bold blue]Repository Configuration[/bold blue]")

    def validate_repo_name(name: str) -> None:
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValueError(
                "Repository name must contain only letters, numbers, underscores, and hyphens"
            )

    name = prompt_text("Repository name", validator=validate_repo_name)
    fork = prompt_text("Fork repository (username/repo)")
    upstream = prompt_text("Upstream repository (owner/repo)")

    # Validate repository format
    for repo in [fork, upstream]:
        if not re.match(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$", repo):
            console.print(
                "[yellow]Warning: Repository format should be 'owner/repo'[/yellow]"
            )

    local_path = prompt_path(
        "Local path", default=f"~/code/{name}", create_if_missing=True
    )

    skills = prompt_list("Skills (comma-separated)", allow_empty=True)

    analysis_enabled = prompt_confirm(
        "Enable AI analysis for this repository?", default=True
    )

    return {
        "name": name,
        "fork": fork,
        "upstream": upstream,
        "local_path": local_path,
        "skills": skills,
        "analysis_enabled": analysis_enabled,
    }


def prompt_llm_settings() -> dict[str, Any]:
    """Prompt for LLM provider settings.

    Returns:
        LLM settings dictionary
    """
    console.print("\n[bold blue]LLM Provider Configuration[/bold blue]")

    settings = {"llm_provider": "openai"}

    console.print("\n[bold]Configuring OpenAI[/bold]")

    settings["api_key_env"] = prompt_text(
        "OpenAI API key environment variable", default="OPENAI_API_KEY"
    )

    return settings


def prompt_github_settings() -> dict[str, Any]:
    """Prompt for GitHub settings.

    Returns:
        GitHub settings dictionary
    """
    console.print("\n[bold blue]GitHub Configuration[/bold blue]")

    use_github = prompt_confirm("Configure GitHub integration?", default=True)

    if not use_github:
        return {}

    settings = {}

    auth_method = prompt_choice(
        "GitHub authentication method",
        ["token", "username/password", "none"],
        default="token",
    )

    if auth_method == "token":
        settings["github_token_env"] = prompt_text(
            "GitHub token environment variable", default="GITHUB_TOKEN"
        )
    elif auth_method == "username/password":
        settings["github_username_env"] = prompt_text(
            "GitHub username environment variable", default="GITHUB_USERNAME"
        )
        settings["github_password_env"] = prompt_text(
            "GitHub password environment variable", default="GITHUB_PASSWORD"
        )

    settings["github_api_url"] = prompt_text(
        "GitHub API URL", default="https://api.github.com"
    )

    return settings


def prompt_general_settings() -> dict[str, Any]:
    """Prompt for general settings.

    Returns:
        General settings dictionary
    """
    console.print("\n[bold blue]General Settings[/bold blue]")

    settings: dict[str, Any] = {}

    default_path = prompt_path(
        "Default code directory", default="~/code", create_if_missing=True
    )
    settings["default_path"] = default_path

    max_repos = IntPrompt.ask("Maximum repositories per batch", default=10)
    settings["max_repos_per_batch"] = max_repos

    analysis_enabled = prompt_confirm("Enable AI analysis by default?", default=True)
    settings["analysis_enabled"] = analysis_enabled

    return settings


def prompt_repositories() -> list[dict[str, Any]]:
    """Prompt for repository configuration.

    Returns:
        List of repository configurations
    """
    console.print("\n[bold blue]Repository Setup[/bold blue]")

    repositories: list[dict[str, Any]] = []

    while True:
        console.print(f"\n[bold]Repository {len(repositories) + 1}[/bold]")

        repo_info = prompt_repository_info()
        repositories.append(repo_info)

        if not prompt_confirm("Add another repository?", default=False):
            break

    return repositories


def show_configuration_summary(
    repositories: list[dict[str, Any]],
    settings: dict[str, Any],
    llm_settings: dict[str, Any],
    github_settings: dict[str, Any],
) -> None:
    """Show configuration summary.

    Args:
        repositories: List of repository configurations
        settings: General settings
        llm_settings: LLM provider settings
        github_settings: GitHub settings
    """
    console.print("\n[bold green]Configuration Summary[/bold green]")

    # Repositories
    console.print(f"\n[bold]Repositories ({len(repositories)}):[/bold]")
    for repo in repositories:
        console.print(f"  • {repo['name']}: {repo['fork']} → {repo['upstream']}")
        console.print(f"    Path: {repo['local_path']}")
        if repo["skills"]:
            console.print(f"    Skills: {', '.join(repo['skills'])}")

    # Settings
    console.print("\n[bold]General Settings:[/bold]")
    console.print(f"  • Default path: {settings.get('default_path', '~/code')}")
    console.print(f"  • Max repos per batch: {settings.get('max_repos_per_batch', 10)}")
    console.print(f"  • Analysis enabled: {settings.get('analysis_enabled', True)}")

    # LLM Settings
    if llm_settings:
        console.print(
            f"\n[bold]LLM Provider:[/bold] {llm_settings.get('llm_provider', 'none')}"
        )
        if llm_settings.get("api_key_env"):
            console.print(f"  • API key env: {llm_settings['api_key_env']}")

    # GitHub Settings
    if github_settings:
        console.print("\n[bold]GitHub Integration:[/bold]")
        if github_settings.get("github_token_env"):
            console.print(f"  • Token env: {github_settings['github_token_env']}")
        if github_settings.get("github_username_env"):
            console.print(f"  • Username env: {github_settings['github_username_env']}")
        console.print(
            f"  • API URL: {github_settings.get('github_api_url', 'https://api.github.com')}"
        )


def prompt_save_configuration() -> bool:
    """Prompt to save configuration.

    Returns:
        Whether to save configuration
    """
    console.print("\n[bold]Save Configuration[/bold]")
    return prompt_confirm("Save this configuration?", default=True)
