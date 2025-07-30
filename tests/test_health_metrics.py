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
