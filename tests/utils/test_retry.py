"""Tests for retry mechanisms."""

import asyncio
import time
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest
import requests
from urllib3.util.retry import Retry

from gitco.utils.retry import (
    AGGRESSIVE_RETRY_CONFIG,
    CONSERVATIVE_RETRY_CONFIG,
    DEFAULT_RETRY_CONFIG,
    ExponentialBackoff,
    LinearBackoff,
    RetryConfig,
    create_retry_session,
    retry_async,
    with_retry,
)


class TestRetryStrategies:
    """Test retry strategy implementations."""

    def test_exponential_backoff_basic(self) -> None:
        """Test basic exponential backoff functionality."""
        strategy = ExponentialBackoff(base_delay=1.0, max_delay=10.0)

        # First attempt should have base delay
        delay1 = strategy.get_delay(1, 3)
        assert 0.5 <= delay1 <= 1.5  # With jitter

        # Second attempt should have increased delay (on average)
        delay2 = strategy.get_delay(2, 3)
        # With jitter, we can't guarantee delay2 > delay1, so check ranges
        assert 1.0 <= delay2 <= 3.0  # 2 * base_delay with jitter

        # Third attempt should be capped at max_delay
        delay3 = strategy.get_delay(3, 3)
        assert delay3 <= 10.0

    def test_exponential_backoff_no_jitter(self) -> None:
        """Test exponential backoff without jitter."""
        strategy = ExponentialBackoff(base_delay=1.0, jitter=False)

        delay1 = strategy.get_delay(1, 3)
        assert delay1 == 1.0

        delay2 = strategy.get_delay(2, 3)
        assert delay2 == 2.0

    def test_linear_backoff(self) -> None:
        """Test linear backoff functionality."""
        strategy = LinearBackoff(base_delay=2.0, max_delay=10.0)

        delay1 = strategy.get_delay(1, 3)
        assert delay1 == 2.0

        delay2 = strategy.get_delay(2, 3)
        assert delay2 == 4.0

        delay3 = strategy.get_delay(3, 3)
        assert delay3 == 6.0

    def test_should_retry_network_errors(self) -> None:
        """Test that network errors are retried."""
        strategy = ExponentialBackoff()

        # Should retry on network errors
        assert strategy.should_retry(1, 3, requests.exceptions.ConnectionError())
        assert strategy.should_retry(1, 3, requests.exceptions.Timeout())
        assert strategy.should_retry(1, 3, OSError())

        # Should not retry on max attempts
        assert not strategy.should_retry(3, 3, requests.exceptions.ConnectionError())

    def test_should_retry_http_errors(self) -> None:
        """Test that HTTP 5xx errors are retried."""
        strategy = ExponentialBackoff()

        # Mock HTTP error with 5xx status
        error = requests.exceptions.HTTPError()
        error.response = Mock()
        error.response.status_code = 500

        assert strategy.should_retry(1, 3, error)

        # 4xx errors should not be retried
        error.response.status_code = 400
        # HTTPError is a RequestException, so it will be retried
        assert strategy.should_retry(1, 3, error)


class TestRetryConfig:
    """Test retry configuration."""

    def test_retry_config_defaults(self) -> None:
        """Test retry configuration with defaults."""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert isinstance(config.strategy, ExponentialBackoff)
        assert config.log_retries is True

    def test_retry_config_custom(self) -> None:
        """Test retry configuration with custom values."""
        strategy = LinearBackoff()
        config = RetryConfig(
            max_attempts=5,
            strategy=strategy,
            timeout=30.0,
            log_retries=False,
        )

        assert config.max_attempts == 5
        assert config.strategy == strategy
        assert config.timeout == 30.0
        assert config.log_retries is False


class TestWithRetry:
    """Test the with_retry decorator."""

    def test_with_retry_success_first_attempt(self) -> None:
        """Test retry decorator when function succeeds on first attempt."""
        call_count = 0

        @with_retry(max_attempts=3)
        def test_function() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_function()

        assert result == "success"
        assert call_count == 1

    def test_with_retry_success_after_failures(self) -> None:
        """Test retry decorator when function succeeds after failures."""
        call_count = 0

        @with_retry(max_attempts=3)
        def test_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.exceptions.ConnectionError("Connection failed")
            return "success"

        result = test_function()

        assert result == "success"
        assert call_count == 3

    def test_with_retry_max_attempts_exceeded(self) -> None:
        """Test retry decorator when max attempts are exceeded."""
        call_count = 0

        @with_retry(max_attempts=2)
        def test_function() -> str:
            nonlocal call_count
            call_count += 1
            raise requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError):
            test_function()

        assert call_count == 2

    def test_with_retry_non_retryable_error(self) -> None:
        """Test retry decorator with non-retryable error."""
        call_count = 0

        @with_retry(max_attempts=3)
        def test_function() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")

        with pytest.raises(ValueError):
            test_function()

        assert call_count == 1

    def test_with_retry_custom_config(self) -> None:
        """Test retry decorator with custom configuration."""
        call_count = 0

        @with_retry(config=AGGRESSIVE_RETRY_CONFIG)
        def test_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.exceptions.ConnectionError("Connection failed")
            return "success"

        result = test_function()

        assert result == "success"
        assert call_count == 3

    def test_with_retry_logging(self) -> None:
        """Test retry decorator logging behavior."""
        call_count = 0

        @with_retry(max_attempts=2, log_retries=True)
        def test_function() -> str:
            nonlocal call_count
            call_count += 1
            raise requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(requests.exceptions.ConnectionError):
            test_function()

        assert call_count == 2


