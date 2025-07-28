"""GitCo CLI interface."""

import click
import sys
from typing import Optional

from . import __version__
from .config import ConfigManager, create_sample_config
from .utils import (
    setup_logging, get_logger, log_error_and_exit, safe_execute,
    log_operation_start, log_operation_success, log_operation_failure,
    handle_validation_errors, GitCoError, ConfigurationError, ValidationError
)


@click.group()
@click.version_option(version=__version__, prog_name="gitco")
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output"
)
@click.option(
    "--quiet", "-q", is_flag=True, help="Suppress output"
)
@click.option(
    "--log-file", help="Log to file"
)
@click.pass_context
def main(ctx: click.Context, verbose: bool, quiet: bool, log_file: Optional[str]) -> None:
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
    ctx.obj["log_file"] = log_file
    
    # Setup logging
    setup_logging(
        verbose=verbose,
        quiet=quiet,
        log_file=log_file
    )
    
    logger = get_logger()
    logger.debug("GitCo CLI started")


@main.command()
@click.option(
    "--force", "-f", is_flag=True, help="Overwrite existing configuration"
)
@click.option(
    "--template", "-t", help="Use custom template for configuration"
)
@click.pass_context
def init(ctx: click.Context, force: bool, template: Optional[str]) -> None:
    """Initialize a new GitCo configuration.
    
    Creates a gitco-config.yml file in the current directory with default settings.
    """
    logger = get_logger()
    log_operation_start("configuration initialization", force=force, template=template)
    
    try:
        config_manager = ConfigManager()
        
        if template:
            logger.info(f"Using custom template: {template}")
            # TODO: Implement custom template loading
        else:
            # Create default configuration
            config = config_manager.create_default_config(force=force)
            
            # Add sample repositories if force or new file
            if force or not config_manager.config_path:
                sample_data = create_sample_config()
                config = config_manager._parse_config(sample_data)
                config_manager.save_config(config)
        
        log_operation_success("configuration initialization", config_file=config_manager.config_path)
        click.echo("✅ Configuration initialized successfully!")
        click.echo(f"Configuration file created: {config_manager.config_path}")
        click.echo("Next steps:")
        click.echo("1. Edit gitco-config.yml to add your repositories")
        click.echo("2. Set up your LLM API key")
        click.echo("3. Run 'gitco sync' to start managing your forks")
        
    except FileExistsError as e:
        log_operation_failure("configuration initialization", e, force=force)
        click.echo("❌ Configuration file already exists. Use --force to overwrite.")
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration initialization", e, force=force)
        click.echo(f"❌ Error initializing configuration: {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--repo", "-r", help="Sync specific repository"
)
@click.option(
    "--analyze", "-a", is_flag=True, help="Include AI analysis of changes"
)
@click.option(
    "--export", "-e", help="Export report to file"
)
@click.option(
    "--quiet", "-q", is_flag=True, help="Suppress output"
)
@click.option(
    "--log", "-l", help="Log to file"
)
@click.option(
    "--batch", "-b", is_flag=True, help="Process all repositories in batch"
)
@click.pass_context
def sync(
    ctx: click.Context,
    repo: Optional[str],
    analyze: bool,
    export: Optional[str],
    quiet: bool,
    log: Optional[str],
    batch: bool
) -> None:
    """Synchronize repositories with upstream changes.
    
    Fetches the latest changes from upstream repositories and merges them into your forks.
    """
    click.echo("Synchronizing repositories...")
    
    # TODO: Implement repository synchronization
    # This will be implemented in Commit 15
    
    if repo:
        click.echo(f"Syncing repository: {repo}")
    else:
        click.echo("Syncing all repositories")
    
    if analyze:
        click.echo("AI analysis enabled")
    
    if export:
        click.echo(f"Exporting report to: {export}")
    
    if quiet:
        click.echo("Quiet mode enabled")
    
    if log:
        click.echo(f"Logging to: {log}")
    
    if batch:
        click.echo("Batch processing enabled")
    
    click.echo("✅ Repository synchronization completed!")


@main.command()
@click.option(
    "--repo", "-r", required=True, help="Repository to analyze"
)
@click.option(
    "--prompt", "-p", help="Custom analysis prompt"
)
@click.option(
    "--repos", help="Analyze multiple repositories (comma-separated)"
)
@click.option(
    "--export", "-e", help="Export analysis to file"
)
@click.pass_context
def analyze(
    ctx: click.Context,
    repo: str,
    prompt: Optional[str],
    repos: Optional[str],
    export: Optional[str]
) -> None:
    """Analyze repository changes with AI.
    
    Generates human-readable summaries of upstream changes using AI analysis.
    """
    click.echo("Analyzing repository changes...")
    
    # TODO: Implement AI analysis
    # This will be implemented in Commit 22
    
    click.echo(f"Analyzing repository: {repo}")
    
    if prompt:
        click.echo(f"Using custom prompt: {prompt}")
    
    if repos:
        click.echo(f"Analyzing multiple repositories: {repos}")
    
    if export:
        click.echo(f"Exporting analysis to: {export}")
    
    click.echo("✅ Analysis completed!")


