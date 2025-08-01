"""Custom exception classes for GitCo."""

from typing import Optional


class GitCoError(Exception):
    """Base exception for GitCo errors."""

    def __init__(self, message: Optional[str] = None):
        """Initialize GitCoError.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(message)


class ConfigurationError(GitCoError):
    """Raised when there's a configuration error."""

    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize ConfigurationError.

        Args:
            message: Error message
            details: Additional details about the configuration error
        """
        self.details = details
        super().__init__(message)


class GitOperationError(GitCoError):
    """Raised when a Git operation fails."""

    def __init__(self, message: str, operation_type: Optional[str] = None):
        """Initialize GitOperationError.

        Args:
            message: Error message
            operation_type: Type of Git operation that failed
        """
        self.operation_type = operation_type
        super().__init__(message)


class ValidationError(GitCoError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        """Initialize ValidationError.

        Args:
            message: Error message
            field: Field that failed validation
        """
        self.field = field
        super().__init__(message)


class APIError(GitCoError):
    """Raised when an API call fails."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize APIError.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.status_code = status_code
        super().__init__(message)


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
