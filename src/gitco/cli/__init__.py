"""GitCo CLI modular interface.

This module provides a modular CLI structure for GitCo commands.
Each command group is organized into separate modules for maintainability.
"""

from .backup import backup_commands
from .config import config_commands
from .contributions import contributions_commands
from .core import core_commands
from .github import github_commands
from .upstream import upstream_commands

__all__ = [
    "core_commands",
    "config_commands",
    "upstream_commands",
    "github_commands",
    "contributions_commands",
    "backup_commands",
]
