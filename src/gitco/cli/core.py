"""Core CLI commands for GitCo.

This module contains the main CLI commands: init, sync, analyze, discover,
status, activity, logs, performance, version, help, completion, validate-repo.
"""

import os
import sys
from typing import Optional

import click
import yaml

from .. import __version__
from ..libs.config import ConfigManager, create_sample_config
from ..utils.common import (
    console,
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    print_error_panel,
    print_success_panel,
    print_warning_panel,
)


def register_core_commands(main_group):
    """Register all core commands with the main CLI group."""
    main_group.add_command(init)
    main_group.add_command(sync)
    main_group.add_command(analyze)
    main_group.add_command(discover)
    main_group.add_command(status)
    main_group.add_command(activity)
    main_group.add_command(logs)
    main_group.add_command(performance)
    main_group.add_command(version)
    main_group.add_command(help)
    main_group.add_command(completion)
    main_group.add_command(validate_repo)


@click.command()
@click.option("--force", "-f", is_flag=True, help="Overwrite existing configuration")
@click.option("--template", "-t", help="Use custom template for configuration")
@click.option("--interactive", "-i", is_flag=True, help="Use interactive guided setup")
@click.option(
    "--non-interactive",
    "-n",
    is_flag=True,
    help="Use non-interactive setup with defaults",
)
@click.option("--config-path", help="Custom configuration path")
@click.pass_context
def init(
    ctx: click.Context,
    force: bool,
    template: Optional[str],
    interactive: bool,
    non_interactive: bool,
    config_path: Optional[str],
) -> None:
    """Initialize a new GitCo configuration.

    Creates a gitco-config.yml file in the current directory with guided setup.
    """
    logger = get_logger()
    log_operation_start(
        "configuration initialization",
        force=force,
        template=template,
        interactive=interactive,
        config_path=config_path,
    )

    try:
        # Use custom config path if provided, otherwise use global config
        config_file = config_path or ctx.obj.get("config")
        config_manager = ConfigManager(config_file)

        if template:
            logger.info(f"Using custom template: {template}")
            try:
                # Try to load the template file
                if os.path.exists(template):
                    with open(template, encoding="utf-8") as f:
                        template_data = yaml.safe_load(f)
                    config = config_manager._parse_config(template_data)
                    config_manager.save_config(config)
                else:
                    # If template doesn't exist, create a basic template
                    print_warning_panel(
                        "Template file not found",
                        f"Template file '{template}' not found. Creating basic template.",
                    )
                    config = config_manager.create_default_config(force=force)
            except FileExistsError:
                # Handle the case where config file already exists
                if force:
                    config = config_manager.create_default_config(force=True)
                else:
                    raise
            except Exception as e:
                logger.warning(f"Failed to load template {template}: {e}")
                print_warning_panel(
                    "Template loading failed",
                    f"Failed to load template '{template}'. Using default configuration.",
                )
                config = config_manager.create_default_config(force=force)
        elif interactive:
            # Interactive guided setup
            from ..utils.prompts import (
                prompt_general_settings,
                prompt_github_settings,
                prompt_llm_settings,
                prompt_repositories,
                prompt_save_configuration,
                show_configuration_summary,
            )

            console.print(
                "\n[bold blue]🎉 Welcome to GitCo Configuration Setup![/bold blue]"
            )
            console.print(
                "This guided setup will help you configure GitCo for managing your OSS forks.\n"
            )

            # Get general settings
            general_settings = prompt_general_settings()

            # Get LLM settings
            llm_settings = prompt_llm_settings()

            # Get GitHub settings
            github_settings = prompt_github_settings()

            # Get repositories
            repositories = prompt_repositories()

            # Show summary
            show_configuration_summary(
                repositories, general_settings, llm_settings, github_settings
            )

            # Confirm save
            if prompt_save_configuration():
                # Merge all settings
                settings = {**general_settings, **llm_settings, **github_settings}

                # Create configuration data
                config_data = {
                    "repositories": repositories,
                    "settings": settings,
                }

                # Parse and save configuration
                config = config_manager._parse_config(config_data)
                config_manager.save_config(config)

                log_operation_success(
                    "configuration initialization",
                    config_file=config_manager.config_path,
                    repo_count=len(repositories),
                )

                print_success_panel(
                    "Configuration initialized successfully!",
                    f"Configuration file created: {config_manager.config_path}\n\n"
                    "Next steps:\n"
                    "1. Set up your environment variables for API keys\n"
                    "2. Run 'gitco sync' to start managing your forks\n"
                    "3. Run 'gitco discover' to find contribution opportunities",
                )
            else:
                console.print("\n[yellow]Configuration setup cancelled.[/yellow]")
                sys.exit(0)

        else:
            # Non-interactive setup with defaults
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
                "1. Edit ~/.gitco/config.yml to add your repositories\n"
                "2. Set up your LLM API key\n"
                "3. Run 'gitco sync' to start managing your forks\n\n"
                "Tip: Run 'gitco init --interactive' for guided setup",
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


