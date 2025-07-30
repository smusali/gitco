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
    "GitHubRateLimitExceeded",
    "GitHubAuthenticationError",
    "ContributionTrackerError",
    "DiscoveryError",
    "HealthMetricsError",
    "ActivityDashboardError",
    "BackupError",
    "RecoveryError",
]
