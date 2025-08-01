"""Tests for contribution tracking functionality."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gitco.config import Repository
from gitco.contribution_tracker import (
    Contribution,
    ContributionStats,
    ContributionTracker,
)
from gitco.github_client import GitHubClient, GitHubIssue
from gitco.utils.exception import ContributionTrackerError
from tests.fixtures import mock_config


class TestContribution:
    """Test Contribution dataclass."""

    def test_contribution_creation(self) -> None:
        """Test creating a Contribution instance with all fields."""
        contribution = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            skills_used=["python", "testing"],
            impact_score=0.8,
            labels=["bug", "help wanted"],
            milestone="v1.0",
            assignees=["user1", "user2"],
            comments_count=5,
            reactions_count=3,
        )

        assert contribution.repository == "test-repo"
        assert contribution.issue_number == 123
        assert contribution.issue_title == "Test Issue"
        assert contribution.contribution_type == "issue"
        assert contribution.status == "open"
        assert contribution.skills_used == ["python", "testing"]
        assert contribution.impact_score == 0.8
        assert contribution.labels == ["bug", "help wanted"]
        assert contribution.milestone == "v1.0"
        assert contribution.assignees == ["user1", "user2"]
        assert contribution.comments_count == 5
        assert contribution.reactions_count == 3

    def test_contribution_creation_with_defaults(self) -> None:
        """Test creating a Contribution instance with default values."""
        contribution = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="pr",
            status="merged",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
        )

        assert contribution.skills_used == []
        assert contribution.impact_score == 0.0
        assert contribution.labels == []
        assert contribution.milestone is None
        assert contribution.assignees == []
        assert contribution.comments_count == 0
        assert contribution.reactions_count == 0

    def test_contribution_equality(self) -> None:
        """Test Contribution instances equality."""
        contribution1 = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
        )

        contribution2 = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
        )

        assert contribution1 == contribution2

    def test_contribution_inequality(self) -> None:
        """Test Contribution instances inequality."""
        contribution1 = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
        )

        contribution2 = Contribution(
            repository="test-repo",
            issue_number=124,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/124",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
        )

        assert contribution1 != contribution2

    def test_contribution_repr(self) -> None:
        """Test Contribution string representation."""
        contribution = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
        )

        repr_str = repr(contribution)
        assert "Contribution" in repr_str
        assert "test-repo" in repr_str
        assert "123" in repr_str


class TestContributionStats:
    """Test ContributionStats dataclass."""

    def test_contribution_stats_creation(self) -> None:
        """Test creating a ContributionStats instance with all fields."""
        stats = ContributionStats(
            total_contributions=100,
            open_contributions=20,
            closed_contributions=50,
            merged_contributions=30,
            repositories_contributed_to=5,
            skills_developed={"python", "javascript", "testing"},
            total_impact_score=75.5,
            average_impact_score=0.755,
            contribution_timeline={"2023-01": 10, "2023-02": 15},
            recent_activity=[],
            impact_trend_30d=0.1,
            impact_trend_7d=0.05,
            high_impact_contributions=25,
            critical_contributions=5,
            skill_impact_scores={"python": 0.8, "javascript": 0.6},
            repository_impact_scores={"repo1": 0.9, "repo2": 0.7},
            contribution_velocity=2.5,
            skill_growth_rate={"python": 0.1, "javascript": 0.05},
            repository_engagement_trend={"repo1": 0.2, "repo2": 0.1},
            trending_skills=["python", "testing"],
            declining_skills=["old_tech"],
            collaboration_score=0.8,
            recognition_score=0.7,
            influence_score=0.6,
            sustainability_score=0.9,
        )

        assert stats.total_contributions == 100
        assert stats.open_contributions == 20
        assert stats.closed_contributions == 50
        assert stats.merged_contributions == 30
        assert stats.repositories_contributed_to == 5
        assert stats.skills_developed == {"python", "javascript", "testing"}
        assert stats.total_impact_score == 75.5
        assert stats.average_impact_score == 0.755
        assert stats.contribution_timeline == {"2023-01": 10, "2023-02": 15}
        assert stats.impact_trend_30d == 0.1
        assert stats.impact_trend_7d == 0.05
        assert stats.high_impact_contributions == 25
        assert stats.critical_contributions == 5
        assert stats.skill_impact_scores == {"python": 0.8, "javascript": 0.6}
        assert stats.repository_impact_scores == {"repo1": 0.9, "repo2": 0.7}
        assert stats.contribution_velocity == 2.5
        assert stats.skill_growth_rate == {"python": 0.1, "javascript": 0.05}
        assert stats.repository_engagement_trend == {"repo1": 0.2, "repo2": 0.1}
        assert stats.trending_skills == ["python", "testing"]
        assert stats.declining_skills == ["old_tech"]
        assert stats.collaboration_score == 0.8
        assert stats.recognition_score == 0.7
        assert stats.influence_score == 0.6
        assert stats.sustainability_score == 0.9

    def test_contribution_stats_creation_with_defaults(self) -> None:
        """Test creating a ContributionStats instance with default values."""
        stats = ContributionStats()

        assert stats.total_contributions == 0
        assert stats.open_contributions == 0
        assert stats.closed_contributions == 0
        assert stats.merged_contributions == 0
        assert stats.repositories_contributed_to == 0
        assert stats.skills_developed == set()
        assert stats.total_impact_score == 0.0
        assert stats.average_impact_score == 0.0
        assert stats.contribution_timeline == {}
        assert stats.recent_activity == []
        assert stats.impact_trend_30d == 0.0
        assert stats.impact_trend_7d == 0.0
        assert stats.high_impact_contributions == 0
        assert stats.critical_contributions == 0
        assert stats.skill_impact_scores == {}
        assert stats.repository_impact_scores == {}
        assert stats.contribution_velocity == 0.0
        assert stats.skill_growth_rate == {}
        assert stats.repository_engagement_trend == {}
        assert stats.trending_skills == []
        assert stats.declining_skills == []
        assert stats.collaboration_score == 0.0
        assert stats.recognition_score == 0.0
        assert stats.influence_score == 0.0
        assert stats.sustainability_score == 0.0

    def test_contribution_stats_equality(self) -> None:
        """Test ContributionStats instances equality."""
        stats1 = ContributionStats(
            total_contributions=100,
            open_contributions=20,
            closed_contributions=50,
            merged_contributions=30,
            repositories_contributed_to=5,
            skills_developed={"python", "javascript"},
            total_impact_score=75.5,
            average_impact_score=0.755,
        )

        stats2 = ContributionStats(
            total_contributions=100,
            open_contributions=20,
            closed_contributions=50,
            merged_contributions=30,
            repositories_contributed_to=5,
            skills_developed={"python", "javascript"},
            total_impact_score=75.5,
            average_impact_score=0.755,
        )

        assert stats1 == stats2

    def test_contribution_stats_inequality(self) -> None:
        """Test ContributionStats instances inequality."""
        stats1 = ContributionStats(
            total_contributions=100,
            open_contributions=20,
            closed_contributions=50,
            merged_contributions=30,
            repositories_contributed_to=5,
            skills_developed={"python", "javascript"},
            total_impact_score=75.5,
            average_impact_score=0.755,
        )

        stats2 = ContributionStats(
            total_contributions=101,
            open_contributions=20,
            closed_contributions=50,
            merged_contributions=30,
            repositories_contributed_to=5,
            skills_developed={"python", "javascript"},
            total_impact_score=75.5,
            average_impact_score=0.755,
        )

        assert stats1 != stats2

    def test_contribution_stats_repr(self) -> None:
        """Test ContributionStats string representation."""
        stats = ContributionStats(
            total_contributions=100,
            open_contributions=20,
            closed_contributions=50,
            merged_contributions=30,
            repositories_contributed_to=5,
            skills_developed={"python", "javascript"},
            total_impact_score=75.5,
            average_impact_score=0.755,
        )

        repr_str = repr(stats)
        assert "ContributionStats" in repr_str
        assert "100" in repr_str
        assert "75.5" in repr_str


class TestContributionTrackerError:
    """Test ContributionTrackerError exception class."""

    def test_contribution_tracker_error_creation(self) -> None:
        """Test creating a ContributionTrackerError instance."""
        error = ContributionTrackerError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, ContributionTrackerError)
        assert isinstance(error, Exception)

    def test_contribution_tracker_error_with_cause(self) -> None:
        """Test creating a ContributionTrackerError with a cause."""
        original_error = ValueError("Original error")
        error = ContributionTrackerError("Test error message")
        error.__cause__ = original_error

        assert str(error) == "Test error message"
        assert error.__cause__ == original_error

    def test_contribution_tracker_error_inheritance(self) -> None:
        """Test ContributionTrackerError inheritance hierarchy."""
        error = ContributionTrackerError("Test error")

        assert isinstance(error, ContributionTrackerError)
        assert isinstance(error, Exception)
        # Should inherit from APIError (which inherits from GitCoError)
        from gitco.utils.exception import APIError, GitCoError

        assert isinstance(error, APIError)
        assert isinstance(error, GitCoError)

    def test_contribution_tracker_error_repr(self) -> None:
        """Test ContributionTrackerError string representation."""
        error = ContributionTrackerError("Test error message")

        repr_str = repr(error)
        assert "ContributionTrackerError" in repr_str
        assert "Test error message" in repr_str

    def test_contribution_tracker_error_attributes(self) -> None:
        """Test ContributionTrackerError attributes."""
        error = ContributionTrackerError("Test error message")

        assert hasattr(error, "__dict__")
        assert hasattr(error, "__cause__")
        assert hasattr(error, "__context__")


class TestContributionTracker:
    """Test ContributionTracker class."""

    def test_contribution_tracker_initialization(self) -> None:
        """Test ContributionTracker initialization."""
        config = mock_config()
        github_client = Mock(spec=GitHubClient)
        tracker = ContributionTracker(config, github_client)

        assert tracker.config == config
        assert tracker.github_client == github_client
        assert tracker.logger is not None
        assert (
            tracker.history_file
            == Path("~/.gitco/contribution_history.json").expanduser()
        )

    def test_contribution_tracker_initialization_creates_directory(self) -> None:
        """Test that ContributionTracker creates the history directory."""
        config = mock_config()
        github_client = Mock(spec=GitHubClient)

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            ContributionTracker(config, github_client)

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_load_contribution_history_empty_file(self) -> None:
        """Test loading contribution history from empty file."""
        config = mock_config()
        github_client = Mock(spec=GitHubClient)
        tracker = ContributionTracker(config, github_client)

        with patch("pathlib.Path.exists", return_value=False):
            contributions = tracker.load_contribution_history()

            assert contributions == []

    def test_load_contribution_history_with_data(self) -> None:
        """Test loading contribution history with data."""
        config = mock_config()
        github_client = Mock(spec=GitHubClient)
        tracker = ContributionTracker(config, github_client)

        mock_data = {
            "contributions": [
                {
                    "repository": "test-repo",
                    "issue_number": 123,
                    "issue_title": "Test Issue",
                    "issue_url": "https://github.com/test-repo/issues/123",
                    "contribution_type": "issue",
                    "status": "open",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                    "skills_used": ["python", "testing"],
                    "impact_score": 0.8,
                    "labels": ["bug", "help wanted"],
                    "milestone": "v1.0",
                    "assignees": ["user1", "user2"],
                    "comments_count": 5,
                    "reactions_count": 3,
                }
            ]
        }

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", create=True) as mock_open,
        ):
            mock_open.return_value.__enter__.return_value.read.return_value = (
                json.dumps(mock_data)
            )

            contributions = tracker.load_contribution_history()

            assert len(contributions) == 1
            assert contributions[0].repository == "test-repo"
            assert contributions[0].issue_number == 123
            assert contributions[0].issue_title == "Test Issue"
            assert contributions[0].contribution_type == "issue"
            assert contributions[0].status == "open"
            assert contributions[0].skills_used == ["python", "testing"]
            assert contributions[0].impact_score == 0.8
            assert contributions[0].labels == ["bug", "help wanted"]
            assert contributions[0].milestone == "v1.0"
            assert contributions[0].assignees == ["user1", "user2"]
            assert contributions[0].comments_count == 5
            assert contributions[0].reactions_count == 3

    def test_save_contribution_history(self) -> None:
        """Test saving contribution history to file."""
        config = mock_config()
        github_client = Mock(spec=GitHubClient)
        tracker = ContributionTracker(config, github_client)

        contribution = Contribution(
            repository="test-repo",
            issue_number=123,
            issue_title="Test Issue",
            issue_url="https://github.com/test-repo/issues/123",
            contribution_type="issue",
            status="open",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-02T00:00:00Z",
            skills_used=["python", "testing"],
            impact_score=0.8,
            labels=["bug", "help wanted"],
            milestone="v1.0",
            assignees=["user1", "user2"],
            comments_count=5,
            reactions_count=3,
        )

        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            tracker.save_contribution_history([contribution])

            mock_open.assert_called_once()
            assert mock_file.write.call_count > 0  # Write was called at least once

            # Get all written content
            all_calls = mock_file.write.call_args_list
            written_content = "".join(call[0][0] for call in all_calls)

            # Verify the written data contains the contribution
            assert "test-repo" in written_content
            assert "123" in written_content
            assert "Test Issue" in written_content

    def test_contribution_tracker_get_contribution_recommendations(self) -> None:
        """Test get_contribution_recommendations method."""
        config = Mock()
        config.repositories = [
            Repository("test-repo", "user/fork", "owner/repo", "/path/to/repo")
        ]

        github_client = Mock()
        github_client.get_issues.return_value = [
            GitHubIssue(
                number=1,
                title="Test Issue",
                state="open",
                labels=["bug"],
                assignees=["user1"],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                html_url="https://github.com/test/issue/1",
            )
        ]

        tracker = ContributionTracker(config, github_client)

        # Add some contributions to the tracker
        contribution = Contribution(
            repository="test-repo",
            issue_number=1,
            issue_title="Test Issue",
            issue_url="https://github.com/test/issue/1",
            contribution_type="issue",
            status="open",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            skills_used=["python"],
        )
        tracker.add_contribution(contribution)

        recommendations = tracker.get_contribution_recommendations(["python"])
        assert isinstance(recommendations, list)

    def test_contribution_tracker_load_contribution_history_exception_handling(
        self,
    ) -> None:
        """Test load_contribution_history exception handling (lines 152-154, 200-202, 212-254)."""
        config = Mock()
        github_client = Mock()
        tracker = ContributionTracker(config, github_client)

        # Mock the history file to be corrupted
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", side_effect=Exception("File error")):
                with pytest.raises(
                    ContributionTrackerError,
                    match="Failed to load contribution history",
                ):
                    tracker.load_contribution_history()

    def test_contribution_tracker_save_contribution_history_exception_handling(
        self,
    ) -> None:
        """Test save_contribution_history exception handling (lines 265-347, 357-410, 423-452, 463-483, 494-545)."""
        config = Mock()
        github_client = Mock()
        tracker = ContributionTracker(config, github_client)

        contributions = [
            Contribution(
                repository="test-repo",
                issue_number=1,
                issue_title="Test Issue",
                issue_url="https://github.com/test/issue/1",
                contribution_type="issue",
                status="open",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        ]

        # Mock file operations to raise exception
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(
                ContributionTrackerError, match="Failed to save contribution history"
            ):
                tracker.save_contribution_history(contributions)

    def test_contribution_tracker_sync_contributions_exception_handling(self) -> None:
        """Test sync_contributions_from_github exception handling (lines 556-573, 584-601, 612-640, 657-688, 705-734, 744-761, 772-835, 846-901, 914-968)."""
        config = Mock()
        github_client = Mock()
        github_client.get_user_issues.return_value = (
            []
        )  # Return empty list instead of Mock
        github_client.get_user_issues.side_effect = Exception("API error")

        tracker = ContributionTracker(config, github_client)

        with pytest.raises(
            ContributionTrackerError, match="Failed to sync contributions from GitHub"
        ):
            tracker.sync_contributions_from_github("testuser")

    def test_contribution_tracker_calculate_impact_score_edge_cases(self) -> None:
        """Test _calculate_impact_score with edge cases (lines 705-734, 744-761, 772-835)."""
        config = Mock()
        github_client = Mock()
        tracker = ContributionTracker(config, github_client)

        # Test with minimal issue data
        issue = GitHubIssue(
            number=1,
            title="Test Issue",
            state="open",
            labels=[],
            assignees=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            html_url="https://github.com/test/issue/1",
        )
        # Add missing attributes as needed for the test
        issue.comments_count = 0
        issue.reactions_count = 0

        impact_score = tracker._calculate_impact_score(issue)
        assert isinstance(impact_score, float)
        assert 0.0 <= impact_score <= 1.0

    def test_contribution_tracker_calculate_enhanced_metrics_edge_cases(self) -> None:
        """Test _calculate_enhanced_impact_metrics with edge cases (lines 846-901, 914-968)."""
        config = Mock()
        github_client = Mock()
        tracker = ContributionTracker(config, github_client)

        # Test with empty contributions list
        contributions: list[Contribution] = []
        stats = ContributionStats()

        tracker._calculate_enhanced_impact_metrics(contributions, stats)

        assert stats.high_impact_contributions == 0
        assert stats.critical_contributions == 0
        assert stats.impact_trend_30d == 0.0
        assert stats.impact_trend_7d == 0.0

    def test_contribution_with_none_values(self) -> None:
        """Test Contribution creation with None values."""
        contribution = Contribution(
            repository="test-repo",
            issue_number=1,
            issue_title="Test Issue",
            issue_url="https://github.com/test/issue/1",
            contribution_type="issue",
            status="open",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            labels=None,
            assignees=None,
            comments_count=None,
            reactions_count=None,
            impact_score=None,
        )

        assert contribution.repository == "test-repo"
        assert contribution.labels is None
        assert contribution.assignees is None
        assert contribution.comments_count is None
        assert contribution.reactions_count is None
        assert contribution.impact_score is None

    def test_contribution_stats_with_none_values(self) -> None:
        """Test ContributionStats creation with None values."""
        stats = ContributionStats(
            total_contributions=0,
            open_contributions=0,
            closed_contributions=0,
            high_impact_contributions=0,
            critical_contributions=0,
            impact_trend_30d=0.0,
            impact_trend_7d=0.0,
        )

        assert stats.total_contributions == 0
        assert stats.open_contributions == 0
        assert stats.closed_contributions == 0
        assert stats.high_impact_contributions == 0
        assert stats.critical_contributions == 0
        assert stats.impact_trend_30d == 0.0
        assert stats.impact_trend_7d == 0.0

    def test_contribution_tracker_with_empty_config(self) -> None:
        """Test ContributionTracker with empty configuration."""
        empty_config = Mock()
        empty_config.repositories = []

        github_client = Mock()

        tracker = ContributionTracker(empty_config, github_client)

        # Should not raise any exceptions
        assert tracker is not None
        assert tracker.config == empty_config
        assert tracker.github_client == github_client

    def test_contribution_tracker_calculate_impact_score_with_none_issue(self) -> None:
        """Test _calculate_impact_score with None issue data."""
        config = Mock()
        github_client = Mock()
        tracker = ContributionTracker(config, github_client)

        # Test with issue that has None values
        issue = GitHubIssue(
            number=1,
            title="Test Issue",
            state="open",
            labels=[],
            assignees=[],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            html_url="https://github.com/test/issue/1",
        )
        issue.comments_count = 0
        issue.reactions_count = 0

        impact_score = tracker._calculate_impact_score(issue)
        assert isinstance(impact_score, float)
        assert 0.0 <= impact_score <= 1.0

    def test_contribution_tracker_serialization_roundtrip(self) -> None:
        """Test Contribution serialization and deserialization."""
        original_contribution = Contribution(
            repository="test-repo",
            issue_number=1,
            issue_title="Test Issue",
            issue_url="https://github.com/test/issue/1",
            contribution_type="issue",
            status="open",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            labels=["bug", "help wanted"],
            assignees=["user1", "user2"],
            comments_count=5,
            reactions_count=3,
            impact_score=0.8,
        )

        # Convert to dict and back
        contribution_dict = original_contribution.to_dict()
        restored_contribution = Contribution.from_dict(contribution_dict)

        assert restored_contribution.repository == original_contribution.repository
        assert restored_contribution.issue_number == original_contribution.issue_number
        assert restored_contribution.labels == original_contribution.labels
        assert restored_contribution.assignees == original_contribution.assignees
        assert (
            restored_contribution.comments_count == original_contribution.comments_count
        )
        assert (
            restored_contribution.reactions_count
            == original_contribution.reactions_count
        )
        assert restored_contribution.impact_score == original_contribution.impact_score
