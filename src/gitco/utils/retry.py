"""Retry mechanisms for network operations."""

import asyncio
import functools
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TypeVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .common import get_logger

T = TypeVar("T")


class RetryStrategy(ABC):
    """Abstract base class for retry strategies."""

    @abstractmethod
    def get_delay(self, attempt: int, max_attempts: int) -> float:
        """Get delay for the current attempt.

        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts

        Returns:
            Delay in seconds
        """
        pass

    @abstractmethod
    def should_retry(
        self, attempt: int, max_attempts: int, exception: Exception
    ) -> bool:
        """Determine if the operation should be retried.

        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts
            exception: The exception that occurred

        Returns:
            True if the operation should be retried
        """
        pass


class ExponentialBackoff(RetryStrategy):
    """Exponential backoff retry strategy."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize exponential backoff strategy.

        Args:
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            multiplier: Multiplier for exponential increase
            jitter: Whether to add random jitter to delays
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter

    def get_delay(self, attempt: int, max_attempts: int) -> float:
        """Get delay for the current attempt.

        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts

        Returns:
            Delay in seconds
        """
        delay = min(
            self.base_delay * (self.multiplier ** (attempt - 1)), self.max_delay
        )

        if self.jitter:
            # Add jitter to prevent thundering herd
            jitter_factor = random.uniform(0.5, 1.5)
            delay *= jitter_factor

        return delay

    def should_retry(
        self, attempt: int, max_attempts: int, exception: Exception
    ) -> bool:
        """Determine if the operation should be retried.

        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts
            exception: The exception that occurred

        Returns:
            True if the operation should be retried
        """
        if attempt >= max_attempts:
            return False

        # Retry on network-related exceptions
        if isinstance(
            exception,
            (
                requests.exceptions.RequestException,
                OSError,
                ConnectionError,
                TimeoutError,
            ),
        ):
            return True

        # Retry on HTTP 5xx errors
        if isinstance(exception, requests.exceptions.HTTPError):
            response = getattr(exception, "response", None)
            if response and 500 <= response.status_code < 600:
                return True

        return False


class LinearBackoff(RetryStrategy):
    """Linear backoff retry strategy."""

    def __init__(self, base_delay: float = 1.0, max_delay: float = 30.0):
        """Initialize linear backoff strategy.

        Args:
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.base_delay = base_delay
        self.max_delay = max_delay

    def get_delay(self, attempt: int, max_attempts: int) -> float:
        """Get delay for the current attempt.

        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts

        Returns:
            Delay in seconds
        """
        return min(self.base_delay * attempt, self.max_delay)

    def should_retry(
        self, attempt: int, max_attempts: int, exception: Exception
    ) -> bool:
        """Determine if the operation should be retried.

        Args:
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts
            exception: The exception that occurred

        Returns:
            True if the operation should be retried
        """
        if attempt >= max_attempts:
            return False

        # Retry on network-related exceptions
        if isinstance(
            exception,
            (
                requests.exceptions.RequestException,
                OSError,
                ConnectionError,
                TimeoutError,
            ),
        ):
            return True

        # Retry on HTTP 5xx errors
        if isinstance(exception, requests.exceptions.HTTPError):
            response = getattr(exception, "response", None)
            if response and 500 <= response.status_code < 600:
                return True

        return False


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        strategy: Optional[RetryStrategy] = None,
        retry_on_exceptions: Optional[tuple[type[Exception], ...]] = None,
        timeout: Optional[float] = None,
        log_retries: bool = True,
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            strategy: Retry strategy to use
            retry_on_exceptions: Specific exceptions to retry on
            timeout: Timeout for each attempt
            log_retries: Whether to log retry attempts
        """
        self.max_attempts = max_attempts
        self.strategy = strategy or ExponentialBackoff()
        self.retry_on_exceptions = retry_on_exceptions or (
            requests.exceptions.RequestException,
            OSError,
            ConnectionError,
            TimeoutError,
        )
        self.timeout = timeout
        self.log_retries = log_retries


def with_retry(
    config: Optional[RetryConfig] = None,
    max_attempts: int = 3,
    strategy: Optional[RetryStrategy] = None,
    timeout: Optional[float] = None,
    log_retries: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add retry functionality to a function.

    Args:
        config: Retry configuration
        max_attempts: Maximum number of retry attempts
        strategy: Retry strategy to use
        timeout: Timeout for each attempt
        log_retries: Whether to log retry attempts

    Returns:
        Decorated function with retry functionality
    """
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            strategy=strategy,
            timeout=timeout,
            log_retries=log_retries,
        )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            logger = get_logger()
            last_exception: Optional[Exception] = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    if config.timeout:
                        # For timeout support, we'd need to implement it per function
                        # This is a simplified version
                        return func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if not config.strategy.should_retry(
                        attempt, config.max_attempts, e
                    ):
                        raise

                    # Calculate delay
                    delay = config.strategy.get_delay(attempt, config.max_attempts)

                    if config.log_retries:
                        logger.warning(
                            f"Attempt {attempt}/{config.max_attempts} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                    # Wait before retry
                    time.sleep(delay)

            # If we get here, all attempts failed
            if last_exception:
                raise last_exception

            # This should never happen, but just in case
            raise RuntimeError("Retry mechanism failed unexpectedly")

        return wrapper

    return decorator


def create_retry_session(
    max_attempts: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Optional[list[int]] = None,
    allowed_methods: Optional[list[str]] = None,
) -> requests.Session:
    """Create a requests session with retry capabilities.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Backoff factor for exponential backoff
        status_forcelist: HTTP status codes to retry on
        allowed_methods: HTTP methods to retry on

    Returns:
        Requests session with retry capabilities
    """
    if status_forcelist is None:
        status_forcelist = [500, 502, 503, 504]

    if allowed_methods is None:
        allowed_methods = ["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]

    retry_strategy = Retry(
        total=max_attempts,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def retry_async(
    config: Optional[RetryConfig] = None,
    max_attempts: int = 3,
    strategy: Optional[RetryStrategy] = None,
    timeout: Optional[float] = None,
    log_retries: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to add retry functionality to an async function.

    Args:
        config: Retry configuration
        max_attempts: Maximum number of retry attempts
        strategy: Retry strategy to use
        timeout: Timeout for each attempt
        log_retries: Whether to log retry attempts

    Returns:
        Decorated async function with retry functionality
    """
    if config is None:
        config = RetryConfig(
            max_attempts=max_attempts,
            strategy=strategy,
            timeout=timeout,
            log_retries=log_retries,
        )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger()
            last_exception: Optional[Exception] = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    if config.timeout:
                        # For async timeout support
                        return await asyncio.wait_for(
                            func(*args, **kwargs), timeout=config.timeout
                        )
                    else:
                        return await func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Check if we should retry
                    if not config.strategy.should_retry(
                        attempt, config.max_attempts, e
                    ):
                        raise

                    # Calculate delay
                    delay = config.strategy.get_delay(attempt, config.max_attempts)

                    if config.log_retries:
                        logger.warning(
                            f"Attempt {attempt}/{config.max_attempts} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )

                    # Wait before retry
                    await asyncio.sleep(delay)

            # If we get here, all attempts failed
            if last_exception:
                raise last_exception

            # This should never happen, but just in case
            raise RuntimeError("Retry mechanism failed unexpectedly")

        return wrapper

    return decorator


# Pre-configured retry configurations for common use cases
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    strategy=ExponentialBackoff(base_delay=1.0, max_delay=60.0),
    log_retries=True,
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    strategy=ExponentialBackoff(base_delay=0.5, max_delay=30.0),
    log_retries=True,
)

CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=2,
    strategy=LinearBackoff(base_delay=2.0, max_delay=10.0),
    log_retries=True,
)

__all__ = [
    "RetryStrategy",
    "ExponentialBackoff",
    "LinearBackoff",
    "RetryConfig",
    "with_retry",
    "create_retry_session",
    "retry_async",
    "DEFAULT_RETRY_CONFIG",
    "AGGRESSIVE_RETRY_CONFIG",
    "CONSERVATIVE_RETRY_CONFIG",
]
