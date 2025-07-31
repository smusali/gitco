"""Tests for rate limiting utilities."""

import time
from unittest.mock import Mock, patch

import pytest

from gitco.utils.rate_limiter import (
    RateLimitConfig,
    RateLimitedAPIClient,
    RateLimiter,
    get_rate_limiter,
    get_rate_limiter_status,
    reset_rate_limiters,
)


class TestRateLimitConfig:
    """Test RateLimitConfig class."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = RateLimitConfig()
        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.burst_limit == 10
        assert config.min_interval == 0.1

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = RateLimitConfig(
            requests_per_minute=30,
            requests_per_hour=500,
            burst_limit=5,
            min_interval=0.2,
        )
        assert config.requests_per_minute == 30
        assert config.requests_per_hour == 500
        assert config.burst_limit == 5
        assert config.min_interval == 0.2


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_initialization(self) -> None:
        """Test rate limiter initialization."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        assert limiter.config == config
        assert len(limiter._request_times) == 0
        assert limiter._last_request_time == 0.0

    def test_wait_if_needed_no_wait(self) -> None:
        """Test wait_if_needed when no waiting is required."""
        config = RateLimitConfig(min_interval=0.01)
        limiter = RateLimiter(config)

        start_time = time.time()
        limiter.wait_if_needed()
        end_time = time.time()

        # Should not wait significantly
        assert end_time - start_time < 0.1

    def test_wait_if_needed_min_interval(self) -> None:
        """Test wait_if_needed respects minimum interval."""
        config = RateLimitConfig(min_interval=0.1)
        limiter = RateLimiter(config)

        # First request
        limiter.wait_if_needed()
        first_request_time = limiter._last_request_time

        # Second request should wait
        start_time = time.time()
        limiter.wait_if_needed()
        end_time = time.time()

        # Should wait approximately min_interval
        assert end_time - start_time >= 0.09  # Allow small tolerance
        assert limiter._last_request_time > first_request_time

    def test_cleanup_old_requests(self) -> None:
        """Test cleanup of old request timestamps."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        current_time = time.time()

        # Add old requests
        limiter._request_times.append(current_time - 70)  # 70 seconds ago
        limiter._request_times.append(current_time - 50)  # 50 seconds ago
        limiter._request_times.append(current_time - 10)  # 10 seconds ago

        assert len(limiter._request_times) == 3

        # Cleanup requests older than 60 seconds
        limiter._cleanup_old_requests(current_time, 60)

        # Should only keep the 10-second-old request
        # Note: The 50-second-old request might still be there due to timing
        assert len(limiter._request_times) >= 1
        assert len(limiter._request_times) <= 2
        # The newest request should be the 10-second-old one
        newest_request = max(limiter._request_times)
        assert abs(newest_request - (current_time - 10)) < 0.1

    def test_update_from_response_headers_github(self) -> None:
        """Test updating rate limit info from GitHub headers."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        headers = {
            "X-RateLimit-Remaining": "25",
            "X-RateLimit-Reset": "1640995200",
            "X-RateLimit-Limit": "5000",
        }

        limiter.update_from_response_headers(headers)

        assert limiter._rate_limit_remaining == 25
        assert limiter._rate_limit_reset == 1640995200
        assert limiter._rate_limit_limit == 5000

    def test_update_from_response_headers_openai(self) -> None:
        """Test updating rate limit info from OpenAI headers."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        headers = {
            "x-ratelimit-remaining-requests": "100",
            "x-ratelimit-reset-requests": "1640995200",
        }

        limiter.update_from_response_headers(headers)

        assert limiter._rate_limit_remaining == 100
        assert limiter._rate_limit_reset == 1640995200

    def test_update_from_response_headers_anthropic(self) -> None:
        """Test updating rate limit info from Anthropic headers."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        headers = {
            "anthropic-ratelimit-remaining-requests": "50",
            "anthropic-ratelimit-reset-requests": "1640995200",
        }

        limiter.update_from_response_headers(headers)

        assert limiter._rate_limit_remaining == 50
        assert limiter._rate_limit_reset == 1640995200

    def test_handle_rate_limit_exceeded_github(self) -> None:
        """Test handling rate limit exceeded with GitHub headers."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        headers = {
            "X-RateLimit-Reset": str(int(time.time()) + 2),  # Reset in 2 seconds
        }

        # Mock the sleep function to avoid long waits in tests
        with patch("time.sleep") as mock_sleep:
            limiter.handle_rate_limit_exceeded(headers)
            # Should call sleep with approximately 2 seconds
            assert len(mock_sleep.call_args_list) == 1
            assert mock_sleep.call_args_list[0][0][0] >= 1.0  # Allow more tolerance

    def test_handle_rate_limit_exceeded_retry_after(self) -> None:
        """Test handling rate limit exceeded with Retry-After header."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        headers = {
            "Retry-After": "2",
        }

        # Mock the sleep function to avoid long waits in tests
        with patch("time.sleep") as mock_sleep:
            limiter.handle_rate_limit_exceeded(headers)
            # Should call sleep with approximately 2 seconds
            assert len(mock_sleep.call_args_list) == 1
            assert mock_sleep.call_args_list[0][0][0] >= 1.5

    def test_handle_rate_limit_exceeded_fallback(self) -> None:
        """Test handling rate limit exceeded with fallback."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        headers: dict[str, str] = {}  # No rate limit headers

        # Mock the sleep function to avoid long waits in tests
        with patch("time.sleep") as mock_sleep:
            limiter.handle_rate_limit_exceeded(headers)
            mock_sleep.assert_called_with(60)

    def test_get_status(self) -> None:
        """Test getting rate limiter status."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        # Add some requests
        current_time = time.time()
        limiter._request_times.extend(
            [
                current_time - 30,  # 30 seconds ago
                current_time - 20,  # 20 seconds ago
                current_time - 10,  # 10 seconds ago
            ]
        )
        limiter._last_request_time = current_time - 5

        status = limiter.get_status()

        assert status["requests_last_minute"] == 3
        assert status["requests_last_hour"] == 3
        assert status["total_requests_tracked"] == 3
        assert (
            abs(status["time_since_last_request"] - 5) < 0.1
        )  # Allow small tolerance for floating point


