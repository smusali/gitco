"""Tests for completion utilities."""

from gitco.utils.completion import (
    CompletionConfig,
    CompletionManager,
    CompletionResult,
    get_completion_manager,
    reset_completion_manager,
)


class TestCompletionConfig:
    """Test CompletionConfig dataclass."""

    def test_completion_config_creation(self) -> None:
        """Test creating CompletionConfig with default values."""
        config = CompletionConfig()

        assert config.enable_completion is True
        assert config.max_suggestions == 5
        assert config.min_confidence == 0.7
        assert config.provider == "default"

    def test_completion_config_with_custom_values(self) -> None:
        """Test creating CompletionConfig with custom values."""
        config = CompletionConfig(
            enable_completion=False,
            max_suggestions=10,
            min_confidence=0.8,
            provider="custom",
        )

        assert config.enable_completion is False
        assert config.max_suggestions == 10
        assert config.min_confidence == 0.8
        assert config.provider == "custom"

    def test_completion_config_with_none_values(self) -> None:
        """Test CompletionConfig creation with None values."""
        config = CompletionConfig(
            enable_completion=None,
            max_suggestions=None,
            min_confidence=None,
            provider=None,
        )

        assert config.enable_completion is None
        assert config.max_suggestions is None
        assert config.min_confidence is None
        assert config.provider is None


class TestCompletionResult:
    """Test CompletionResult dataclass."""

    def test_completion_result_creation(self) -> None:
        """Test creating CompletionResult with values."""
        result = CompletionResult(
            suggestions=["suggestion1", "suggestion2"],
            confidence=0.9,
            provider="test_provider",
        )

        assert result.suggestions == ["suggestion1", "suggestion2"]
        assert result.confidence == 0.9
        assert result.provider == "test_provider"

    def test_completion_result_with_empty_suggestions(self) -> None:
        """Test CompletionResult with empty suggestions."""
        result = CompletionResult(
            suggestions=[], confidence=0.0, provider="test_provider"
        )

        assert result.suggestions == []
        assert result.confidence == 0.0
        assert result.provider == "test_provider"

    def test_completion_result_with_none_values(self) -> None:
        """Test CompletionResult creation with None values."""
        result = CompletionResult(suggestions=None, confidence=None, provider=None)

        assert result.suggestions is None
        assert result.confidence is None
        assert result.provider is None


class TestCompletionManager:
    """Test CompletionManager class."""

    def test_completion_manager_initialization(self) -> None:
        """Test CompletionManager initialization."""
        config = CompletionConfig()
        manager = CompletionManager(config)

        assert manager.config == config
        assert manager.logger is not None

    def test_completion_manager_with_none_config(self) -> None:
        """Test CompletionManager with None config."""
        manager = CompletionManager(None)

        # Should handle None config gracefully
        assert manager.config is None
        assert manager.logger is not None

    def test_get_completion_suggestions_disabled(self) -> None:
        """Test get_completion_suggestions when completion is disabled."""
        config = CompletionConfig(enable_completion=False)
        manager = CompletionManager(config)

        suggestions = manager.get_completion_suggestions("test input")

        assert suggestions.suggestions == []
        assert suggestions.confidence == 0.0

    def test_get_completion_suggestions_with_empty_input(self) -> None:
        """Test get_completion_suggestions with empty input."""
        config = CompletionConfig()
        manager = CompletionManager(config)

        suggestions = manager.get_completion_suggestions("")

        assert suggestions.suggestions == []
        assert suggestions.confidence == 0.0

    def test_get_completion_suggestions_with_none_input(self) -> None:
        """Test get_completion_suggestions with None input."""
        config = CompletionConfig()
        manager = CompletionManager(config)

        suggestions = manager.get_completion_suggestions(None)

        assert suggestions.suggestions == []
        assert suggestions.confidence == 0.0


class TestGlobalFunctions:
    """Test global functions."""

    def test_get_completion_manager(self) -> None:
        """Test getting global completion manager."""
        # Reset first
        reset_completion_manager()

        manager1 = get_completion_manager()
        manager2 = get_completion_manager()

        # Should return the same instance
        assert manager1 is manager2

    def test_reset_completion_manager(self) -> None:
        """Test resetting global completion manager."""
        manager1 = get_completion_manager()
        reset_completion_manager()
        manager2 = get_completion_manager()

        # Should be different instances
        assert manager1 is not manager2
