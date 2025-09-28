"""Shell completion functionality for GitCo CLI."""

import logging
import os
from dataclasses import dataclass
from typing import Optional

import click

from ..templates.shell_completion import (
    BASH_COMPLETION_TEMPLATE,
    ZSH_COMPLETION_TEMPLATE,
)


@dataclass
class CompletionConfig:
    """Configuration for completion functionality."""

    enable_completion: Optional[bool] = True
    max_suggestions: Optional[int] = 5
    min_confidence: Optional[float] = 0.7
    provider: Optional[str] = "default"


@dataclass
class CompletionResult:
    """Result of completion operation."""

    suggestions: Optional[list[str]] = None
    confidence: Optional[float] = None
    provider: Optional[str] = None


class CompletionManager:
    """Manager for completion functionality."""

    def __init__(self, config: Optional[CompletionConfig] = None):
        """Initialize the completion manager.

        Args:
            config: Configuration for completion
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_completion_suggestions(self, input_text: Optional[str]) -> CompletionResult:
        """Get completion suggestions for input text.

        Args:
            input_text: Input text to get suggestions for

        Returns:
            Completion result with suggestions
        """
        if not self.config or not self.config.enable_completion:
            return CompletionResult([], 0.0, "disabled")

        if not input_text:
            return CompletionResult([], 0.0, "empty")

        # Simple completion logic - in a real implementation this would use AI
        suggestions = []
        confidence = 0.8

        # Add some basic suggestions based on input
        if "git" in input_text.lower():
            suggestions.extend(["gitco", "git status", "git commit"])
        if "config" in input_text.lower():
            suggestions.extend(["configure", "configuration", "config file"])
        if "help" in input_text.lower():
            suggestions.extend(["help", "usage", "documentation"])

        return CompletionResult(
            suggestions, confidence, self.config.provider or "default"
        )


# Global completion manager instance
_completion_manager: Optional[CompletionManager] = None


def get_completion_manager() -> CompletionManager:
    """Get the global completion manager instance.

    Returns:
        Global completion manager
    """
    global _completion_manager
    if _completion_manager is None:
        _completion_manager = CompletionManager()
    return _completion_manager


def reset_completion_manager() -> None:
    """Reset the global completion manager instance."""
    global _completion_manager
    _completion_manager = None


def get_all_commands(ctx: click.Context) -> list[str]:
    """Get all available commands from the Click context."""
    commands = []

    def collect_commands(cmd: click.Command, prefix: str = "") -> None:
        """Recursively collect all command names."""
        if isinstance(cmd, click.Group):
            for name, subcmd in cmd.commands.items():
                full_name = f"{prefix}{name}" if prefix else name
                commands.append(full_name)
                collect_commands(subcmd, f"{full_name} ")
        else:
            commands.append(prefix.rstrip())

    collect_commands(ctx.command)
    return commands


def get_command_options(ctx: click.Context, command_name: str) -> dict[str, list[str]]:
    """Get options for a specific command."""
    options: dict[str, list[str]] = {"flags": [], "options": []}

    def find_command(cmd: click.Command, target_name: str) -> Optional[click.Command]:
        """Find a specific command by name."""
        if isinstance(cmd, click.Group):
            for name, subcmd in cmd.commands.items():
                if name == target_name:
                    return subcmd
                result = find_command(subcmd, target_name)
                if result:
                    return result
        return None

    # Find the target command
    target_cmd = find_command(ctx.command, command_name)
    if not target_cmd:
        return options

    # Collect options
    for param in target_cmd.params:
        if isinstance(param, click.Option):
            # Add the main option name
            if param.name:
                options["options"].append(f"--{param.name}")

            # Add short options
            if param.opts:
                for opt in param.opts:
                    if opt.startswith("-") and len(opt) == 2:
                        options["flags"].append(opt)

    return options


def get_repository_names() -> list[str]:
    """Get repository names from configuration."""
    try:
        from ..config import get_config_manager

        config_manager = get_config_manager()
        if (
            config_manager
            and config_manager.config
            and config_manager.config.repositories
        ):
            return [repo.name for repo in config_manager.config.repositories]
    except Exception:
        pass
    return []


def get_skill_names() -> list[str]:
    """Get skill names from configuration."""
    try:
        from ..config import get_config_manager

        config_manager = get_config_manager()
        if (
            config_manager
            and config_manager.config
            and config_manager.config.repositories
        ):
            skills: set[str] = set()
            for repo in config_manager.config.repositories:
                if repo.skills:
                    skills.update(repo.skills)
            return list(skills)
    except Exception:
        pass
    return []


def get_label_names() -> list[str]:
    """Get common label names for completion."""
    return [
        "good first issue",
        "help wanted",
        "bug",
        "enhancement",
        "documentation",
        "question",
        "invalid",
        "wontfix",
        "duplicate",
        "feature",
        "improvement",
        "refactor",
        "test",
        "ci",
        "build",
        "deploy",
        "security",
        "performance",
        "accessibility",
        "internationalization",
    ]


def get_provider_names() -> list[str]:
    """Get available LLM provider names."""
    return ["openai"]


def get_format_names() -> list[str]:
    """Get available export format names."""
    return ["json", "csv"]


def get_backup_type_names() -> list[str]:
    """Get available backup type names."""
    return ["full", "incremental", "config-only"]


def get_strategy_names() -> list[str]:
    """Get available merge strategy names."""
    return ["ours", "theirs", "manual"]


def get_state_names() -> list[str]:
    """Get available issue state names."""
    return ["open", "closed", "all"]


def get_filter_names() -> list[str]:
    """Get available filter names."""
    return ["healthy", "needs_attention", "critical"]


def get_sort_names() -> list[str]:
    """Get available sort names."""
    return [
        "health",
        "activity",
        "stars",
        "forks",
        "engagement",
        "commits",
        "contributors",
    ]


def get_activity_level_names() -> list[str]:
    """Get available activity level names."""
    return ["high", "moderate", "low"]


def generate_bash_completion() -> str:
    """Generate bash completion script."""
    return BASH_COMPLETION_TEMPLATE


def generate_zsh_completion() -> str:
    """Generate zsh completion script."""
    return ZSH_COMPLETION_TEMPLATE


def install_completion(shell: str, completion_file: Optional[str] = None) -> None:
    """Install completion script for the specified shell."""
    if shell not in ["bash", "zsh"]:
        raise ValueError("Shell must be 'bash' or 'zsh'")

    if shell == "bash":
        script = generate_bash_completion()
        default_file = os.path.expanduser("~/.bash_completion.d/gitco")
    else:  # zsh
        script = generate_zsh_completion()
        default_file = os.path.expanduser("~/.zsh/completions/_gitco")

    target_file = completion_file or default_file

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(target_file), exist_ok=True)

    # Write completion script
    with open(target_file, "w") as f:
        f.write(script)

    print(f"Completion script installed to: {target_file}")

    if shell == "bash":
        print("\nTo enable completion, add this line to your ~/.bashrc:")
        print(f"source {target_file}")
    else:  # zsh
        print("\nTo enable completion, add this line to your ~/.zshrc:")
        print("autoload -U compinit && compinit")


def generate_completion_script(shell: str) -> str:
    """Generate completion script for the specified shell."""
    if shell == "bash":
        return generate_bash_completion()
    elif shell == "zsh":
        return generate_zsh_completion()
    else:
        raise ValueError("Shell must be 'bash' or 'zsh'")


def get_completion_data(data_type: str) -> list[str]:
    """Get completion data for internal use."""
    if data_type == "repos":
        return get_repository_names()
    elif data_type == "skills":
        return get_skill_names()
    elif data_type == "labels":
        return get_label_names()
    elif data_type == "providers":
        return get_provider_names()
    elif data_type == "formats":
        return get_format_names()
    elif data_type == "backup-types":
        return get_backup_type_names()
    elif data_type == "strategies":
        return get_strategy_names()
    elif data_type == "states":
        return get_state_names()
    elif data_type == "filters":
        return get_filter_names()
    elif data_type == "sorts":
        return get_sort_names()
    elif data_type == "activity-levels":
        return get_activity_level_names()
    else:
        return []