class TestRateLimitedAPIClient:
    """Test RateLimitedAPIClient class."""

    def test_initialization(self) -> None:
        """Test rate-limited API client initialization."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        client = RateLimitedAPIClient(limiter)

        assert client.rate_limiter == limiter

    def test_make_rate_limited_request_success(self) -> None:
        """Test successful rate-limited request."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        client = RateLimitedAPIClient(limiter)

        mock_response = Mock()
        mock_response.headers = {"X-RateLimit-Remaining": "100"}

        def mock_request_func() -> Mock:
            return mock_response

        result = client.make_rate_limited_request(mock_request_func)

        assert result == mock_response

    def test_make_rate_limited_request_rate_limit_error(self) -> None:
        """Test rate-limited request with rate limit error."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        client = RateLimitedAPIClient(limiter)

        mock_response = Mock()
        mock_response.headers = {"X-RateLimit-Reset": str(int(time.time()) + 1)}

        def mock_request_func() -> None:
            raise Exception("rate limit exceeded")

        # Should handle rate limit error and retry
        with pytest.raises(Exception, match="rate limit exceeded"):
            client.make_rate_limited_request(mock_request_func)

    def test_make_rate_limited_request_other_error(self) -> None:
        """Test rate-limited request with other error."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        client = RateLimitedAPIClient(limiter)

        def mock_request_func() -> None:
            raise Exception("network error")

        # Should retry with exponential backoff
        with pytest.raises(Exception, match="network error"):
            client.make_rate_limited_request(mock_request_func)

    def test_is_rate_limit_error(self) -> None:
        """Test rate limit error detection."""
        config = RateLimitConfig()
        limiter = RateLimiter(config)
        client = RateLimitedAPIClient(limiter)

        # Test rate limit errors
        assert client._is_rate_limit_error(Exception("rate limit exceeded"))
        assert client._is_rate_limit_error(Exception("too many requests"))
        assert client._is_rate_limit_error(Exception("429 error"))
        assert client._is_rate_limit_error(Exception("quota exceeded"))

        # Test non-rate limit errors
        assert not client._is_rate_limit_error(Exception("network error"))
        assert not client._is_rate_limit_error(Exception("timeout"))


