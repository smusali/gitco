"""Tests for GitHub client module."""

import os
import unittest
from unittest.mock import Mock, patch

import pytest
from github import GithubException

from gitco.github_client import (
    GitHubClient,
    GitHubIssue,
    GitHubRepository,
    create_github_client,
)
from gitco.utils.exception import (
    APIError,
    GitHubAuthenticationError,
    GitHubRateLimitExceeded,
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

    @patch("gitco.utils.common.get_logger")
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

    @patch("gitco.utils.common.get_logger")
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

    @patch("gitco.utils.common.get_logger")
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

    @patch("gitco.utils.common.get_logger")
    @patch("gitco.github_client.Github")
    def test_init_anonymous(self, mock_github: Mock, mock_get_logger: Mock) -> None:
        """Test GitHubClient initialization with anonymous access."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            GitHubClient()

        mock_github.assert_called_once_with(base_url="https://api.github.com")

    @patch("gitco.utils.rate_limiter.get_logger")
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
        mock_logger.info.assert_called_with(
            "GitHub authentication successful for user: testuser"
        )

    @patch("gitco.utils.rate_limiter.get_logger")
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
            GitHubAuthenticationError, match="Failed to set up GitHub authentication"
        ):
            GitHubClient(token="invalid_token")

    @patch("gitco.utils.rate_limiter.get_logger")
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

        with pytest.raises(
            GitHubAuthenticationError, match="Failed to set up GitHub authentication"
        ):
            GitHubClient(token="invalid_token")

    @patch("gitco.utils.common.get_logger")
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

    @patch("gitco.utils.rate_limiter.get_logger")
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

    @patch("gitco.utils.common.get_logger")
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

    @patch("gitco.utils.common.get_logger")
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
        mock_issue1.get_reactions.return_value = [Mock(), Mock()]  # 2 reactions

        mock_github_instance.search_issues.return_value = [mock_issue1]
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

    @patch("gitco.utils.common.get_logger")
    @patch("gitco.github_client.Github")
    def test_get_issues_with_filters(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test issues fetch with filters."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_repo = Mock()
        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.state = "closed"
        mock_label = Mock()
        mock_label.name = "bug"
        mock_issue.labels = [mock_label]
        mock_issue.assignees = [Mock(login="user1")]
        mock_issue.created_at.isoformat.return_value = "2023-01-01T00:00:00Z"
        mock_issue.updated_at.isoformat.return_value = "2023-01-02T00:00:00Z"
        mock_issue.html_url = "https://github.com/owner/repo/issues/1"
        mock_issue.body = "Test issue body"
        mock_issue.user.login = "testuser"
        mock_issue.milestone.title = "v1.0"
        mock_issue.comments = 3
        mock_issue.get_reactions.return_value = [Mock(), Mock()]  # 2 reactions

        mock_github_instance.search_issues.return_value = [mock_issue]
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

        assert len(result) == 1
        issue = result[0]
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.state == "closed"

    @patch("gitco.utils.common.get_logger")
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
        mock_issue.get_reactions.return_value = [Mock()]  # 1 reaction

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

    @patch("gitco.utils.common.get_logger")
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
        # Mock datetime objects for reset times
        from datetime import datetime

        mock_reset_time = datetime.fromtimestamp(1640995200)
        mock_rate_limit.core.reset = mock_reset_time
        mock_rate_limit.search.limit = 30
        mock_rate_limit.search.remaining = 25
        mock_rate_limit.search.reset = mock_reset_time
        mock_rate_limit.graphql.limit = 5000
        mock_rate_limit.graphql.remaining = 4500
        mock_rate_limit.graphql.reset = mock_reset_time

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
            "graphql": {
                "limit": 5000,
                "remaining": 4500,
                "reset": 1640995200,
            },
        }

        assert result == expected

    @patch("gitco.utils.common.get_logger")
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

    @patch("gitco.utils.rate_limiter.get_logger")
    @patch("gitco.github_client.Github")
    def test_test_connection_failure(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test failed connection test."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_github_instance.get_user.side_effect = Exception("Connection failed")
        mock_github.return_value = mock_github_instance

        with pytest.raises(
            GitHubAuthenticationError, match="Failed to set up GitHub authentication"
        ):
            GitHubClient(token="test_token")


class TestCreateGitHubClient:
    """Test create_github_client function."""

    @patch("gitco.utils.common.get_logger")
    @patch("gitco.github_client.Github")
    def test_create_github_client_with_token(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test creating GitHub client with token."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        result = create_github_client(token="test_token")

        assert isinstance(result, GitHubClient)
        mock_github.assert_called_once()

    @patch("gitco.utils.common.get_logger")
    @patch("gitco.github_client.Github")
    def test_create_github_client_with_username_password(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test creating GitHub client with username/password."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        result = create_github_client(
            username="testuser",
            password="testpass",
            base_url="https://api.github.com",
        )

        assert isinstance(result, GitHubClient)
        mock_github.assert_called_once()

    @patch("gitco.utils.common.get_logger")
    @patch("gitco.github_client.Github")
    @patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"})
    def test_create_github_client_defaults(
        self, mock_github: Mock, mock_get_logger: Mock
    ) -> None:
        """Test creating GitHub client with defaults."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        mock_github_instance = Mock()
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        result = create_github_client()

        assert isinstance(result, GitHubClient)
        mock_github.assert_called_once()


if __name__ == "__main__":
    unittest.main()


# Additional test cases for GitHubIssue dataclass
def test_github_issue_with_all_fields() -> None:
    """Test GitHubIssue with all fields populated."""
    issue = GitHubIssue(
        number=123,
        title="Fix bug in authentication",
        state="open",
        labels=["bug", "help wanted"],
        assignees=["user1", "user2"],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/123",
        body="There's a bug in the authentication system",
        user="testuser",
        milestone="v2.0",
        comments_count=5,
        reactions_count=3,
    )

    assert issue.number == 123
    assert issue.title == "Fix bug in authentication"
    assert issue.body == "There's a bug in the authentication system"
    assert issue.state == "open"
    assert issue.labels == ["bug", "help wanted"]
    assert issue.assignees == ["user1", "user2"]
    assert issue.milestone == "v2.0"
    assert issue.created_at == "2023-01-01T00:00:00Z"
    assert issue.updated_at == "2023-01-02T00:00:00Z"
    assert issue.comments_count == 5
    assert issue.reactions_count == 3


def test_github_issue_with_minimal_fields() -> None:
    """Test GitHubIssue with minimal required fields."""
    issue = GitHubIssue(
        number=456,
        title="Documentation update",
        state="open",
        labels=[],
        assignees=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/456",
        body="Update the README file",
    )

    assert issue.number == 456
    assert issue.title == "Documentation update"
    assert issue.body == "Update the README file"
    assert issue.state == "open"
    assert issue.labels == []
    assert issue.assignees == []
    assert issue.milestone is None
    assert issue.created_at == "2023-01-01T00:00:00Z"
    assert issue.updated_at == "2023-01-02T00:00:00Z"
    assert issue.comments_count == 0
    assert issue.reactions_count == 0


def test_github_issue_equality() -> None:
    """Test GitHubIssue instances equality."""
    issue1 = GitHubIssue(
        number=123,
        title="Test issue",
        state="open",
        labels=["bug"],
        assignees=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/123",
        body="Test body",
    )

    issue2 = GitHubIssue(
        number=123,
        title="Test issue",
        state="open",
        labels=["bug"],
        assignees=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/123",
        body="Test body",
    )

    assert issue1 == issue2


def test_github_issue_inequality() -> None:
    """Test GitHubIssue instances inequality."""
    issue1 = GitHubIssue(
        number=123,
        title="Test issue 1",
        state="open",
        labels=[],
        assignees=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/123",
        body="Test body 1",
    )

    issue2 = GitHubIssue(
        number=124,
        title="Test issue 2",
        state="closed",
        labels=[],
        assignees=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/124",
        body="Test body 2",
    )

    assert issue1 != issue2


def test_github_issue_repr() -> None:
    """Test GitHubIssue string representation."""
    issue = GitHubIssue(
        number=123,
        title="Fix authentication bug",
        state="open",
        labels=["bug", "security"],
        assignees=[],
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/repo/issues/123",
        body="There's a bug in auth",
    )

    repr_str = repr(issue)
    assert "GitHubIssue" in repr_str
    assert "123" in repr_str
    assert "Fix authentication bug" in repr_str


# Additional test cases for GitHubRepository dataclass
def test_github_repository_with_all_fields() -> None:
    """Test GitHubRepository with all fields populated."""
    repo = GitHubRepository(
        name="test-repo",
        full_name="owner/test-repo",
        description="A test repository",
        language="Python",
        stargazers_count=100,
        forks_count=25,
        open_issues_count=10,
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/test-repo",
        clone_url="https://github.com/owner/test-repo.git",
        default_branch="main",
        topics=["python", "testing", "automation"],
        archived=False,
        disabled=False,
    )

    assert repo.name == "test-repo"
    assert repo.full_name == "owner/test-repo"
    assert repo.description == "A test repository"
    assert repo.language == "Python"
    assert repo.topics == ["python", "testing", "automation"]
    assert repo.stargazers_count == 100
    assert repo.forks_count == 25
    assert repo.open_issues_count == 10
    assert repo.default_branch == "main"
    assert repo.updated_at == "2023-01-02T00:00:00Z"
    assert repo.clone_url == "https://github.com/owner/test-repo.git"
    assert repo.archived is False
    assert repo.disabled is False


def test_github_repository_with_minimal_fields() -> None:
    """Test GitHubRepository with minimal required fields."""
    repo = GitHubRepository(
        name="minimal-repo",
        full_name="owner/minimal-repo",
        description="A minimal repository",
        language="JavaScript",
        stargazers_count=0,
        forks_count=0,
        open_issues_count=0,
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/owner/minimal-repo",
        clone_url="https://github.com/owner/minimal-repo.git",
        default_branch="main",
    )

    assert repo.name == "minimal-repo"
    assert repo.full_name == "owner/minimal-repo"
    assert repo.description == "A minimal repository"
    assert repo.language == "JavaScript"
    assert repo.topics is None
    assert repo.stargazers_count == 0
    assert repo.forks_count == 0
    assert repo.open_issues_count == 0
    assert repo.default_branch == "main"
    assert repo.updated_at == "2023-01-01T00:00:00Z"
    assert repo.clone_url == "https://github.com/owner/minimal-repo.git"
    assert repo.archived is False
    assert repo.disabled is False


def test_github_repository_equality() -> None:
    """Test GitHubRepository instances equality."""
    repo1 = GitHubRepository(
        name="test-repo",
        full_name="owner/test-repo",
        description="Test repository",
        language="Python",
        stargazers_count=100,
        forks_count=25,
        open_issues_count=10,
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/owner/test-repo",
        clone_url="https://github.com/owner/test-repo.git",
        default_branch="main",
    )

    repo2 = GitHubRepository(
        name="test-repo",
        full_name="owner/test-repo",
        description="Test repository",
        language="Python",
        stargazers_count=100,
        forks_count=25,
        open_issues_count=10,
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/owner/test-repo",
        clone_url="https://github.com/owner/test-repo.git",
        default_branch="main",
    )

    assert repo1 == repo2


def test_github_repository_inequality() -> None:
    """Test GitHubRepository instances inequality."""
    repo1 = GitHubRepository(
        name="test-repo-1",
        full_name="owner/test-repo-1",
        description="Test repository 1",
        language="Python",
        stargazers_count=100,
        forks_count=25,
        open_issues_count=10,
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/owner/test-repo-1",
        clone_url="https://github.com/owner/test-repo-1.git",
        default_branch="main",
    )

    repo2 = GitHubRepository(
        name="test-repo-2",
        full_name="owner/test-repo-2",
        description="Test repository 2",
        language="JavaScript",
        stargazers_count=200,
        forks_count=50,
        open_issues_count=20,
        updated_at="2023-01-02T00:00:00Z",
        html_url="https://github.com/owner/test-repo-2",
        clone_url="https://github.com/owner/test-repo-2.git",
        default_branch="main",
    )

    assert repo1 != repo2


def test_github_repository_repr() -> None:
    """Test GitHubRepository string representation."""
    repo = GitHubRepository(
        name="test-repo",
        full_name="owner/test-repo",
        description="A test repository",
        language="Python",
        stargazers_count=100,
        forks_count=25,
        open_issues_count=10,
        updated_at="2023-01-01T00:00:00Z",
        html_url="https://github.com/owner/test-repo",
        clone_url="https://github.com/owner/test-repo.git",
        default_branch="main",
    )

    repr_str = repr(repo)
    assert "GitHubRepository" in repr_str
    assert "test-repo" in repr_str
    assert "Python" in repr_str


# Additional test cases for GitHubRateLimitExceeded exception class
def test_github_rate_limit_exceeded_creation() -> None:
    """Test GitHubRateLimitExceeded creation."""
    error = GitHubRateLimitExceeded("Rate limit exceeded")

    assert str(error) == "Rate limit exceeded"
    assert isinstance(error, GitHubRateLimitExceeded)
    assert isinstance(error, Exception)


def test_github_rate_limit_exceeded_with_cause() -> None:
    """Test GitHubRateLimitExceeded with a cause."""
    original_error = ValueError("Original error")
    error = GitHubRateLimitExceeded("Rate limit exceeded")
    error.__cause__ = original_error

    assert str(error) == "Rate limit exceeded"
    assert error.__cause__ == original_error


def test_github_rate_limit_exceeded_inheritance() -> None:
    """Test GitHubRateLimitExceeded inheritance hierarchy."""
    error = GitHubRateLimitExceeded("Rate limit exceeded")

    assert isinstance(error, GitHubRateLimitExceeded)
    assert isinstance(error, Exception)
    # Should inherit from APIError (which inherits from GitCoError)
    from gitco.utils.exception import GitCoError

    assert isinstance(error, APIError)
    assert isinstance(error, GitCoError)


def test_github_rate_limit_exceeded_repr() -> None:
    """Test GitHubRateLimitExceeded string representation."""
    error = GitHubRateLimitExceeded("Rate limit exceeded")

    repr_str = repr(error)
    assert "GitHubRateLimitExceeded" in repr_str
    assert "Rate limit exceeded" in repr_str


def test_github_rate_limit_exceeded_attributes() -> None:
    """Test GitHubRateLimitExceeded attributes."""
    error = GitHubRateLimitExceeded("Rate limit exceeded")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


# Additional test cases for GitHubAuthenticationError exception class
def test_github_authentication_error_creation() -> None:
    """Test GitHubAuthenticationError creation."""
    error = GitHubAuthenticationError("Authentication failed")

    assert str(error) == "Authentication failed"
    assert isinstance(error, GitHubAuthenticationError)
    assert isinstance(error, Exception)


def test_github_authentication_error_with_cause() -> None:
    """Test GitHubAuthenticationError with a cause."""
    original_error = ValueError("Original error")
    error = GitHubAuthenticationError("Authentication failed")
    error.__cause__ = original_error

    assert str(error) == "Authentication failed"
    assert error.__cause__ == original_error


def test_github_authentication_error_inheritance() -> None:
    """Test GitHubAuthenticationError inheritance hierarchy."""
    error = GitHubAuthenticationError("Authentication failed")

    assert isinstance(error, GitHubAuthenticationError)
    assert isinstance(error, Exception)
    # Should inherit from APIError (which inherits from GitCoError)
    from gitco.utils.exception import GitCoError

    assert isinstance(error, APIError)
    assert isinstance(error, GitCoError)


def test_github_authentication_error_repr() -> None:
    """Test GitHubAuthenticationError string representation."""
    error = GitHubAuthenticationError("Authentication failed")

    repr_str = repr(error)
    assert "GitHubAuthenticationError" in repr_str
    assert "Authentication failed" in repr_str


def test_github_authentication_error_attributes() -> None:
    """Test GitHubAuthenticationError attributes."""
    error = GitHubAuthenticationError("Authentication failed")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


# Additional test cases for GitHubClient class
def test_github_client_with_custom_base_url() -> None:
    """Test GitHubClient with custom base URL."""
    with patch("gitco.github_client.Github") as mock_github:
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        client = GitHubClient(
            token="test_token",
            base_url="https://api.github.com",
        )

        assert client.base_url == "https://api.github.com"
        mock_github.assert_called_once()


def test_github_client_with_custom_timeout() -> None:
    """Test GitHubClient with custom timeout."""
    with patch("gitco.github_client.Github") as mock_github:
        mock_github_instance = Mock()
        mock_github.return_value = mock_github_instance

        client = GitHubClient(
            token="test_token",
            timeout=60,
        )

        assert client.timeout == 60


def test_github_client_get_user_info() -> None:
    """Test GitHubClient get_user_info method."""
    with patch("gitco.github_client.Github") as mock_github:
        mock_github_instance = Mock()
        mock_user = Mock()
        mock_user.login = "testuser"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_github_instance.get_user.return_value = mock_user
        mock_github.return_value = mock_github_instance

        client = GitHubClient(token="test_token")
        user_info = client.get_user_info()

        assert user_info["login"] == "testuser"
        assert user_info["name"] == "Test User"
        assert user_info["email"] == "test@example.com"


def test_github_client_get_user_info_error() -> None:
    """Test GitHubClient get_user_info method with error."""
    with patch("gitco.github_client.Github") as mock_github:
        mock_github_instance = Mock()
        mock_github_instance.get_user.side_effect = Exception("API Error")
        mock_github.return_value = mock_github_instance

        with pytest.raises(
            GitHubAuthenticationError, match="GitHub authentication failed"
        ):
            GitHubClient(token="test_token")


def test_github_client_get_rate_limit_info() -> None:
    """Test GitHubClient get_rate_limit_info method."""
    with patch("gitco.github_client.Github") as mock_github:
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
        rate_limit_info = client.get_rate_limit_info()

        assert rate_limit_info["core"]["limit"] == 5000
        assert rate_limit_info["core"]["remaining"] == 4500
        assert rate_limit_info["core"]["reset"] == 1640995200
        assert rate_limit_info["search"]["limit"] == 30
        assert rate_limit_info["search"]["remaining"] == 25
        assert rate_limit_info["search"]["reset"] == 1640995200
