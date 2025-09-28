"""Rate limiting utilities for GitCo API calls."""

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .common import get_logger
from .retry import DEFAULT_RETRY_CONFIG, with_retry


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    min_interval: float = 0.1  # Minimum time between requests in seconds
    retry_after_header: Optional[str] = None  # Header name for retry-after info


class RateLimiter:
    """Thread-safe rate limiter for API calls."""

    def __init__(self, config: Optional[RateLimitConfig]):
        """Initialize rate limiter.

        Args:
            config: Rate limiting configuration, or None for no rate limiting
        """
        self.config = config or RateLimitConfig()
        self.logger = get_logger()
        self._lock = threading.Lock()

        # Track request timestamps
        self._request_times: deque[float] = deque()
        self._last_request_time = 0.0

        # Track rate limit headers from responses
        self._rate_limit_remaining: Optional[int] = None
        self._rate_limit_reset: Optional[int] = None
        self._rate_limit_limit: Optional[int] = None

    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits."""
        with self._lock:
            current_time = time.time()

            # Check minimum interval
            if current_time - self._last_request_time < self.config.min_interval:
                sleep_time = self.config.min_interval - (
                    current_time - self._last_request_time
                )
                if sleep_time > 0:
                    self.logger.debug(
                        f"Rate limiting: waiting {sleep_time:.2f}s for minimum interval"
                    )
                    time.sleep(sleep_time)

            # Check per-minute limit
            self._cleanup_old_requests(current_time, 60)
            if len(self._request_times) >= self.config.requests_per_minute:
                oldest_request = self._request_times[0]
                wait_time = 60 - (current_time - oldest_request)
                if wait_time > 0:
                    self.logger.warning(
                        f"Rate limiting: waiting {wait_time:.2f}s for minute limit"
                    )
                    time.sleep(wait_time)

            # Check per-hour limit
            self._cleanup_old_requests(current_time, 3600)
            if len(self._request_times) >= self.config.requests_per_hour:
                oldest_request = self._request_times[0]
                wait_time = 3600 - (current_time - oldest_request)
                if wait_time > 0:
                    self.logger.warning(
                        f"Rate limiting: waiting {wait_time:.2f}s for hour limit"
                    )
                    time.sleep(wait_time)

            # Check burst limit
            recent_requests = sum(
                1 for req_time in self._request_times if current_time - req_time < 1.0
            )
            if recent_requests >= self.config.burst_limit:
                sleep_time = 1.0 - (current_time - self._request_times[-1])
                if sleep_time > 0:
                    self.logger.warning(
                        f"Rate limiting: waiting {sleep_time:.2f}s for burst limit"
                    )
                    time.sleep(sleep_time)

            # Update tracking
            self._request_times.append(current_time)
            self._last_request_time = current_time

    def _cleanup_old_requests(self, current_time: float, window_seconds: int) -> None:
        """Remove old request timestamps outside the window."""
        cutoff_time = current_time - window_seconds
        while self._request_times and self._request_times[0] < cutoff_time:
            self._request_times.popleft()

        # Also update last_request_time if it's too old
        if self._last_request_time < cutoff_time:
            self._last_request_time = 0.0

    def update_from_response_headers(
        self, headers: Optional[dict[str, Any]], provider: Optional[str] = None
    ) -> None:
        """Update rate limit info from response headers.

        Args:
            headers: Response headers from API call
            provider: API provider name (optional, for future use)
        """
        with self._lock:
            # Handle None headers gracefully
            if headers is None:
                return

            # Ensure headers is a dictionary-like object
            if not hasattr(headers, "get"):
                return

            # GitHub-style rate limit headers
            if "X-RateLimit-Remaining" in headers:
                self._rate_limit_remaining = int(
                    headers.get("X-RateLimit-Remaining", 0)
                )
                self._rate_limit_reset = int(headers.get("X-RateLimit-Reset", 0))
                self._rate_limit_limit = int(headers.get("X-RateLimit-Limit", 0))

            # OpenAI-style rate limit headers
            elif "x-ratelimit-remaining-requests" in headers:
                self._rate_limit_remaining = int(
                    headers.get("x-ratelimit-remaining-requests", 0)
                )
                reset_time = headers.get("x-ratelimit-reset-requests")
                if reset_time:
                    self._rate_limit_reset = int(reset_time)

    def handle_rate_limit_exceeded(self, headers: dict[str, Any]) -> None:
        """Handle rate limit exceeded by waiting for reset.

        Args:
            headers: Response headers containing rate limit info
        """
        with self._lock:
            current_time = time.time()

            # Try to get reset time from headers
            reset_time: Optional[float] = None

            # GitHub-style
            if "X-RateLimit-Reset" in headers:
                reset_time = int(headers.get("X-RateLimit-Reset", 0))

            # OpenAI-style
            elif "x-ratelimit-reset-requests" in headers:
                reset_time = int(headers.get("x-ratelimit-reset-requests", 0))

            # Generic retry-after header
            elif "Retry-After" in headers:
                retry_after = headers.get("Retry-After")
                if retry_after:
                    try:
                        reset_time = current_time + int(retry_after)
                    except ValueError:
                        pass

            if reset_time:
                wait_time = max(0, reset_time - current_time)
                if wait_time > 0:
                    self.logger.warning(
                        f"Rate limit exceeded. Waiting {wait_time:.2f}s for reset"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.warning("Rate limit exceeded but reset time has passed")
            else:
                # Fallback: wait 60 seconds
                self.logger.warning("Rate limit exceeded. Waiting 60s as fallback")
                time.sleep(60)

    def get_status(self) -> dict[str, Any]:
        """Get current rate limiter status.

        Returns:
            Dictionary with rate limiter status information
        """
        with self._lock:
            current_time = time.time()

            # Count recent requests
            requests_last_minute = sum(
                1 for req_time in self._request_times if current_time - req_time < 60
            )
            requests_last_hour = sum(
                1 for req_time in self._request_times if current_time - req_time < 3600
            )

            return {
                "requests_last_minute": requests_last_minute,
                "requests_last_hour": requests_last_hour,
                "total_requests_tracked": len(self._request_times),
                "rate_limit_remaining": self._rate_limit_remaining,
                "rate_limit_reset": self._rate_limit_reset,
                "rate_limit_limit": self._rate_limit_limit,
                "time_since_last_request": (
                    current_time - self._last_request_time
                    if self._last_request_time > 0
                    else None
                ),
            }


class RateLimitedAPIClient:
    """Base class for rate-limited API clients."""

    def __init__(self, rate_limiter: RateLimiter):
        """Initialize rate-limited API client.

        Args:
            rate_limiter: Rate limiter instance
        """
        self.rate_limiter = rate_limiter
        self.logger = get_logger()

    @with_retry(config=DEFAULT_RETRY_CONFIG)
    def make_rate_limited_request(
        self, request_func: Callable, *args: Any, **kwargs: Any
    ) -> Any:
        """Make a rate-limited API request.

        Args:
            request_func: Function that makes the actual API request
            *args: Arguments to pass to request_func
            **kwargs: Keyword arguments to pass to request_func

        Returns:
            Response from the API request

        Raises:
            Exception: If the request fails
        """
        # Wait for rate limiter
        self.rate_limiter.wait_if_needed()

        # Make the request
        response = request_func(*args, **kwargs)

        # Update rate limiter with response headers
        if hasattr(response, "headers") and response.headers is not None:
            try:
                self.rate_limiter.update_from_response_headers(response.headers)
            except (TypeError, AttributeError):
                # Handle cases where headers might be a Mock or not iterable
                pass

        return response

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error.

        Args:
            error: Exception to check

        Returns:
            True if the error is a rate limit error
        """
        error_str = str(error).lower()
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "quota exceeded",
            "rate exceeded",
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)