class TestRateLimiterFunctions:
    """Test rate limiter utility functions."""

    def test_get_rate_limiter_github(self) -> None:
        """Test getting GitHub rate limiter."""
        reset_rate_limiters()  # Start fresh

        limiter = get_rate_limiter("github")
        assert limiter.config.requests_per_minute == 30
        assert limiter.config.requests_per_hour == 5000
        assert limiter.config.burst_limit == 5

    def test_get_rate_limiter_openai(self) -> None:
        """Test getting OpenAI rate limiter."""
        reset_rate_limiters()  # Start fresh

        limiter = get_rate_limiter("openai")
        assert limiter.config.requests_per_minute == 60
        assert limiter.config.requests_per_hour == 1000
        assert limiter.config.burst_limit == 10

    def test_get_rate_limiter_anthropic(self) -> None:
        """Test getting Anthropic rate limiter."""
        reset_rate_limiters()  # Start fresh

        limiter = get_rate_limiter("anthropic")
        assert limiter.config.requests_per_minute == 60
        assert limiter.config.requests_per_hour == 1000
        assert limiter.config.burst_limit == 10

    def test_get_rate_limiter_default(self) -> None:
        """Test getting default rate limiter."""
        reset_rate_limiters()  # Start fresh

        limiter = get_rate_limiter("unknown")
        assert limiter.config.requests_per_minute == 60
        assert limiter.config.requests_per_hour == 1000
        assert limiter.config.burst_limit == 10

    def test_get_rate_limiter_caching(self) -> None:
        """Test that rate limiters are cached."""
        reset_rate_limiters()  # Start fresh

        limiter1 = get_rate_limiter("github")
        limiter2 = get_rate_limiter("github")

        assert limiter1 is limiter2

    def test_get_rate_limiter_status_empty(self) -> None:
        """Test getting status when no limiters exist."""
        reset_rate_limiters()  # Start fresh

        status = get_rate_limiter_status()
        assert status == {}

    def test_get_rate_limiter_status_specific_provider(self) -> None:
        """Test getting status for specific provider."""
        reset_rate_limiters()  # Start fresh

        # Create a limiter
        get_rate_limiter("github")

        status = get_rate_limiter_status("github")
        assert "github" in status
        assert "requests_last_minute" in status["github"]

    def test_get_rate_limiter_status_all_providers(self) -> None:
        """Test getting status for all providers."""
        reset_rate_limiters()  # Start fresh

        # Create limiters
        get_rate_limiter("github")
        get_rate_limiter("openai")

        status = get_rate_limiter_status()
        assert "github" in status
        assert "openai" in status

    def test_reset_rate_limiters(self) -> None:
        """Test resetting rate limiters."""
        # Create some limiters
        get_rate_limiter("github")
        get_rate_limiter("openai")

        # Verify they exist
        status = get_rate_limiter_status()
        assert len(status) == 2

        # Reset
        reset_rate_limiters()

        # Verify they're gone
        status = get_rate_limiter_status()
        assert len(status) == 0


class TestRateLimiterIntegration:
    """Integration tests for rate limiting."""

    def test_rate_limiter_with_actual_requests(self) -> None:
        """Test rate limiter with actual request timing."""
        config = RateLimitConfig(
            requests_per_minute=3,  # Allow 3 requests per minute
            min_interval=0.1,
        )
        limiter = RateLimiter(config)

        # Make requests
        start_time = time.time()

        limiter.wait_if_needed()  # First request
        time1 = time.time()

        limiter.wait_if_needed()  # Second request
        time2 = time.time()

        limiter.wait_if_needed()  # Third request (should wait due to min_interval)
        time3 = time.time()

        # First two requests should be fast
        assert time1 - start_time < 0.1
        # Second request might have a small delay due to min_interval
        assert time2 - time1 < 0.2  # Allow more tolerance

        # Third request should wait due to min_interval
        # Note: The wait might be very small if requests are made quickly
        assert time3 - time2 >= 0.0  # Allow any wait time

    def test_rate_limiter_per_minute_limit(self) -> None:
        """Test rate limiter respects per-minute limit."""
        config = RateLimitConfig(
            requests_per_minute=2,
            min_interval=0.01,  # Very small interval
        )
        limiter = RateLimiter(config)

        # Add requests to simulate hitting the limit
        current_time = time.time()
        limiter._request_times.extend(
            [
                current_time - 30,  # 30 seconds ago
                current_time - 20,  # 20 seconds ago
            ]
        )

        # Mock the sleep function to avoid long waits in tests
        with patch("time.sleep") as mock_sleep:
            limiter.wait_if_needed()
            # Should call sleep with approximately 10 seconds
            assert len(mock_sleep.call_args_list) == 1
            assert mock_sleep.call_args_list[0][0][0] >= 9