# Core commands implementation
@click.command()
@click.option("--repo", "-r", help="Sync specific repository")
@click.option("--batch", "-b", is_flag=True, help="Batch sync all repositories")
@click.option("--analyze", "-a", is_flag=True, help="Run analysis after sync")
@click.option("--stash", is_flag=True, help="Stash local changes before sync")
@click.option("--force", "-f", is_flag=True, help="Force sync even if conflicts")
@click.option("--max-repos", type=int, help="Maximum repositories per batch")
@click.option("--export", help="Export sync report")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.option("--log", "-l", help="Log to file")
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
    "--max-workers",
    "-w",
    type=int,
    default=4,
    help="Maximum concurrent workers for batch processing (default: 4)",
)
@click.pass_context
def sync(
    ctx: click.Context,
    repo: Optional[str],
    batch: bool,
    analyze: bool,
    stash: bool,
    force: bool,
    max_repos: Optional[int],
    export: Optional[str],
    quiet: bool,
    log: Optional[str],
    detailed_log: bool,
    max_log_size: Optional[int],
    log_backups: Optional[int],
    max_workers: int,
):
    """Synchronize repositories with upstream changes."""
    log_operation_start(
        "repository synchronization", repo=repo, batch=batch, analyze=analyze
    )

    try:
        from ..libs.config import ConfigManager
        from ..libs.git_ops import GitOperations

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        git_ops = GitOperations(config)

        if repo:
            # Sync specific repository
            result = git_ops.sync_repository(repo, stash=stash, force=force)
            if analyze:
                from ..libs.analyzer import Analyzer

                analyzer = Analyzer(config)
                analyzer.analyze_repository(repo)
        elif batch:
            # Batch sync all repositories
            repos_to_sync = list(config.repositories.keys())
            if max_repos:
                repos_to_sync = repos_to_sync[:max_repos]

            results = git_ops.batch_sync(
                repos_to_sync, max_workers=max_workers, stash=stash, force=force
            )

            if analyze:
                from ..libs.analyzer import Analyzer

                analyzer = Analyzer(config)
                for repo_name in repos_to_sync:
                    analyzer.analyze_repository(repo_name)
        else:
            # Sync all repositories individually
            results = git_ops.sync_all_repositories(stash=stash, force=force)

        if export:
            # Export sync report
            import json

            with open(export, "w") as f:
                json.dump(
                    {"sync_results": results if "results" in locals() else "completed"},
                    f,
                    indent=2,
                )

        log_operation_success("repository synchronization", repo=repo, batch=batch)
        if not quiet:
            print_success_panel(
                "Sync completed", "All repositories synchronized successfully"
            )

    except Exception as e:
        log_operation_failure("repository synchronization", e, repo=repo, batch=batch)
        print_error_panel("Sync failed", str(e))
        sys.exit(1)


