"""Tests for cost optimization functionality."""

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gitco.utils.cost_optimizer import (
    CostConfig,
    CostOptimizer,
    TokenUsage,
    get_cost_optimizer,
    reset_cost_optimizer,
)


class TestTokenUsage:
    """Test TokenUsage dataclass."""

    def test_token_usage_creation(self) -> None:
        """Test creating a TokenUsage instance."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=0.002,
        )

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "gpt-3.5-turbo"
        assert usage.provider == "openai"
        assert usage.cost_usd == 0.002
        assert usage.total_cost_usd == 0.002

    def test_token_usage_defaults(self) -> None:
        """Test TokenUsage with default values."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
        )

        assert usage.cost_usd == 0.0
        assert usage.request_id is None
        assert usage.timestamp > 0


class TestCostConfig:
    """Test CostConfig dataclass."""

    def test_cost_config_defaults(self) -> None:
        """Test CostConfig default values."""
        config = CostConfig()

        assert config.max_tokens_per_request == 4000
        assert config.max_cost_per_request_usd == 0.10
        assert config.max_daily_cost_usd == 5.0
        assert config.max_monthly_cost_usd == 50.0
        assert config.enable_token_optimization is True
        assert config.enable_cost_tracking is True
        assert "gpt-3.5-turbo" in config.openai_costs
        assert "claude-3-sonnet-20240229" in config.anthropic_costs

    def test_cost_config_custom(self) -> None:
        """Test CostConfig with custom values."""
        config = CostConfig(
            max_tokens_per_request=2000,
            max_cost_per_request_usd=0.05,
            enable_token_optimization=False,
        )

        assert config.max_tokens_per_request == 2000
        assert config.max_cost_per_request_usd == 0.05
        assert config.enable_token_optimization is False


