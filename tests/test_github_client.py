"""Tests for GitHub client module."""

import os
import unittest
from unittest.mock import Mock, patch

import pytest
from github import GithubException

from gitco.github_client import (
    GitHubAuthenticationError,
    GitHubClient,
    GitHubIssue,
    GitHubRepository,
    create_github_client,
)


class TestGitHubIssue:
    """Test GitHubIssue dataclass."""

    def test_github_issue_creation(self) -> None:
        """Test creating a GitHubIssue instance."""
        issue = GitHubIssue(
            number=123,
            title="Test Issue",
            state="open",
            labels=["bug", "help wanted"],
            assignees=["user1", "user2"],
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            html_url="https://github.com/owner/repo/issues/123",
            body="This is a test issue",
            user="testuser",
            milestone="v1.0",
            comments_count=5,
            reactions_count=2,
        )

        assert issue.number == 123
        assert issue.title == "Test Issue"
        assert issue.state == "open"
        assert issue.labels == ["bug", "help wanted"]
        assert issue.assignees == ["user1", "user2"]
        assert issue.created_at == "2023-01-01T00:00:00Z"
        assert issue.updated_at == "2023-01-02T00:00:00Z"
        assert issue.html_url == "https://github.com/owner/repo/issues/123"
        assert issue.body == "This is a test issue"
        assert issue.user == "testuser"
        assert issue.milestone == "v1.0"
        assert issue.comments_count == 5
        assert issue.reactions_count == 2

    def test_github_issue_defaults(self) -> None:
        """Test GitHubIssue with default values."""
        issue = GitHubIssue(
            number=123,
            title="Test Issue",
            state="open",
            labels=[],
            assignees=[],
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            html_url="https://github.com/owner/repo/issues/123",
        )

        assert issue.body is None
        assert issue.user is None
        assert issue.milestone is None
        assert issue.comments_count == 0
        assert issue.reactions_count == 0


class TestGitHubRepository:
    """Test GitHubRepository dataclass."""

    def test_github_repository_creation(self) -> None:
        """Test creating a GitHubRepository instance."""
        repo = GitHubRepository(
            name="test-repo",
            full_name="owner/test-repo",
            description="A test repository",
            language="Python",
            stargazers_count=100,
            forks_count=50,
            open_issues_count=10,
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/owner/test-repo",
            clone_url="https://github.com/owner/test-repo.git",
            default_branch="main",
            topics=["python", "test"],
            archived=False,
            disabled=False,
        )

        assert repo.name == "test-repo"
        assert repo.full_name == "owner/test-repo"
        assert repo.description == "A test repository"
        assert repo.language == "Python"
        assert repo.stargazers_count == 100
        assert repo.forks_count == 50
        assert repo.open_issues_count == 10
        assert repo.updated_at == "2023-01-01T00:00:00Z"
        assert repo.html_url == "https://github.com/owner/test-repo"
        assert repo.clone_url == "https://github.com/owner/test-repo.git"
        assert repo.default_branch == "main"
        assert repo.topics == ["python", "test"]
        assert repo.archived is False
        assert repo.disabled is False

    def test_github_repository_defaults(self) -> None:
        """Test GitHubRepository with default values."""
        repo = GitHubRepository(
            name="test-repo",
            full_name="owner/test-repo",
            description=None,
            language=None,
            stargazers_count=0,
            forks_count=0,
            open_issues_count=0,
            updated_at="2023-01-01T00:00:00Z",
            html_url="https://github.com/owner/test-repo",
            clone_url="https://github.com/owner/test-repo.git",
            default_branch="main",
        )

        assert repo.description is None
        assert repo.language is None
        assert repo.topics is None
        assert repo.archived is False
        assert repo.disabled is False