# Global rate limiters for different API providers
_rate_limiters: dict[str, RateLimiter] = {}


def get_rate_limiter(provider: str) -> RateLimiter:
    """Get or create a rate limiter for the specified provider.

    Args:
        provider: API provider name (e.g., 'github', 'openai')

    Returns:
        Rate limiter instance for the provider
    """
    if provider not in _rate_limiters:
        # Configure rate limits based on provider
        if provider == "github":
            config = RateLimitConfig(
                requests_per_minute=30,  # GitHub's authenticated rate limit
                requests_per_hour=5000,
                burst_limit=5,
                min_interval=0.1,
            )
        elif provider == "openai":
            config = RateLimitConfig(
                requests_per_minute=60,  # Conservative limit for LLM APIs
                requests_per_hour=1000,
                burst_limit=10,
                min_interval=0.2,
            )
        else:
            # Default configuration
            config = RateLimitConfig(
                requests_per_minute=60,
                requests_per_hour=1000,
                burst_limit=10,
                min_interval=0.1,
            )

        _rate_limiters[provider] = RateLimiter(config)

    return _rate_limiters[provider]


def get_rate_limiter_status(provider: Optional[str] = None) -> dict[str, Any]:
    """Get status of rate limiters.

    Args:
        provider: Specific provider to get status for, or None for all

    Returns:
        Dictionary with rate limiter status information
    """
    if provider:
        if provider in _rate_limiters:
            return {provider: _rate_limiters[provider].get_status()}
        return {}

    return {
        provider_name: limiter.get_status()
        for provider_name, limiter in _rate_limiters.items()
    }


def reset_rate_limiters() -> None:
    """Reset all rate limiters (useful for testing)."""
    global _rate_limiters
    _rate_limiters.clear()