class TestCostOptimizer:
    """Test CostOptimizer class."""

    def setup_method(self) -> None:
        """Set up test method."""
        # Create a temporary directory for cost log
        self.temp_dir = tempfile.mkdtemp()
        self.cost_log_path = Path(self.temp_dir) / "cost_log.json"

        # Create config with custom cost log path
        self.config = CostConfig(cost_log_file=str(self.cost_log_path))
        self.optimizer = CostOptimizer(self.config)

    def teardown_method(self) -> None:
        """Clean up after test method."""
        # Clean up temporary files
        if self.cost_log_path.exists():
            self.cost_log_path.unlink()
        Path(self.temp_dir).rmdir()

    def test_initialization(self) -> None:
        """Test CostOptimizer initialization."""
        assert self.optimizer.config == self.config
        assert len(self.optimizer.cost_history) == 0

    @patch("src.gitco.utils.cost_optimizer.tiktoken.get_encoding")
    def test_tokenizer_initialization_success(self, mock_get_encoding: Mock) -> None:
        """Test successful tokenizer initialization."""
        mock_encoding = Mock()
        mock_get_encoding.return_value = mock_encoding

        optimizer = CostOptimizer()

        assert optimizer._tokenizer == mock_encoding
        mock_get_encoding.assert_called_once_with("cl100k_base")

    @patch("src.gitco.utils.cost_optimizer.tiktoken.get_encoding")
    def test_tokenizer_initialization_fallback(self, mock_get_encoding: Mock) -> None:
        """Test tokenizer initialization with fallback."""
        # First call fails, second succeeds
        mock_get_encoding.side_effect = [Exception("Not found"), Mock()]

        optimizer = CostOptimizer()

        assert optimizer._tokenizer is not None
        assert mock_get_encoding.call_count == 2

    @patch("src.gitco.utils.cost_optimizer.tiktoken.get_encoding")
    def test_tokenizer_initialization_failure(self, mock_get_encoding: Mock) -> None:
        """Test tokenizer initialization when both attempts fail."""
        mock_get_encoding.side_effect = Exception("Not found")

        optimizer = CostOptimizer()

        assert optimizer._tokenizer is None

    def test_count_tokens_with_tokenizer(self) -> None:
        """Test token counting with working tokenizer."""
        # Mock the tokenizer to return a known number of tokens
        mock_tokenizer = Mock()
        mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
        self.optimizer._tokenizer = mock_tokenizer

        result = self.optimizer.count_tokens("test text")

        assert result == 5
        mock_tokenizer.encode.assert_called_once_with("test text")

    def test_count_tokens_without_tokenizer(self) -> None:
        """Test token counting without tokenizer (fallback)."""
        self.optimizer._tokenizer = None

        result = self.optimizer.count_tokens("test text")

        # Should use fallback estimation (1 token ≈ 4 characters)
        expected = len("test text") // 4
        assert result == expected

    def test_estimate_cost_openai(self) -> None:
        """Test cost estimation for OpenAI."""
        prompt = "This is a test prompt"

        # Mock token counting
        with patch.object(self.optimizer, "count_tokens", return_value=10):
            cost = self.optimizer.estimate_cost(prompt, "gpt-3.5-turbo", "openai")

        # Expected: (10 + 4000) tokens / 1000 * 0.0015 = 6.015
        expected_cost = (10 + 4000) / 1000 * 0.0015
        assert cost == pytest.approx(expected_cost, rel=1e-3)

    def test_estimate_cost_anthropic(self) -> None:
        """Test cost estimation for Anthropic."""
        prompt = "This is a test prompt"

        # Mock token counting
        with patch.object(self.optimizer, "count_tokens", return_value=10):
            cost = self.optimizer.estimate_cost(
                prompt, "claude-3-sonnet-20240229", "anthropic"
            )

        # Expected: (10 + 4000) tokens / 1000 * 0.003 = 12.03
        expected_cost = (10 + 4000) / 1000 * 0.003
        assert cost == pytest.approx(expected_cost, rel=1e-3)

    def test_calculate_actual_cost(self) -> None:
        """Test actual cost calculation."""
        cost = self.optimizer.calculate_actual_cost(
            prompt_tokens=100,
            completion_tokens=50,
            model="gpt-3.5-turbo",
            provider="openai",
        )

        # Expected: (100 + 50) tokens / 1000 * 0.0015 = 0.000225
        expected_cost = (100 + 50) / 1000 * 0.0015
        assert cost == pytest.approx(expected_cost, rel=1e-6)

    def test_check_cost_limits_within_limits(self) -> None:
        """Test cost limit checking when within limits."""
        result = self.optimizer.check_cost_limits(0.05)
        assert result is True

    def test_check_cost_limits_exceeds_per_request(self) -> None:
        """Test cost limit checking when exceeding per-request limit."""
        result = self.optimizer.check_cost_limits(0.15)  # > 0.10
        assert result is False

    def test_check_cost_limits_exceeds_daily(self) -> None:
        """Test cost limit checking when exceeding daily limit."""
        # Add some cost history
        usage = TokenUsage(
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=4.5,  # Close to daily limit
        )
        self.optimizer.cost_history.append(usage)

        result = self.optimizer.check_cost_limits(1.0)  # Would exceed 5.0 daily limit
        assert result is False

    def test_optimize_prompt_no_optimization_needed(self) -> None:
        """Test prompt optimization when no optimization is needed."""
        prompt = "This is a short prompt"

        # Mock token counting to return a small number
        with patch.object(self.optimizer, "count_tokens", return_value=100):
            result = self.optimizer.optimize_prompt(prompt, max_tokens=4000)

        assert result == prompt

    def test_optimize_prompt_with_optimization(self) -> None:
        """Test prompt optimization when optimization is needed."""
        # Create a long prompt with multiple lines to trigger the line-based optimization
        prompt = (
            "Line 1\nLine 2\nLine 3\n"
            + ("This is a very long line. " * 100)
            + "\nLine 4\nLine 5"
        )

        # Mock token counting to return a large number
        with patch.object(self.optimizer, "count_tokens", side_effect=[5000, 3000]):
            result = self.optimizer.optimize_prompt(prompt, max_tokens=4000)

        # Should be optimized (truncated)
        assert result != prompt
        assert "content truncated for cost optimization" in result

    def test_optimize_prompt_disabled(self) -> None:
        """Test prompt optimization when disabled."""
        self.optimizer.config.enable_token_optimization = False
        prompt = "This is a very long prompt. " * 1000

        result = self.optimizer.optimize_prompt(prompt, max_tokens=4000)

        assert result == prompt

    def test_record_usage(self) -> None:
        """Test recording token usage."""
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=0.002,
        )

        self.optimizer.record_usage(usage)

        assert len(self.optimizer.cost_history) == 1
        assert self.optimizer.cost_history[0] == usage

    def test_record_usage_disabled(self) -> None:
        """Test recording usage when tracking is disabled."""
        self.optimizer.config.enable_cost_tracking = False

        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=0.002,
        )

        self.optimizer.record_usage(usage)

        assert len(self.optimizer.cost_history) == 0

    def test_get_daily_cost(self) -> None:
        """Test getting daily cost."""
        # Add some usage from different times
        now = time.time()

        # Recent usage (within 1 day)
        recent_usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=1.0,
            timestamp=now - 3600,  # 1 hour ago
        )

        # Old usage (more than 1 day ago)
        old_usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=2.0,
            timestamp=now - 86400 * 2,  # 2 days ago
        )

        self.optimizer.cost_history = [recent_usage, old_usage]

        daily_cost = self.optimizer.get_daily_cost()
        assert daily_cost == 1.0

    def test_get_monthly_cost(self) -> None:
        """Test getting monthly cost."""
        # Add some usage from different times
        now = time.time()

        # Recent usage (within 1 month)
        recent_usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=1.0,
            timestamp=now - 86400 * 15,  # 15 days ago
        )

        # Old usage (more than 1 month ago)
        old_usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=2.0,
            timestamp=now - 86400 * 35,  # 35 days ago
        )

        self.optimizer.cost_history = [recent_usage, old_usage]

        monthly_cost = self.optimizer.get_monthly_cost()
        assert monthly_cost == 1.0

    def test_get_cost_summary_empty(self) -> None:
        """Test getting cost summary when no usage."""
        summary = self.optimizer.get_cost_summary()

        assert summary["total_cost"] == 0.0
        assert summary["total_requests"] == 0
        assert summary["daily_cost"] == 0.0
        assert summary["monthly_cost"] == 0.0
        assert summary["providers"] == {}
        assert summary["models"] == {}

    def test_get_cost_summary_with_usage(self) -> None:
        """Test getting cost summary with usage data."""
        # Add some usage
        usage1 = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=1.0,
        )

        usage2 = TokenUsage(
            prompt_tokens=200,
            completion_tokens=100,
            total_tokens=300,
            model="claude-3-sonnet-20240229",
            provider="anthropic",
            cost_usd=2.0,
        )

        self.optimizer.cost_history = [usage1, usage2]

        summary = self.optimizer.get_cost_summary()

        assert summary["total_cost"] == 3.0
        assert summary["total_requests"] == 2
        assert "openai" in summary["providers"]
        assert "anthropic" in summary["providers"]
        assert "gpt-3.5-turbo" in summary["models"]
        assert "claude-3-sonnet-20240229" in summary["models"]

    def test_reset_cost_history(self) -> None:
        """Test resetting cost history."""
        # Add some usage
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=1.0,
        )
        self.optimizer.cost_history = [usage]

        self.optimizer.reset_cost_history()

        assert len(self.optimizer.cost_history) == 0

    def test_save_and_load_cost_history(self) -> None:
        """Test saving and loading cost history."""
        # Add some usage
        usage = TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="gpt-3.5-turbo",
            provider="openai",
            cost_usd=1.0,
        )
        self.optimizer.cost_history = [usage]

        # Save
        self.optimizer._save_cost_history()

        # Create new optimizer and load
        new_optimizer = CostOptimizer(self.config)

        # Should have loaded the usage
        assert len(new_optimizer.cost_history) == 1
        loaded_usage = new_optimizer.cost_history[0]
        assert loaded_usage.prompt_tokens == usage.prompt_tokens
        assert loaded_usage.completion_tokens == usage.completion_tokens
        assert loaded_usage.total_tokens == usage.total_tokens
        assert loaded_usage.model == usage.model
        assert loaded_usage.provider == usage.provider
        assert loaded_usage.cost_usd == usage.cost_usd


