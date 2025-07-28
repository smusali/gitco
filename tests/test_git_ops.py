"""Tests for git operations and repository management."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gitco.git_ops import GitRepository, GitRepositoryManager
from gitco.utils import GitOperationError


class TestGitRepository:
    """Test GitRepository class."""

    def test_init_with_path(self):
        """Test GitRepository initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            assert repo.path == Path(temp_dir).resolve()

    def test_is_git_repository_false(self):
        """Test is_git_repository returns False for non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            assert not repo.is_git_repository()

    def test_is_git_repository_true(self):
        """Test is_git_repository returns True for git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock git repository
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            (git_dir / "HEAD").write_text("ref: refs/heads/main")

            repo = GitRepository(temp_dir)
            # Mock git status to return success
            with patch.object(repo, "_run_git_command") as mock_run:
                mock_run.return_value.returncode = 0
                assert repo.is_git_repository()

    def test_get_remote_urls(self):
        """Test get_remote_urls method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            # Mock git remote -v output
            mock_output = "origin\tgit@github.com:user/repo.git (fetch)\norigin\tgit@github.com:user/repo.git (push)\nupstream\tgit@github.com:original/repo.git (fetch)\nupstream\tgit@github.com:original/repo.git (push)"

            with patch.object(repo, "_run_git_command") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = mock_output

                remotes = repo.get_remote_urls()
                assert remotes == {
                    "origin": "git@github.com:user/repo.git",
                    "upstream": "git@github.com:original/repo.git",
                }

    def test_get_current_branch(self):
        """Test get_current_branch method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "_run_git_command") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "main\n"

                branch = repo.get_current_branch()
                assert branch == "main"

    def test_get_default_branch(self):
        """Test get_default_branch method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "_run_git_command") as mock_run:
                # Mock symbolic-ref to return main
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "refs/remotes/origin/main\n"

                branch = repo.get_default_branch()
                assert branch == "main"

    def test_get_repository_status(self):
        """Test get_repository_status method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            # Mock all git operations
            with (
                patch.object(repo, "is_git_repository", return_value=True),
                patch.object(repo, "get_current_branch", return_value="main"),
                patch.object(repo, "get_default_branch", return_value="main"),
                patch.object(repo, "get_remote_urls", return_value={"origin": "url"}),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = ""  # Clean working directory

                status = repo.get_repository_status()

                assert status["is_git_repository"] is True
                assert status["current_branch"] == "main"
                assert status["default_branch"] == "main"
                assert status["remotes"] == {"origin": "url"}
                assert status["is_clean"] is True

    def test_validate_repository_path_not_exists(self):
        """Test validate_repository with non-existent path."""
        repo = GitRepository("/non/existent/path")
        errors = repo.validate_repository()
        assert len(errors) > 0
        assert any("does not exist" in error for error in errors)

    def test_validate_repository_not_git(self):
        """Test validate_repository with non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            errors = repo.validate_repository()
            assert len(errors) > 0
            assert any("not a valid Git repository" in error for error in errors)

    def test_run_git_command_timeout(self):
        """Test _run_git_command with timeout."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = TimeoutError("Command timed out")

                with pytest.raises(GitOperationError):
                    repo._run_git_command(["status"])


class TestGitRepositoryManager:
    """Test GitRepositoryManager class."""

    def test_init(self):
        """Test GitRepositoryManager initialization."""
        manager = GitRepositoryManager()
        assert manager.logger is not None

    def test_detect_repositories_empty_directory(self):
        """Test detect_repositories with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            repositories = manager.detect_repositories(temp_dir)
            assert len(repositories) == 0

    def test_detect_repositories_with_git_repos(self):
        """Test detect_repositories with git repositories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock git repositories
            repo1_dir = Path(temp_dir) / "repo1"
            repo1_dir.mkdir()
            (repo1_dir / ".git").mkdir()
            (repo1_dir / ".git" / "HEAD").write_text("ref: refs/heads/main")

            repo2_dir = Path(temp_dir) / "repo2"
            repo2_dir.mkdir()
            (repo2_dir / ".git").mkdir()
            (repo2_dir / ".git" / "HEAD").write_text("ref: refs/heads/main")

            manager = GitRepositoryManager()

            with patch.object(GitRepository, "is_git_repository", return_value=True):
                repositories = manager.detect_repositories(temp_dir)
                assert len(repositories) == 2

    def test_validate_repository_path(self):
        """Test validate_repository_path method."""
        manager = GitRepositoryManager()

        # Test with non-existent path
        is_valid, errors = manager.validate_repository_path("/non/existent/path")
        assert not is_valid
        assert len(errors) > 0

        # Test with valid git repository
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            (git_dir / "HEAD").write_text("ref: refs/heads/main")

            with (
                patch.object(GitRepository, "is_git_repository", return_value=True),
                patch.object(
                    GitRepository, "get_remote_urls", return_value={"origin": "url"}
                ),
                patch.object(GitRepository, "get_default_branch", return_value="main"),
            ):
                is_valid, errors = manager.validate_repository_path(temp_dir)
                assert is_valid
                assert len(errors) == 0

    def test_get_repository_info(self):
        """Test get_repository_info method."""
        manager = GitRepositoryManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(GitRepository, "get_repository_status") as mock_status:
                mock_status.return_value = {
                    "path": temp_dir,
                    "is_git_repository": True,
                    "current_branch": "main",
                    "default_branch": "main",
                    "remotes": {"origin": "url"},
                    "has_uncommitted_changes": False,
                    "has_untracked_files": False,
                    "is_clean": True,
                }

                info = manager.get_repository_info(temp_dir)
                assert info["is_git_repository"] is True
                assert info["current_branch"] == "main"

    def test_validate_repository_config(self):
        """Test validate_repository_config method."""
        manager = GitRepositoryManager()

        # Test with missing required fields
        config = {"name": "test"}
        errors = manager.validate_repository_config(config)
        assert len(errors) > 0
        assert any("Missing required field" in error for error in errors)

        # Test with valid config
        config = {
            "name": "test",
            "fork": "user/fork",
            "upstream": "original/repo",
            "local_path": "/path/to/repo",
        }

        with patch.object(manager, "validate_repository_path", return_value=(True, [])):
            errors = manager.validate_repository_config(config)
            assert len(errors) == 0

    def test_check_repository_sync_status(self):
        """Test check_repository_sync_status method."""
        manager = GitRepositoryManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(GitRepository, "get_repository_status") as mock_status:
                mock_status.return_value = {
                    "is_git_repository": True,
                    "current_branch": "main",
                    "remotes": {"upstream": "url"},
                    "has_uncommitted_changes": False,
                    "has_untracked_files": False,
                }

                with patch.object(GitRepository, "_run_git_command") as mock_run:
                    mock_run.return_value.returncode = 0
                    mock_run.return_value.stdout = "0\n"  # No commits behind/ahead

                    status = manager.check_repository_sync_status(temp_dir)
                    assert status["is_syncable"] is True
                    assert status["behind_upstream"] == 0
                    assert status["ahead_upstream"] == 0
