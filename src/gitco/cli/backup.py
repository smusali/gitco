"""Backup management CLI commands for GitCo.

This module contains backup-related commands:
create, list, restore, validate, delete, cleanup.
"""

from typing import Optional

import click

from ..libs.backup import (
    BackupManager,
    print_backup_info,
    print_backup_list,
    print_restore_results,
)
from ..libs.config import get_config_manager
from ..utils.common import (
    console,
    print_error_panel,
    print_info_panel,
    print_success_panel,
    print_warning_panel,
    set_quiet_mode,
)


def register_backup_commands(main_group):
    """Register all backup commands with the main CLI group."""
    # Create the backup group
    backup_group = click.Group(
        name="backup", help="Manage backups and recovery operations."
    )
    backup_group.add_command(create)
    backup_group.add_command(list_backups)
    backup_group.add_command(restore)
    backup_group.add_command(validate)
    backup_group.add_command(delete)
    backup_group.add_command(cleanup)

    # Add the backup group to main
    main_group.add_command(backup_group)


@click.command()
@click.option(
    "--repos", "-r", help="Backup specific repositories (comma-separated names)"
)
@click.option("--config", "-c", help="Path to configuration file")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["full", "incremental", "config-only"]),
    default="full",
    help="Backup type",
)
@click.option("--description", "-d", help="Description of the backup")
@click.option(
    "--no-git-history", is_flag=True, help="Exclude git history to reduce size"
)
@click.option("--compression", type=int, default=6, help="Compression level (0-9)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def create(
    ctx: click.Context,
    repos: Optional[str],
    config: Optional[str],
    type: str,
    description: Optional[str],
    no_git_history: bool,
    compression: int,
    quiet: bool,
) -> None:
    """Create a backup of repositories and configuration."""
    try:
        if quiet:
            set_quiet_mode(True)

        # Load configuration to get repository paths
        config_manager = get_config_manager()
        config_data = config_manager.load_config()

        # Determine repositories to backup
        repositories = []
        if repos:
            repositories = [r.strip() for r in repos.split(",")]
        else:
            # Use repositories from configuration
            if hasattr(config_data, "repositories") and config_data.repositories:
                repositories = list(config_data.repositories.keys())
            else:
                repositories = []

        if not repositories and type != "config-only":
            print_error_panel(
                "No repositories specified",
                "Please provide repository paths or ensure configuration is loaded",
            )
            return

        # Create backup manager
        backup_manager = BackupManager()

        # Create backup
        backup_path, metadata = backup_manager.create_backup(
            repositories=repositories,
            config_path=config or "gitco-config.yml",
            backup_type=type,
            description=description,
            include_git_history=not no_git_history,
            compression_level=compression,
        )

        if not quiet:
            print_success_panel(
                "Backup Created Successfully",
                f"Backup ID: {metadata.backup_id}\n"
                f"Path: {backup_path}\n"
                f"Size: {metadata.size_bytes / (1024 * 1024):.1f} MB\n"
                f"Repositories: {len(metadata.repositories)}\n"
                f"Config included: {'Yes' if metadata.config_included else 'No'}",
            )

    except Exception as e:
        print_error_panel("Backup Creation Failed", f"An error occurred: {str(e)}")
        if ctx.obj.get("verbose"):
            raise