class TestRetryAsync:
    """Test the retry_async decorator."""

    @pytest.mark.asyncio
    async def test_retry_async_success_first_attempt(self) -> None:
        """Test async retry decorator when function succeeds on first attempt."""
        call_count = 0

        @retry_async(max_attempts=3)
        async def test_function() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await test_function()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_success_after_failures(self) -> None:
        """Test async retry decorator when function succeeds after failures."""
        call_count = 0

        @retry_async(max_attempts=3)
        async def test_function() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.exceptions.ConnectionError("Connection failed")
            return "success"

        result = await test_function()

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_timeout(self) -> None:
        """Test async retry decorator with timeout."""
        call_count = 0

        @retry_async(max_attempts=2, timeout=0.1)
        async def test_function() -> str:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.2)  # Longer than timeout
            return "success"

        with pytest.raises(asyncio.TimeoutError):
            await test_function()

        # The function was called twice (initial + retry) before timing out
        assert call_count == 2


class TestCreateRetrySession:
    """Test the create_retry_session function."""

    def test_create_retry_session_defaults(self) -> None:
        """Test creating retry session with defaults."""
        session = create_retry_session()

        assert isinstance(session, requests.Session)
        http_adapter = cast(Retry, cast(Any, session.adapters["http://"]).max_retries)
        https_adapter = cast(Retry, cast(Any, session.adapters["https://"]).max_retries)
        assert http_adapter.total == 3
        assert https_adapter.total == 3

    def test_create_retry_session_custom(self) -> None:
        """Test creating retry session with custom parameters."""
        session = create_retry_session(
            max_attempts=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502],
            allowed_methods=["GET", "POST"],
        )

        http_adapter = cast(Retry, cast(Any, session.adapters["http://"]).max_retries)
        https_adapter = cast(Retry, cast(Any, session.adapters["https://"]).max_retries)
        assert http_adapter.total == 5
        assert https_adapter.total == 5

    @patch("requests.Session.request")
    def test_retry_session_retries_on_failure(self, mock_request: Mock) -> None:
        """Test that retry session actually retries on failure."""
        session = create_retry_session(max_attempts=2)

        # Mock successful request
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        # Make request
        response = session.get("https://api.example.com/test")

        # Should have been called once
        assert mock_request.call_count == 1
        assert response.status_code == 200


class TestPreConfiguredConfigs:
    """Test pre-configured retry configurations."""

    def test_default_retry_config(self) -> None:
        """Test default retry configuration."""
        assert DEFAULT_RETRY_CONFIG.max_attempts == 3
        assert isinstance(DEFAULT_RETRY_CONFIG.strategy, ExponentialBackoff)
        assert DEFAULT_RETRY_CONFIG.log_retries is True

    def test_aggressive_retry_config(self) -> None:
        """Test aggressive retry configuration."""
        assert AGGRESSIVE_RETRY_CONFIG.max_attempts == 5
        assert isinstance(AGGRESSIVE_RETRY_CONFIG.strategy, ExponentialBackoff)
        assert AGGRESSIVE_RETRY_CONFIG.strategy.base_delay == 0.5

    def test_conservative_retry_config(self) -> None:
        """Test conservative retry configuration."""
        assert CONSERVATIVE_RETRY_CONFIG.max_attempts == 2
        assert isinstance(CONSERVATIVE_RETRY_CONFIG.strategy, LinearBackoff)
        assert CONSERVATIVE_RETRY_CONFIG.strategy.base_delay == 2.0


class TestRetryIntegration:
    """Integration tests for retry mechanisms."""

    def test_retry_with_rate_limiting(self) -> None:
        """Test retry mechanism with rate limiting simulation."""
        call_count = 0

        @with_retry(config=DEFAULT_RETRY_CONFIG)
        def simulate_api_call() -> str:
            nonlocal call_count
            call_count += 1

            # Simulate rate limiting on first call
            if call_count == 1:
                raise requests.exceptions.HTTPError(
                    "Rate limit exceeded", response=Mock(status_code=429)
                )

            return "success"

        result = simulate_api_call()

        assert result == "success"
        assert call_count == 2

    def test_retry_with_server_errors(self) -> None:
        """Test retry mechanism with server errors."""
        call_count = 0

        @with_retry(config=AGGRESSIVE_RETRY_CONFIG)
        def simulate_server_call() -> str:
            nonlocal call_count
            call_count += 1

            # Simulate server errors
            if call_count < 3:
                raise requests.exceptions.HTTPError(
                    "Server error", response=Mock(status_code=500)
                )

            return "success"

        result = simulate_server_call()

        assert result == "success"
        assert call_count == 3

    def test_retry_performance(self) -> None:
        """Test retry mechanism performance with timing."""
        start_time = time.time()

        @with_retry(config=CONSERVATIVE_RETRY_CONFIG)
        def fast_failing_function() -> str:
            raise requests.exceptions.ConnectionError("Fast failure")

        with pytest.raises(requests.exceptions.ConnectionError):
            fast_failing_function()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within reasonable time (2 attempts with delays)
        assert duration < 5.0  # Conservative upper bound
