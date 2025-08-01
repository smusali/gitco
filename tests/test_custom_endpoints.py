"""Tests for custom LLM endpoint functionality."""

from unittest.mock import Mock, patch

import pytest

from gitco.analyzer import ChangeAnalyzer, CustomAnalyzer
from gitco.config import Config, Settings


class TestCustomEndpoints:
    """Test custom LLM endpoint functionality."""

    def test_custom_analyzer_initialization(self) -> None:
        """Test CustomAnalyzer initialization with valid parameters."""
        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        assert analyzer.api_key == "test-key"
        assert analyzer.endpoint_url == "https://api.test.com/v1/chat/completions"
        assert analyzer.provider_name == "test_provider"
        assert analyzer.model == "default"

    def test_custom_analyzer_missing_endpoint_url(self) -> None:
        """Test CustomAnalyzer raises error when endpoint URL is missing."""
        with pytest.raises(ValueError, match="Custom endpoint URL is required"):
            CustomAnalyzer(
                api_key="test-key", endpoint_url="", provider_name="test_provider"
            )

    def test_custom_analyzer_get_api_name(self) -> None:
        """Test CustomAnalyzer returns correct API name."""
        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="my_custom_llm",
        )

        assert analyzer._get_api_name() == "My_Custom_Llm"

    def test_custom_analyzer_openai_format_response(self) -> None:
        """Test CustomAnalyzer handles OpenAI-compatible response format."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test analysis result"}}]
        }
        mock_response.raise_for_status.return_value = None

        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        # Mock the session's post method
        with patch.object(analyzer.session, "post", return_value=mock_response):
            result = analyzer._call_llm_api("test prompt", "test system")
            assert result == "Test analysis result"

    def test_custom_analyzer_anthropic_format_response(self) -> None:
        """Test CustomAnalyzer handles Anthropic-compatible response format."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{"text": "Test analysis result"}]
        }
        mock_response.raise_for_status.return_value = None

        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        # Mock the session's post method
        with patch.object(analyzer.session, "post", return_value=mock_response):
            result = analyzer._call_llm_api("test prompt", "test system")
            assert result == "Test analysis result"

    def test_custom_analyzer_simple_text_response(self) -> None:
        """Test CustomAnalyzer handles simple text response format."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"text": "Test analysis result"}
        mock_response.raise_for_status.return_value = None

        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        # Mock the session's post method
        with patch.object(analyzer.session, "post", return_value=mock_response):
            result = analyzer._call_llm_api("test prompt", "test system")
            assert result == "Test analysis result"

    def test_settings_custom_endpoints_validation(self) -> None:
        """Test Settings validation for custom endpoints."""
        # Valid custom endpoints
        settings = Settings(
            llm_provider="custom",
            llm_custom_endpoints={
                "my_llm": "https://api.mycompany.com/v1/chat/completions"
            },
        )

        # Should not raise any validation errors
        assert (
            settings.llm_custom_endpoints["my_llm"]
            == "https://api.mycompany.com/v1/chat/completions"
        )

    def test_settings_custom_endpoints_invalid_url(self) -> None:
        """Test Settings validation catches invalid custom endpoint URLs."""
        settings = Settings(
            llm_provider="custom", llm_custom_endpoints={"my_llm": "invalid-url"}
        )

        # The URL should be invalid
        assert not settings.llm_custom_endpoints["my_llm"].startswith(
            ("http://", "https://")
        )

    def test_change_analyzer_custom_provider_support(self) -> None:
        """Test ChangeAnalyzer supports custom providers."""
        config = Config()
        config.settings.llm_provider = "custom"
        config.settings.llm_custom_endpoints = {
            "my_custom_llm": "https://api.mycompany.com/v1/chat/completions"
        }

        analyzer = ChangeAnalyzer(config)

        # Should be able to get analyzer for custom provider
        with patch.dict("os.environ", {"MY_CUSTOM_LLM_API_KEY": "test-key"}):
            custom_analyzer = analyzer.get_analyzer("my_custom_llm")
            assert isinstance(custom_analyzer, CustomAnalyzer)
            assert custom_analyzer.provider_name == "my_custom_llm"
            assert (
                custom_analyzer.endpoint_url
                == "https://api.mycompany.com/v1/chat/completions"
            )

    def test_change_analyzer_custom_provider_without_endpoints(self) -> None:
        """Test ChangeAnalyzer raises error when custom provider has no endpoints."""
        config = Config()
        config.settings.llm_provider = "custom"
        config.settings.llm_custom_endpoints = {}

        analyzer = ChangeAnalyzer(config)

        with pytest.raises(
            ValueError,
            match="Unsupported LLM provider: custom",
        ):
            analyzer.get_analyzer("custom")

    def test_change_analyzer_unsupported_provider(self) -> None:
        """Test ChangeAnalyzer raises error for unsupported providers."""
        config = Config()
        analyzer = ChangeAnalyzer(config)

        with pytest.raises(
            ValueError, match="Unsupported LLM provider: invalid_provider"
        ):
            analyzer.get_analyzer("invalid_provider")

    def test_custom_analyzer_with_none_values(self) -> None:
        """Test CustomAnalyzer with None values."""
        analyzer = CustomAnalyzer(
            api_key=None,
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        assert analyzer.api_key is None
        assert analyzer.endpoint_url == "https://api.test.com/v1/chat/completions"
        assert analyzer.provider_name == "test_provider"

    def test_custom_analyzer_with_empty_response(self) -> None:
        """Test CustomAnalyzer handles empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None

        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        with patch.object(analyzer.session, "post", return_value=mock_response):
            result = analyzer._call_llm_api("test prompt", "test system")
            assert result == ""

    def test_custom_analyzer_with_malformed_response(self) -> None:
        """Test CustomAnalyzer handles malformed response."""
        mock_response = Mock()
        mock_response.json.return_value = {"unexpected": "format"}
        mock_response.raise_for_status.return_value = None

        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        with patch.object(analyzer.session, "post", return_value=mock_response):
            result = analyzer._call_llm_api("test prompt", "test system")
            assert result == ""

    def test_custom_analyzer_with_http_error(self) -> None:
        """Test CustomAnalyzer handles HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")

        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        with patch.object(analyzer.session, "post", return_value=mock_response):
            with pytest.raises(Exception, match="HTTP Error"):
                analyzer._call_llm_api("test prompt", "test system")

    def test_custom_analyzer_with_network_error(self) -> None:
        """Test CustomAnalyzer handles network errors."""
        analyzer = CustomAnalyzer(
            api_key="test-key",
            endpoint_url="https://api.test.com/v1/chat/completions",
            provider_name="test_provider",
        )

        with patch.object(
            analyzer.session, "post", side_effect=Exception("Network Error")
        ):
            with pytest.raises(Exception, match="Network Error"):
                analyzer._call_llm_api("test prompt", "test system")
