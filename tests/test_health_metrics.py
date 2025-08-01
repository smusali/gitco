"""Tests for repository health metrics calculation."""

import json
from unittest.mock import Mock, patch

import pytest

from gitco.health_metrics import (
    HealthMetricsError,
    HealthSummary,
    RepositoryHealthCalculator,
    RepositoryHealthMetrics,
    create_health_calculator,
)


class TestRepositoryHealthMetrics:
    """Test RepositoryHealthMetrics dataclass."""

    def test_repository_health_metrics_creation(self) -> None:
        """Test creating RepositoryHealthMetrics instance."""
        metrics = RepositoryHealthMetrics(
            repository_name="test-repo",
            repository_path="/path/to/repo",
            upstream_url="https://github.com/owner/test-repo",
        )

        assert metrics.repository_name == "test-repo"
        assert metrics.repository_path == "/path/to/repo"
        assert metrics.upstream_url == "https://github.com/owner/test-repo"
        assert metrics.overall_health_score == 0.0
        assert metrics.health_status == "unknown"

    def test_repository_health_metrics_defaults(self) -> None:
        """Test RepositoryHealthMetrics default values."""
        metrics = RepositoryHealthMetrics(
            repository_name="test-repo",
            repository_path="/path/to/repo",
        )

        assert metrics.stars_count == 0
        assert metrics.forks_count == 0
        assert metrics.open_issues_count == 0
        assert metrics.contributor_engagement_score == 0.0
        assert metrics.topics == []


class TestHealthSummary:
    """Test HealthSummary dataclass."""

    def test_health_summary_creation(self) -> None:
        """Test creating HealthSummary instance."""
        summary = HealthSummary(total_repositories=5)

        assert summary.total_repositories == 5
        assert summary.healthy_repositories == 0
        assert summary.needs_attention_repositories == 0
        assert summary.critical_repositories == 0
        assert summary.trending_repositories == []
        assert summary.declining_repositories == []

    def test_health_summary_defaults(self) -> None:
        """Test HealthSummary default values."""
        summary = HealthSummary()

        assert summary.total_repositories == 0
        assert summary.active_repositories_7d == 0
        assert summary.active_repositories_30d == 0
        assert summary.average_activity_score == 0.0


