"""Cost optimization utilities for LLM usage in GitCo."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import tiktoken
from rich.console import Console
from rich.table import Table

from .common import get_logger


@dataclass
class TokenUsage:
    """Token usage statistics for a single API call."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    provider: str
    timestamp: float = field(default_factory=time.time)
    cost_usd: float = 0.0
    request_id: Optional[str] = None

    @property
    def total_cost_usd(self) -> float:
        """Get total cost in USD."""
        return self.cost_usd


@dataclass
class CostConfig:
    """Configuration for cost tracking and optimization."""

    # Token costs per 1K tokens (USD)
    openai_costs: dict[str, float] = field(
        default_factory=lambda: {
            "gpt-4": 0.03,  # input
            "gpt-4-32k": 0.06,
            "gpt-3.5-turbo": 0.0015,
            "gpt-3.5-turbo-16k": 0.003,
        }
    )
    anthropic_costs: dict[str, float] = field(
        default_factory=lambda: {
            "claude-3-opus-20240229": 0.015,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.00025,
        }
    )

    # Optimization settings
    max_tokens_per_request: int = 4000
    max_cost_per_request_usd: float = 0.10
    max_daily_cost_usd: float = 5.0
    max_monthly_cost_usd: float = 50.0

    # Token counting settings
    encoding_model: str = "cl100k_base"  # OpenAI's encoding
    fallback_encoding: str = "gpt2"  # Fallback for unsupported models

    # Cost tracking file
    cost_log_file: str = "~/.gitco/cost_log.json"

    # Optimization strategies
    enable_token_optimization: bool = True
    enable_cost_tracking: bool = True
    enable_daily_limits: bool = True
    enable_monthly_limits: bool = True


