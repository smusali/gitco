"""Tests for git operations and repository management."""

import subprocess
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

    def test_add_upstream_remote_new(self):
        """Test add_upstream_remote for new upstream remote."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            upstream_url = "git@github.com:original/repo.git"

            with (
                patch.object(repo, "get_remote_urls", return_value={}),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0

                success = repo.add_upstream_remote(upstream_url)

                assert success
                mock_run.assert_called_with(["remote", "add", "upstream", upstream_url])

    def test_add_upstream_remote_existing(self):
        """Test add_upstream_remote for existing upstream remote."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            upstream_url = "git@github.com:original/repo.git"

            with (
                patch.object(
                    repo, "get_remote_urls", return_value={"upstream": "old_url"}
                ),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0

                success = repo.add_upstream_remote(upstream_url)

                assert success
                mock_run.assert_called_with(
                    ["remote", "set-url", "upstream", upstream_url]
                )

    def test_add_upstream_remote_failure(self):
        """Test add_upstream_remote when git command fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            upstream_url = "git@github.com:original/repo.git"

            with (
                patch.object(repo, "get_remote_urls", return_value={}),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Permission denied"

                success = repo.add_upstream_remote(upstream_url)

                assert not success

    def test_remove_upstream_remote_exists(self):
        """Test remove_upstream_remote when upstream exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with (
                patch.object(repo, "get_remote_urls", return_value={"upstream": "url"}),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0

                success = repo.remove_upstream_remote()

                assert success
                mock_run.assert_called_with(["remote", "remove", "upstream"])

    def test_remove_upstream_remote_not_exists(self):
        """Test remove_upstream_remote when upstream doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "get_remote_urls", return_value={}):
                success = repo.remove_upstream_remote()

                assert success

    def test_remove_upstream_remote_failure(self):
        """Test remove_upstream_remote when git command fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with (
                patch.object(repo, "get_remote_urls", return_value={"upstream": "url"}),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Remote not found"

                success = repo.remove_upstream_remote()

                assert not success

    def test_update_upstream_remote_exists(self):
        """Test update_upstream_remote when upstream exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            new_url = "git@github.com:new/repo.git"

            with (
                patch.object(
                    repo, "get_remote_urls", return_value={"upstream": "old_url"}
                ),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0

                success = repo.update_upstream_remote(new_url)

                assert success
                mock_run.assert_called_with(["remote", "set-url", "upstream", new_url])

    def test_update_upstream_remote_not_exists(self):
        """Test update_upstream_remote when upstream doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            new_url = "git@github.com:new/repo.git"

            with (
                patch.object(repo, "get_remote_urls", return_value={}),
                patch.object(repo, "add_upstream_remote") as mock_add,
            ):
                mock_add.return_value = True

                success = repo.update_upstream_remote(new_url)

                assert success
                mock_add.assert_called_with(new_url)

    def test_validate_upstream_remote_exists_valid(self):
        """Test validate_upstream_remote when upstream exists and is valid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            upstream_url = "git@github.com:original/repo.git"

            with (
                patch.object(
                    repo, "get_remote_urls", return_value={"upstream": upstream_url}
                ),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "refs/heads/main"

                validation = repo.validate_upstream_remote()

                assert validation["has_upstream"]
                assert validation["is_valid"]
                assert validation["url"] == upstream_url
                assert validation["accessible"]

    def test_validate_upstream_remote_exists_invalid(self):
        """Test validate_upstream_remote when upstream exists but is invalid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            upstream_url = "git@github.com:original/repo.git"

            with (
                patch.object(
                    repo, "get_remote_urls", return_value={"upstream": upstream_url}
                ),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Repository not found"

                validation = repo.validate_upstream_remote()

                assert validation["has_upstream"]
                assert not validation["is_valid"]
                assert validation["url"] == upstream_url
                assert not validation["accessible"]
                assert "Repository not found" in validation["error"]

    def test_validate_upstream_remote_not_exists(self):
        """Test validate_upstream_remote when upstream doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "get_remote_urls", return_value={}):
                validation = repo.validate_upstream_remote()

                assert not validation["has_upstream"]
                assert not validation["is_valid"]
                assert validation["url"] is None
                assert "No upstream remote configured" in validation["error"]

    def test_fetch_upstream_success(self):
        """Test fetch_upstream when successful."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with (
                patch.object(repo, "validate_upstream_remote") as mock_validate,
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_validate.return_value = {
                    "has_upstream": True,
                    "is_valid": True,
                    "accessible": True,
                }
                mock_run.return_value.returncode = 0

                success = repo.fetch_upstream()

                assert success
                mock_run.assert_called_with(["fetch", "upstream"])

    def test_fetch_upstream_no_upstream(self):
        """Test fetch_upstream when no upstream is configured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "validate_upstream_remote") as mock_validate:
                mock_validate.return_value = {
                    "has_upstream": False,
                    "is_valid": False,
                    "error": "No upstream remote configured",
                }

                success = repo.fetch_upstream()

                assert not success

    def test_fetch_upstream_invalid_upstream(self):
        """Test fetch_upstream when upstream is invalid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "validate_upstream_remote") as mock_validate:
                mock_validate.return_value = {
                    "has_upstream": True,
                    "is_valid": False,
                    "error": "Repository not accessible",
                }

                success = repo.fetch_upstream()

                assert not success

    def test_fetch_upstream_failure(self):
        """Test fetch_upstream when git fetch fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with (
                patch.object(repo, "validate_upstream_remote") as mock_validate,
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_validate.return_value = {
                    "has_upstream": True,
                    "is_valid": True,
                    "accessible": True,
                }
                mock_run.return_value.returncode = 1
                mock_run.return_value.stderr = "Network error"

                success = repo.fetch_upstream()

                assert not success

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
                patch.object(
                    repo,
                    "validate_upstream_remote",
                    return_value={
                        "has_upstream": True,
                        "is_valid": True,
                        "url": "upstream_url",
                    },
                ),
                patch.object(repo, "_run_git_command") as mock_run,
            ):
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = ""  # Clean working directory

                status = repo.get_repository_status()

                assert status["is_git_repository"] is True
                assert status["current_branch"] == "main"
                assert status["default_branch"] == "main"
                assert status["remotes"] == {"origin": "url"}
                assert status["upstream_status"]["has_upstream"]
                assert status["upstream_status"]["is_valid"]

    def test_validate_repository_path_not_exists(self):
        """Test validate_repository when path doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_path = Path(temp_dir) / "nonexistent"
            repo = GitRepository(str(non_existent_path))

            errors = repo.validate_repository()
            assert len(errors) == 1
            assert "does not exist" in errors[0]

    def test_validate_repository_not_git(self):
        """Test validate_repository when path is not a git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch.object(repo, "is_git_repository", return_value=False):
                errors = repo.validate_repository()
                assert len(errors) == 1
                assert "not a valid Git repository" in errors[0]

    def test_run_git_command_timeout(self):
        """Test _run_git_command timeout handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired("git", 30)

                with pytest.raises(GitOperationError):
                    repo._run_git_command(["status"])

    def test_run_git_command_exception(self):
        """Test _run_git_command exception handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Test exception")

                with pytest.raises(GitOperationError):
                    repo._run_git_command(["status"])


class TestGitRepositoryManager:
    """Test GitRepositoryManager class."""

    def test_init(self):
        """Test GitRepositoryManager initialization."""
        manager = GitRepositoryManager()
        assert manager is not None

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
            repo1 = Path(temp_dir) / "repo1"
            repo1.mkdir()
            (repo1 / ".git").mkdir()
            (repo1 / ".git" / "HEAD").write_text("ref: refs/heads/main")

            repo2 = Path(temp_dir) / "repo2"
            repo2.mkdir()
            (repo2 / ".git").mkdir()
            (repo2 / ".git" / "HEAD").write_text("ref: refs/heads/main")

            manager = GitRepositoryManager()

            with patch.object(GitRepository, "is_git_repository", return_value=True):
                repositories = manager.detect_repositories(temp_dir)
                assert len(repositories) == 2

    def test_validate_repository_path(self):
        """Test validate_repository_path method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()

            # Test valid repository
            with patch.object(GitRepository, "validate_repository", return_value=[]):
                is_valid, errors = manager.validate_repository_path(temp_dir)
                assert is_valid
                assert len(errors) == 0

            # Test invalid repository
            with patch.object(
                GitRepository, "validate_repository", return_value=["Error"]
            ):
                is_valid, errors = manager.validate_repository_path(temp_dir)
                assert not is_valid
                assert len(errors) == 1

    def test_get_repository_info(self):
        """Test get_repository_info method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()

            with patch.object(GitRepository, "get_repository_status") as mock_status:
                mock_status.return_value = {
                    "path": temp_dir,
                    "is_git_repository": True,
                    "current_branch": "main",
                }

                info = manager.get_repository_info(temp_dir)
                assert info["path"] == temp_dir
                assert info["is_git_repository"]
                assert info["current_branch"] == "main"

    def test_validate_repository_config(self):
        """Test validate_repository_config method."""
        manager = GitRepositoryManager()

        # Test valid config
        valid_config = {
            "name": "test",
            "fork": "user/fork",
            "upstream": "original/repo",
            "local_path": "/path/to/repo",
        }

        with patch.object(manager, "validate_repository_path", return_value=(True, [])):
            errors = manager.validate_repository_config(valid_config)
            assert len(errors) == 0

        # Test invalid config
        invalid_config = {
            "name": "test",
            # Missing required fields
        }

        errors = manager.validate_repository_config(invalid_config)
        assert len(errors) > 0

    def test_check_repository_sync_status(self):
        """Test check_repository_sync_status method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()

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
                    mock_run.return_value.stdout = "0\n"

                    status = manager.check_repository_sync_status(temp_dir)
                    assert status["is_syncable"]
                    assert status["behind_upstream"] == 0

    def test_setup_upstream_remote(self):
        """Test setup_upstream_remote method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            upstream_url = "git@github.com:original/repo.git"

            with (
                patch.object(GitRepository, "is_git_repository", return_value=True),
                patch.object(GitRepository, "add_upstream_remote", return_value=True),
            ):
                success = manager.setup_upstream_remote(temp_dir, upstream_url)
                assert success

    def test_remove_upstream_remote(self):
        """Test remove_upstream_remote method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()

            with (
                patch.object(GitRepository, "is_git_repository", return_value=True),
                patch.object(
                    GitRepository, "remove_upstream_remote", return_value=True
                ),
            ):
                success = manager.remove_upstream_remote(temp_dir)
                assert success

    def test_update_upstream_remote(self):
        """Test update_upstream_remote method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            new_url = "git@github.com:new/repo.git"

            with (
                patch.object(GitRepository, "is_git_repository", return_value=True),
                patch.object(
                    GitRepository, "update_upstream_remote", return_value=True
                ),
            ):
                success = manager.update_upstream_remote(temp_dir, new_url)
                assert success

    def test_validate_upstream_remote(self):
        """Test validate_upstream_remote method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()

            with (
                patch.object(GitRepository, "is_git_repository", return_value=True),
                patch.object(
                    GitRepository, "validate_upstream_remote"
                ) as mock_validate,
            ):
                mock_validate.return_value = {
                    "has_upstream": True,
                    "is_valid": True,
                    "url": "upstream_url",
                }

                validation = manager.validate_upstream_remote(temp_dir)
                assert validation["has_upstream"]
                assert validation["is_valid"]