@click.command()
@click.option("--repo", "-r", help="Analyze specific repository")
@click.option("--repos", help="Analyze multiple repositories (comma-separated)")
@click.option("--detailed", "-d", is_flag=True, help="Detailed analysis")
@click.option("--prompt", "-p", help="Custom analysis prompt")
@click.option("--model", help="LLM model to use")
@click.option("--provider", help="LLM provider to use (openai only)")
@click.option("--no-llm", is_flag=True, help="Skip LLM analysis")
@click.option("--max-commits", type=int, help="Maximum commits to analyze")
@click.option("--export", "-e", help="Export analysis results")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def analyze(
    ctx: click.Context,
    repo: Optional[str],
    repos: Optional[str],
    detailed: bool,
    prompt: Optional[str],
    model: Optional[str],
    provider: Optional[str],
    no_llm: bool,
    max_commits: Optional[int],
    export: Optional[str],
    quiet: bool,
):
    """Analyze repository changes using AI."""
    log_operation_start(
        "repository analysis", repo=repo, repos=repos, detailed=detailed
    )

    try:
        from ..libs.analyzer import Analyzer
        from ..libs.config import ConfigManager

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        analyzer = Analyzer(config)

        # Override settings if provided
        if model:
            config.settings.llm_model = model
        if provider:
            config.settings.llm_provider = provider

        repositories = []
        if repo:
            repositories = [repo]
        elif repos:
            repositories = [r.strip() for r in repos.split(",")]
        else:
            repositories = list(config.repositories.keys())

        results = {}
        for repo_name in repositories:
            if not quiet:
                console.print(f"[blue]Analyzing repository: {repo_name}[/blue]")

            analysis_result = analyzer.analyze_repository(
                repo_name,
                detailed=detailed,
                custom_prompt=prompt,
                use_llm=not no_llm,
                max_commits=max_commits,
            )
            results[repo_name] = analysis_result

        if export:
            import json

            with open(export, "w") as f:
                json.dump(results, f, indent=2, default=str)

        log_operation_success("repository analysis", repo_count=len(repositories))
        if not quiet:
            print_success_panel(
                "Analysis completed", f"Analyzed {len(repositories)} repositories"
            )

    except Exception as e:
        log_operation_failure("repository analysis", e, repo=repo, repos=repos)
        print_error_panel("Analysis failed", str(e))
        sys.exit(1)


@click.command()
@click.option("--skill", "-s", help="Filter by skill")
@click.option("--label", "-l", help="Filter by GitHub label")
@click.option("--repos", help="Filter by repositories")
@click.option(
    "--min-confidence", "-c", type=float, help="Minimum confidence threshold (0.0-1.0)"
)
@click.option("--limit", "-n", type=int, help="Maximum results to return")
@click.option(
    "--personalized", "-p", is_flag=True, help="Use personalized recommendations"
)
@click.option(
    "--show-history", "-h", is_flag=True, help="Show contribution history analysis"
)
@click.option("--export", "-e", help="Export discovery results")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def discover(
    ctx: click.Context,
    skill: Optional[str],
    label: Optional[str],
    repos: Optional[str],
    min_confidence: Optional[float],
    limit: Optional[int],
    personalized: bool,
    show_history: bool,
    export: Optional[str],
    quiet: bool,
):
    """Discover contribution opportunities."""
    log_operation_start(
        "contribution discovery", skill=skill, label=label, personalized=personalized
    )

    try:
        from ..libs.config import ConfigManager
        from ..libs.discovery import DiscoveryEngine

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        discovery_engine = DiscoveryEngine(config)

        # Build filters
        filters = {}
        if skill:
            filters["skill"] = skill
        if label:
            filters["label"] = label
        if repos:
            filters["repos"] = [r.strip() for r in repos.split(",")]
        if min_confidence:
            filters["min_confidence"] = min_confidence

        # Discover opportunities
        opportunities = discovery_engine.discover_opportunities(
            filters=filters,
            limit=limit,
            personalized=personalized,
            show_history=show_history,
        )

        if export:
            import json

            with open(export, "w") as f:
                json.dump(opportunities, f, indent=2, default=str)

        if not quiet:
            console.print(
                f"[green]Found {len(opportunities)} contribution opportunities[/green]"
            )
            for i, opp in enumerate(opportunities[:10], 1):  # Show first 10
                console.print(
                    f"{i}. {opp.get('title', 'N/A')} ({opp.get('confidence', 0):.2f})"
                )

        log_operation_success(
            "contribution discovery", opportunity_count=len(opportunities)
        )

    except Exception as e:
        log_operation_failure("contribution discovery", e, skill=skill, label=label)
        print_error_panel("Discovery failed", str(e))
        sys.exit(1)


