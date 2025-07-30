"""Tests for backup and recovery functionality."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from gitco.backup import (
    BackupManager,
    BackupMetadata,
    print_backup_info,
    print_backup_list,
    print_restore_results,
)
from gitco.utils.exception import BackupError, RecoveryError


class TestBackupMetadata:
    """Test BackupMetadata class."""

    def test_backup_metadata_creation(self) -> None:
        """Test creating backup metadata."""
        timestamp = datetime.now()
        metadata = BackupMetadata(
            backup_id="test_backup_123",
            timestamp=timestamp,
            repositories=["/path/to/repo1", "/path/to/repo2"],
            config_included=True,
            backup_type="full",
            size_bytes=1024,
            description="Test backup",
        )

        assert metadata.backup_id == "test_backup_123"
        assert metadata.timestamp == timestamp
        assert metadata.repositories == ["/path/to/repo1", "/path/to/repo2"]
        assert metadata.config_included is True
        assert metadata.backup_type == "full"
        assert metadata.size_bytes == 1024
        assert metadata.description == "Test backup"

    def test_backup_metadata_to_dict(self) -> None:
        """Test converting metadata to dictionary."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        metadata = BackupMetadata(
            backup_id="test_backup_123",
            timestamp=timestamp,
            repositories=["/path/to/repo1"],
            config_included=True,
            backup_type="full",
            size_bytes=1024,
            description="Test backup",
        )

        data = metadata.to_dict()
        assert data["backup_id"] == "test_backup_123"
        assert data["timestamp"] == "2023-01-01T12:00:00"
        assert data["repositories"] == ["/path/to/repo1"]
        assert data["config_included"] is True
        assert data["backup_type"] == "full"
        assert data["size_bytes"] == 1024
        assert data["description"] == "Test backup"

    def test_backup_metadata_from_dict(self) -> None:
        """Test creating metadata from dictionary."""
        data = {
            "backup_id": "test_backup_123",
            "timestamp": "2023-01-01T12:00:00",
            "repositories": ["/path/to/repo1"],
            "config_included": True,
            "backup_type": "full",
            "size_bytes": 1024,
            "description": "Test backup",
        }

        metadata = BackupMetadata.from_dict(data)
        assert metadata.backup_id == "test_backup_123"
        assert metadata.timestamp == datetime(2023, 1, 1, 12, 0, 0)
        assert metadata.repositories == ["/path/to/repo1"]
        assert metadata.config_included is True
        assert metadata.backup_type == "full"
        assert metadata.size_bytes == 1024
        assert metadata.description == "Test backup"