class CostOptimizer:
    """Cost optimization and tracking for LLM usage."""

    def __init__(self, config: Optional[CostConfig] = None):
        """Initialize cost optimizer.

        Args:
            config: Cost configuration. If None, uses default config.
        """
        self.config = config or CostConfig()
        self.logger = get_logger()
        self.console = Console()

        # Initialize tokenizer
        self._tokenizer: Optional[Any] = None
        self._initialize_tokenizer()

        # Load cost history
        self.cost_history: list[TokenUsage] = []
        self._load_cost_history()

    def _initialize_tokenizer(self) -> None:
        """Initialize the tokenizer for counting tokens."""
        try:
            self._tokenizer = tiktoken.get_encoding(self.config.encoding_model)
        except Exception as e:
            self.logger.warning(
                f"Failed to initialize {self.config.encoding_model} tokenizer: {e}"
            )
            try:
                self._tokenizer = tiktoken.get_encoding(self.config.fallback_encoding)
                self.logger.info(
                    f"Using fallback tokenizer: {self.config.fallback_encoding}"
                )
            except Exception as e2:
                self.logger.error(f"Failed to initialize fallback tokenizer: {e2}")
                self._tokenizer = None

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.
        """
        if not self._tokenizer:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4

        try:
            return len(self._tokenizer.encode(text))
        except Exception as e:
            self.logger.warning(f"Token counting failed: {e}")
            # Fallback estimation
            return len(text) // 4

    def estimate_cost(
        self,
        prompt: str,
        model: str,
        provider: str,
        max_completion_tokens: Optional[int] = None,
    ) -> float:
        """Estimate cost for an API call.

        Args:
            prompt: The prompt text.
            model: The model name.
            provider: The provider (openai, anthropic).
            max_completion_tokens: Maximum completion tokens to estimate.

        Returns:
            Estimated cost in USD.
        """
        prompt_tokens = self.count_tokens(prompt)

        # Estimate completion tokens if not provided
        if max_completion_tokens is None:
            max_completion_tokens = self.config.max_tokens_per_request

        total_tokens = prompt_tokens + max_completion_tokens

        # Get cost per 1K tokens
        if provider.lower() == "openai":
            cost_per_1k = self.config.openai_costs.get(model, 0.002)
        elif provider.lower() == "anthropic":
            cost_per_1k = self.config.anthropic_costs.get(model, 0.003)
        else:
            cost_per_1k = 0.002  # Default fallback

        return (total_tokens / 1000) * cost_per_1k

    def calculate_actual_cost(
        self, prompt_tokens: int, completion_tokens: int, model: str, provider: str
    ) -> float:
        """Calculate actual cost from token usage.

        Args:
            prompt_tokens: Number of prompt tokens.
            completion_tokens: Number of completion tokens.
            model: The model name.
            provider: The provider (openai, anthropic).

        Returns:
            Actual cost in USD.
        """
        total_tokens = prompt_tokens + completion_tokens

        # Get cost per 1K tokens
        if provider.lower() == "openai":
            cost_per_1k = self.config.openai_costs.get(model, 0.002)
        elif provider.lower() == "anthropic":
            cost_per_1k = self.config.anthropic_costs.get(model, 0.003)
        else:
            cost_per_1k = 0.002  # Default fallback

        return (total_tokens / 1000) * cost_per_1k

    def check_cost_limits(self, estimated_cost: float) -> bool:
        """Check if estimated cost is within limits.

        Args:
            estimated_cost: Estimated cost in USD.

        Returns:
            True if cost is within limits, False otherwise.
        """
        if estimated_cost > self.config.max_cost_per_request_usd:
            self.logger.warning(
                f"Estimated cost ${estimated_cost:.4f} exceeds per-request limit "
                f"${self.config.max_cost_per_request_usd}"
            )
            return False

        if self.config.enable_daily_limits:
            daily_cost = self.get_daily_cost()
            if daily_cost + estimated_cost > self.config.max_daily_cost_usd:
                self.logger.warning(
                    f"Estimated cost would exceed daily limit. "
                    f"Current: ${daily_cost:.2f}, Limit: ${self.config.max_daily_cost_usd}"
                )
                return False

        if self.config.enable_monthly_limits:
            monthly_cost = self.get_monthly_cost()
            if monthly_cost + estimated_cost > self.config.max_monthly_cost_usd:
                self.logger.warning(
                    f"Estimated cost would exceed monthly limit. "
                    f"Current: ${monthly_cost:.2f}, Limit: ${self.config.max_monthly_cost_usd}"
                )
                return False

        return True

    def optimize_prompt(self, prompt: str, max_tokens: int = 4000) -> str:
        """Optimize prompt to reduce token usage.

        Args:
            prompt: Original prompt.
            max_tokens: Maximum tokens allowed.

        Returns:
            Optimized prompt.
        """
        if not self.config.enable_token_optimization:
            return prompt

        current_tokens = self.count_tokens(prompt)

        if current_tokens <= max_tokens:
            return prompt

        # Simple optimization: truncate while preserving structure
        self.logger.info(f"Optimizing prompt: {current_tokens} -> {max_tokens} tokens")

        # Try to preserve important parts (first and last sections)
        lines = prompt.split("\n")
        if len(lines) <= 2:
            # If very short, just truncate
            return prompt[: max_tokens * 4]  # Rough character estimation

        # Keep first and last sections, truncate middle
        first_section = lines[: len(lines) // 3]
        last_section = lines[-len(lines) // 3 :]

        optimized_lines = (
            first_section
            + ["\n... (content truncated for cost optimization) ...\n"]
            + last_section
        )
        optimized_prompt = "\n".join(optimized_lines)

        # Ensure we're under the limit
        while (
            self.count_tokens(optimized_prompt) > max_tokens
            and len(optimized_lines) > 3
        ):
            # Remove more from the middle
            optimized_lines = (
                optimized_lines[:-1]
                if len(optimized_lines) % 2 == 0
                else optimized_lines[1:]
            )
            optimized_prompt = "\n".join(optimized_lines)

        return optimized_prompt

    def record_usage(self, usage: TokenUsage) -> None:
        """Record token usage for cost tracking.

        Args:
            usage: Token usage information.
        """
        if not self.config.enable_cost_tracking:
            return

        self.cost_history.append(usage)
        self._save_cost_history()

    def get_daily_cost(self, days: int = 1) -> float:
        """Get total cost for the last N days.

        Args:
            days: Number of days to look back.

        Returns:
            Total cost in USD.
        """
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_usage = [
            usage for usage in self.cost_history if usage.timestamp >= cutoff_time
        ]
        return sum(usage.total_cost_usd for usage in recent_usage)

    def get_monthly_cost(self, months: int = 1) -> float:
        """Get total cost for the last N months.

        Args:
            months: Number of months to look back.

        Returns:
            Total cost in USD.
        """
        cutoff_time = time.time() - (months * 30 * 24 * 3600)
        recent_usage = [
            usage for usage in self.cost_history if usage.timestamp >= cutoff_time
        ]
        return sum(usage.total_cost_usd for usage in recent_usage)

    def get_cost_summary(self) -> dict[str, Any]:
        """Get comprehensive cost summary.

        Returns:
            Cost summary dictionary.
        """
        if not self.cost_history:
            return {
                "total_cost": 0.0,
                "total_requests": 0,
                "daily_cost": 0.0,
                "monthly_cost": 0.0,
                "providers": {},
                "models": {},
            }

        # Calculate totals
        total_cost = sum(usage.total_cost_usd for usage in self.cost_history)
        total_requests = len(self.cost_history)

        # Group by provider
        providers = {}
        for usage in self.cost_history:
            if usage.provider not in providers:
                providers[usage.provider] = {"cost": 0.0, "requests": 0, "tokens": 0}
            providers[usage.provider]["cost"] += usage.total_cost_usd
            providers[usage.provider]["requests"] += 1
            providers[usage.provider]["tokens"] += usage.total_tokens

        # Group by model
        models = {}
        for usage in self.cost_history:
            if usage.model not in models:
                models[usage.model] = {"cost": 0.0, "requests": 0, "tokens": 0}
            models[usage.model]["cost"] += usage.total_cost_usd
            models[usage.model]["requests"] += 1
            models[usage.model]["tokens"] += usage.total_tokens

        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "daily_cost": self.get_daily_cost(),
            "monthly_cost": self.get_monthly_cost(),
            "providers": providers,
            "models": models,
        }

    def display_cost_summary(self) -> None:
        """Display cost summary in a formatted table."""
        summary = self.get_cost_summary()

        if summary["total_requests"] == 0:
            self.console.print("No cost data available.")
            return

        # Create summary table
        table = Table(title="GitCo LLM Cost Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Cost", f"${summary['total_cost']:.4f}")
        table.add_row("Total Requests", str(summary["total_requests"]))
        table.add_row("Daily Cost", f"${summary['daily_cost']:.4f}")
        table.add_row("Monthly Cost", f"${summary['monthly_cost']:.4f}")

        self.console.print(table)

        # Provider breakdown
        if summary["providers"]:
            provider_table = Table(title="Cost by Provider")
            provider_table.add_column("Provider", style="cyan")
            provider_table.add_column("Cost", style="green")
            provider_table.add_column("Requests", style="yellow")
            provider_table.add_column("Tokens", style="blue")

            for provider, data in summary["providers"].items():
                provider_table.add_row(
                    provider.title(),
                    f"${data['cost']:.4f}",
                    str(data["requests"]),
                    f"{data['tokens']:,}",
                )

            self.console.print(provider_table)

        # Model breakdown
        if summary["models"]:
            model_table = Table(title="Cost by Model")
            model_table.add_column("Model", style="cyan")
            model_table.add_column("Cost", style="green")
            model_table.add_column("Requests", style="yellow")
            model_table.add_column("Tokens", style="blue")

            for model, data in summary["models"].items():
                model_table.add_row(
                    model,
                    f"${data['cost']:.4f}",
                    str(data["requests"]),
                    f"{data['tokens']:,}",
                )

            self.console.print(model_table)

    def _load_cost_history(self) -> None:
        """Load cost history from file."""
        if not self.config.enable_cost_tracking:
            return

        cost_log_path = Path(self.config.cost_log_file).expanduser()
        if not cost_log_path.exists():
            return

        try:
            with open(cost_log_path) as f:
                data = json.load(f)
                self.cost_history = [TokenUsage(**usage) for usage in data]
        except Exception as e:
            self.logger.warning(f"Failed to load cost history: {e}")

    def _save_cost_history(self) -> None:
        """Save cost history to file."""
        if not self.config.enable_cost_tracking:
            return

        cost_log_path = Path(self.config.cost_log_file).expanduser()
        cost_log_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(cost_log_path, "w") as f:
                json.dump([vars(usage) for usage in self.cost_history], f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save cost history: {e}")

    def reset_cost_history(self) -> None:
        """Reset cost history."""
        self.cost_history = []
        self._save_cost_history()
        self.logger.info("Cost history reset.")


# Global cost optimizer instance
_cost_optimizer: Optional[CostOptimizer] = None


def get_cost_optimizer() -> CostOptimizer:
    """Get global cost optimizer instance.

    Returns:
        Cost optimizer instance.
    """
    global _cost_optimizer
    if _cost_optimizer is None:
        _cost_optimizer = CostOptimizer()
    return _cost_optimizer


def reset_cost_optimizer() -> None:
    """Reset global cost optimizer instance."""
    global _cost_optimizer
    _cost_optimizer = None