class TestGitHubClient:
    """Test GitHubClient class."""

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_init_with_token(self, mock_github: Mock, mock_get_logger: Mock) -> None:
        """Test GitHubClient initialization with token."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        client = GitHubClient(token="test_token")

        assert client.base_url == "https://api.github.com"
        assert client.timeout == 30
        assert client.max_retries == 3
        mock_github.assert_called_once_with(
            "test_token", base_url="https://api.github.com"
        )

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_init_with_username_password(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test GitHubClient initialization with username/password."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        client = GitHubClient(username="testuser", password="testpass")

        assert client.base_url == "https://api.github.com"
        assert client.timeout == 30
        assert client.max_retries == 3
        mock_github.assert_called_once_with(
            "testuser", "testpass", base_url="https://api.github.com"
        )

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    @patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"})
    def test_init_with_env_token(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test GitHubClient initialization with environment token."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        GitHubClient()

        mock_github.assert_called_once_with(
            "env_token", base_url="https://api.github.com"
        )

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_init_anonymous(self, mock_github: Mock, mock_get_logger: Mock) -> None:
        """Test GitHubClient initialization with anonymous access."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            GitHubClient()

        mock_github.assert_called_once_with(base_url="https://api.github.com")

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_authentication_test_success(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test successful authentication."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        GitHubClient(token="test_token")

        # Authentication test is called during init
        mock_github_instance.get_user.assert_called_once()
        mock_logger.info.assert_called_with("Authenticated as: testuser")

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_authentication_test_failure_401(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test authentication failure with 401 error."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_user.side_effect = GithubException(401, "Unauthorized")
        mock_github.return_value = mock_github_instance

        with pytest.raises(
            GitHubAuthenticationError, match="Invalid GitHub credentials"
        ):
            GitHubClient(token="invalid_token")

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_authentication_test_failure_403(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test authentication failure with 403 error."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_user.side_effect = GithubException(403, "Forbidden")
        mock_github.return_value = mock_github_instance

        with pytest.raises(GitHubAuthenticationError, match="GitHub API access denied"):
            GitHubClient(token="invalid_token")

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_repository_success(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test successful repository fetch."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.full_name = "owner/test-repo"
        mock_repo.description = "Test repository"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 100
        mock_repo.forks_count = 50
        mock_repo.open_issues_count = 10
        mock_repo.updated_at.isoformat.return_value = "2023-01-01T00:00:00Z"
        mock_repo.html_url = "https://github.com/owner/test-repo"
        mock_repo.clone_url = "https://github.com/owner/test-repo.git"
        mock_repo.default_branch = "main"
        mock_repo.get_topics.return_value = ["python", "test"]
        mock_repo.archived = False
        mock_repo.disabled = False

        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.get_repository("owner/test-repo")

        assert result is not None
        assert result.name == "test-repo"
        assert result.full_name == "owner/test-repo"
        assert result.description == "Test repository"
        assert result.language == "Python"
        assert result.stargazers_count == 100
        assert result.forks_count == 50
        assert result.open_issues_count == 10
        assert result.updated_at == "2023-01-01T00:00:00Z"
        assert result.html_url == "https://github.com/owner/test-repo"
        assert result.clone_url == "https://github.com/owner/test-repo.git"
        assert result.default_branch == "main"
        assert result.topics == ["python", "test"]
        assert result.archived is False
        assert result.disabled is False

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_repository_not_found(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test repository fetch when repository not found."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_repo.side_effect = GithubException(404, "Not Found")
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.get_repository("owner/nonexistent")

        assert result is None
        mock_logger.warning.assert_called_with(
            "Repository not found: owner/nonexistent"
        )

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_repository_error(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test repository fetch with error."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_repo.side_effect = GithubException(
            500, "Internal Server Error"
        )
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")

        with pytest.raises(
            Exception, match="Failed to fetch repository owner/test-repo"
        ):
            client.get_repository("owner/test-repo")

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_issues_success(self, mock_github: Mock, mock_get_logger: Mock) -> None:
        """Test successful issues fetch."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_repo = Mock()
        mock_issue1 = Mock()
        mock_issue1.number = 1
        mock_issue1.title = "Test Issue 1"
        mock_issue1.state = "open"
        mock_label1 = Mock()
        mock_label1.name = "bug"
        mock_label2 = Mock()
        mock_label2.name = "help wanted"
        mock_issue1.labels = [mock_label1, mock_label2]
        mock_issue1.assignees = [Mock(login="user1"), Mock(login="user2")]
        mock_issue1.created_at.isoformat.return_value = "2023-01-01T00:00:00Z"
        mock_issue1.updated_at.isoformat.return_value = "2023-01-02T00:00:00Z"
        mock_issue1.html_url = "https://github.com/owner/repo/issues/1"
        mock_issue1.body = "Test issue body"
        mock_issue1.user.login = "testuser"
        mock_issue1.milestone.title = "v1.0"
        mock_issue1.comments = 5
        mock_issue1.reactions.totalCount = 2

        mock_repo.get_issues.return_value = [mock_issue1]
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.get_issues("owner/repo")

        assert len(result) == 1
        issue = result[0]
        assert issue.number == 1
        assert issue.title == "Test Issue 1"
        assert issue.state == "open"
        assert issue.labels == ["bug", "help wanted"]
        assert issue.assignees == ["user1", "user2"]
        assert issue.created_at == "2023-01-01T00:00:00Z"
        assert issue.updated_at == "2023-01-02T00:00:00Z"
        assert issue.html_url == "https://github.com/owner/repo/issues/1"
        assert issue.body == "Test issue body"
        assert issue.user == "testuser"
        assert issue.milestone == "v1.0"
        assert issue.comments_count == 5
        assert issue.reactions_count == 2

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_issues_with_filters(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test issues fetch with filters."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_repo = Mock()
        mock_repo.get_issues.return_value = []
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.get_issues(
            repo_name="owner/repo",
            state="closed",
            labels=["bug", "critical"],
            assignee="testuser",
            milestone="v1.0",
            limit=10,
        )

        assert len(result) == 0
        mock_repo.get_issues.assert_called_once_with(
            state="closed",
            labels="bug,critical",
            assignee="testuser",
            milestone="v1.0",
        )

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_search_issues_success(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test successful issues search."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "open"
        mock_label = Mock()
        mock_label.name = "bug"
        mock_issue.labels = [mock_label]
        mock_issue.assignees = [Mock(login="user1")]
        mock_issue.created_at.isoformat.return_value = "2023-01-01T00:00:00Z"
        mock_issue.updated_at.isoformat.return_value = "2023-01-02T00:00:00Z"
        mock_issue.html_url = "https://github.com/owner/repo/issues/1"
        mock_issue.body = "Test issue body"
        mock_issue.user.login = "testuser"
        mock_issue.milestone = None
        mock_issue.comments = 3
        mock_issue.reactions.totalCount = 1

        mock_github_instance.search_issues.return_value = [mock_issue]
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.search_issues(
            "test query", state="open", labels=["bug"], language="python"
        )

        assert len(result) == 1
        issue = result[0]
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.state == "open"
        assert issue.labels == ["bug"]
        assert issue.assignees == ["user1"]
        assert issue.created_at == "2023-01-01T00:00:00Z"
        assert issue.updated_at == "2023-01-02T00:00:00Z"
        assert issue.html_url == "https://github.com/owner/repo/issues/1"
        assert issue.body == "Test issue body"
        assert issue.user == "testuser"
        assert issue.milestone is None
        assert issue.comments_count == 3
        assert issue.reactions_count == 1

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_rate_limit_status(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test rate limit status fetch."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_rate_limit = Mock()
        mock_rate_limit.core.limit = 5000
        mock_rate_limit.core.remaining = 4500
        mock_rate_limit.core.reset = 1640995200
        mock_rate_limit.search.limit = 30
        mock_rate_limit.search.remaining = 25
        mock_rate_limit.search.reset = 1640995200

        mock_github_instance.get_rate_limit.return_value = mock_rate_limit
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.get_rate_limit_status()

        expected = {
            "core": {
                "limit": 5000,
                "remaining": 4500,
                "reset": 1640995200,
            },
            "search": {
                "limit": 30,
                "remaining": 25,
                "reset": 1640995200,
            },
        }

        assert result == expected

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_test_connection_success(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test successful connection test."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_rate_limit.return_value = Mock()
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.test_connection()

        assert result is True

    @patch("gitco.github_client.get_logger")
    @patch("gitco.github_client.Github")
    def test_test_connection_failure(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test failed connection test."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_rate_limit.side_effect = Exception("Connection failed")
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        result = client.test_connection()

        assert result is False
        mock_logger.error.assert_called_with(
            "GitHub API connection test failed: Connection failed"
        )


class TestCreateGitHubClient:
    """Test create_github_client function."""

    def test_create_github_client_with_token(self) -> None:
        """Test creating GitHub client with token."""
        with patch("src.gitco.github_client.GitHubClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            result = create_github_client(token="test_token")

            mock_client_class.assert_called_once_with(
                token="test_token",
                username=None,
                password=None,
                base_url="https://api.github.com",
            )
            assert result == mock_client

    def test_create_github_client_with_username_password(self) -> None:
        """Test creating GitHub client with username/password."""
        with patch("src.gitco.github_client.GitHubClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            result = create_github_client(
                username="testuser",
                password="testpass",
                base_url="https://api.github.com",
            )

            mock_client_class.assert_called_once_with(
                token=None,
                username="testuser",
                password="testpass",
                base_url="https://api.github.com",
            )
            assert result == mock_client

    def test_create_github_client_defaults(self) -> None:
        """Test creating GitHub client with defaults."""
        with patch("src.gitco.github_client.GitHubClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            result = create_github_client()

            mock_client_class.assert_called_once_with(
                token=None,
                username=None,
                password=None,
                base_url="https://api.github.com",
            )
            assert result == mock_client


if __name__ == "__main__":
    unittest.main()
