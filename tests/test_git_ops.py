"""Tests for Git operations module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from gitco.git_ops import GitRepository, GitRepositoryManager


class TestGitRepository:
    """Test GitRepository class."""

    def test_init(self):
        """Test GitRepository initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            assert repo.path == Path(temp_dir).resolve()

    def test_is_git_repository_false(self):
        """Test is_git_repository returns False for non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = GitRepository(temp_dir)
            assert not repo.is_git_repository()

    @patch("gitco.git_ops.subprocess.run")
    def test_is_git_repository_true(self, mock_run):
        """Test is_git_repository returns True for valid git repository."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert repo.is_git_repository()

    @patch("gitco.git_ops.subprocess.run")
    def test_get_remote_urls(self, mock_run):
        """Test get_remote_urls method."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\thttps://github.com/user/repo.git (fetch)\norigin\thttps://github.com/user/repo.git (push)\nupstream\thttps://github.com/upstream/repo.git (fetch)\nupstream\thttps://github.com/upstream/repo.git (push)\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            remotes = repo.get_remote_urls()
            assert remotes == {
                "origin": "https://github.com/user/repo.git",
                "upstream": "https://github.com/upstream/repo.git",
            }

    @patch("gitco.git_ops.subprocess.run")
    def test_has_uncommitted_changes_true(self, mock_run):
        """Test has_uncommitted_changes returns True when there are changes."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "M  modified_file.txt\nA  new_file.txt\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert repo.has_uncommitted_changes()

    @patch("gitco.git_ops.subprocess.run")
    def test_has_uncommitted_changes_false(self, mock_run):
        """Test has_uncommitted_changes returns False when no changes."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert not repo.has_uncommitted_changes()

    @patch("gitco.git_ops.subprocess.run")
    def test_create_stash_success(self, mock_run):
        """Test create_stash method success."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Saved working directory and index state WIP on main: abc1234 GitCo: Auto-stash before sync\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            with patch.object(repo, "has_uncommitted_changes", return_value=True):
                stash_ref = repo.create_stash()
                assert stash_ref == "stash@{0}"

    @patch("gitco.git_ops.subprocess.run")
    def test_create_stash_no_changes(self, mock_run):
        """Test create_stash method when no changes to stash."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            with patch.object(repo, "has_uncommitted_changes", return_value=False):
                stash_ref = repo.create_stash()
                assert stash_ref is None

    @patch("gitco.git_ops.subprocess.run")
    def test_create_stash_failure(self, mock_run):
        """Test create_stash method failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: No local changes to save\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            with patch.object(repo, "has_uncommitted_changes", return_value=True):
                stash_ref = repo.create_stash()
                assert stash_ref is None

    @patch("gitco.git_ops.subprocess.run")
    def test_apply_stash_success(self, mock_run):
        """Test apply_stash method success."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert repo.apply_stash("stash@{0}")

    @patch("gitco.git_ops.subprocess.run")
    def test_apply_stash_failure(self, mock_run):
        """Test apply_stash method failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: No stash found with the given name\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert not repo.apply_stash("stash@{0}")

    @patch("gitco.git_ops.subprocess.run")
    def test_drop_stash_success(self, mock_run):
        """Test drop_stash method success."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert repo.drop_stash("stash@{0}")

    @patch("gitco.git_ops.subprocess.run")
    def test_drop_stash_failure(self, mock_run):
        """Test drop_stash method failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: No stash found with the given name\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            assert not repo.drop_stash("stash@{0}")

    @patch("gitco.git_ops.subprocess.run")
    def test_list_stashes(self, mock_run):
        """Test list_stashes method."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc1234 1234567890 GitCo: Auto-stash before sync\ndef4567 1234567891 Another stash\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            stashes = repo.list_stashes()
            assert len(stashes) == 2
            assert stashes[0]["hash"] == "abc1234"
            assert stashes[0]["message"] == "GitCo: Auto-stash before sync"
            assert stashes[1]["hash"] == "def4567"
            assert stashes[1]["message"] == "Another stash"

    @patch("gitco.git_ops.subprocess.run")
    def test_safe_stash_and_restore_success(self, mock_run):
        """Test safe_stash_and_restore method success."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Saved working directory and index state WIP on main: abc1234 GitCo: Auto-stash before sync\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            def mock_operation():
                return True

            with patch.object(repo, "has_uncommitted_changes", return_value=True):
                success, stash_ref = repo.safe_stash_and_restore(mock_operation)
                assert success
                assert stash_ref == "stash@{0}"

    @patch("gitco.git_ops.subprocess.run")
    def test_safe_stash_and_restore_no_changes(self, mock_run):
        """Test safe_stash_and_restore method when no changes to stash."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            def mock_operation():
                return True

            with patch.object(repo, "has_uncommitted_changes", return_value=False):
                success, stash_ref = repo.safe_stash_and_restore(mock_operation)
                assert success
                assert stash_ref is None

    @patch("gitco.git_ops.subprocess.run")
    def test_safe_stash_and_restore_operation_failure(self, mock_run):
        """Test safe_stash_and_restore method when operation fails."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Saved working directory and index state WIP on main: abc1234 GitCo: Auto-stash before sync\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            def mock_operation():
                return False

            with patch.object(repo, "has_uncommitted_changes", return_value=True):
                success, stash_ref = repo.safe_stash_and_restore(mock_operation)
                assert not success
                assert stash_ref == "stash@{0}"

    @patch("gitco.git_ops.subprocess.run")
    def test_safe_stash_and_restore_stash_failure(self, mock_run):
        """Test safe_stash_and_restore method when stashing fails."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: No local changes to save\n"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            def mock_operation():
                return True

            with patch.object(repo, "has_uncommitted_changes", return_value=True):
                success, stash_ref = repo.safe_stash_and_restore(mock_operation)
                assert not success
                assert stash_ref is None


class TestGitRepositoryManager:
    """Test GitRepositoryManager class."""

    def test_init(self):
        """Test GitRepositoryManager initialization."""
        manager = GitRepositoryManager()
        assert manager.logger is not None

    def test_detect_repositories_empty(self):
        """Test detect_repositories with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            repos = manager.detect_repositories(temp_dir)
            assert repos == []

    def test_detect_repositories_with_git(self):
        """Test detect_repositories with git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                repos = manager.detect_repositories(temp_dir)
                assert len(repos) == 1
                assert repos[0].path == Path(temp_dir).resolve()

    def test_validate_repository_path_valid(self):
        """Test validate_repository_path with valid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository,
                    "get_remote_urls",
                    return_value={"origin": "https://github.com/user/repo.git"},
                ):
                    is_valid, errors = manager.validate_repository_path(temp_dir)
                    assert is_valid
                    assert errors == []

    def test_validate_repository_path_invalid(self):
        """Test validate_repository_path with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=False):
                is_valid, errors = manager.validate_repository_path(temp_dir)
                assert not is_valid
                assert len(errors) > 0

    def test_safe_stash_changes_success(self):
        """Test safe_stash_changes method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository, "create_stash", return_value="stash@{0}"
                ):
                    stash_ref = manager.safe_stash_changes(temp_dir)
                    assert stash_ref == "stash@{0}"

    def test_safe_stash_changes_invalid_repo(self):
        """Test safe_stash_changes method with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=False):
                stash_ref = manager.safe_stash_changes(temp_dir)
                assert stash_ref is None

    def test_restore_stash_success(self):
        """Test restore_stash method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(GitRepository, "apply_stash", return_value=True):
                    success = manager.restore_stash(temp_dir)
                    assert success

    def test_restore_stash_invalid_repo(self):
        """Test restore_stash method with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=False):
                success = manager.restore_stash(temp_dir)
                assert not success

    def test_drop_stash_success(self):
        """Test drop_stash method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(GitRepository, "drop_stash", return_value=True):
                    success = manager.drop_stash(temp_dir)
                    assert success

    def test_list_stashes_success(self):
        """Test list_stashes method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository,
                    "list_stashes",
                    return_value=[{"hash": "abc123", "message": "test"}],
                ):
                    stashes = manager.list_stashes(temp_dir)
                    assert len(stashes) == 1
                    assert stashes[0]["hash"] == "abc123"

    def test_has_uncommitted_changes_success(self):
        """Test has_uncommitted_changes method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository, "has_uncommitted_changes", return_value=True
                ):
                    has_changes = manager.has_uncommitted_changes(temp_dir)
                    assert has_changes

    def test_safe_stash_and_restore_success(self):
        """Test safe_stash_and_restore method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository,
                    "safe_stash_and_restore",
                    return_value=(True, "stash@{0}"),
                ):

                    def mock_operation():
                        return True

                    success, stash_ref = manager.safe_stash_and_restore(
                        temp_dir, mock_operation
                    )
                    assert success
                    assert stash_ref == "stash@{0}"

    def test_safe_stash_and_restore_invalid_repo(self):
        """Test safe_stash_and_restore method with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=False):

                def mock_operation():
                    return True

                success, stash_ref = manager.safe_stash_and_restore(
                    temp_dir, mock_operation
                )
                assert not success
                assert stash_ref is None
