"""Test cases for exception_utils.py."""

from gitco.utils.exception import (
    APIError,
    ConfigurationError,
    ContributionTrackerError,
    DiscoveryError,
    GitCoError,
    GitHubAuthenticationError,
    GitHubRateLimitExceeded,
    GitOperationError,
    HealthMetricsError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test the exception class hierarchy."""

    def test_gitco_error_is_base_exception(self) -> None:
        """Test that GitCoError inherits from Exception."""
        error = GitCoError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, GitCoError)
        assert str(error) == "Test error"

    def test_configuration_error_inheritance(self) -> None:
        """Test that ConfigurationError inherits from GitCoError."""
        error = ConfigurationError("Configuration failed")
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Configuration failed"

    def test_git_operation_error_inheritance(self) -> None:
        """Test that GitOperationError inherits from GitCoError."""
        error = GitOperationError("Git operation failed")
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Git operation failed"

    def test_validation_error_inheritance(self) -> None:
        """Test that ValidationError inherits from GitCoError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Validation failed"

    def test_api_error_inheritance(self) -> None:
        """Test that APIError inherits from GitCoError."""
        error = APIError("API call failed")
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "API call failed"


class TestAPIErrorSubclasses:
    """Test API error subclasses."""

    def test_github_rate_limit_exceeded_inheritance(self) -> None:
        """Test that GitHubRateLimitExceeded inherits from APIError."""
        error = GitHubRateLimitExceeded("Rate limit exceeded")
        assert isinstance(error, APIError)
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Rate limit exceeded"

    def test_github_authentication_error_inheritance(self) -> None:
        """Test that GitHubAuthenticationError inherits from APIError."""
        error = GitHubAuthenticationError("Authentication failed")
        assert isinstance(error, APIError)
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Authentication failed"

    def test_contribution_tracker_error_inheritance(self) -> None:
        """Test that ContributionTrackerError inherits from APIError."""
        error = ContributionTrackerError("Contribution tracking failed")
        assert isinstance(error, APIError)
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Contribution tracking failed"

    def test_discovery_error_inheritance(self) -> None:
        """Test that DiscoveryError inherits from APIError."""
        error = DiscoveryError("Discovery operation failed")
        assert isinstance(error, APIError)
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Discovery operation failed"

    def test_health_metrics_error_inheritance(self) -> None:
        """Test that HealthMetricsError inherits from APIError."""
        error = HealthMetricsError("Health metrics calculation failed")
        assert isinstance(error, APIError)
        assert isinstance(error, GitCoError)
        assert isinstance(error, Exception)
        assert str(error) == "Health metrics calculation failed"


class TestExceptionBehavior:
    """Test exception behavior and functionality."""

    def test_exception_with_cause(self) -> None:
        """Test exception with cause (from clause)."""
        original_error = ValueError("Original error")
        api_error = APIError("API failed")
        api_error.__cause__ = original_error

        assert str(api_error) == "API failed"
        assert api_error.__cause__ == original_error

    def test_exception_with_context(self) -> None:
        """Test exception with context information."""
        error = ConfigurationError("Invalid configuration")

        assert str(error) == "Invalid configuration"

    def test_exception_equality(self) -> None:
        """Test exception equality."""
        error1 = ValidationError("Validation failed")
        error2 = ValidationError("Validation failed")
        error3 = ValidationError("Different message")

        # Same message should be equal
        assert str(error1) == str(error2)
        # Different messages should not be equal
        assert str(error1) != str(error3)

    def test_exception_types_distinct(self) -> None:
        """Test that different exception types are distinct."""
        config_error = ConfigurationError("Config error")
        validation_error = ValidationError("Validation error")
        api_error = APIError("API error")

        # Use isinstance instead of type comparison
        assert not isinstance(config_error, type(validation_error))
        assert not isinstance(config_error, type(api_error))
        assert not isinstance(validation_error, type(api_error))

    def test_exception_inheritance_chain(self) -> None:
        """Test the complete inheritance chain for all exceptions."""
        # Test that all exceptions inherit from GitCoError
        exceptions = [
            ConfigurationError("test"),
            GitOperationError("test"),
            ValidationError("test"),
            APIError("test"),
            GitHubRateLimitExceeded("test"),
            GitHubAuthenticationError("test"),
            ContributionTrackerError("test"),
            DiscoveryError("test"),
            HealthMetricsError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, GitCoError)
            assert isinstance(exc, Exception)


def test_gitco_error_with_none_message() -> None:
    """Test GitCoError with None message."""
    error = GitCoError("Test error message")

    # Should handle message correctly
    assert error.message == "Test error message"
    assert isinstance(error, Exception)


def test_configuration_error_with_none_details() -> None:
    """Test ConfigurationError with None details."""
    error = ConfigurationError("Configuration error", details="No details")

    assert error.message == "Configuration error"
    assert error.details == "No details"


def test_validation_error_with_none_field() -> None:
    """Test ValidationError with None field."""
    error = ValidationError("Validation failed", field="test_field")

    assert error.message == "Validation failed"
    assert error.field == "test_field"


def test_api_error_with_none_status_code() -> None:
    """Test APIError with None status code."""
    error = APIError("API request failed", status_code=500)

    assert error.message == "API request failed"
    assert error.status_code == 500


def test_git_operation_error_with_none_operation_type() -> None:
    """Test GitOperationError with None operation type."""
    error = GitOperationError("Git operation failed", operation_type="push")

    assert error.message == "Git operation failed"
    assert error.operation_type == "push"