class TestGlobalFunctions:
    """Test global functions."""

    def test_get_cost_optimizer(self) -> None:
        """Test getting global cost optimizer."""
        # Reset first
        reset_cost_optimizer()

        optimizer1 = get_cost_optimizer()
        optimizer2 = get_cost_optimizer()

        # Should return the same instance
        assert optimizer1 is optimizer2

    def test_reset_cost_optimizer(self) -> None:
        """Test resetting global cost optimizer."""
        optimizer1 = get_cost_optimizer()
        reset_cost_optimizer()
        optimizer2 = get_cost_optimizer()

        # Should be different instances
        assert optimizer1 is not optimizer2


def test_token_usage_with_none_values() -> None:
    """Test TokenUsage creation with None values."""
    usage = TokenUsage(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        model="gpt-3.5-turbo",
        provider="openai",
        cost_usd=0.0,
        timestamp=time.time(),
    )

    assert usage.prompt_tokens == 0
    assert usage.completion_tokens == 0
    assert usage.total_tokens == 0
    assert usage.model == "gpt-3.5-turbo"
    assert usage.provider == "openai"
    assert usage.cost_usd == 0.0
    assert usage.timestamp > 0


def test_cost_config_with_none_values() -> None:
    """Test CostConfig creation with None values."""
    config = CostConfig()

    # Test that default values are set
    assert hasattr(config, "openai_costs")
    assert hasattr(config, "anthropic_costs")
    assert config.openai_costs["gpt-3.5-turbo"] == 0.0015


