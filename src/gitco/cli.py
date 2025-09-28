"""GitCo CLI interface - Main entry point.

This is the main CLI module that orchestrates all command groups.
Each command group is organized into separate modules for maintainability.
"""

from typing import Optional

import click

from . import __version__
from .utils.common import (
    console,
    get_logger,
    set_quiet_mode,
    setup_logging,
)


@click.group()
@click.version_option(version=__version__, prog_name="gitco")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--log-file", help="Log to file")
@click.option(
    "--detailed-log",
    is_flag=True,
    help="Use detailed log format with function names and line numbers",
)
@click.option(
    "--max-log-size",
    type=int,
    help="Maximum log file size in MB before rotation (default: 10)",
)
@click.option(
    "--log-backups", type=int, help="Number of backup log files to keep (default: 5)"
)
@click.option(
    "--config", "-c", help="Path to configuration file (default: ~/.gitco/config.yml)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set log level",
)
@click.option(
    "--output-format",
    type=click.Choice(["text", "json", "csv"]),
    help="Output format for commands",
)
@click.option("--no-color", is_flag=True, help="Disable colored output")
@click.pass_context
def main(
    ctx: click.Context,
    verbose: bool,
    quiet: bool,
    debug: bool,
    log_file: Optional[str],
    detailed_log: bool,
    max_log_size: Optional[int],
    log_backups: Optional[int],
    config: Optional[str],
    log_level: Optional[str],
    output_format: Optional[str],
    no_color: bool,
) -> None:
    """GitCo - A simple CLI tool for intelligent OSS fork management and contribution discovery.

    GitCo transforms the tedious process of managing multiple OSS forks into an intelligent,
    context-aware workflow. It combines automated synchronization with AI-powered insights
    to help developers stay current with upstream changes and discover meaningful
    contribution opportunities.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Set global options
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["debug"] = debug
    ctx.obj["log_file"] = log_file
    ctx.obj["detailed_log"] = detailed_log
    ctx.obj["max_log_size"] = max_log_size
    ctx.obj["log_backups"] = log_backups
    ctx.obj["config"] = config
    ctx.obj["log_level"] = log_level
    ctx.obj["output_format"] = output_format
    ctx.obj["no_color"] = no_color

    # Set global quiet mode state
    set_quiet_mode(quiet)

    # Calculate max file size in bytes if specified
    max_file_size = None
    if max_log_size:
        max_file_size = max_log_size * 1024 * 1024  # Convert MB to bytes

    # Setup logging with enhanced options
    setup_logging(
        verbose=verbose or debug,
        quiet=quiet,
        log_file=log_file,
        detailed=detailed_log,
        max_file_size=max_file_size,
        backup_count=log_backups,
        log_level=log_level,
    )

    logger = get_logger()
    logger.debug("GitCo CLI started")


# Register all command groups from modular structure
try:
    from .cli.backup import register_backup_commands
    from .cli.config import register_config_commands
    from .cli.contributions import register_contributions_commands
    from .cli.core import register_core_commands
    from .cli.github import register_github_commands
    from .cli.upstream import register_upstream_commands

    # Register all command groups
    register_core_commands(main)
    register_config_commands(main)
    register_upstream_commands(main)
    register_github_commands(main)
    register_contributions_commands(main)
    register_backup_commands(main)

except ImportError as e:
    # Fallback to show at least the main group structure
    console.print(f"[red]Warning: Could not load all command modules: {e}[/red]")
    console.print("[yellow]Some commands may not be available.[/yellow]")


if __name__ == "__main__":
    main()