class TestBackupManager:
    """Test BackupManager class."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.temp_dir, "backups")
        self.backup_manager = BackupManager(self.backup_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_backup_manager_initialization(self) -> None:
        """Test backup manager initialization."""
        assert self.backup_manager.backup_dir == Path(self.backup_dir)
        assert self.backup_manager.backup_dir.exists()
        assert (
            self.backup_manager.metadata_file == Path(self.backup_dir) / "metadata.json"
        )

    def test_generate_backup_id(self) -> None:
        """Test backup ID generation."""
        backup_id = self.backup_manager._generate_backup_id()
        assert backup_id.startswith("gitco_backup_")
        assert len(backup_id) > len("gitco_backup_")

    def test_create_backup_with_valid_repositories(self) -> None:
        """Test creating backup with valid repositories."""
        # Create test repositories
        repo1_path = os.path.join(self.temp_dir, "repo1")
        repo2_path = os.path.join(self.temp_dir, "repo2")

        os.makedirs(repo1_path)
        os.makedirs(repo2_path)

        # Create some files in repositories
        with open(os.path.join(repo1_path, "file1.txt"), "w") as f:
            f.write("test content 1")

        with open(os.path.join(repo2_path, "file2.txt"), "w") as f:
            f.write("test content 2")

        # Create backup
        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo1_path, repo2_path],
            backup_type="full",
            description="Test backup",
        )

        assert os.path.exists(backup_path)
        assert metadata.backup_id.startswith("gitco_backup_")
        assert len(metadata.repositories) == 2
        assert metadata.config_included is False
        assert metadata.backup_type == "full"
        assert metadata.description == "Test backup"

    def test_create_backup_with_config(self) -> None:
        """Test creating backup with configuration file."""
        # Create test repository
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        # Create config file
        config_path = os.path.join(self.temp_dir, "gitco-config.yml")
        with open(config_path, "w") as f:
            f.write("repositories:\n  - name: test\n")

        # Create backup
        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo_path],
            config_path=config_path,
            backup_type="full",
        )

        assert metadata.config_included is True

    def test_create_backup_with_nonexistent_repositories(self) -> None:
        """Test creating backup with nonexistent repositories."""
        with pytest.raises(BackupError, match="No valid repositories found"):
            self.backup_manager.create_backup(
                repositories=["/nonexistent/path"],
                backup_type="full",
            )

    def test_create_config_only_backup(self) -> None:
        """Test creating config-only backup."""
        # Create config file
        config_path = os.path.join(self.temp_dir, "gitco-config.yml")
        with open(config_path, "w") as f:
            f.write("repositories:\n  - name: test\n")

        # Create backup
        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[],
            config_path=config_path,
            backup_type="config-only",
        )

        assert metadata.backup_type == "config-only"
        assert metadata.config_included is True
        assert len(metadata.repositories) == 0

    def test_list_backups(self) -> None:
        """Test listing backups."""
        # Create a backup first
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        self.backup_manager.create_backup(
            repositories=[repo_path],
            backup_type="full",
        )

        backups = self.backup_manager.list_backups()
        assert len(backups) == 1
        assert backups[0].backup_type == "full"

    def test_get_backup_info(self) -> None:
        """Test getting backup information."""
        # Create a backup first
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo_path],
            backup_type="full",
        )

        backup_info = self.backup_manager.get_backup_info(metadata.backup_id)
        assert backup_info is not None
        assert backup_info.backup_id == metadata.backup_id

        # Test with nonexistent backup
        backup_info = self.backup_manager.get_backup_info("nonexistent")
        assert backup_info is None

    def test_delete_backup(self) -> None:
        """Test deleting backup."""
        # Create a backup first
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo_path],
            backup_type="full",
        )

        # Delete backup
        result = self.backup_manager.delete_backup(metadata.backup_id)
        assert result is True

        # Verify backup is deleted
        backups = self.backup_manager.list_backups()
        assert len(backups) == 0

        # Test deleting nonexistent backup
        result = self.backup_manager.delete_backup("nonexistent")
        assert result is False

    def test_validate_backup(self) -> None:
        """Test backup validation."""
        # Create a backup first
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo_path],
            backup_type="full",
        )

        # Validate backup
        result = self.backup_manager.validate_backup(metadata.backup_id)
        assert result["valid"] is True
        assert "metadata" in result
        assert "archive_size" in result

        # Test validating nonexistent backup
        result = self.backup_manager.validate_backup("nonexistent")
        assert result["valid"] is False
        assert "error" in result

    def test_cleanup_old_backups(self) -> None:
        """Test cleaning up old backups."""
        # Create multiple backups
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        for i in range(7):
            self.backup_manager.create_backup(
                repositories=[repo_path],
                backup_type="full",
                description=f"Backup {i}",
            )

        # Clean up old backups
        deleted_count = self.backup_manager.cleanup_old_backups(keep_count=3)
        assert deleted_count == 4

        # Verify only 3 backups remain
        backups = self.backup_manager.list_backups()
        assert len(backups) == 3

    def test_restore_backup(self) -> None:
        """Test restoring backup."""
        # Create test repository
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        with open(os.path.join(repo_path, "test.txt"), "w") as f:
            f.write("test content")

        # Create backup
        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo_path],
            backup_type="full",
        )

        # Restore backup
        results = self.backup_manager.restore_backup(
            backup_id=metadata.backup_id,
            target_dir=os.path.join(self.temp_dir, "restored"),
        )

        assert results["backup_id"] == metadata.backup_id
        assert len(results["repositories_restored"]) == 1
        assert results["config_restored"] is False
        assert len(results["errors"]) == 0

    def test_restore_nonexistent_backup(self) -> None:
        """Test restoring nonexistent backup."""
        with pytest.raises(RecoveryError, match="Backup not found"):
            self.backup_manager.restore_backup(backup_id="nonexistent")


class TestBackupPrintFunctions:
    """Test backup print functions."""

    def test_print_backup_list(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test printing backup list."""
        metadata = BackupMetadata(
            backup_id="test_backup_123",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            repositories=["/path/to/repo1", "/path/to/repo2"],
            config_included=True,
            backup_type="full",
            size_bytes=1024 * 1024,  # 1 MB
            description="Test backup",
        )

        print_backup_list([metadata])
        captured = capsys.readouterr()
        assert "test_backup_123" in captured.out
        assert "Test backup" in captured.out

    def test_print_backup_list_empty(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test printing empty backup list."""
        print_backup_list([])
        captured = capsys.readouterr()
        assert "No backups found" in captured.out

    def test_print_backup_info(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test printing backup info."""
        metadata = BackupMetadata(
            backup_id="test_backup_123",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            repositories=["/path/to/repo1"],
            config_included=True,
            backup_type="full",
            size_bytes=1024 * 1024,
            description="Test backup",
        )

        print_backup_info(metadata)
        captured = capsys.readouterr()
        assert "test_backup_123" in captured.out
        assert "Test backup" in captured.out

    def test_print_restore_results_success(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing successful restore results."""
        results = {
            "backup_id": "test_backup_123",
            "repositories_restored": ["/path/to/repo1", "/path/to/repo2"],
            "config_restored": True,
            "errors": [],
        }

        print_restore_results(results)
        captured = capsys.readouterr()
        assert "Backup restored successfully" in captured.out

    def test_print_restore_results_with_errors(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test printing restore results with errors."""
        results = {
            "backup_id": "test_backup_123",
            "repositories_restored": ["/path/to/repo1"],
            "config_restored": False,
            "errors": ["Failed to restore repo2"],
        }

        print_restore_results(results)
        captured = capsys.readouterr()
        assert "Backup restored with errors" in captured.out
        assert "Failed to restore repo2" in captured.out


class TestBackupIntegration:
    """Integration tests for backup functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.temp_dir, "backups")
        self.backup_manager = BackupManager(self.backup_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_backup_and_restore_workflow(self) -> None:
        """Test complete backup and restore workflow."""
        # Create test repositories with git history
        repo1_path = os.path.join(self.temp_dir, "repo1")
        repo2_path = os.path.join(self.temp_dir, "repo2")

        os.makedirs(repo1_path)
        os.makedirs(repo2_path)

        # Create files in repositories
        with open(os.path.join(repo1_path, "file1.txt"), "w") as f:
            f.write("content 1")

        with open(os.path.join(repo2_path, "file2.txt"), "w") as f:
            f.write("content 2")

        # Create config file
        config_path = os.path.join(self.temp_dir, "gitco-config.yml")
        with open(config_path, "w") as f:
            f.write("repositories:\n  - name: test\n")

        # Create backup
        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo1_path, repo2_path],
            config_path=config_path,
            backup_type="full",
            description="Integration test backup",
        )

        # Verify backup was created
        assert os.path.exists(backup_path)
        assert metadata.config_included is True
        assert len(metadata.repositories) == 2

        # Validate backup
        validation_result = self.backup_manager.validate_backup(metadata.backup_id)
        assert validation_result["valid"] is True

        # Restore backup to different location
        restore_dir = os.path.join(self.temp_dir, "restored")
        results = self.backup_manager.restore_backup(
            backup_id=metadata.backup_id,
            target_dir=restore_dir,
            restore_config=True,
            overwrite_existing=True,
        )

        # Verify restoration
        assert len(results["repositories_restored"]) == 2
        assert results["config_restored"] is True
        assert len(results["errors"]) == 0

        # Verify files were restored
        restored_repo1 = os.path.join(restore_dir, "repo1")
        restored_repo2 = os.path.join(restore_dir, "repo2")
        restored_config = os.path.join(restore_dir, "gitco-config.yml")

        assert os.path.exists(restored_repo1)
        assert os.path.exists(restored_repo2)
        assert os.path.exists(restored_config)
        assert os.path.exists(os.path.join(restored_repo1, "file1.txt"))
        assert os.path.exists(os.path.join(restored_repo2, "file2.txt"))

    def test_backup_without_git_history(self) -> None:
        """Test backup without git history."""
        # Create test repository
        repo_path = os.path.join(self.temp_dir, "repo")
        os.makedirs(repo_path)

        # Create .git directory to simulate git repository
        git_dir = os.path.join(repo_path, ".git")
        os.makedirs(git_dir)

        # Create some files
        with open(os.path.join(repo_path, "file.txt"), "w") as f:
            f.write("content")

        # Create backup without git history
        backup_path, metadata = self.backup_manager.create_backup(
            repositories=[repo_path],
            backup_type="full",
            include_git_history=False,
        )

        # Verify backup was created
        assert os.path.exists(backup_path)
        assert metadata.size_bytes > 0

        # Restore and verify .git directory is not included
        restore_dir = os.path.join(self.temp_dir, "restored")
        self.backup_manager.restore_backup(
            backup_id=metadata.backup_id,
            target_dir=restore_dir,
            overwrite_existing=True,
        )

        restored_repo = os.path.join(restore_dir, "repo")
        assert os.path.exists(restored_repo)
        assert not os.path.exists(os.path.join(restored_repo, ".git"))
        assert os.path.exists(os.path.join(restored_repo, "file.txt"))
