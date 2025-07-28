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

    # Merge operation tests
    @patch("gitco.git_ops.subprocess.run")
    def test_merge_upstream_branch_success(self, mock_run):
        """Test merge_upstream_branch method success."""
        # Mock git commands for successful merge
        mock_results = [
            Mock(returncode=0, stdout="main"),  # get_current_branch
            Mock(returncode=0, stdout=""),  # has_uncommitted_changes
            Mock(returncode=0, stdout="5"),  # rev-list count
            Mock(returncode=0, stdout=""),  # merge
            Mock(returncode=0, stdout="abc123"),  # rev-parse HEAD
        ]
        mock_run.side_effect = mock_results

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            with patch.object(repo, "get_default_branch", return_value="main"):
                with patch.object(
                    repo,
                    "validate_upstream_remote",
                    return_value={
                        "has_upstream": True,
                        "is_valid": True,
                        "error": None,
                    },
                ):
                    result = repo.merge_upstream_branch()
                    assert result["success"]
                    assert result["message"] == "Successfully merged 5 commits"
                    assert result["merge_commit"] == "abc123"
                    assert result["conflicts"] == []

    @patch("gitco.git_ops.subprocess.run")
    def test_merge_upstream_branch_conflicts(self, mock_run):
        """Test merge_upstream_branch method with conflicts."""
        # Mock git commands for merge with conflicts
        mock_results = [
            Mock(returncode=0, stdout="main"),  # get_current_branch
            Mock(returncode=0, stdout=""),  # has_uncommitted_changes
            Mock(returncode=0, stdout="3"),  # rev-list count
            Mock(returncode=1, stderr="Merge conflict"),  # merge fails
            Mock(returncode=0, stdout="file1.txt\nfile2.txt"),  # detect conflicts
        ]
        mock_run.side_effect = mock_results

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            with patch.object(repo, "get_default_branch", return_value="main"):
                with patch.object(
                    repo,
                    "validate_upstream_remote",
                    return_value={
                        "has_upstream": True,
                        "is_valid": True,
                        "error": None,
                    },
                ):
                    result = repo.merge_upstream_branch()
                    assert not result["success"]
                    assert "Merge conflict" in result["error"]
                    assert result["conflicts"] == ["file1.txt", "file2.txt"]

    @patch("gitco.git_ops.subprocess.run")
    def test_merge_upstream_branch_already_up_to_date(self, mock_run):
        """Test merge_upstream_branch method when already up to date."""
        # Mock git commands for already up to date
        mock_results = [
            Mock(returncode=0, stdout="main"),  # get_current_branch
            Mock(returncode=0, stdout=""),  # has_uncommitted_changes
            Mock(returncode=0, stdout="0"),  # rev-list count (no commits ahead)
        ]
        mock_run.side_effect = mock_results

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)

            with patch.object(repo, "get_default_branch", return_value="main"):
                with patch.object(
                    repo,
                    "validate_upstream_remote",
                    return_value={
                        "has_upstream": True,
                        "is_valid": True,
                        "error": None,
                    },
                ):
                    result = repo.merge_upstream_branch()
                    assert result["success"]
                    assert result["message"] == "Already up to date"
                    assert result["conflicts"] == []

    @patch("gitco.git_ops.subprocess.run")
    def test_abort_merge_success(self, mock_run):
        """Test abort_merge method success."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            success = repo.abort_merge()
            assert success

    @patch("gitco.git_ops.subprocess.run")
    def test_abort_merge_failure(self, mock_run):
        """Test abort_merge method failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "No merge in progress"
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            success = repo.abort_merge()
            assert not success

    @patch("gitco.git_ops.subprocess.run")
    def test_resolve_conflicts_ours_strategy(self, mock_run):
        """Test resolve_conflicts method with ours strategy."""
        # Mock git commands for conflict resolution
        mock_results = [
            Mock(returncode=0, stdout="file1.txt\nfile2.txt"),  # detect conflicts
            Mock(returncode=0, stdout=""),  # checkout --ours
            Mock(returncode=0, stdout=""),  # add .
        ]
        mock_run.side_effect = mock_results

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            success = repo.resolve_conflicts("ours")
            assert success

    @patch("gitco.git_ops.subprocess.run")
    def test_resolve_conflicts_theirs_strategy(self, mock_run):
        """Test resolve_conflicts method with theirs strategy."""
        # Mock git commands for conflict resolution
        mock_results = [
            Mock(returncode=0, stdout="file1.txt\nfile2.txt"),  # detect conflicts
            Mock(returncode=0, stdout=""),  # checkout --theirs
            Mock(returncode=0, stdout=""),  # add .
        ]
        mock_run.side_effect = mock_results

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            success = repo.resolve_conflicts("theirs")
            assert success

    @patch("gitco.git_ops.subprocess.run")
    def test_resolve_conflicts_no_conflicts(self, mock_run):
        """Test resolve_conflicts method when no conflicts exist."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""  # No conflicts
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            success = repo.resolve_conflicts("ours")
            assert success

    @patch("gitco.git_ops.subprocess.run")
    def test_get_merge_status_clean(self, mock_run):
        """Test get_merge_status method when repository is clean."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""  # Clean status
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            status = repo.get_merge_status()
            assert not status["in_merge"]
            assert status["conflicts"] == []
            assert status["status"] == "clean"

    @patch("gitco.git_ops.subprocess.run")
    def test_get_merge_status_conflicted(self, mock_run):
        """Test get_merge_status method when merge has conflicts."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "UU file1.txt\nAA file2.txt"  # Conflicted status
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()
            repo = GitRepository(temp_dir)
            status = repo.get_merge_status()
            assert status["in_merge"]
            assert "file1.txt" in status["conflicts"]
            assert "file2.txt" in status["conflicts"]
            assert status["status"] == "conflicted"

    # GitRepositoryManager merge tests
    def test_fetch_upstream_success(self):
        """Test fetch_upstream method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(GitRepository, "fetch_upstream", return_value=True):
                    success = manager.fetch_upstream(temp_dir)
                    assert success

    def test_fetch_upstream_invalid_repo(self):
        """Test fetch_upstream method with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=False):
                success = manager.fetch_upstream(temp_dir)
                assert not success

    def test_manager_merge_upstream_branch_success(self):
        """Test merge_upstream_branch method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository,
                    "merge_upstream_branch",
                    return_value={
                        "success": True,
                        "message": "Successfully merged 5 commits",
                        "conflicts": [],
                        "merge_commit": "abc123",
                    },
                ):
                    result = manager.merge_upstream_branch(temp_dir)
                    assert result["success"]
                    assert result["message"] == "Successfully merged 5 commits"

    def test_merge_upstream_branch_invalid_repo(self):
        """Test merge_upstream_branch method with invalid repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=False):
                result = manager.merge_upstream_branch(temp_dir)
                assert not result["success"]
                assert result["error"] == "Not a valid Git repository"

    def test_manager_abort_merge_success(self):
        """Test abort_merge method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(GitRepository, "abort_merge", return_value=True):
                    success = manager.abort_merge(temp_dir)
                    assert success

    def test_resolve_conflicts_success(self):
        """Test resolve_conflicts method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository, "resolve_conflicts", return_value=True
                ):
                    success = manager.resolve_conflicts(temp_dir, "ours")
                    assert success

    def test_get_merge_status_success(self):
        """Test get_merge_status method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(
                    GitRepository,
                    "get_merge_status",
                    return_value={
                        "in_merge": False,
                        "conflicts": [],
                        "status": "clean",
                    },
                ):
                    status = manager.get_merge_status(temp_dir)
                    assert not status["in_merge"]
                    assert status["status"] == "clean"

    def test_sync_repository_with_upstream_success(self):
        """Test sync_repository_with_upstream method success."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(GitRepository, "fetch_upstream", return_value=True):
                    with patch.object(
                        GitRepository,
                        "merge_upstream_branch",
                        return_value={
                            "success": True,
                            "message": "Successfully merged 5 commits",
                            "conflicts": [],
                            "merge_commit": "abc123",
                        },
                    ):
                        result = manager.sync_repository_with_upstream(temp_dir)
                        assert result["success"]
                        assert result["fetch_success"]
                        assert result["merge_success"]
                        assert result["message"] == "Successfully merged 5 commits"

    def test_sync_repository_with_upstream_fetch_failure(self):
        """Test sync_repository_with_upstream method with fetch failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            manager = GitRepositoryManager()
            with patch.object(GitRepository, "is_git_repository", return_value=True):
                with patch.object(GitRepository, "fetch_upstream", return_value=False):
                    result = manager.sync_repository_with_upstream(temp_dir)
                    assert not result["success"]
                    assert not result["fetch_success"]
                    assert not result["merge_success"]
                    assert "Failed to fetch from upstream" in result["error"]