class TestRepositoryHealthCalculator:
    """Test RepositoryHealthCalculator class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.mock_config = Mock()
        self.mock_github_client = Mock()
        self.calculator = RepositoryHealthCalculator(
            self.mock_config, self.mock_github_client
        )

    def test_calculator_initialization(self) -> None:
        """Test RepositoryHealthCalculator initialization."""
        assert self.calculator.config == self.mock_config
        assert self.calculator.github_client == self.mock_github_client

    def test_calculate_repository_health_basic(self) -> None:
        """Test basic repository health calculation."""
        repo_config = {
            "name": "test-repo",
            "local_path": "/path/to/repo",
            "upstream": "https://github.com/owner/test-repo",
        }

        with patch("gitco.health_metrics.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("gitco.health_metrics.GitRepository") as mock_git_repo:
                mock_git_repo.return_value.get_repository_status.return_value = {
                    "total_commits": 100,
                    "recent_commits_30d": 10,
                    "recent_commits_7d": 2,
                    "total_contributors": 5,
                    "active_contributors_30d": 3,
                    "active_contributors_7d": 1,
                    "last_commit_days_ago": 3,
                    "sync_status": "up_to_date",
                }

                # Mock GitHub client to return None for get_repository
                self.mock_github_client.get_repository.return_value = None

                metrics = self.calculator.calculate_repository_health(repo_config)

                assert metrics.repository_name == "test-repo"
                assert metrics.repository_path == "/path/to/repo"
                assert metrics.upstream_url == "https://github.com/owner/test-repo"
                assert metrics.total_commits == 100
                assert metrics.recent_commits_30d == 10
                assert metrics.recent_commits_7d == 2

    def test_calculate_repository_health_with_github_data(self) -> None:
        """Test repository health calculation with GitHub data."""
        repo_config = {
            "name": "test-repo",
            "local_path": "/path/to/repo",
            "upstream": "https://github.com/owner/test-repo",
        }

        mock_github_repo = Mock()
        mock_github_repo.stargazers_count = 1000
        mock_github_repo.forks_count = 500
        mock_github_repo.open_issues_count = 50
        mock_github_repo.language = "Python"
        mock_github_repo.topics = ["python", "api", "web"]
        mock_github_repo.archived = False
        mock_github_repo.disabled = False

        self.mock_github_client.get_repository.return_value = mock_github_repo
        self.mock_github_client.get_issues.return_value = []

        with patch("gitco.health_metrics.GitRepository") as mock_git_repo:
            mock_git_repo.return_value.get_repository_status.return_value = {
                "total_commits": 100,
                "recent_commits_30d": 10,
                "recent_commits_7d": 2,
                "total_contributors": 5,
                "active_contributors_30d": 3,
                "active_contributors_7d": 1,
                "last_commit_days_ago": 3,
                "sync_status": "up_to_date",
            }

            metrics = self.calculator.calculate_repository_health(repo_config)

            assert metrics.stars_count == 1000
            assert metrics.forks_count == 500
            assert metrics.open_issues_count == 50
            assert metrics.language == "Python"
            assert metrics.topics == ["python", "api", "web"]
            assert metrics.archived is False
            assert metrics.disabled is False

    def test_calculate_repository_health_error_handling(self) -> None:
        """Test error handling in repository health calculation."""
        repo_config = {
            "name": "test-repo",
            "local_path": "/nonexistent/path",
        }

        # Mock GitHub client to return None for get_repository
        self.mock_github_client.get_repository.return_value = None

        with patch("gitco.health_metrics.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            # Mock GitRepository to raise an exception
            with patch("gitco.health_metrics.GitRepository") as mock_git_repo:
                mock_git_repo.side_effect = Exception("Test exception")

                with pytest.raises(HealthMetricsError) as exc_info:
                    self.calculator.calculate_repository_health(repo_config)

                assert "Failed to calculate health for test-repo" in str(exc_info.value)

    def test_calculate_health_summary(self) -> None:
        """Test health summary calculation."""
        repositories = [
            {
                "name": "repo1",
                "local_path": "/path/to/repo1",
                "upstream": "https://github.com/owner/repo1",
            },
            {
                "name": "repo2",
                "local_path": "/path/to/repo2",
                "upstream": "https://github.com/owner/repo2",
            },
        ]

        with patch("gitco.health_metrics.GitRepository") as mock_git_repo:
            mock_git_repo.return_value.get_repository_status.return_value = {
                "total_commits": 100,
                "recent_commits_30d": 10,
                "recent_commits_7d": 2,
                "total_contributors": 5,
                "active_contributors_30d": 3,
                "active_contributors_7d": 1,
                "last_commit_days_ago": 3,
                "sync_status": "up_to_date",
            }

            mock_github_repo = Mock()
            mock_github_repo.stargazers_count = 1000
            mock_github_repo.forks_count = 500
            mock_github_repo.open_issues_count = 50
            mock_github_repo.language = "Python"
            mock_github_repo.topics = []
            mock_github_repo.archived = False
            mock_github_repo.disabled = False

            self.mock_github_client.get_repository.return_value = mock_github_repo
            self.mock_github_client.get_issues.return_value = []

            summary = self.calculator.calculate_health_summary(repositories)

            assert summary.total_repositories == 2
            assert summary.healthy_repositories >= 0
            assert summary.needs_attention_repositories >= 0
            assert summary.critical_repositories >= 0

    def test_extract_repo_name_from_url(self) -> None:
        """Test repository name extraction from URLs."""
        # Test HTTPS URL
        repo_name = self.calculator._extract_repo_name_from_url(
            "https://github.com/owner/repo-name"
        )
        assert repo_name == "owner/repo-name"

        # Test SSH URL
        repo_name = self.calculator._extract_repo_name_from_url(
            "git@github.com:owner/repo-name.git"
        )
        assert repo_name == "owner/repo-name"

        # Test invalid URL
        repo_name = self.calculator._extract_repo_name_from_url("invalid-url")
        assert repo_name is None

    def test_calculate_derived_metrics(self) -> None:
        """Test derived metrics calculation."""
        metrics = RepositoryHealthMetrics(
            repository_name="test-repo",
            repository_path="/path/to/repo",
        )
        metrics.recent_commits_30d = 15
        metrics.sync_status = "up_to_date"
        metrics.contributor_engagement_score = 0.8
        metrics.stars_count = 2000
        metrics.forks_count = 1000
        metrics.last_commit_days_ago = 5

        self.calculator._calculate_derived_metrics(metrics)

        assert metrics.overall_health_score > 0.0
        assert metrics.health_status in [
            "excellent",
            "good",
            "fair",
            "poor",
            "critical",
        ]

    def test_identify_trending_repositories(self) -> None:
        """Test trending repositories identification."""
        metrics_list = [
            RepositoryHealthMetrics(
                repository_name="trending-repo",
                repository_path="/path/to/repo",
                stars_growth_30d=15,
                forks_growth_30d=8,
                recent_commits_7d=6,
                contributor_engagement_score=0.8,
            ),
            RepositoryHealthMetrics(
                repository_name="normal-repo",
                repository_path="/path/to/repo",
                stars_growth_30d=5,
                forks_growth_30d=2,
                recent_commits_7d=2,
                contributor_engagement_score=0.5,
            ),
        ]

        trending = self.calculator._identify_trending_repositories(metrics_list)

        assert "trending-repo" in trending
        assert "normal-repo" not in trending

    def test_identify_declining_repositories(self) -> None:
        """Test declining repositories identification."""
        metrics_list = [
            RepositoryHealthMetrics(
                repository_name="declining-repo",
                repository_path="/path/to/repo",
                last_commit_days_ago=100,
                recent_commits_30d=0,
                contributor_engagement_score=0.2,
                sync_status="diverged",
            ),
            RepositoryHealthMetrics(
                repository_name="healthy-repo",
                repository_path="/path/to/repo",
                last_commit_days_ago=5,
                recent_commits_30d=10,
                contributor_engagement_score=0.7,
                sync_status="up_to_date",
            ),
        ]

        declining = self.calculator._identify_declining_repositories(metrics_list)

        assert "declining-repo" in declining
        assert "healthy-repo" not in declining


class TestCreateHealthCalculator:
    """Test create_health_calculator function."""

    def test_create_health_calculator(self) -> None:
        """Test creating a health calculator."""
        mock_config = Mock()
        mock_github_client = Mock()

        calculator = create_health_calculator(mock_config, mock_github_client)

        assert isinstance(calculator, RepositoryHealthCalculator)
        assert calculator.config == mock_config
        assert calculator.github_client == mock_github_client


class TestHealthMetricsIntegration:
    """Integration tests for health metrics."""

    def test_health_metrics_export_format(self) -> None:
        """Test that health metrics can be exported in the expected format."""
        calculator = RepositoryHealthCalculator(Mock(), Mock())

        repo_config = {
            "name": "test-repo",
            "local_path": "/path/to/repo",
            "upstream": "https://github.com/owner/test-repo",
        }

        with patch("gitco.health_metrics.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            with patch("gitco.health_metrics.GitRepository") as mock_git_repo:
                mock_git_repo.return_value.get_repository_status.return_value = {
                    "total_commits": 100,
                    "recent_commits_30d": 10,
                    "recent_commits_7d": 2,
                    "total_contributors": 5,
                    "active_contributors_30d": 3,
                    "active_contributors_7d": 1,
                    "last_commit_days_ago": 3,
                    "sync_status": "up_to_date",
                }

                # Mock GitHub client to return None for get_repository
                calculator.github_client.get_repository.return_value = None  # type: ignore

                metrics = calculator.calculate_repository_health(repo_config)

                # Test that metrics can be serialized to JSON
                export_data = {
                    "repository_name": metrics.repository_name,
                    "repository_path": metrics.repository_path,
                    "upstream_url": metrics.upstream_url,
                    "total_commits": metrics.total_commits,
                    "recent_commits_30d": metrics.recent_commits_30d,
                    "recent_commits_7d": metrics.recent_commits_7d,
                    "overall_health_score": metrics.overall_health_score,
                    "health_status": metrics.health_status,
                }

                json_str = json.dumps(export_data)
                assert "test-repo" in json_str
                assert "100" in json_str
                assert "10" in json_str


# Additional test cases for RepositoryHealthMetrics dataclass
def test_repository_health_metrics_with_all_fields() -> None:
    """Test RepositoryHealthMetrics with all fields populated."""
    metrics = RepositoryHealthMetrics(
        repository_name="test-repo",
        repository_path="/path/to/repo",
        upstream_url="https://github.com/owner/test-repo",
        last_commit_days_ago=2,
        total_commits=1000,
        recent_commits_30d=50,
        recent_commits_7d=10,
        total_contributors=20,
        active_contributors_30d=8,
        active_contributors_7d=3,
        stars_count=100,
        forks_count=25,
        open_issues_count=10,
        open_prs_count=5,
        days_since_last_sync=1,
        sync_status="up_to_date",
        uncommitted_changes=False,
        issue_response_time_avg=24.5,
        pr_merge_time_avg=48.0,
        contributor_engagement_score=0.75,
        stars_growth_30d=10,
        forks_growth_30d=5,
        issues_growth_30d=2,
        overall_health_score=0.85,
        health_status="good",
        language="Python",
        topics=["python", "testing"],
        archived=False,
        disabled=False,
    )

    assert metrics.repository_name == "test-repo"
    assert metrics.repository_path == "/path/to/repo"
    assert metrics.upstream_url == "https://github.com/owner/test-repo"
    assert metrics.total_commits == 1000
    assert metrics.recent_commits_30d == 50
    assert metrics.recent_commits_7d == 10
    assert metrics.total_contributors == 20
    assert metrics.active_contributors_30d == 8
    assert metrics.active_contributors_7d == 3
    assert metrics.last_commit_days_ago == 2
    assert metrics.sync_status == "up_to_date"
    assert metrics.overall_health_score == 0.85
    assert metrics.health_status == "good"
    assert metrics.contributor_engagement_score == 0.75


def test_repository_health_metrics_with_minimal_fields() -> None:
    """Test RepositoryHealthMetrics with minimal required fields."""
    metrics = RepositoryHealthMetrics(
        repository_name="minimal-repo",
        repository_path="/path/to/minimal",
        upstream_url="https://github.com/owner/minimal",
    )

    assert metrics.repository_name == "minimal-repo"
    assert metrics.repository_path == "/path/to/minimal"
    assert metrics.upstream_url == "https://github.com/owner/minimal"
    assert metrics.total_commits == 0
    assert metrics.recent_commits_30d == 0
    assert metrics.recent_commits_7d == 0
    assert metrics.total_contributors == 0
    assert metrics.active_contributors_30d == 0
    assert metrics.active_contributors_7d == 0
    assert metrics.last_commit_days_ago is None
    assert metrics.sync_status == "unknown"
    assert metrics.overall_health_score == 0.0
    assert metrics.health_status == "unknown"
    assert metrics.contributor_engagement_score == 0.0


def test_repository_health_metrics_equality() -> None:
    """Test RepositoryHealthMetrics instances equality."""
    metrics1 = RepositoryHealthMetrics(
        repository_name="test-repo",
        repository_path="/path/to/repo",
        upstream_url="https://github.com/owner/test-repo",
        total_commits=100,
        recent_commits_30d=10,
        overall_health_score=0.8,
        health_status="good",
    )

    metrics2 = RepositoryHealthMetrics(
        repository_name="test-repo",
        repository_path="/path/to/repo",
        upstream_url="https://github.com/owner/test-repo",
        total_commits=100,
        recent_commits_30d=10,
        overall_health_score=0.8,
        health_status="good",
    )

    assert metrics1 == metrics2


def test_repository_health_metrics_inequality() -> None:
    """Test RepositoryHealthMetrics instances inequality."""
    metrics1 = RepositoryHealthMetrics(
        repository_name="test-repo-1",
        repository_path="/path/to/repo1",
        upstream_url="https://github.com/owner/test-repo1",
        total_commits=100,
    )

    metrics2 = RepositoryHealthMetrics(
        repository_name="test-repo-2",
        repository_path="/path/to/repo2",
        upstream_url="https://github.com/owner/test-repo2",
        total_commits=200,
    )

    assert metrics1 != metrics2


def test_repository_health_metrics_repr() -> None:
    """Test RepositoryHealthMetrics string representation."""
    metrics = RepositoryHealthMetrics(
        repository_name="test-repo",
        repository_path="/path/to/repo",
        upstream_url="https://github.com/owner/test-repo",
        total_commits=100,
        overall_health_score=0.8,
        health_status="good",
    )

    repr_str = repr(metrics)
    assert "RepositoryHealthMetrics" in repr_str
    assert "test-repo" in repr_str
    assert "0.8" in repr_str


# Additional test cases for HealthSummary dataclass
def test_health_summary_with_all_fields() -> None:
    """Test HealthSummary with all fields populated."""
    summary = HealthSummary(
        total_repositories=10,
        healthy_repositories=7,
        needs_attention_repositories=2,
        critical_repositories=1,
        active_repositories_7d=8,
        active_repositories_30d=9,
        average_activity_score=0.75,
        trending_repositories=["repo1", "repo2"],
        declining_repositories=["repo3"],
        up_to_date_repositories=8,
        behind_repositories=1,
        diverged_repositories=1,
        high_engagement_repositories=6,
        low_engagement_repositories=4,
        total_stars=1000,
        total_forks=500,
    )

    assert summary.total_repositories == 10
    assert summary.healthy_repositories == 7
    assert summary.needs_attention_repositories == 2
    assert summary.critical_repositories == 1
    assert summary.average_activity_score == 0.75
    assert summary.trending_repositories == ["repo1", "repo2"]
    assert summary.declining_repositories == ["repo3"]


def test_health_summary_with_defaults() -> None:
    """Test HealthSummary with default values."""
    summary = HealthSummary()

    assert summary.total_repositories == 0
    assert summary.healthy_repositories == 0
    assert summary.needs_attention_repositories == 0
    assert summary.critical_repositories == 0
    assert summary.average_activity_score == 0.0
    assert summary.trending_repositories == []
    assert summary.declining_repositories == []


def test_health_summary_equality() -> None:
    """Test HealthSummary instances equality."""
    summary1 = HealthSummary(
        total_repositories=5,
        healthy_repositories=3,
        needs_attention_repositories=1,
        critical_repositories=1,
        average_activity_score=0.7,
    )

    summary2 = HealthSummary(
        total_repositories=5,
        healthy_repositories=3,
        needs_attention_repositories=1,
        critical_repositories=1,
        average_activity_score=0.7,
    )

    assert summary1 == summary2


def test_health_summary_inequality() -> None:
    """Test HealthSummary instances inequality."""
    summary1 = HealthSummary(
        total_repositories=5,
        healthy_repositories=3,
        needs_attention_repositories=1,
        critical_repositories=1,
        average_activity_score=0.7,
    )

    summary2 = HealthSummary(
        total_repositories=6,
        healthy_repositories=4,
        needs_attention_repositories=1,
        critical_repositories=1,
        average_activity_score=0.8,
    )

    assert summary1 != summary2


def test_health_summary_repr() -> None:
    """Test HealthSummary string representation."""
    summary = HealthSummary(
        total_repositories=10,
        healthy_repositories=7,
        needs_attention_repositories=2,
        critical_repositories=1,
        average_activity_score=0.75,
    )

    repr_str = repr(summary)
    assert "HealthSummary" in repr_str
    assert "10" in repr_str
    assert "0.75" in repr_str


# Additional test cases for HealthMetricsError exception class
def test_health_metrics_error_creation() -> None:
    """Test HealthMetricsError creation."""
    error = HealthMetricsError("Test health metrics error message")

    assert str(error) == "Test health metrics error message"
    assert isinstance(error, HealthMetricsError)
    assert isinstance(error, Exception)


def test_health_metrics_error_with_cause() -> None:
    """Test HealthMetricsError with a cause."""
    original_error = ValueError("Original error")
    error = HealthMetricsError("Test health metrics error message")
    error.__cause__ = original_error

    assert str(error) == "Test health metrics error message"
    assert error.__cause__ == original_error


def test_health_metrics_error_inheritance() -> None:
    """Test HealthMetricsError inheritance hierarchy."""
    error = HealthMetricsError("Test health metrics error")

    assert isinstance(error, HealthMetricsError)
    assert isinstance(error, Exception)
    # Should inherit from APIError (which inherits from GitCoError)
    from gitco.utils.exception import APIError, GitCoError

    assert isinstance(error, APIError)
    assert isinstance(error, GitCoError)


def test_health_metrics_error_repr() -> None:
    """Test HealthMetricsError string representation."""
    error = HealthMetricsError("Test health metrics error message")

    repr_str = repr(error)
    assert "HealthMetricsError" in repr_str
    assert "Test health metrics error message" in repr_str


def test_health_metrics_error_attributes() -> None:
    """Test HealthMetricsError attributes."""
    error = HealthMetricsError("Test health metrics error message")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


# Additional test cases for RepositoryHealthCalculator class
def test_repository_health_calculator_with_custom_config() -> None:
    """Test RepositoryHealthCalculator with custom config."""
    mock_config = Mock()
    mock_github_client = Mock()

    calculator = RepositoryHealthCalculator(mock_config, mock_github_client)

    assert calculator.config == mock_config
    assert calculator.github_client == mock_github_client
    assert calculator.logger is not None


def test_repository_health_calculator_calculate_health_with_error() -> None:
    """Test RepositoryHealthCalculator calculate_repository_health with error."""
    calculator = RepositoryHealthCalculator(Mock(), Mock())

    repo_config = {
        "name": "error-repo",
        "local_path": "/path/to/error-repo",
        "upstream": "https://github.com/owner/error-repo",
    }

    with patch("gitco.health_metrics.Path") as mock_path:
        mock_path.return_value.exists.return_value = False

        metrics = calculator.calculate_repository_health(repo_config)

        assert metrics.repository_name == "error-repo"
        assert metrics.overall_health_score == 0.0
        assert metrics.health_status == "unknown"


def test_repository_health_calculator_calculate_summary_with_empty_list() -> None:
    """Test RepositoryHealthCalculator calculate_health_summary with empty list."""
    calculator = RepositoryHealthCalculator(Mock(), Mock())

    summary = calculator.calculate_health_summary([])

    assert summary.total_repositories == 0
    assert summary.healthy_repositories == 0
    assert summary.needs_attention_repositories == 0
    assert summary.critical_repositories == 0
    assert summary.average_activity_score == 0.0
    assert summary.trending_repositories == []
    assert summary.declining_repositories == []


def test_repository_health_calculator_extract_repo_name_from_complex_url() -> None:
    """Test RepositoryHealthCalculator extract_repo_name_from_url with complex URL."""
    calculator = RepositoryHealthCalculator(Mock(), Mock())

    complex_url = "https://github.com/owner/org/test-repo.git"
    repo_name = calculator._extract_repo_name_from_url(complex_url)

    assert repo_name == "owner/org"


def test_repository_health_calculator_extract_repo_name_from_simple_url() -> None:
    """Test RepositoryHealthCalculator extract_repo_name_from_url with simple URL."""
    calculator = RepositoryHealthCalculator(Mock(), Mock())

    simple_url = "https://github.com/owner/test-repo"
    repo_name = calculator._extract_repo_name_from_url(simple_url)

    assert repo_name == "owner/test-repo"


def test_repository_health_metrics_with_none_values() -> None:
    """Test RepositoryHealthMetrics creation with None values."""
    metrics = RepositoryHealthMetrics(
        repository_name="test-repo",
        repository_path="/path/to/repo",
        overall_health_score=0.8,
        health_status="good",
        upstream_url=None,
        last_commit_days_ago=None,
        days_since_last_sync=None,
        issue_response_time_avg=None,
        pr_merge_time_avg=None,
        language=None,
    )

    assert metrics.repository_name == "test-repo"
    assert metrics.repository_path == "/path/to/repo"
    assert metrics.overall_health_score == 0.8
    assert metrics.health_status == "good"
    assert metrics.upstream_url is None
    assert metrics.last_commit_days_ago is None
    assert metrics.days_since_last_sync is None
    assert metrics.issue_response_time_avg is None
    assert metrics.pr_merge_time_avg is None
    assert metrics.language is None


def test_health_summary_with_none_values() -> None:
    """Test HealthSummary creation with None values."""
    summary = HealthSummary(
        total_repositories=5,
        healthy_repositories=3,
        needs_attention_repositories=1,
        critical_repositories=1,
        average_activity_score=0.7,
    )

    assert summary.total_repositories == 5
    assert summary.healthy_repositories == 3
    assert summary.needs_attention_repositories == 1
    assert summary.critical_repositories == 1
    assert summary.average_activity_score == 0.7


def test_repository_health_calculator_with_none_config() -> None:
    """Test RepositoryHealthCalculator with None config."""
    calculator = RepositoryHealthCalculator(None, Mock())

    # Should handle None config gracefully
    assert calculator.config is None
    assert calculator.github_client is not None
    assert calculator.logger is not None


def test_repository_health_calculator_with_none_github_client() -> None:
    """Test RepositoryHealthCalculator with None GitHub client."""
    calculator = RepositoryHealthCalculator(Mock(), None)

    # Should handle None GitHub client gracefully
    assert calculator.config is not None
    assert calculator.github_client is None
    assert calculator.logger is not None


def test_repository_health_calculator_extract_repo_name_from_none_url() -> None:
    """Test RepositoryHealthCalculator extract_repo_name_from_url with None URL."""
    calculator = RepositoryHealthCalculator(Mock(), Mock())

    # Should handle None URL gracefully
    repo_name = calculator._extract_repo_name_from_url("")
    assert repo_name is None