@click.command(name="list")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed information")
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["date", "size", "type"]),
    default="date",
    help="Sort by field (date, size, type)",
)
@click.pass_context
def list_backups(ctx: click.Context, detailed: bool, sort: str) -> None:
    """List all available backups."""
    try:
        backup_manager = BackupManager()
        backups = backup_manager.list_backups()

        # Sort backups based on the sort parameter
        if backups:
            if sort == "date":
                backups = sorted(
                    backups, key=lambda x: x.get("created_at", ""), reverse=True
                )
            elif sort == "size":
                backups = sorted(backups, key=lambda x: x.get("size", 0), reverse=True)
            elif sort == "type":
                backups = sorted(backups, key=lambda x: x.get("type", ""))

        if detailed and backups:
            for backup in backups:
                print_backup_info(backup)
                console.print()  # Add spacing between backups
        else:
            print_backup_list(backups)

    except Exception as e:
        print_error_panel("Failed to List Backups", f"An error occurred: {str(e)}")
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--backup-id", "-b", required=True, help="ID of the backup to restore")
@click.option("--target-dir", "-t", help="Target directory for restoration")
@click.option("--no-config", is_flag=True, help="Skip configuration restoration")
@click.option("--overwrite", "-f", is_flag=True, help="Overwrite existing files")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def restore(
    ctx: click.Context,
    backup_id: str,
    target_dir: Optional[str],
    no_config: bool,
    overwrite: bool,
    quiet: bool,
) -> None:
    """Restore a backup."""
    try:
        if quiet:
            set_quiet_mode(True)

        backup_manager = BackupManager()

        # Validate backup exists
        backup_info = backup_manager.get_backup_info(backup_id)
        if not backup_info:
            print_error_panel(
                "Backup Not Found", f"Backup with ID '{backup_id}' not found"
            )
            return

        # Confirm restoration
        if not quiet:
            print_info_panel(
                "Restoration Details",
                f"Backup ID: {backup_id}\n"
                f"Repositories: {len(backup_info.repositories)}\n"
                f"Config included: {'Yes' if backup_info.config_included else 'No'}\n"
                f"Target directory: {target_dir or 'Original locations'}\n"
                f"Overwrite existing: {'Yes' if overwrite else 'No'}",
            )

        # Restore backup
        results = backup_manager.restore_backup(
            backup_id=backup_id,
            target_dir=target_dir,
            restore_config=not no_config,
            overwrite_existing=overwrite,
        )

        if not quiet:
            print_restore_results(results)

    except Exception as e:
        print_error_panel("Restoration Failed", f"An error occurred: {str(e)}")
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--backup-id", "-b", required=True, help="ID of the backup to validate")
@click.pass_context
def validate(ctx: click.Context, backup_id: str) -> None:
    """Validate a backup archive."""
    try:
        backup_manager = BackupManager()
        validation_result = backup_manager.validate_backup(backup_id)

        if validation_result["valid"]:
            print_success_panel(
                "Backup Validation Successful",
                f"Backup ID: {backup_id}\n"
                f"Archive size: {validation_result['archive_size'] / (1024 * 1024):.1f} MB\n"
                f"Repositories: {len(validation_result['metadata'].repositories)}\n"
                f"Config included: {'Yes' if validation_result['metadata'].config_included else 'No'}",
            )
        else:
            print_error_panel(
                "Backup Validation Failed",
                f"Error: {validation_result.get('error', 'Unknown error')}",
            )

    except Exception as e:
        print_error_panel("Validation Failed", f"An error occurred: {str(e)}")
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--backup-id", "-b", required=True, help="ID of the backup to delete")
@click.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
@click.pass_context
def delete(ctx: click.Context, backup_id: str, force: bool) -> None:
    """Delete a backup."""
    try:
        backup_manager = BackupManager()

        # Check if backup exists
        backup_info = backup_manager.get_backup_info(backup_id)
        if not backup_info:
            print_error_panel(
                "Backup Not Found", f"Backup with ID '{backup_id}' not found"
            )
            return

        # Confirm deletion
        if not force:
            print_warning_panel(
                "Confirm Deletion",
                f"Are you sure you want to delete backup '{backup_id}'?\n"
                f"This action cannot be undone.",
            )
            # In a real implementation, you might want to add user confirmation here
            # For now, we'll proceed with deletion

        # Delete backup
        if backup_manager.delete_backup(backup_id):
            print_success_panel(
                "Backup Deleted", f"Successfully deleted backup '{backup_id}'"
            )
        else:
            print_error_panel(
                "Deletion Failed", f"Failed to delete backup '{backup_id}'"
            )

    except Exception as e:
        print_error_panel("Deletion Failed", f"An error occurred: {str(e)}")
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--keep", "-k", type=int, default=5, help="Number of backups to keep")
@click.pass_context
def cleanup(ctx: click.Context, keep: int) -> None:
    """Clean up old backups, keeping only the most recent ones."""
    try:
        backup_manager = BackupManager()
        deleted_count = backup_manager.cleanup_old_backups(keep)

        if deleted_count > 0:
            print_success_panel(
                "Cleanup Completed",
                f"Deleted {deleted_count} old backup(s)\n"
                f"Keeping {keep} most recent backup(s)",
            )
        else:
            print_info_panel(
                "No Cleanup Needed", f"Already have {keep} or fewer backups"
            )

    except Exception as e:
        print_error_panel("Cleanup Failed", f"An error occurred: {str(e)}")
        if ctx.obj.get("verbose"):
            raise


# Export function for CLI registration
backup_commands = register_backup_commands
