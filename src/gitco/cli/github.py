"""GitHub integration CLI commands for GitCo.

This module contains GitHub API-related commands:
connection-status, rate-limit-status, get-repo, get-issues, get-issues-multi.
"""

import sys
from typing import Optional

import click

from ..libs.config import ConfigManager
from ..libs.github_client import create_github_client
from ..utils.common import (
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    print_error_panel,
    print_info_panel,
    print_success_panel,
    print_warning_panel,
)


def register_github_commands(main_group):
    """Register all GitHub commands with the main CLI group."""
    # Create the github group
    github_group = click.Group(name="github", help="GitHub API operations.")
    github_group.add_command(connection_status)
    github_group.add_command(rate_limit_status)
    github_group.add_command(get_repo)
    github_group.add_command(get_issues)
    github_group.add_command(get_issues_multi)

    # Add the github group to main
    main_group.add_command(github_group)


@click.command(name="connection-status")
@click.option("--detailed", "-d", is_flag=True, help="Detailed connection check")
@click.pass_context
def connection_status(ctx: click.Context, detailed: bool) -> None:
    """Test GitHub API connection and authentication.

    Tests the GitHub API connection using configured credentials.
    """
    log_operation_start("github connection test")

    try:
        # Load configuration
        config_manager = ConfigManager(ctx.obj.get("config"))
        config_manager.load_config()

        # Get GitHub credentials
        credentials = config_manager.get_github_credentials()

        # Create GitHub client
        github_client = create_github_client(
            token=(
                credentials["token"] if isinstance(credentials["token"], str) else None
            ),
            username=(
                credentials["username"]
                if isinstance(credentials["username"], str)
                else None
            ),
            password=(
                credentials["password"]
                if isinstance(credentials["password"], str)
                else None
            ),
            base_url=(
                str(credentials["base_url"])
                if credentials["base_url"]
                else "https://api.github.com"
            ),
        )

        # Test connection
        if github_client.test_connection():
            log_operation_success("github connection test")
            print_success_panel(
                "GitHub API Connection Successful!",
                "✅ Successfully connected to GitHub API\n\n"
                "Authentication: Working\n"
                "Rate Limits: Available\n"
                "API Endpoint: Ready",
            )

            # Show rate limit status
            try:
                rate_limit = github_client.get_rate_limit_status()
                print_info_panel(
                    "Rate Limit Status",
                    f"Core API: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']} remaining\n"
                    f"Search API: {rate_limit['search']['remaining']}/{rate_limit['search']['limit']} remaining",
                )
            except Exception as e:
                print_warning_panel(
                    "Rate Limit Info",
                    f"Could not retrieve rate limit information: {e}",
                )
        else:
            log_operation_failure(
                "github connection test", Exception("Connection test failed")
            )
            print_error_panel(
                "GitHub API Connection Failed",
                "❌ Failed to connect to GitHub API\n\n"
                "Please check:\n"
                "1. Your GitHub credentials (GITHUB_TOKEN or GITHUB_USERNAME/GITHUB_PASSWORD)\n"
                "2. Network connectivity\n"
                "3. GitHub API status",
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("github connection test", e)
        print_error_panel("Error testing GitHub connection", str(e))
        sys.exit(1)


@click.command(name="rate-limit-status")
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed rate limiting information"
)
@click.option("--wait", is_flag=True, help="Wait for rate limit reset")
@click.pass_context
def rate_limit_status(ctx: click.Context, detailed: bool, wait: bool) -> None:
    """Show rate limiting status for API providers.

    Displays current rate limiting status and usage information for all API providers.
    """
    log_operation_start("rate limit status check")

    try:
        from ..utils.rate_limiter import get_rate_limiter_status

        # Get rate limiter status
        status = get_rate_limiter_status()

        if not status:
            print_warning_panel(
                "No Rate Limiters Found",
                "No rate limiters have been initialized yet. "
                "Rate limiters are created when API calls are made.",
            )
            return

        # Display status for each provider
        for provider_name, provider_status in status.items():
            print_info_panel(
                f"Rate Limit Status - {provider_name.upper()}",
                f"Requests (last minute): {provider_status.get('requests_last_minute', 0)}\n"
                f"Requests (last hour): {provider_status.get('requests_last_hour', 0)}\n"
                f"Total tracked requests: {provider_status.get('total_requests_tracked', 0)}\n"
                f"Time since last request: {provider_status.get('time_since_last_request', 'N/A')}s",
            )

            if detailed:
                # Show detailed information
                remaining = provider_status.get("rate_limit_remaining")
                reset = provider_status.get("rate_limit_reset")
                limit = provider_status.get("rate_limit_limit")

                if remaining is not None:
                    print_info_panel(
                        f"Detailed Status - {provider_name.upper()}",
                        f"API Rate Limit Remaining: {remaining}\n"
                        f"API Rate Limit Total: {limit}\n"
                        f"API Rate Limit Reset: {reset}",
                    )

        log_operation_success("rate limit status check")

    except Exception as e:
        log_operation_failure("rate limit status check", e)
        print_error_panel("Rate Limit Status Error", str(e))


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name (owner/repo)")
@click.pass_context
def get_repo(ctx: click.Context, repo: str) -> None:
    """Get repository information from GitHub.

    Fetches detailed information about a GitHub repository.
    """
    log_operation_start("github repository fetch", repo=repo)

    try:
        # Load configuration
        config_manager = ConfigManager(ctx.obj.get("config"))
        config_manager.load_config()

        # Get GitHub credentials
        credentials = config_manager.get_github_credentials()

        # Create GitHub client
        github_client = create_github_client(
            token=(
                credentials["token"] if isinstance(credentials["token"], str) else None
            ),
            username=(
                credentials["username"]
                if isinstance(credentials["username"], str)
                else None
            ),
            password=(
                credentials["password"]
                if isinstance(credentials["password"], str)
                else None
            ),
            base_url=(
                str(credentials["base_url"])
                if credentials["base_url"]
                else "https://api.github.com"
            ),
        )

        # Get repository information
        github_repo = github_client.get_repository(repo)

        if github_repo:
            log_operation_success("github repository fetch", repo=repo)
            print_success_panel(
                f"Repository: {github_repo.name}",
                f"📁 {github_repo.full_name}\n\n"
                f"Description: {github_repo.description or 'No description'}\n"
                f"Language: {github_repo.language or 'Unknown'}\n"
                f"Stars: {github_repo.stargazers_count}\n"
                f"Forks: {github_repo.forks_count}\n"
                f"Open Issues: {github_repo.open_issues_count}\n"
                f"Default Branch: {github_repo.default_branch}\n"
                f"Last Updated: {github_repo.updated_at}\n"
                f"URL: {github_repo.html_url}",
            )

            if github_repo.topics:
                print_info_panel(
                    "Topics",
                    f"Topics: {', '.join(github_repo.topics)}",
                )
        else:
            log_operation_failure(
                "github repository fetch", Exception("Repository not found")
            )
            print_error_panel(
                "Repository Not Found",
                f"❌ Repository '{repo}' not found or not accessible",
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("github repository fetch", e)
        print_error_panel("Error fetching repository", str(e))
        sys.exit(1)


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name (owner/repo)")
@click.option("--state", "-s", default="open", help="Issue state (open, closed, all)")
@click.option("--labels", "-l", help="Filter by labels (comma-separated)")
@click.option("--exclude-labels", "-e", help="Exclude labels (comma-separated)")
@click.option("--assignee", "-a", help="Filter by assignee")
@click.option("--limit", type=int, help="Maximum results to return")
@click.option("--export", help="Export results to file")
@click.pass_context
def get_issues(
    ctx: click.Context,
    repo: str,
    state: str,
    labels: Optional[str],
    exclude_labels: Optional[str],
    assignee: Optional[str],
    limit: Optional[int],
    export: Optional[str],
) -> None:
    """Get issues from a GitHub repository with advanced filtering.

    Fetches issues from the specified repository with comprehensive filtering options.
    """
    log_operation_start("github issues fetch", repo=repo, state=state)

    try:
        # Load configuration
        config_manager = ConfigManager(ctx.obj.get("config"))
        config_manager.load_config()

        # Get GitHub credentials
        credentials = config_manager.get_github_credentials()

        # Create GitHub client
        github_client = create_github_client(
            token=(
                credentials["token"] if isinstance(credentials["token"], str) else None
            ),
            username=(
                credentials["username"]
                if isinstance(credentials["username"], str)
                else None
            ),
            password=(
                credentials["password"]
                if isinstance(credentials["password"], str)
                else None
            ),
            base_url=(
                str(credentials["base_url"])
                if credentials["base_url"]
                else "https://api.github.com"
            ),
        )

        # Parse labels
        label_list = None
        if labels:
            label_list = [label.strip() for label in labels.split(",")]

        exclude_label_list = None
        if exclude_labels:
            exclude_label_list = [label.strip() for label in exclude_labels.split(",")]

        # Get issues
        issues = github_client.get_issues(
            repo_name=repo,
            state=state,
            labels=label_list,
            exclude_labels=exclude_label_list,
            assignee=assignee,
            limit=limit,
        )

        log_operation_success("github issues fetch", repo=repo, count=len(issues))
        print_success_panel(
            f"Found {len(issues)} issues",
            f"📋 Found {len(issues)} issues in {repo}",
        )

        for issue in issues:
            print_info_panel(
                f"#{issue.number} - {issue.title}",
                f"State: {issue.state}\n"
                f"Labels: {', '.join(issue.labels) if issue.labels else 'None'}\n"
                f"Assignee: {', '.join(issue.assignees) if issue.assignees else 'None'}\n"
                f"Created: {issue.created_at}\n"
                f"URL: {issue.html_url}",
            )

        # Export if requested
        if export:
            import json
            from datetime import datetime

            export_data = {
                "timestamp": datetime.now().isoformat(),
                "repository": repo,
                "total_issues": len(issues),
                "filters": {
                    "state": state,
                    "labels": label_list,
                    "exclude_labels": exclude_label_list,
                    "assignee": assignee,
                    "limit": limit,
                },
                "issues": [
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "state": issue.state,
                        "labels": issue.labels,
                        "assignees": issue.assignees,
                        "created_at": issue.created_at,
                        "html_url": issue.html_url,
                    }
                    for issue in issues
                ],
            }

            try:
                with open(export, "w") as f:
                    json.dump(export_data, f, indent=2)
                print_success_panel(f"Issues exported to {export}")
            except Exception as export_error:
                print_error_panel("Failed to export issues", str(export_error))

    except Exception as e:
        log_operation_failure("github issues fetch", e)
        print_error_panel("Error fetching issues", str(e))
        sys.exit(1)