@main.command()
@click.option(
    "--skill", "-s", help="Filter by skill"
)
@click.option(
    "--label", "-l", help="Filter by label"
)
@click.option(
    "--export", "-e", help="Export results to file"
)
@click.option(
    "--limit", "-n", type=int, help="Limit number of results"
)
@click.pass_context
def discover(
    ctx: click.Context,
    skill: Optional[str],
    label: Optional[str],
    export: Optional[str],
    limit: Optional[int]
) -> None:
    """Discover contribution opportunities.
    
    Scans repositories for issues matching your skills and interests.
    """
    click.echo("Discovering contribution opportunities...")
    
    # TODO: Implement opportunity discovery
    # This will be implemented in Commit 30
    
    if skill:
        click.echo(f"Filtering by skill: {skill}")
    
    if label:
        click.echo(f"Filtering by label: {label}")
    
    if export:
        click.echo(f"Exporting results to: {export}")
    
    if limit:
        click.echo(f"Limiting results to: {limit}")
    
    click.echo("✅ Discovery completed!")


@main.command()
@click.option(
    "--repo", "-r", help="Show specific repository"
)
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed information"
)
@click.option(
    "--export", "-e", help="Export status to file"
)
@click.pass_context
def status(
    ctx: click.Context,
    repo: Optional[str],
    detailed: bool,
    export: Optional[str]
) -> None:
    """Show repository status.
    
    Displays the current status of your repositories and their sync state.
    """
    click.echo("Checking repository status...")
    
    # TODO: Implement status reporting
    # This will be implemented in Commit 33
    
    if repo:
        click.echo(f"Checking status for: {repo}")
    else:
        click.echo("Checking status for all repositories")
    
    if detailed:
        click.echo("Detailed mode enabled")
    
    if export:
        click.echo(f"Exporting status to: {export}")
    
    click.echo("✅ Status check completed!")


@main.command()
@click.pass_context
def help(ctx: click.Context) -> None:
    """Show detailed help information.
    
    Provides comprehensive help and usage examples for GitCo commands.
    """
    click.echo("GitCo Help")
    click.echo("==========")
    click.echo()
    click.echo("GitCo is a CLI tool for intelligent OSS fork management and contribution discovery.")
    click.echo()
    click.echo("Basic Commands:")
    click.echo("  init      Initialize configuration")
    click.echo("  config    Validate configuration")
    click.echo("  sync      Synchronize repositories")
    click.echo("  analyze   Analyze changes with AI")
    click.echo("  discover  Find contribution opportunities")
    click.echo("  status    Show repository status")
    click.echo("  help      Show this help message")
    click.echo()
    click.echo("For detailed help on any command, use:")
    click.echo("  gitco <command> --help")
    click.echo()
    click.echo("Examples:")
    click.echo("  gitco init")
    click.echo("  gitco config validate")
    click.echo("  gitco sync --repo django")
    click.echo("  gitco analyze --repo fastapi")
    click.echo("  gitco discover --skill python")
    click.echo("  gitco status --detailed")


@main.group()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Configuration management commands."""
    pass


@config.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration file.
    
    Checks the configuration file for errors and displays validation results.
    """
    logger = get_logger()
    log_operation_start("configuration validation")
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        errors = config_manager.validate_config(config)
        
        if not errors:
            log_operation_success("configuration validation", repo_count=len(config.repositories))
            click.echo("✅ Configuration is valid!")
            click.echo(f"Found {len(config.repositories)} repositories")
            click.echo(f"LLM provider: {config.settings.llm_provider}")
        else:
            log_operation_failure("configuration validation", ValidationError("Configuration has errors"))
            handle_validation_errors(errors, "Configuration")
            click.echo("❌ Configuration has errors:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)
            
    except FileNotFoundError as e:
        log_operation_failure("configuration validation", e)
        click.echo("❌ Configuration file not found. Run 'gitco init' to create one.")
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration validation", e)
        click.echo(f"❌ Error validating configuration: {e}")
        sys.exit(1)


@config.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show configuration status.
    
    Displays information about the current configuration.
    """
    logger = get_logger()
    log_operation_start("configuration status")
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        log_operation_success("configuration status", repo_count=len(config.repositories))
        click.echo("Configuration Status")
        click.echo("===================")
        
        click.echo(f"Configuration file: {config_manager.config_path}")
        click.echo(f"Repositories: {len(config.repositories)}")
        click.echo(f"LLM provider: {config.settings.llm_provider}")
        click.echo(f"Analysis enabled: {config.settings.analysis_enabled}")
        click.echo(f"Max repos per batch: {config.settings.max_repos_per_batch}")
        
        if config.repositories:
            click.echo("\nRepositories:")
            for repo in config.repositories:
                click.echo(f"  - {repo.name}: {repo.fork} -> {repo.upstream}")
        
    except FileNotFoundError as e:
        log_operation_failure("configuration status", e)
        click.echo("❌ Configuration file not found. Run 'gitco init' to create one.")
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration status", e)
        click.echo(f"❌ Error reading configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