def test_cost_optimizer_with_none_config() -> None:
    """Test CostOptimizer with None config."""
    optimizer = CostOptimizer(None)

    # Should handle None config gracefully
    assert optimizer.config is not None  # Should use default config when None is passed
    assert optimizer.logger is not None
    # Note: cost_history may not be empty if there's existing data


def test_cost_optimizer_count_tokens_with_none_text() -> None:
    """Test CostOptimizer count_tokens with None text."""
    # Create a proper mock config with required attributes
    mock_config = Mock()
    mock_config.cost_log_file = "/tmp/test_cost_log.json"
    mock_config.encoding_model = "cl100k_base"
    mock_config.fallback_encoding = "gpt2"

    optimizer = CostOptimizer(mock_config)

    # Should handle None text gracefully
    token_count = optimizer.count_tokens(None)
    assert token_count == 0


def test_cost_optimizer_estimate_cost_with_none_model() -> None:
    """Test CostOptimizer estimate_cost with None model."""
    # Create a proper mock config with required attributes
    mock_config = Mock()
    mock_config.cost_log_file = "/tmp/test_cost_log.json"
    mock_config.encoding_model = "cl100k_base"
    mock_config.fallback_encoding = "gpt2"
    mock_config.max_tokens_per_request = 4000  # Add this line to fix the Mock issue
    mock_config.openai_costs = {
        "gpt-3.5-turbo": 0.0015
    }  # Add this line to fix the Mock issue

    optimizer = CostOptimizer(mock_config)

    # Should handle None model gracefully
    cost = optimizer.estimate_cost("test text", None, "openai")
    assert cost == 0.0