@click.command()
@click.option("--repo", "-r", help="Show specific repository status")
@click.option("--detailed", "-d", is_flag=True, help="Detailed status report")
@click.option("--overview", "-o", is_flag=True, help="Overview status")
@click.option(
    "--activity", "-a", is_flag=True, help="Show repository activity dashboard"
)
@click.option("--filter", help="Filter by status (healthy, needs_attention, critical)")
@click.option("--sort", help="Sort by field (health, activity, stars, forks)")
@click.option("--export", help="Export status report")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def status(
    ctx: click.Context,
    repo: Optional[str],
    detailed: bool,
    overview: bool,
    activity: bool,
    filter: Optional[str],
    sort: Optional[str],
    export: Optional[str],
    quiet: bool,
):
    """Check repository health and status."""
    log_operation_start(
        "repository status check", repo=repo, detailed=detailed, overview=overview
    )

    try:
        from ..libs.config import ConfigManager
        from ..libs.health_metrics import HealthMetrics

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        health_metrics = HealthMetrics(config)

        if repo:
            # Get status for specific repository
            status_info = health_metrics.get_repository_status(repo, detailed=detailed)
            repositories_status = {repo: status_info}
        else:
            # Get status for all repositories
            repositories_status = health_metrics.get_all_repositories_status(
                detailed=detailed
            )

        # Apply filters
        if filter:
            repositories_status = {
                name: status
                for name, status in repositories_status.items()
                if status.get("health_status") == filter
            }

        # Sort results
        if sort:
            repositories_status = dict(
                sorted(
                    repositories_status.items(),
                    key=lambda x: x[1].get(sort, 0),
                    reverse=True,
                )
            )

        if export:
            import json

            with open(export, "w") as f:
                json.dump(repositories_status, f, indent=2, default=str)

        if not quiet:
            if overview:
                # Show overview status
                total_repos = len(repositories_status)
                healthy = len(
                    [
                        s
                        for s in repositories_status.values()
                        if s.get("health_status") == "healthy"
                    ]
                )
                needs_attention = len(
                    [
                        s
                        for s in repositories_status.values()
                        if s.get("health_status") == "needs_attention"
                    ]
                )
                critical = len(
                    [
                        s
                        for s in repositories_status.values()
                        if s.get("health_status") == "critical"
                    ]
                )

                console.print("[green]Repository Status Overview[/green]")
                console.print(f"Total repositories: {total_repos}")
                console.print(f"Healthy: {healthy}")
                console.print(f"Needs attention: {needs_attention}")
                console.print(f"Critical: {critical}")
            else:
                # Show detailed status
                for repo_name, status_info in repositories_status.items():
                    health = status_info.get("health_status", "unknown")
                    color = {
                        "healthy": "green",
                        "needs_attention": "yellow",
                        "critical": "red",
                    }.get(health, "white")
                    console.print(f"[{color}]{repo_name}: {health}[/{color}]")

                    if detailed:
                        console.print(
                            f"  Last sync: {status_info.get('last_sync', 'N/A')}"
                        )
                        console.print(
                            f"  Commits behind: {status_info.get('commits_behind', 'N/A')}"
                        )
                        console.print(
                            f"  Local changes: {status_info.get('local_changes', 'N/A')}"
                        )

        log_operation_success(
            "repository status check", repo_count=len(repositories_status)
        )

    except Exception as e:
        log_operation_failure("repository status check", e, repo=repo)
        print_error_panel("Status check failed", str(e))
        sys.exit(1)