@click.command()
@click.option("--repos", "-r", required=True, help="Repository names (comma-separated)")
@click.option("--state", "-s", default="open", help="Issue state (open, closed, all)")
@click.option("--labels", "-l", help="Filter by labels (comma-separated)")
@click.option("--exclude-labels", "-e", help="Exclude labels (comma-separated)")
@click.option("--assignee", "-a", help="Filter by assignee")
@click.option("--limit", type=int, help="Maximum results to return per repository")
@click.option("--export", help="Export results to JSON file")
@click.pass_context
def get_issues_multi(
    ctx: click.Context,
    repos: str,
    state: str,
    labels: Optional[str],
    exclude_labels: Optional[str],
    assignee: Optional[str],
    limit: Optional[int],
    export: Optional[str],
) -> None:
    """Get issues from multiple GitHub repositories with advanced filtering.

    Fetches issues from multiple repositories with comprehensive filtering options.
    """
    log_operation_start("github issues fetch multiple repos", repos=repos, state=state)

    try:
        # Load configuration
        config_manager = ConfigManager(ctx.obj.get("config"))
        config_manager.load_config()

        # Get GitHub credentials
        credentials = config_manager.get_github_credentials()

        # Create GitHub client
        github_client = create_github_client(
            token=(
                credentials["token"] if isinstance(credentials["token"], str) else None
            ),
            username=(
                credentials["username"]
                if isinstance(credentials["username"], str)
                else None
            ),
            password=(
                credentials["password"]
                if isinstance(credentials["password"], str)
                else None
            ),
            base_url=(
                str(credentials["base_url"])
                if credentials["base_url"]
                else "https://api.github.com"
            ),
        )

        # Parse repository list
        repo_list = [repo.strip() for repo in repos.split(",")]

        # Parse labels
        label_list = None
        if labels:
            label_list = [label.strip() for label in labels.split(",")]

        exclude_label_list = None
        if exclude_labels:
            exclude_label_list = [label.strip() for label in exclude_labels.split(",")]

        # Get issues from multiple repositories
        all_issues = github_client.get_issues_for_repositories(
            repositories=repo_list,
            state=state,
            labels=label_list,
            exclude_labels=exclude_label_list,
            assignee=assignee,
            limit_per_repo=limit,
        )

        total_issues = sum(len(issues) for issues in all_issues.values())
        log_operation_success(
            "github issues fetch multiple repos", repos=repos, total_count=total_issues
        )
        print_success_panel(
            f"Found {total_issues} issues across {len(repo_list)} repositories",
            f"📋 Found {total_issues} issues across {len(repo_list)} repositories",
        )

        # Display results by repository
        for repo_name, issues in all_issues.items():
            if issues:
                print_info_panel(
                    f"Repository: {repo_name}",
                    f"Found {len(issues)} issues",
                )

                for issue in issues:
                    print_info_panel(
                        f"#{issue.number} - {issue.title}",
                        f"Repository: {repo_name}\n"
                        f"State: {issue.state}\n"
                        f"Labels: {', '.join(issue.labels) if issue.labels else 'None'}\n"
                        f"Assignee: {', '.join(issue.assignees) if issue.assignees else 'None'}\n"
                        f"Created: {issue.created_at}\n"
                        f"URL: {issue.html_url}",
                    )

        # Export results if requested
        if export:
            import json
            from datetime import datetime

            export_data = {
                "timestamp": datetime.now().isoformat(),
                "repositories": repo_list,
                "total_issues": total_issues,
                "filters": {
                    "state": state,
                    "labels": label_list,
                    "exclude_labels": exclude_label_list,
                    "assignee": assignee,
                    "limit": limit,
                },
                "issues": {
                    repo_name: [
                        {
                            "number": issue.number,
                            "title": issue.title,
                            "state": issue.state,
                            "labels": issue.labels,
                            "assignees": issue.assignees,
                            "created_at": issue.created_at,
                            "html_url": issue.html_url,
                        }
                        for issue in issues
                    ]
                    for repo_name, issues in all_issues.items()
                },
            }

            try:
                with open(export, "w") as f:
                    json.dump(export_data, f, indent=2)
                print_success_panel(f"Issues exported to {export}")
            except Exception as export_error:
                print_error_panel("Failed to export issues", str(export_error))

    except Exception as e:
        log_operation_failure("github issues fetch multiple repos", e)
        print_error_panel("Error fetching issues from multiple repositories", str(e))
        sys.exit(1)


# Export function for CLI registration
github_commands = register_github_commands
