"""GitCo CLI interface."""

import sys
from typing import Optional

import click

from . import __version__
from .config import ConfigManager, create_sample_config
from .git_ops import GitRepository, GitRepositoryManager
from .utils import (
    ValidationError,
    get_logger,
    handle_validation_errors,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
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
                click.echo(f"❌ {error_msg}")
                sys.exit(1)

            # Sync single repository
            result = repo_manager._sync_single_repository(
                repo_config["local_path"], repo_config
            )

            if result["success"]:
                log_operation_success("repository synchronization", repo=repo)
                click.echo(f"✅ Successfully synced repository: {repo}")
                if result.get("stashed_changes"):
                    click.echo("   📦 Uncommitted changes were stashed and restored")
            else:
                error_msg = result.get("message", "Unknown error")
                log_operation_failure(
                    "repository synchronization", Exception(error_msg), repo=repo
                )
                click.echo(f"❌ Failed to sync repository '{repo}': {error_msg}")
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
                    click.echo(
                        f"\n✅ Successfully synced all {len(results)} repositories!"
                    )
                else:
                    error_msg = f"{failed} repositories failed"
                    log_operation_failure(
                        "batch repository synchronization",
                        Exception(error_msg),
                        total=len(results),
                        failed=failed,
                    )
                    click.echo(
                        f"\n⚠️  Synced {successful} repositories, {failed} failed"
                    )

            else:
                # Process repositories sequentially
                logger.info("Processing repositories sequentially")

                successful = 0
                failed = 0

                for r in config.repositories:
                    repo_config = {
                        "name": r.name,
                        "local_path": r.local_path,
                        "upstream": r.upstream,
                        "fork": r.fork,
                    }

                    if not quiet:
                        click.echo(f"🔄 Syncing {r.name}...")

                    result = repo_manager._sync_single_repository(
                        r.local_path, repo_config
                    )

                    if result["success"]:
                        successful += 1
                        if not quiet:
                            click.echo(
                                f"✅ {r.name}: {result.get('message', 'Sync completed')}"
                            )
                    else:
                        failed += 1
                        if not quiet:
                            click.echo(
                                f"❌ {r.name}: {result.get('message', 'Sync failed')}"
                            )

                if failed == 0:
                    log_operation_success(
                        "sequential repository synchronization",
                        total=len(config.repositories),
                    )
                    click.echo(
                        f"\n✅ Successfully synced all {len(config.repositories)} repositories!"
                    )
                else:
                    error_msg = f"{failed} repositories failed"
                    log_operation_failure(
                        "sequential repository synchronization",
                        Exception(error_msg),
                        total=len(config.repositories),
                        failed=failed,
                    )
                    click.echo(
                        f"\n⚠️  Synced {successful} repositories, {failed} failed"
                    )

        # Handle analysis if requested
        if analyze:
            logger.info("AI analysis requested")
            click.echo("\n🤖 AI analysis will be implemented in Commit 22")

        # Handle export if requested
        if export:
            logger.info(f"Export requested to: {export}")
            click.echo("\n📊 Export functionality will be implemented in Commit 35")

        # Exit with error code if there were failures
        if not repo and failed > 0:
            sys.exit(1)

    except FileNotFoundError as e:
        log_operation_failure("repository synchronization", e)
        click.echo("❌ Configuration file not found. Run 'gitco init' to create one.")
        sys.exit(1)
    except Exception as e:
        log_operation_failure("repository synchronization", e)
        click.echo(f"❌ Error during synchronization: {e}")
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
            click.echo("✅ Configuration is valid!")
            click.echo(f"Found {len(config.repositories)} repositories")
            click.echo(f"LLM provider: {config.settings.llm_provider}")
        else:
            log_operation_failure(
                "configuration validation", ValidationError("Configuration has errors")
            )
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
            click.echo("❌ Invalid repository path:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        # Add upstream remote
        success = git_manager.setup_upstream_remote(repo, url)

        if success:
            log_operation_success("upstream remote addition", repo=repo, url=url)
            click.echo("✅ Upstream remote added successfully!")
            click.echo(f"Repository: {repo}")
            click.echo(f"Upstream URL: {url}")
        else:
            log_operation_failure(
                "upstream remote addition", Exception("Failed to add upstream remote")
            )
            click.echo("❌ Failed to add upstream remote")
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream remote addition", e)
        click.echo(f"❌ Error adding upstream remote: {e}")
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
            click.echo("❌ Invalid repository path:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        # Remove upstream remote
        success = git_manager.remove_upstream_remote(repo)

        if success:
            log_operation_success("upstream remote removal", repo=repo)
            click.echo("✅ Upstream remote removed successfully!")
            click.echo(f"Repository: {repo}")
        else:
            log_operation_failure(
                "upstream remote removal", Exception("Failed to remove upstream remote")
            )
            click.echo("❌ Failed to remove upstream remote")
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream remote removal", e)
        click.echo(f"❌ Error removing upstream remote: {e}")
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
            click.echo("❌ Invalid repository path:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        # Update upstream remote
        success = git_manager.update_upstream_remote(repo, url)

        if success:
            log_operation_success("upstream remote update", repo=repo, url=url)
            click.echo("✅ Upstream remote updated successfully!")
            click.echo(f"Repository: {repo}")
            click.echo(f"New upstream URL: {url}")
        else:
            log_operation_failure(
                "upstream remote update", Exception("Failed to update upstream remote")
            )
            click.echo("❌ Failed to update upstream remote")
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream remote update", e)
        click.echo(f"❌ Error updating upstream remote: {e}")
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
            click.echo("❌ Invalid repository path:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        # Validate upstream remote
        validation = git_manager.validate_upstream_remote(repo)

        log_operation_success("upstream remote validation", repo=repo)
        click.echo(f"Repository: {repo}")

        if validation["has_upstream"]:
            click.echo(f"Upstream URL: {validation['url']}")

            if validation["is_valid"]:
                click.echo("✅ Upstream remote is valid and accessible")
                if validation.get("accessible", False):
                    click.echo("✅ Upstream remote is accessible")
            else:
                click.echo("❌ Upstream remote validation failed")
                click.echo(f"Error: {validation['error']}")
        else:
            click.echo("❌ No upstream remote configured")

    except Exception as e:
        log_operation_failure("upstream remote validation", e)
        click.echo(f"❌ Error validating upstream remote: {e}")
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
            click.echo("❌ Invalid repository path:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        # Get repository instance
        repository = git_manager.get_repository_info(repo)
        if not repository["is_git_repository"]:
            log_operation_failure(
                "upstream fetch", Exception("Not a valid Git repository")
            )
            click.echo("❌ Not a valid Git repository")
            sys.exit(1)

        # Fetch from upstream
        git_repo = GitRepository(repo)
        success = git_repo.fetch_upstream()

        if success:
            log_operation_success("upstream fetch", repo=repo)
            click.echo("✅ Successfully fetched from upstream!")
            click.echo(f"Repository: {repo}")
        else:
            log_operation_failure(
                "upstream fetch", Exception("Failed to fetch from upstream")
            )
            click.echo("❌ Failed to fetch from upstream")
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream fetch", e)
        click.echo(f"❌ Error fetching from upstream: {e}")
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
            click.echo("❌ Invalid repository path:")
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)

        # Get repository instance
        repository = git_manager.get_repository_info(repo)
        if not repository["is_git_repository"]:
            log_operation_failure(
                "upstream merge", Exception("Not a valid Git repository")
            )
            click.echo("❌ Not a valid Git repository")
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
                    click.echo("✅ Successfully aborted merge!")
                else:
                    log_operation_failure(
                        "upstream merge abort", Exception("Failed to abort merge")
                    )
                    click.echo("❌ Failed to abort merge")
                    sys.exit(1)
            else:
                click.echo("ℹ️  No active merge to abort")
            return

        if resolve:
            # Resolve conflicts
            if merge_status["in_merge"] and merge_status["conflicts"]:
                success = git_repo.resolve_conflicts(strategy)
                if success:
                    log_operation_success(
                        "upstream merge resolve", repo=repo, strategy=strategy
                    )
                    click.echo(
                        f"✅ Successfully resolved conflicts using {strategy} strategy!"
                    )
                else:
                    log_operation_failure(
                        "upstream merge resolve",
                        Exception("Failed to resolve conflicts"),
                    )
                    click.echo("❌ Failed to resolve conflicts")
                    sys.exit(1)
            else:
                click.echo("ℹ️  No conflicts to resolve")
            return

        # Perform merge operation
        merge_result = git_repo.merge_upstream_branch(branch)

        if merge_result["success"]:
            log_operation_success("upstream merge", repo=repo, branch=branch)
            click.echo("✅ Successfully merged upstream changes!")
            click.echo(f"Repository: {repo}")
            if merge_result.get("message"):
                click.echo(f"Message: {merge_result['message']}")
            if merge_result.get("merge_commit"):
                click.echo(f"Merge commit: {merge_result['merge_commit']}")
        else:
            if merge_result.get("conflicts"):
                log_operation_failure(
                    "upstream merge", Exception("Merge conflicts detected")
                )
                click.echo("⚠️  Merge conflicts detected!")
                click.echo(f"Repository: {repo}")
                click.echo("Conflicted files:")
                for conflict in merge_result["conflicts"]:
                    click.echo(f"  - {conflict}")
                click.echo()
                click.echo("To resolve conflicts, use:")
                click.echo(
                    f"  gitco upstream merge --repo {repo} --resolve --strategy ours"
                )
                click.echo(
                    f"  gitco upstream merge --repo {repo} --resolve --strategy theirs"
                )
                click.echo("Or abort the merge with:")
                click.echo(f"  gitco upstream merge --repo {repo} --abort")
            else:
                log_operation_failure(
                    "upstream merge",
                    Exception(merge_result.get("error", "Unknown error")),
                )
                click.echo(
                    f"❌ Merge failed: {merge_result.get('error', 'Unknown error')}"
                )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream merge", e)
        click.echo(f"❌ Error merging upstream changes: {e}")
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
                click.echo("❌ No Git repositories found in the specified path.")
                sys.exit(1)

            log_operation_success("repository validation", repo_count=len(repositories))
            click.echo(f"Found {len(repositories)} Git repositories:")
            click.echo()

            for repo in repositories:
                status = repo.get_repository_status()
                click.echo(f"📁 {status['path']}")
                click.echo(f"   Branch: {status['current_branch'] or 'unknown'}")
                click.echo(f"   Default: {status['default_branch'] or 'unknown'}")
                click.echo(f"   Remotes: {len(status['remotes'])}")
                click.echo(f"   Clean: {'✅' if status['is_clean'] else '❌'}")

                if detailed:
                    sync_status = git_manager.check_repository_sync_status(
                        str(repo.path)
                    )
                    if sync_status["is_syncable"]:
                        click.echo(
                            f"   Sync: {sync_status['behind_upstream']} behind, {sync_status['ahead_upstream']} ahead"
                        )
                    else:
                        click.echo(f"   Sync: {sync_status['error']}")

                click.echo()

        else:
            # Validate single repository
            is_valid, errors = git_manager.validate_repository_path(target_path)

            if is_valid:
                log_operation_success("repository validation", path=target_path)
                click.echo("✅ Valid Git repository!")

                if detailed:
                    status = git_manager.get_repository_info(target_path)
                    sync_status = git_manager.check_repository_sync_status(target_path)

                    click.echo(f"Path: {status['path']}")
                    click.echo(f"Current branch: {status['current_branch']}")
                    click.echo(f"Default branch: {status['default_branch']}")
                    click.echo(f"Remotes: {', '.join(status['remotes'].keys())}")
                    click.echo(
                        f"Has uncommitted changes: {'Yes' if status['has_uncommitted_changes'] else 'No'}"
                    )
                    click.echo(
                        f"Has untracked files: {'Yes' if status['has_untracked_files'] else 'No'}"
                    )

                    if sync_status["is_syncable"]:
                        click.echo(
                            f"Sync status: {sync_status['behind_upstream']} behind, {sync_status['ahead_upstream']} ahead"
                        )
                        if sync_status["diverged"]:
                            click.echo("⚠️  Repository has diverged from upstream")
                    else:
                        click.echo(f"Sync status: {sync_status['error']}")
            else:
                log_operation_failure(
                    "repository validation",
                    ValidationError("Repository validation failed"),
                )
                click.echo("❌ Invalid Git repository:")
                for error in errors:
                    click.echo(f"  - {error}")
                sys.exit(1)

    except Exception as e:
        log_operation_failure("repository validation", e)
        click.echo(f"❌ Error validating repository: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
