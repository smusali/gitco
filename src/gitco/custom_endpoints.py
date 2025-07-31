"""Custom LLM endpoints functionality for GitCo."""

import os
from typing import TYPE_CHECKING

from .utils.common import get_logger

if TYPE_CHECKING:
    from .config import Config, Settings


def get_custom_endpoint_config(config: "Config", provider: str) -> tuple[str, str]:
    """Get custom endpoint configuration for a provider.

    Args:
        config: Configuration object.
        provider: Provider name.

    Returns:
        Tuple of (endpoint_url, api_key).

    Raises:
        ValueError: If custom endpoint is not configured or API key is missing.
    """
    if not config.settings.llm_custom_endpoints:
        raise ValueError("Custom LLM provider requires custom endpoints configuration")

    if provider not in config.settings.llm_custom_endpoints:
        raise ValueError(f"Custom endpoint '{provider}' not found in configuration")

    endpoint_url = config.settings.llm_custom_endpoints[provider]
    api_key_env_var = f"{provider.upper()}_API_KEY"
    api_key = os.getenv(api_key_env_var)

    if not api_key:
        raise ValueError(
            f"API key for custom endpoint '{provider}' not found. "
            f"Set {api_key_env_var} environment variable."
        )

    return endpoint_url, api_key


def get_default_custom_endpoint(config: "Config") -> tuple[str, str, str]:
    """Get the first custom endpoint as default.

    Args:
        config: Configuration object.

    Returns:
        Tuple of (endpoint_name, endpoint_url, api_key_env_var).

    Raises:
        ValueError: If no custom endpoints are configured.
    """
    if not config.settings.llm_custom_endpoints:
        raise ValueError("Custom LLM provider requires custom endpoints configuration")

    # Use the first custom endpoint as default
    endpoint_name, endpoint_url = next(
        iter(config.settings.llm_custom_endpoints.items())
    )
    api_key_env_var = f"{endpoint_name.upper()}_API_KEY"
    api_key = os.getenv(api_key_env_var)

    if not api_key:
        raise ValueError(
            f"API key for custom endpoint '{endpoint_name}' not found. "
            f"Set {api_key_env_var} environment variable."
        )

    return endpoint_name, endpoint_url, api_key


def validate_custom_endpoints(settings: "Settings") -> None:
    """Validate custom endpoints configuration.

    Args:
        settings: Settings to validate.

    Raises:
        ValueError: If custom endpoints configuration is invalid.
    """
    if settings.llm_provider == "custom" and not settings.llm_custom_endpoints:
        raise ValueError("Custom LLM provider requires at least one custom endpoint")

    # Validate custom endpoint URLs
    for endpoint_name, endpoint_url in settings.llm_custom_endpoints.items():
        if not endpoint_url.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid URL format for custom endpoint '{endpoint_name}': {endpoint_url}. "
                "URL must start with http:// or https://"
            )


def is_custom_provider(provider: str, config: "Config") -> bool:
    """Check if a provider is a custom endpoint.

    Args:
        provider: Provider name.
        config: Configuration object.

    Returns:
        True if provider is a custom endpoint, False otherwise.
    """
    return provider in config.settings.llm_custom_endpoints


def get_custom_providers(config: "Config") -> list[str]:
    """Get list of available custom providers.

    Args:
        config: Configuration object.

    Returns:
        List of custom provider names.
    """
    return list(config.settings.llm_custom_endpoints.keys())


def log_custom_endpoint_usage(provider: str, endpoint_url: str) -> None:
    """Log custom endpoint usage for debugging.

    Args:
        provider: Provider name.
        endpoint_url: Endpoint URL.
    """
    logger = get_logger()
    logger.info(f"Using custom endpoint: {provider} -> {endpoint_url}")