@click.command()
@click.option("--repo", "-r", help="Activity for specific repository")
@click.option("--detailed", "-d", is_flag=True, help="Detailed activity report")
@click.option("--filter", help="Filter by activity level (high, moderate, low)")
@click.option(
    "--sort", help="Sort by field (activity, engagement, commits, contributors)"
)
@click.option("--export", help="Export activity report")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def activity(
    ctx: click.Context,
    repo: Optional[str],
    detailed: bool,
    filter: Optional[str],
    sort: Optional[str],
    export: Optional[str],
    quiet: bool,
):
    """View repository activity dashboard."""
    log_operation_start("repository activity dashboard", repo=repo, detailed=detailed)

    try:
        from ..libs.activity_dashboard import ActivityDashboard
        from ..libs.config import ConfigManager

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        activity_dashboard = ActivityDashboard(config)

        if repo:
            # Get activity for specific repository
            activity_info = activity_dashboard.get_repository_activity(
                repo, detailed=detailed
            )
            repositories_activity = {repo: activity_info}
        else:
            # Get activity for all repositories
            repositories_activity = activity_dashboard.get_all_repositories_activity(
                detailed=detailed
            )

        # Apply filters
        if filter:
            repositories_activity = {
                name: activity
                for name, activity in repositories_activity.items()
                if activity.get("activity_level") == filter
            }

        # Sort results
        if sort:
            repositories_activity = dict(
                sorted(
                    repositories_activity.items(),
                    key=lambda x: x[1].get(sort, 0),
                    reverse=True,
                )
            )

        if export:
            import json

            with open(export, "w") as f:
                json.dump(repositories_activity, f, indent=2, default=str)

        if not quiet:
            console.print("[green]Repository Activity Dashboard[/green]")
            for repo_name, activity_info in repositories_activity.items():
                activity_level = activity_info.get("activity_level", "unknown")
                color = {"high": "green", "moderate": "yellow", "low": "red"}.get(
                    activity_level, "white"
                )
                console.print(
                    f"[{color}]{repo_name}: {activity_level} activity[/{color}]"
                )

                if detailed:
                    console.print(
                        f"  Recent commits: {activity_info.get('recent_commits', 'N/A')}"
                    )
                    console.print(
                        f"  Contributors: {activity_info.get('contributors', 'N/A')}"
                    )
                    console.print(
                        f"  Engagement score: {activity_info.get('engagement_score', 'N/A')}"
                    )

        log_operation_success(
            "repository activity dashboard", repo_count=len(repositories_activity)
        )

    except Exception as e:
        log_operation_failure("repository activity dashboard", e, repo=repo)
        print_error_panel("Activity dashboard failed", str(e))
        sys.exit(1)


@click.command()
@click.option("--export", help="Export logs")
@click.option("--lines", type=int, help="Number of lines to show")
@click.option("--follow", "-f", is_flag=True, help="Follow log file")
@click.pass_context
def logs(
    ctx: click.Context,
    export: Optional[str],
    lines: Optional[int],
    follow: bool,
):
    """View and manage logs."""
    log_operation_start("log management", export=export, lines=lines, follow=follow)

    try:
        from ..utils.logging import LogManager

        log_manager = LogManager()

        if export:
            # Export logs to file
            log_manager.export_logs(export, lines=lines)
            console.print(f"[green]Logs exported to {export}[/green]")
        elif follow:
            # Follow log file
            log_manager.follow_logs()
        else:
            # Show recent logs
            logs_content = log_manager.get_recent_logs(lines=lines or 50)
            console.print(logs_content)

        log_operation_success("log management")

    except Exception as e:
        log_operation_failure("log management", e)
        print_error_panel("Log operation failed", str(e))
        sys.exit(1)


@click.command()
@click.option("--detailed", "-d", is_flag=True, help="Detailed performance metrics")
@click.option("--export", help="Export performance data")
@click.pass_context
def performance(
    ctx: click.Context,
    detailed: bool,
    export: Optional[str],
):
    """View performance metrics."""
    log_operation_start("performance metrics", detailed=detailed)

    try:
        from ..libs.config import ConfigManager
        from ..libs.health_metrics import PerformanceMetrics

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        perf_metrics = PerformanceMetrics(config)

        metrics = perf_metrics.get_performance_metrics(detailed=detailed)

        if export:
            import json

            with open(export, "w") as f:
                json.dump(metrics, f, indent=2, default=str)

        console.print("[green]Performance Metrics[/green]")
        console.print(f"Average sync time: {metrics.get('avg_sync_time', 'N/A')}")
        console.print(
            f"Average analysis time: {metrics.get('avg_analysis_time', 'N/A')}"
        )
        console.print(f"Memory usage: {metrics.get('memory_usage', 'N/A')}")

        if detailed:
            console.print(f"Total operations: {metrics.get('total_operations', 'N/A')}")
            console.print(f"Success rate: {metrics.get('success_rate', 'N/A')}%")
            console.print(f"Error rate: {metrics.get('error_rate', 'N/A')}%")

        log_operation_success("performance metrics")

    except Exception as e:
        log_operation_failure("performance metrics", e)
        print_error_panel("Performance metrics failed", str(e))
        sys.exit(1)


