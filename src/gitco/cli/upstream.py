"""Upstream management CLI commands for GitCo.

This module contains upstream-related commands:
add, remove, update, validate, fetch, merge.
"""

import sys
from typing import Optional

import click

from ..libs.git_ops import GitRepository, GitRepositoryManager
from ..utils.common import (
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    print_error_panel,
    print_info_panel,
    print_success_panel,
)
from ..utils.exception import ValidationError


def register_upstream_commands(main_group):
    """Register all upstream commands with the main CLI group."""
    # Create the upstream group
    upstream_group = click.Group(
        name="upstream", help="Upstream remote management commands."
    )
    upstream_group.add_command(add)
    upstream_group.add_command(remove)
    upstream_group.add_command(update)
    upstream_group.add_command(validate)
    upstream_group.add_command(fetch)
    upstream_group.add_command(merge)

    # Add the upstream group to main
    main_group.add_command(upstream_group)


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name")
@click.option("--url", required=True, help="Upstream repository URL")
@click.option("--name", help="Remote name (default: upstream)")
@click.pass_context
def add(ctx: click.Context, repo: str, url: str, name: Optional[str]) -> None:
    """Add upstream remote to a repository.

    Adds or updates the upstream remote for the specified repository.
    """
    remote_name = name or "upstream"
    log_operation_start(
        "upstream remote addition", repo=repo, url=url, name=remote_name
    )

    try:
        git_manager = GitRepositoryManager()

        # Validate repository path
        is_valid, errors = git_manager.validate_repository_path(repo)
        if not is_valid:
            log_operation_failure(
                "upstream remote addition", ValidationError("Invalid repository path")
            )
            print_error_panel("Invalid Repository Path", "❌ Invalid repository path:\n")
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


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name")
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
            print_error_panel("Invalid Repository Path", "❌ Invalid repository path:\n")
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


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name")
@click.option("--url", required=True, help="New upstream repository URL")
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
            print_error_panel("Invalid Repository Path", "❌ Invalid repository path:\n")
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


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name")
@click.option("--detailed", "-d", is_flag=True, help="Detailed validation")
@click.pass_context
def validate(ctx: click.Context, repo: str, detailed: bool) -> None:
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
            print_error_panel("Invalid Repository Path", "❌ Invalid repository path:\n")
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


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name")
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
            print_error_panel("Invalid Repository Path", "❌ Invalid repository path:\n")
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


@click.command()
@click.option("--repo", "-r", required=True, help="Repository name")
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
            print_error_panel("Invalid Repository Path", "❌ Invalid repository path:\n")
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

        # Determine branch to merge
        merge_branch = branch or git_repo.get_default_branch_name() or "main"

        # Perform merge
        merge_result = git_repo.merge_upstream(merge_branch, strategy=strategy)

        if merge_result["success"]:
            log_operation_success("upstream merge", repo=repo, branch=merge_branch)
            print_success_panel(
                "Successfully merged upstream changes!",
                f"Repository: {repo}\nBranch: {merge_branch}\nStrategy: {strategy}",
            )
        elif merge_result.get("conflicts"):
            print_info_panel(
                "Merge conflicts detected",
                f"Conflicts detected in {len(merge_result['conflicts'])} files.\n"
                f"Please resolve conflicts manually and commit.",
            )
            for conflict in merge_result["conflicts"]:
                print_info_panel("Conflict", f"  - {conflict}")
        else:
            log_operation_failure(
                "upstream merge", Exception("Failed to merge upstream changes")
            )
            print_error_panel(
                "Failed to merge upstream changes",
                f"Error: {merge_result.get('error', 'Unknown error')}",
            )
            sys.exit(1)

    except Exception as e:
        log_operation_failure("upstream merge", e)
        print_error_panel("Error merging upstream changes", str(e))
        sys.exit(1)


# Export function for CLI registration
upstream_commands = register_upstream_commands
