"""Custom exception classes for GitCo."""


class GitCoError(Exception):
    """Base exception for GitCo errors."""

    pass


class ConfigurationError(GitCoError):
    """Raised when there's a configuration error."""

    pass


class GitOperationError(GitCoError):
    """Raised when a Git operation fails."""

    pass


class ValidationError(GitCoError):
    """Raised when validation fails."""

    pass


class APIError(GitCoError):
    """Raised when an API call fails."""

    pass


class NetworkTimeoutError(APIError):
    """Raised when a network operation times out."""

    def __init__(self, message: str, timeout_seconds: float, operation: str = ""):
        """Initialize network timeout error.

        Args:
            message: Error message
            timeout_seconds: Timeout duration in seconds
            operation: Name of the operation that timed out
        """
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        super().__init__(
            f"{message} (timeout: {timeout_seconds}s, operation: {operation})"
        )


class ConnectionTimeoutError(NetworkTimeoutError):
    """Raised when connection establishment times out."""

    pass


class ReadTimeoutError(NetworkTimeoutError):
    """Raised when reading from network connection times out."""

    pass


class RequestTimeoutError(NetworkTimeoutError):
    """Raised when HTTP request times out."""

    pass


class GitHubRateLimitExceeded(APIError):
    """Raised when GitHub API rate limit is exceeded."""

    pass


class GitHubAuthenticationError(APIError):
    """Raised when GitHub authentication fails."""

    pass


class ContributionTrackerError(APIError):
    """Raised when contribution tracking operations fail."""

    pass


class DiscoveryError(APIError):
    """Raised when discovery operations fail."""

    pass


class HealthMetricsError(APIError):
    """Raised when health metrics calculation fails."""

    pass


class ActivityDashboardError(APIError):
    """Raised when activity dashboard operations fail."""

    pass


class BackupError(GitCoError):
    """Raised when backup operations fail."""

    pass


class RecoveryError(GitCoError):
    """Raised when recovery operations fail."""

    pass


__all__ = [
    "GitCoError",
    "ConfigurationError",
    "GitOperationError",
    "ValidationError",
    "APIError",
    "NetworkTimeoutError",
    "ConnectionTimeoutError",
    "ReadTimeoutError",
    "RequestTimeoutError",
    "GitHubRateLimitExceeded",
    "GitHubAuthenticationError",
    "ContributionTrackerError",
    "DiscoveryError",
    "HealthMetricsError",
    "ActivityDashboardError",
    "BackupError",
    "RecoveryError",
]