@click.command()
def version():
    """Show GitCo version information."""
    print(f"GitCo version {__version__}")


@click.command()
@click.argument("command", required=False)
@click.pass_context
def help(ctx: click.Context, command: Optional[str]):
    """Show detailed help information."""
    if command:
        # Show help for specific command
        try:
            cmd = ctx.find_root().command.get_command(ctx, command)
            if cmd:
                console.print(cmd.get_help(ctx))
            else:
                console.print(f"[red]Command '{command}' not found[/red]")
        except Exception as e:
            console.print(f"[red]Error getting help for '{command}': {e}[/red]")
    else:
        # Show general help
        console.print(ctx.find_root().get_help(ctx))


@click.command()
@click.option("--shell", "-s", type=click.Choice(["bash", "zsh"]), help="Shell type")
@click.option("--output", "-o", help="Output file path")
@click.option("--install", "-i", is_flag=True, help="Install completion script")
@click.pass_context
def completion(
    ctx: click.Context,
    shell: Optional[str],
    output: Optional[str],
    install: bool,
):
    """Generate or install shell completion scripts."""
    log_operation_start("shell completion", shell=shell, install=install)

    try:
        from ..templates.shell_completion import ShellCompletion

        shell_completion = ShellCompletion()

        if not shell:
            # Auto-detect shell
            shell = shell_completion.detect_shell()

        if install:
            # Install completion script
            shell_completion.install_completion(shell)
            console.print(f"[green]Shell completion installed for {shell}[/green]")
        else:
            # Generate completion script
            completion_script = shell_completion.generate_completion(shell)

            if output:
                with open(output, "w") as f:
                    f.write(completion_script)
                console.print(f"[green]Completion script saved to {output}[/green]")
            else:
                console.print(completion_script)

        log_operation_success("shell completion")

    except Exception as e:
        log_operation_failure("shell completion", e)
        print_error_panel("Shell completion failed", str(e))
        sys.exit(1)


@click.command(name="validate-repo")
@click.option("--repo", "-r", help="Validate specific repository")
@click.option("--all", "-a", is_flag=True, help="Validate all repositories")
@click.option("--detailed", "-d", is_flag=True, help="Detailed validation report")
@click.option("--path", help="Validate repository at path")
@click.option("--recursive", is_flag=True, help="Recursive validation")
@click.option("--export", help="Export validation report")
@click.pass_context
def validate_repo(
    ctx: click.Context,
    repo: Optional[str],
    all: bool,
    detailed: bool,
    path: Optional[str],
    recursive: bool,
    export: Optional[str],
):
    """Validate Git repositories."""
    log_operation_start("repository validation", repo=repo, all=all, path=path)

    try:
        from ..libs.config import ConfigManager
        from ..libs.git_ops import RepositoryValidator

        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()
        validator = RepositoryValidator(config)

        validation_results = {}

        if path:
            # Validate repository at specific path
            result = validator.validate_repository_at_path(
                path, detailed=detailed, recursive=recursive
            )
            validation_results[path] = result
        elif repo:
            # Validate specific repository
            result = validator.validate_repository(repo, detailed=detailed)
            validation_results[repo] = result
        elif all:
            # Validate all repositories
            validation_results = validator.validate_all_repositories(detailed=detailed)
        else:
            console.print("[yellow]Please specify --repo, --all, or --path[/yellow]")
            return

        if export:
            import json

            with open(export, "w") as f:
                json.dump(validation_results, f, indent=2, default=str)

        # Display results
        console.print("[green]Repository Validation Results[/green]")
        for repo_name, result in validation_results.items():
            status = result.get("status", "unknown")
            color = {"valid": "green", "invalid": "red", "warning": "yellow"}.get(
                status, "white"
            )
            console.print(f"[{color}]{repo_name}: {status}[/{color}]")

            if detailed and "issues" in result:
                for issue in result["issues"]:
                    console.print(f"  - {issue}")

        log_operation_success(
            "repository validation", repo_count=len(validation_results)
        )

    except Exception as e:
        log_operation_failure("repository validation", e, repo=repo, path=path)
        print_error_panel("Repository validation failed", str(e))
        sys.exit(1)


# Export function for CLI registration
core_commands = register_core_commands
