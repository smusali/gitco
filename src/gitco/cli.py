"""GitCo CLI interface."""

import sys
from typing import Optional

import click

from . import __version__
from .config import ConfigManager, create_sample_config
from .git_ops import GitRepository, GitRepositoryManager
from .utils import (
    ValidationError,
    console,
    create_progress_bar,
    get_logger,
    handle_validation_errors,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    print_error_panel,
    print_info_panel,
    print_success_panel,
    print_warning_panel,
    setup_logging,
)


@click.group()
@click.version_option(version=__version__, prog_name="gitco")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.option("--log-file", help="Log to file")
@click.pass_context
def main(
    ctx: click.Context, verbose: bool, quiet: bool, log_file: Optional[str]
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
    ctx.obj["log_file"] = log_file

    # Setup logging
    setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    logger = get_logger()
    logger.debug("GitCo CLI started")


@main.command()
@click.option("--force", "-f", is_flag=True, help="Overwrite existing configuration")
@click.option("--template", "-t", help="Use custom template for configuration")
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

        log_operation_success(
            "configuration initialization", config_file=config_manager.config_path
        )

        print_success_panel(
            "Configuration initialized successfully!",
            f"Configuration file created: {config_manager.config_path}\n\n"
            "Next steps:\n"
            "1. Edit gitco-config.yml to add your repositories\n"
            "2. Set up your LLM API key\n"
            "3. Run 'gitco sync' to start managing your forks",
        )

    except FileExistsError as e:
        log_operation_failure("configuration initialization", e, force=force)
        print_error_panel(
            "Configuration file already exists",
            "Use --force to overwrite the existing configuration file.",
        )
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration initialization", e, force=force)
        print_error_panel("Error initializing configuration", str(e))
        sys.exit(1)


@main.command()
@click.option("--repo", "-r", help="Sync specific repository")
@click.option("--analyze", "-a", is_flag=True, help="Include AI analysis of changes")
@click.option("--export", "-e", help="Export report to file")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.option("--log", "-l", help="Log to file")
@click.option("--batch", "-b", is_flag=True, help="Process all repositories in batch")
@click.option(
    "--max-workers",
    "-w",
    type=int,
    default=4,
    help="Maximum concurrent workers for batch processing",
)
@click.pass_context
def sync(
    ctx: click.Context,
    repo: Optional[str],
    analyze: bool,
    export: Optional[str],
    quiet: bool,
    log: Optional[str],
    batch: bool,
    max_workers: int,
) -> None:
    """Synchronize repositories with upstream changes.

    Fetches the latest changes from upstream repositories and merges them into your forks.
    """
    logger = get_logger()
    log_operation_start(
        "repository synchronization", repo=repo, batch=batch, analyze=analyze
    )

    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()

        # Initialize repository manager
        repo_manager = GitRepositoryManager()

        # Track sync failures
        failed = 0

        if repo:
            # Sync specific repository
            logger.info(f"Syncing specific repository: {repo}")

            # Find repository in config
            repo_config = None
            for r in config.repositories:
                if r.name == repo:
                    repo_config = {
                        "name": r.name,
                        "local_path": r.local_path,
                        "upstream": r.upstream,
                        "fork": r.fork,
                    }
                    break

            if not repo_config:
                error_msg = f"Repository '{repo}' not found in configuration"
                log_operation_failure(
                    "repository synchronization", Exception(error_msg)
                )
                print_error_panel(
                    "Repository not found",
                    f"Repository '{repo}' not found in configuration.\n"
                    "Use 'gitco init' to create a configuration or add the repository.",
                )
                sys.exit(1)

            # Sync single repository with progress indicator
            if not quiet:
                console.print(f"[blue]🔄 Syncing repository: {repo}[/blue]")

            result = repo_manager._sync_single_repository(
                repo_config["local_path"], repo_config
            )

            if result["success"]:
                log_operation_success("repository synchronization", repo=repo)
                details = ""
                if result.get("stashed_changes"):
                    details = "📦 Uncommitted changes were stashed and restored"

                print_success_panel(f"Successfully synced repository: {repo}", details)
            else:
                error_msg = result.get("message", "Unknown error")
                log_operation_failure(
                    "repository synchronization", Exception(error_msg), repo=repo
                )
                print_error_panel(f"Failed to sync repository '{repo}'", error_msg)
                sys.exit(1)

        else:
            # Sync all repositories
            logger.info("Syncing all repositories")

            if batch:
                # Use batch processing
                logger.info(f"Using batch processing with {max_workers} workers")

                # Convert repositories to list of dicts for batch processing
                repositories = []
                for r in config.repositories:
                    repositories.append(
                        {
                            "name": r.name,
                            "local_path": r.local_path,
                            "upstream": r.upstream,
                            "fork": r.fork,
                            "skills": r.skills,
                            "analysis_enabled": r.analysis_enabled,
                        }
                    )

                # Process repositories in batch
                results = repo_manager.batch_sync_repositories(
                    repositories=repositories,
                    max_workers=max_workers,
                    show_progress=not quiet,
                )

                # Count successful and failed operations
                successful = sum(1 for r in results if r.success)
                failed = len(results) - successful

                if failed == 0:
                    log_operation_success(
                        "batch repository synchronization", total=len(results)
                    )
                    print_success_panel(
                        f"Successfully synced all {len(results)} repositories!",
                        "All repositories are now up to date with their upstream sources.",
                    )
                else:
                    error_msg = f"{failed} repositories failed"
                    log_operation_failure(
                        "batch repository synchronization",
                        Exception(error_msg),
                        total=len(results),
                        failed=failed,
                    )
                    print_error_panel(
                        f"Sync completed with {failed} failures",
                        f"Successfully synced {successful} repositories, {failed} failed.\n"
                        "Check the output above for details on failed repositories.",
                    )

            else:
                # Process repositories sequentially with progress bar
                logger.info("Processing repositories sequentially")

                successful = 0
                failed = 0

                if not quiet:
                    with create_progress_bar(
                        "Syncing repositories", len(config.repositories)
                    ) as progress:
                        task = progress.add_task(
                            "[cyan]Syncing repositories[/cyan]",
                            total=len(config.repositories),
                        )

                        for r in config.repositories:
                            repo_config = {
                                "name": r.name,
                                "local_path": r.local_path,
                                "upstream": r.upstream,
                                "fork": r.fork,
                            }

                            progress.update(task, description=f"Syncing {r.name}...")

                            result = repo_manager._sync_single_repository(
                                r.local_path, repo_config
                            )

                            if result["success"]:
                                successful += 1
                                progress.update(
                                    task,
                                    description=f"✅ {r.name}: {result.get('message', 'Sync completed')}",
                                )
                            else:
                                failed += 1
                                progress.update(
                                    task,
                                    description=f"❌ {r.name}: {result.get('message', 'Sync failed')}",
                                )

                            progress.advance(task)
                else:
                    # Quiet mode - no progress bar
                    for r in config.repositories:
                        repo_config = {
                            "name": r.name,
                            "local_path": r.local_path,
                            "upstream": r.upstream,
                            "fork": r.fork,
                        }

                        result = repo_manager._sync_single_repository(
                            r.local_path, repo_config
                        )

                        if result["success"]:
                            successful += 1
                        else:
                            failed += 1

                if failed == 0:
                    log_operation_success(
                        "sequential repository synchronization",
                        total=len(config.repositories),
                    )
                    print_success_panel(
                        f"Successfully synced all {len(config.repositories)} repositories!",
                        "All repositories are now up to date with their upstream sources.",
                    )
                else:
                    error_msg = f"{failed} repositories failed"
                    log_operation_failure(
                        "sequential repository synchronization",
                        Exception(error_msg),
                        total=len(config.repositories),
                        failed=failed,
                    )
                    print_error_panel(
                        f"Sync completed with {failed} failures",
                        f"Successfully synced {successful} repositories, {failed} failed.\n"
                        "Check the output above for details on failed repositories.",
                    )

        # Handle analysis if requested
        if analyze:
            logger.info("AI analysis requested")
            print_info_panel(
                "AI Analysis",
                "AI analysis functionality will be implemented in Commit 22.\n"
                "This will provide intelligent summaries of upstream changes.",
            )

        # Handle export if requested
        if export:
            logger.info(f"Export requested to: {export}")
            print_info_panel(
                "Export Functionality",
                f"Export functionality will be implemented in Commit 35.\n"
                f"Reports will be exported to: {export}",
            )

        # Exit with error code if there were failures
        if not repo and failed > 0:
            sys.exit(1)

    except FileNotFoundError as e:
        log_operation_failure("repository synchronization", e)
        print_error_panel(
            "Configuration file not found",
            "Run 'gitco init' to create a configuration file.",
        )
        sys.exit(1)
    except Exception as e:
        log_operation_failure("repository synchronization", e)
        print_error_panel("Error during synchronization", str(e))
        sys.exit(1)


@main.command()
@click.option("--repo", "-r", required=True, help="Repository to analyze")
@click.option("--prompt", "-p", help="Custom analysis prompt")
@click.option("--repos", help="Analyze multiple repositories (comma-separated)")
@click.option("--export", "-e", help="Export analysis to file")
@click.pass_context
def analyze(
    ctx: click.Context,
    repo: str,
    prompt: Optional[str],
    repos: Optional[str],
    export: Optional[str],
) -> None:
    """Analyze repository changes with AI.

    Generates human-readable summaries of upstream changes using AI analysis.
    """
    print_info_panel(
        "Analyzing Repository Changes",
        f"Analyzing repository: {repo}\n"
        "This functionality will be implemented in Commit 22.",
    )

    # TODO: Implement AI analysis
    # This will be implemented in Commit 22

    if prompt:
        print_info_panel("Using Custom Prompt", f"Using custom prompt: {prompt}")

    if repos:
        print_info_panel(
            "Analyzing Multiple Repositories",
            f"Analyzing multiple repositories: {repos}",
        )

    if export:
        print_info_panel("Exporting Analysis", f"Exporting analysis to: {export}")

    print_success_panel("Analysis Completed", "✅ Analysis completed!")


@main.command()
@click.option("--skill", "-s", help="Filter by skill")
@click.option("--label", "-l", help="Filter by label")
@click.option("--export", "-e", help="Export results to file")
@click.option("--limit", "-n", type=int, help="Limit number of results")
@click.pass_context
def discover(
    ctx: click.Context,
    skill: Optional[str],
    label: Optional[str],
    export: Optional[str],
    limit: Optional[int],
) -> None:
    """Discover contribution opportunities.

    Scans repositories for issues matching your skills and interests.
    """
    print_info_panel(
        "Discovering Contribution Opportunities",
        "This functionality will be implemented in Commit 30.",
    )

    # TODO: Implement opportunity discovery
    # This will be implemented in Commit 30

    if skill:
        print_info_panel("Filtering by Skill", f"Filtering by skill: {skill}")

    if label:
        print_info_panel("Filtering by Label", f"Filtering by label: {label}")

    if export:
        print_info_panel("Exporting Results", f"Exporting results to: {export}")

    if limit:
        print_info_panel("Limiting Results", f"Limiting results to: {limit}")

    print_success_panel("Discovery Completed", "✅ Discovery completed!")


@main.command()
@click.option("--repo", "-r", help="Show specific repository")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed information")
@click.option("--export", "-e", help="Export status to file")
@click.pass_context
def status(
    ctx: click.Context, repo: Optional[str], detailed: bool, export: Optional[str]
) -> None:
    """Show repository status.

    Displays the current status of your repositories and their sync state.
    """
    print_info_panel(
        "Checking Repository Status",
        "This functionality will be implemented in Commit 33.",
    )

    # TODO: Implement status reporting
    # This will be implemented in Commit 33

    if repo:
        print_info_panel(
            "Checking Status for Specific Repository", f"Checking status for: {repo}"
        )
    else:
        print_info_panel(
            "Checking Status for All Repositories",
            "Checking status for all repositories",
        )

    if detailed:
        print_info_panel("Detailed Mode Enabled", "Detailed mode enabled")

    if export:
        print_info_panel("Exporting Status", f"Exporting status to: {export}")

    print_success_panel("Status Check Completed", "✅ Status check completed!")


@main.command()
@click.pass_context
def help(ctx: click.Context) -> None:
    """Show detailed help information.

    Provides comprehensive help and usage examples for GitCo commands.
    """
    print_info_panel(
        "GitCo Help",
        "This provides comprehensive help and usage examples for GitCo commands.",
    )
    click.echo()
    click.echo(
        "GitCo is a CLI tool for intelligent OSS fork management and contribution discovery."
    )
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
    click.echo("  gitco validate-repo --path ~/code/django")
    click.echo("  gitco validate-repo --recursive --detailed")


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
    get_logger()
    log_operation_start("configuration validation")

    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()

        errors = config_manager.validate_config(config)

        if not errors:
            log_operation_success(
                "configuration validation", repo_count=len(config.repositories)
            )
            print_success_panel(
                "Configuration is valid!",
                f"Found {len(config.repositories)} repositories\n"
                f"LLM provider: {config.settings.llm_provider}",
            )
        else:
            log_operation_failure(
                "configuration validation", ValidationError("Configuration has errors")
            )
            handle_validation_errors(errors, "Configuration")
            print_error_panel(
                "Configuration has errors", "❌ Configuration has errors:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

    except FileNotFoundError as e:
        log_operation_failure("configuration validation", e)
        print_error_panel(
            "Configuration file not found",
            "Run 'gitco init' to create a configuration file.",
        )
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration validation", e)
        print_error_panel("Error validating configuration", str(e))
        sys.exit(1)


@config.command()
@click.pass_context
def config_status(ctx: click.Context) -> None:
    """Show configuration status.

    Displays information about the current configuration.
    """
    get_logger()
    log_operation_start("configuration status")

    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()

        log_operation_success(
            "configuration status", repo_count=len(config.repositories)
        )
        print_success_panel(
            "Configuration Status", "Configuration Status\n===================\n\n"
        )

        print_info_panel(
            "Configuration File", f"Configuration file: {config_manager.config_path}"
        )
        print_info_panel("Repositories", f"Repositories: {len(config.repositories)}")
        print_info_panel(
            "LLM Provider", f"LLM provider: {config.settings.llm_provider}"
        )
        print_info_panel(
            "Analysis Enabled", f"Analysis enabled: {config.settings.analysis_enabled}"
        )
        print_info_panel(
            "Max Repos per Batch",
            f"Max repos per batch: {config.settings.max_repos_per_batch}",
        )

        if config.repositories:
            print_info_panel("Repositories", "Repositories:\n")
            for repo in config.repositories:
                print_info_panel(
                    "Repository", f"  - {repo.name}: {repo.fork} -> {repo.upstream}"
                )

    except FileNotFoundError as e:
        log_operation_failure("configuration status", e)
        print_error_panel(
            "Configuration file not found",
            "Run 'gitco init' to create a configuration file.",
        )
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration status", e)
        print_error_panel("Error reading configuration", str(e))
        sys.exit(1)


@main.group()
@click.pass_context
def upstream(ctx: click.Context) -> None:
    """Manage upstream remotes for repositories."""
    pass


@upstream.command()
@click.option("--repo", "-r", required=True, help="Repository path")
@click.option("--url", "-u", required=True, help="Upstream repository URL")
@click.pass_context
def add(ctx: click.Context, repo: str, url: str) -> None:
    """Add upstream remote to a repository.

    Adds or updates the upstream remote for the specified repository.
    """
    log_operation_start("upstream remote addition", repo=repo, url=url)

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream remote addition", ValidationError("Invalid repository path")
            )
            print_error_panel(
                "Invalid Repository Path", "❌ Invalid repository path:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

        # Add upstream remote
        success = git_manager.setup_upstream_remote(repo, url)

        if success:
            log_operation_success("upstream remote addition", repo=repo, url=url)
            print_success_panel(
                "Upstream remote added successfully!",
                f"Repository: {repo}\nUpstream URL: {url}",
            )
        else:
            log_operation_failure(
                "upstream remote addition", Exception("Failed to add upstream remote")
            )
            print_error_panel(
                "Failed to add upstream remote", "❌ Failed to add upstream remote"
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream remote addition", e)
        print_error_panel("Error adding upstream remote", str(e))
        sys.exit(1)


@upstream.command()
@click.option("--repo", "-r", required=True, help="Repository path")
@click.pass_context
def remove(ctx: click.Context, repo: str) -> None:
    """Remove upstream remote from a repository.

    Removes the upstream remote if it exists.
    """
    log_operation_start("upstream remote removal", repo=repo)

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream remote removal", ValidationError("Invalid repository path")
            )
            print_error_panel(
                "Invalid Repository Path", "❌ Invalid repository path:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

        # Remove upstream remote
        success = git_manager.remove_upstream_remote(repo)

        if success:
            log_operation_success("upstream remote removal", repo=repo)
            print_success_panel(
                "Upstream remote removed successfully!", f"Repository: {repo}"
            )
        else:
            log_operation_failure(
                "upstream remote removal", Exception("Failed to remove upstream remote")
            )
            print_error_panel(
                "Failed to remove upstream remote",
                "❌ Failed to remove upstream remote",
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream remote removal", e)
        print_error_panel("Error removing upstream remote", str(e))
        sys.exit(1)


@upstream.command()
@click.option("--repo", "-r", required=True, help="Repository path")
@click.option("--url", "-u", required=True, help="New upstream repository URL")
@click.pass_context
def update(ctx: click.Context, repo: str, url: str) -> None:
    """Update upstream remote URL for a repository.

    Updates the URL of the existing upstream remote.
    """
    log_operation_start("upstream remote update", repo=repo, url=url)

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream remote update", ValidationError("Invalid repository path")
            )
            print_error_panel(
                "Invalid Repository Path", "❌ Invalid repository path:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

        # Update upstream remote
        success = git_manager.update_upstream_remote(repo, url)

        if success:
            log_operation_success("upstream remote update", repo=repo, url=url)
            print_success_panel(
                "Upstream remote updated successfully!",
                f"Repository: {repo}\nNew upstream URL: {url}",
            )
        else:
            log_operation_failure(
                "upstream remote update", Exception("Failed to update upstream remote")
            )
            print_error_panel(
                "Failed to update upstream remote",
                "❌ Failed to update upstream remote",
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream remote update", e)
        print_error_panel("Error updating upstream remote", str(e))
        sys.exit(1)


@upstream.command()
@click.option("--repo", "-r", required=True, help="Repository path")
@click.pass_context
def validate_upstream(ctx: click.Context, repo: str) -> None:
    """Validate upstream remote for a repository.

    Checks if the upstream remote is properly configured and accessible.
    """
    log_operation_start("upstream remote validation", repo=repo)

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream remote validation", ValidationError("Invalid repository path")
            )
            print_error_panel(
                "Invalid Repository Path", "❌ Invalid repository path:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

        # Validate upstream remote
        validation = git_manager.validate_upstream_remote(repo)

        log_operation_success("upstream remote validation", repo=repo)
        print_success_panel(
            f"Repository: {repo}", "Upstream Remote Status\n======================\n\n"
        )

        if validation["has_upstream"]:
            print_info_panel("Upstream URL", f"Upstream URL: {validation['url']}")

            if validation["is_valid"]:
                print_success_panel(
                    "Upstream remote is valid and accessible",
                    "✅ Upstream remote is valid and accessible",
                )
                if validation.get("accessible", False):
                    print_success_panel(
                        "Upstream remote is accessible",
                        "✅ Upstream remote is accessible",
                    )
            else:
                print_error_panel(
                    "Upstream remote validation failed", f"Error: {validation['error']}"
                )
        else:
            print_error_panel(
                "No upstream remote configured", "❌ No upstream remote configured"
            )

    except Exception as e:
        log_operation_failure("upstream remote validation", e)
        print_error_panel("Error validating upstream remote", str(e))
        sys.exit(1)


@upstream.command()
@click.option("--repo", "-r", required=True, help="Repository path")
@click.pass_context
def fetch(ctx: click.Context, repo: str) -> None:
    """Fetch latest changes from upstream.

    Fetches the latest changes from the upstream remote.
    """
    log_operation_start("upstream fetch", repo=repo)

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream fetch", ValidationError("Invalid repository path")
            )
            print_error_panel(
                "Invalid Repository Path", "❌ Invalid repository path:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

        # Get repository instance
        repository = git_manager.get_repository_info(repo)
        if not repository["is_git_repository"]:
            log_operation_failure(
                "upstream fetch", Exception("Not a valid Git repository")
            )
            print_error_panel(
                "Not a valid Git repository", "❌ Not a valid Git repository"
            )
            sys.exit(1)

        # Fetch from upstream
        git_repo = GitRepository(repo)
        success = git_repo.fetch_upstream()

        if success:
            log_operation_success("upstream fetch", repo=repo)
            print_success_panel(
                "Successfully fetched from upstream!", f"Repository: {repo}"
            )
        else:
            log_operation_failure(
                "upstream fetch", Exception("Failed to fetch from upstream")
            )
            print_error_panel(
                "Failed to fetch from upstream", "❌ Failed to fetch from upstream"
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream fetch", e)
        print_error_panel("Error fetching from upstream", str(e))
        sys.exit(1)


@upstream.command()
@click.option("--repo", "-r", required=True, help="Repository path")
@click.option("--branch", "-b", help="Branch to merge (default: default branch)")
@click.option(
    "--strategy",
    "-s",
    type=click.Choice(["ours", "theirs", "manual"]),
    default="ours",
    help="Conflict resolution strategy",
)
@click.option("--abort", "-a", is_flag=True, help="Abort current merge")
@click.option("--resolve", is_flag=True, help="Resolve conflicts automatically")
@click.pass_context
def merge(
    ctx: click.Context,
    repo: str,
    branch: Optional[str],
    strategy: str,
    abort: bool,
    resolve: bool,
) -> None:
    """Merge upstream changes into current branch.

    Merges the latest changes from upstream into the current branch with conflict detection.
    """
    log_operation_start("upstream merge", repo=repo, branch=branch, strategy=strategy)

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream merge", ValidationError("Invalid repository path")
            )
            print_error_panel(
                "Invalid Repository Path", "❌ Invalid repository path:\n"
            )
            for error in errors:
                print_error_panel("Error", f"  - {error}")
            sys.exit(1)

        # Get repository instance
        repository = git_manager.get_repository_info(repo)
        if not repository["is_git_repository"]:
            log_operation_failure(
                "upstream merge", Exception("Not a valid Git repository")
            )
            print_error_panel(
                "Not a valid Git repository", "❌ Not a valid Git repository"
            )
            sys.exit(1)

        git_repo = GitRepository(repo)

        # Check merge status first
        merge_status = git_repo.get_merge_status()

        if abort:
            # Abort current merge
            if merge_status["in_merge"]:
                success = git_repo.abort_merge()
                if success:
                    log_operation_success("upstream merge abort", repo=repo)
                    print_success_panel(
                        "Merge aborted successfully!", "✅ Successfully aborted merge!"
                    )
                else:
                    log_operation_failure(
                        "upstream merge abort", Exception("Failed to abort merge")
                    )
                    print_error_panel(
                        "Failed to abort merge", "❌ Failed to abort merge"
                    )
                    sys.exit(1)
            else:
                print_info_panel(
                    "No active merge to abort", "ℹ️  No active merge to abort"
                )
            return

        if resolve:
            # Resolve conflicts
            if merge_status["in_merge"] and merge_status["conflicts"]:
                success = git_repo.resolve_conflicts(strategy)
                if success:
                    log_operation_success(
                        "upstream merge resolve", repo=repo, strategy=strategy
                    )
                    print_success_panel(
                        f"Conflicts resolved using {strategy} strategy!",
                        f"✅ Successfully resolved conflicts using {strategy} strategy!",
                    )
                else:
                    log_operation_failure(
                        "upstream merge resolve",
                        Exception("Failed to resolve conflicts"),
                    )
                    print_error_panel(
                        "Failed to resolve conflicts", "❌ Failed to resolve conflicts"
                    )
                    sys.exit(1)
            else:
                print_info_panel(
                    "No conflicts to resolve", "ℹ️  No conflicts to resolve"
                )
            return

        # Perform merge operation
        merge_result = git_repo.merge_upstream_branch(branch)

        if merge_result["success"]:
            log_operation_success("upstream merge", repo=repo, branch=branch)
            print_success_panel(
                "Successfully merged upstream changes!", f"Repository: {repo}\n"
            )
            if merge_result.get("message"):
                print_info_panel("Message", f"Message: {merge_result['message']}")
            if merge_result.get("merge_commit"):
                print_info_panel(
                    "Merge Commit", f"Merge commit: {merge_result['merge_commit']}"
                )
        else:
            if merge_result.get("conflicts"):
                log_operation_failure(
                    "upstream merge", Exception("Merge conflicts detected")
                )
                print_error_panel(
                    "Merge Conflicts Detected",
                    "⚠️  Merge conflicts detected!\n\n"
                    f"Repository: {repo}\n"
                    "Conflicted files:\n",
                )
                for conflict in merge_result["conflicts"]:
                    print_error_panel("Conflict", f"  - {conflict}")
                print_info_panel(
                    "Resolution Options",
                    "To resolve conflicts, use:\n"
                    f"  gitco upstream merge --repo {repo} --resolve --strategy ours\n"
                    f"  gitco upstream merge --repo {repo} --resolve --strategy theirs\n",
                )
                print_info_panel(
                    "Abort Merge",
                    "Or abort the merge with:\n"
                    f"  gitco upstream merge --repo {repo} --abort",
                )
            else:
                log_operation_failure(
                    "upstream merge",
                    Exception(merge_result.get("error", "Unknown error")),
                )
                print_error_panel(
                    "Merge failed",
                    f"❌ Merge failed: {merge_result.get('error', 'Unknown error')}",
                )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream merge", e)
        print_error_panel("Error merging upstream changes", str(e))
        sys.exit(1)


@main.command()
@click.option("--path", "-p", help="Path to validate (default: current directory)")
@click.option("--recursive", "-r", is_flag=True, help="Recursively find repositories")
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed repository information"
)
@click.pass_context
def validate_repo(
    ctx: click.Context, path: Optional[str], recursive: bool, detailed: bool
) -> None:
    """Validate Git repositories.

    Checks if the specified path is a valid Git repository and provides detailed
    information about its status, remotes, and sync state.
    """
    log_operation_start("repository validation", path=path, recursive=recursive)

    try:
        git_manager = GitRepositoryManager()
        target_path = path or "."

        if recursive:
            # Find all repositories in the directory tree
            repositories = git_manager.detect_repositories(target_path)

            if not repositories:
                log_operation_failure(
                    "repository validation", Exception("No Git repositories found")
                )
                print_error_panel(
                    "No Git Repositories Found",
                    "❌ No Git repositories found in the specified path.",
                )
                sys.exit(1)

            log_operation_success("repository validation", repo_count=len(repositories))
            print_success_panel(
                f"Found {len(repositories)} Git repositories!",
                f"Found {len(repositories)} Git repositories:\n",
            )
            for repo in repositories:
                status = repo.get_repository_status()
                print_info_panel("Repository", f"📁 {status['path']}\n")
                print_info_panel(
                    "Branch", f"   Branch: {status['current_branch'] or 'unknown'}"
                )
                print_info_panel(
                    "Default Branch",
                    f"   Default: {status['default_branch'] or 'unknown'}",
                )
                print_info_panel("Remotes", f"   Remotes: {len(status['remotes'])}")
                print_info_panel(
                    "Clean", f"   Clean: {'✅' if status['is_clean'] else '❌'}"
                )

                if detailed:
                    sync_status = git_manager.check_repository_sync_status(
                        str(repo.path)
                    )
                    if sync_status["is_syncable"]:
                        print_info_panel(
                            "Sync Status",
                            f"   Sync: {sync_status['behind_upstream']} behind, {sync_status['ahead_upstream']} ahead",
                        )
                    else:
                        print_error_panel(
                            "Sync Status", f"   Sync: {sync_status['error']}"
                        )

                print_info_panel("Repository", "")

        else:
            # Validate single repository
            is_valid, errors = git_manager.validate_repository_path(target_path)

            if is_valid:
                log_operation_success("repository validation", path=target_path)
                print_success_panel("Valid Git repository!", "✅ Valid Git repository!")

                if detailed:
                    status = git_manager.get_repository_info(target_path)
                    sync_status = git_manager.check_repository_sync_status(target_path)

                    print_info_panel("Path", f"Path: {status['path']}")
                    print_info_panel(
                        "Current Branch", f"Current branch: {status['current_branch']}"
                    )
                    print_info_panel(
                        "Default Branch", f"Default branch: {status['default_branch']}"
                    )
                    print_info_panel(
                        "Remotes", f"Remotes: {', '.join(status['remotes'].keys())}"
                    )
                    print_info_panel(
                        "Uncommitted Changes",
                        f"Has uncommitted changes: {'Yes' if status['has_uncommitted_changes'] else 'No'}",
                    )
                    print_info_panel(
                        "Untracked Files",
                        f"Has untracked files: {'Yes' if status['has_untracked_files'] else 'No'}",
                    )

                    if sync_status["is_syncable"]:
                        print_info_panel(
                            "Sync Status",
                            f"Sync status: {sync_status['behind_upstream']} behind, {sync_status['ahead_upstream']} ahead",
                        )
                        if sync_status["diverged"]:
                            print_warning_panel(
                                "Repository Diverged",
                                "⚠️  Repository has diverged from upstream",
                            )
                    else:
                        print_error_panel(
                            "Sync Status", f"Sync status: {sync_status['error']}"
                        )
            else:
                log_operation_failure(
                    "repository validation",
                    ValidationError("Repository validation failed"),
                )
                print_error_panel(
                    "Invalid Git repository", "❌ Invalid Git repository:\n"
                )
                for error in errors:
                    print_error_panel("Error", f"  - {error}")
                sys.exit(1)

    except Exception as e:
        log_operation_failure("repository validation", e)
        print_error_panel("Error validating repository", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
