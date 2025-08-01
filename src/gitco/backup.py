"""Backup and recovery mechanisms for GitCo."""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from zipfile import ZIP_DEFLATED, ZipFile

from rich import box
from rich.panel import Panel
from rich.table import Table

from .utils.common import (
    console,
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    print_error_panel,
    print_success_panel,
    print_warning_panel,
)
from .utils.exception import BackupError, RecoveryError


class BackupMetadata:
    """Metadata for a backup operation."""

    def __init__(
        self,
        backup_id: str,
        timestamp: datetime,
        repositories: list[str],
        config_included: bool,
        backup_type: str,
        size_bytes: int,
        description: Optional[str] = None,
    ):
        """Initialize backup metadata.

        Args:
            backup_id: Unique identifier for the backup
            timestamp: When the backup was created
            repositories: List of repository paths included
            config_included: Whether configuration was included
            backup_type: Type of backup (full, incremental, config-only)
            size_bytes: Size of backup in bytes
            description: Optional description of the backup
        """
        self.backup_id = backup_id
        self.timestamp = timestamp
        self.repositories = repositories
        self.config_included = config_included
        self.backup_type = backup_type
        self.size_bytes = size_bytes
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        return {
            "backup_id": self.backup_id,
            "timestamp": self.timestamp.isoformat(),
            "repositories": self.repositories,
            "config_included": self.config_included,
            "backup_type": self.backup_type,
            "size_bytes": self.size_bytes,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BackupMetadata":
        """Create metadata from dictionary.

        Args:
            data: Dictionary containing metadata

        Returns:
            BackupMetadata instance
        """
        return cls(
            backup_id=data["backup_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            repositories=data["repositories"],
            config_included=data["config_included"],
            backup_type=data["backup_type"],
            size_bytes=data["size_bytes"],
            description=data.get("description"),
        )


class BackupManager:
    """Manages backup and recovery operations for GitCo."""

    def __init__(self, backup_dir: Optional[str] = None):
        """Initialize backup manager.

        Args:
            backup_dir: Directory to store backups (defaults to ~/.gitco/backups)
        """
        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = Path.home() / ".gitco" / "backups"

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_dir / "metadata.json"
        self.backups: dict[str, BackupMetadata] = {}
        self.logger = get_logger()
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load backup metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    data = json.load(f)
                    self.backups = {
                        backup_id: BackupMetadata.from_dict(metadata_data)
                        for backup_id, metadata_data in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"Failed to load backup metadata: {e}")

    def _save_metadata(self) -> None:
        """Save backup metadata to file."""
        try:
            data = {
                backup_id: metadata.to_dict()
                for backup_id, metadata in self.backups.items()
            }
            with open(self.metadata_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save backup metadata: {e}")

    def _generate_backup_id(self) -> str:
        """Generate a unique backup ID.

        Returns:
            Unique backup identifier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"gitco_backup_{timestamp}"

    def create_backup(
        self,
        repositories: list[str],
        config_path: Optional[str] = None,
        backup_type: str = "full",
        description: Optional[str] = None,
        include_git_history: bool = True,
        compression_level: int = 6,
    ) -> tuple[str, BackupMetadata]:
        """Create a backup of repositories and configuration.

        Args:
            repositories: List of repository paths to backup
            config_path: Path to configuration file to include
            backup_type: Type of backup (full, incremental, config-only)
            description: Optional description of the backup
            include_git_history: Whether to include full git history
            compression_level: ZIP compression level (0-9)

        Returns:
            Tuple of (backup_path, metadata)

        Raises:
            BackupError: If backup creation fails
        """
        backup_id = self._generate_backup_id()
        backup_path = self.backup_dir / f"{backup_id}.zip"

        log_operation_start("backup creation", backup_id=backup_id)

        try:
            # Validate repositories exist
            valid_repos = []
            for repo_path in repositories:
                if os.path.exists(repo_path):
                    valid_repos.append(repo_path)
                else:
                    self.logger.warning(f"Repository not found: {repo_path}")

            if not valid_repos and backup_type != "config-only":
                raise BackupError("No valid repositories found for backup")

            # Create backup archive
            total_size = 0
            with ZipFile(
                backup_path,
                "w",
                compression=ZIP_DEFLATED,
                compresslevel=compression_level,
            ) as zip_file:
                # Add repositories
                for repo_path in valid_repos:
                    repo_size = self._add_repository_to_backup(
                        zip_file, repo_path, include_git_history
                    )
                    total_size += repo_size

                # Add configuration
                config_included = False
                if config_path and os.path.exists(config_path):
                    zip_file.write(config_path, "config/gitco-config.yml")
                    config_included = True
                    total_size += os.path.getsize(config_path)

                # Add metadata
                metadata = BackupMetadata(
                    backup_id=backup_id,
                    timestamp=datetime.now(),
                    repositories=valid_repos,
                    config_included=config_included,
                    backup_type=backup_type,
                    size_bytes=total_size,
                    description=description,
                )

                # Add metadata to archive
                metadata_json = json.dumps(metadata.to_dict(), indent=2)
                zip_file.writestr("metadata.json", metadata_json)

            # Store metadata
            self.backups[backup_id] = metadata
            self._save_metadata()

            log_operation_success(
                "backup creation",
                backup_id=backup_id,
                repositories_count=len(valid_repos),
                size_bytes=total_size,
            )

            return str(backup_path), metadata

        except Exception as e:
            # Clean up failed backup
            if backup_path.exists():
                backup_path.unlink()
            log_operation_failure("backup creation", e, backup_id=backup_id)
            raise BackupError(f"Failed to create backup: {e}") from e

    def _add_repository_to_backup(
        self, zip_file: ZipFile, repo_path: str, include_git_history: bool
    ) -> int:
        """Add a repository to the backup archive.

        Args:
            zip_file: ZIP file to add repository to
            repo_path: Path to repository
            include_git_history: Whether to include full git history

        Returns:
            Total size of added files in bytes
        """
        repo_name = os.path.basename(repo_path)
        total_size = 0

        # Create temporary directory for repository copy
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo_path = os.path.join(temp_dir, repo_name)

            # Copy repository
            if os.path.isdir(repo_path):
                shutil.copytree(repo_path, temp_repo_path, dirs_exist_ok=True)

                # Remove git history if not requested
                if not include_git_history:
                    git_dir = os.path.join(temp_repo_path, ".git")
                    if os.path.exists(git_dir):
                        shutil.rmtree(git_dir)

                # Add repository directory to archive (even if empty)
                zip_file.write(temp_repo_path, f"repositories/{repo_name}/")

                # Add files to archive
                for root, dirs, files in os.walk(temp_repo_path):
                    # Skip .git directory if not including history
                    if not include_git_history:
                        dirs[:] = [d for d in dirs if d != ".git"]

                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zip_file.write(file_path, f"repositories/{arc_name}")
                        total_size += os.path.getsize(file_path)

        return total_size

    def list_backups(self) -> list[BackupMetadata]:
        """List all available backups.

        Returns:
            List of backup metadata
        """
        return list(self.backups.values())

    def get_backup_info(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get information about a specific backup.

        Args:
            backup_id: ID of the backup

        Returns:
            Backup metadata if found, None otherwise
        """
        return self.backups.get(backup_id)

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup.

        Args:
            backup_id: ID of the backup to delete

        Returns:
            True if backup was deleted, False otherwise
        """
        if backup_id not in self.backups:
            return False

        backup_path = self.backup_dir / f"{backup_id}.zip"
        if backup_path.exists():
            backup_path.unlink()

        del self.backups[backup_id]
        self._save_metadata()

        self.logger.info(f"Deleted backup: {backup_id}")
        return True

    def restore_backup(
        self,
        backup_id: str,
        target_dir: Optional[str] = None,
        restore_config: bool = True,
        overwrite_existing: bool = False,
    ) -> dict[str, Any]:
        """Restore a backup.

        Args:
            backup_id: ID of the backup to restore
            target_dir: Directory to restore to (defaults to original locations)
            restore_config: Whether to restore configuration
            overwrite_existing: Whether to overwrite existing files

        Returns:
            Dictionary with restoration results

        Raises:
            RecoveryError: If restoration fails
        """
        if backup_id not in self.backups:
            raise RecoveryError(f"Backup not found: {backup_id}")

        backup_path = self.backup_dir / f"{backup_id}.zip"
        if not backup_path.exists():
            raise RecoveryError(f"Backup file not found: {backup_path}")

        metadata = self.backups[backup_id]
        log_operation_start("backup restoration", backup_id=backup_id)

        try:
            results: dict[str, Any] = {
                "backup_id": backup_id,
                "repositories_restored": [],
                "config_restored": False,
                "errors": [],
            }

            with ZipFile(backup_path, "r") as zip_file:
                # Extract metadata
                if "metadata.json" in zip_file.namelist():
                    # Note: metadata is extracted but not used in this context
                    pass

                # Restore repositories
                for repo_path in metadata.repositories:
                    try:
                        restored = self._restore_repository(
                            zip_file, repo_path, target_dir, overwrite_existing
                        )
                        if restored:
                            results["repositories_restored"].append(repo_path)
                    except Exception as e:
                        error_msg = f"Failed to restore repository {repo_path}: {e}"
                        results["errors"].append(error_msg)
                        self.logger.error(error_msg)

                # Restore configuration
                if restore_config and metadata.config_included:
                    try:
                        config_restored = self._restore_config(
                            zip_file, target_dir, overwrite_existing
                        )
                        results["config_restored"] = config_restored
                    except Exception as e:
                        error_msg = f"Failed to restore configuration: {e}"
                        results["errors"].append(error_msg)
                        self.logger.error(error_msg)

            log_operation_success(
                "backup restoration",
                backup_id=backup_id,
                repositories_restored=len(results["repositories_restored"]),
                config_restored=results["config_restored"],
            )

            return results

        except Exception as e:
            log_operation_failure("backup restoration", e, backup_id=backup_id)
            raise RecoveryError(f"Failed to restore backup: {e}") from e

    def _restore_repository(
        self,
        zip_file: ZipFile,
        original_path: str,
        target_dir: Optional[str],
        overwrite_existing: bool,
    ) -> bool:
        """Restore a repository from backup.

        Args:
            zip_file: ZIP file containing backup
            original_path: Original repository path
            target_dir: Target directory for restoration
            overwrite_existing: Whether to overwrite existing files

        Returns:
            True if repository was restored successfully
        """
        repo_name = os.path.basename(original_path)
        target_path = original_path

        if target_dir:
            target_path = os.path.join(target_dir, repo_name)

        # Check if target exists
        if os.path.exists(target_path) and not overwrite_existing:
            self.logger.warning(
                f"Target exists and overwrite not allowed: {target_path}"
            )
            return False

        # Create target directory
        os.makedirs(target_path, exist_ok=True)

        # Extract repository files
        repo_prefix = f"repositories/{repo_name}/"
        extracted_files = []

        for file_info in zip_file.filelist:
            if file_info.filename.startswith(repo_prefix):
                # Calculate the relative path within the repository
                relative_path = file_info.filename[len(repo_prefix) :]
                if relative_path:  # Skip if it's just the directory itself
                    # Create the target file path
                    target_file_path = os.path.join(target_path, relative_path)
                    # Create the directory if it doesn't exist
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    # Extract the file
                    with (
                        zip_file.open(file_info.filename) as source,
                        open(target_file_path, "wb") as target,
                    ):
                        target.write(source.read())
                    extracted_files.append(file_info.filename)

        if extracted_files:
            self.logger.info(f"Restored repository: {target_path}")
            return True

        return False

    def _restore_config(
        self,
        zip_file: ZipFile,
        target_dir: Optional[str],
        overwrite_existing: bool,
    ) -> bool:
        """Restore configuration from backup.

        Args:
            zip_file: ZIP file containing backup
            target_dir: Target directory for restoration
            overwrite_existing: Whether to overwrite existing files

        Returns:
            True if configuration was restored successfully
        """
        config_files = [f for f in zip_file.namelist() if f.startswith("config/")]

        if not config_files:
            return False

        target_path = "gitco-config.yml"
        if target_dir:
            target_path = os.path.join(target_dir, "gitco-config.yml")

        # Check if target exists
        if os.path.exists(target_path) and not overwrite_existing:
            self.logger.warning(
                f"Configuration exists and overwrite not allowed: {target_path}"
            )
            return False

        # Extract configuration
        for config_file in config_files:
            # Extract the file content and write it to the target location
            with (
                zip_file.open(config_file) as source,
                open(target_path, "wb") as target,
            ):
                target.write(source.read())

        self.logger.info(f"Restored configuration: {target_path}")
        return True

    def validate_backup(self, backup_id: str) -> dict[str, Any]:
        """Validate a backup archive.

        Args:
            backup_id: ID of the backup to validate

        Returns:
            Dictionary with validation results
        """
        if backup_id not in self.backups:
            return {"valid": False, "error": "Backup not found"}

        backup_path = self.backup_dir / f"{backup_id}.zip"
        if not backup_path.exists():
            return {"valid": False, "error": "Backup file not found"}

        try:
            with ZipFile(backup_path, "r") as zip_file:
                # Check if metadata exists
                if "metadata.json" not in zip_file.namelist():
                    return {"valid": False, "error": "Missing metadata"}

                # Validate metadata
                metadata_data = json.loads(zip_file.read("metadata.json"))
                metadata = BackupMetadata.from_dict(metadata_data)

                # Check if all referenced repositories exist
                missing_repos = []
                for repo_path in metadata.repositories:
                    repo_name = os.path.basename(repo_path)
                    repo_files = [
                        f
                        for f in zip_file.namelist()
                        if f.startswith(f"repositories/{repo_name}/")
                    ]
                    # For empty repositories, we might not have any files, but the repository should be listed
                    # Check if there are any files or if the repository directory exists
                    if not repo_files:
                        # Check if the repository directory itself exists (for empty repos)
                        repo_dir = f"repositories/{repo_name}/"
                        if repo_dir not in zip_file.namelist():
                            missing_repos.append(repo_path)

                if (
                    metadata.config_included
                    and "config/gitco-config.yml" not in zip_file.namelist()
                ):
                    missing_repos.append("config/gitco-config.yml")

                return {
                    "valid": len(missing_repos) == 0,
                    "metadata": metadata,
                    "missing_files": missing_repos,
                    "archive_size": backup_path.stat().st_size,
                }

        except Exception as e:
            return {"valid": False, "error": f"Validation failed: {e}"}

    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Clean up old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of backups to keep

        Returns:
            Number of backups deleted
        """
        if len(self.backups) <= keep_count:
            return 0

        # Sort backups by timestamp (newest first)
        sorted_backups = sorted(
            self.backups.items(), key=lambda x: x[1].timestamp, reverse=True
        )

        deleted_count = 0
        for backup_id, _ in sorted_backups[keep_count:]:
            if self.delete_backup(backup_id):
                deleted_count += 1

        return deleted_count


def print_backup_list(backups: list[BackupMetadata]) -> None:
    """Print a formatted list of backups.

    Args:
        backups: List of backup metadata
    """
    if not backups:
        console.print("No backups found.")
        return

    table = Table(
        title="Available Backups",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Date", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Repositories", style="blue")
    table.add_column("Size", style="magenta")
    table.add_column("Description", style="white")

    for backup in backups:
        # Format date
        date_str = backup.timestamp.strftime("%Y-%m-%d %H:%M")

        # Format size
        size_mb = backup.size_bytes / (1024 * 1024)
        size_str = f"{size_mb:.1f} MB"

        # Format repositories count
        repo_count = len(backup.repositories)
        repo_str = f"{repo_count} repo{'s' if repo_count != 1 else ''}"

        # Format description
        desc = backup.description or "No description"

        table.add_row(
            backup.backup_id,
            date_str,
            backup.backup_type,
            repo_str,
            size_str,
            desc,
        )

    console.print(table)


def print_backup_info(metadata: BackupMetadata) -> None:
    """Print detailed information about a backup.

    Args:
        metadata: Backup metadata
    """
    panel_content = f"""
[bold]Backup ID:[/bold] {metadata.backup_id}
[bold]Created:[/bold] {metadata.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
[bold]Type:[/bold] {metadata.backup_type}
[bold]Size:[/bold] {metadata.size_bytes / (1024 * 1024):.1f} MB
[bold]Repositories:[/bold] {len(metadata.repositories)}
[bold]Config Included:[/bold] {'Yes' if metadata.config_included else 'No'}
[bold]Description:[/bold] {metadata.description or 'No description'}

[bold]Repositories:[/bold]
"""

    for repo in metadata.repositories:
        panel_content += f"  • {repo}\n"

    panel = Panel(panel_content, title="Backup Information", box=box.ROUNDED)
    console.print(panel)


def print_restore_results(results: dict[str, Any]) -> None:
    """Print restoration results.

    Args:
        results: Dictionary with restoration results
    """
    success_count = len(results["repositories_restored"])
    error_count = len(results["errors"])

    if error_count == 0:
        print_success_panel(
            "Backup restored successfully",
            f"Restored {success_count} repositories and "
            f"{'configuration' if results['config_restored'] else 'no configuration'}",
        )
    else:
        print_warning_panel(
            "Backup restored with errors",
            f"Restored {success_count} repositories, {error_count} errors occurred",
        )

    if results["errors"]:
        print_error_panel("Restoration Errors", "\n".join(results["errors"]))
