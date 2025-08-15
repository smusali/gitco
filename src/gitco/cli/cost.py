"""Cost management CLI commands for GitCo.

This module contains cost tracking and optimization commands:
summary, breakdown, configure, reset.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

import click

from ..utils.common import (
    print_error_panel,
    print_info_panel,
    print_success_panel,
    print_warning_panel,
)
from ..utils.cost_optimizer import get_cost_optimizer


def register_cost_commands(main_group):
    """Register all cost commands with the main CLI group."""
    # Create the cost group
    cost_group = click.Group(
        name="cost", help="Manage LLM cost tracking and optimization."
    )
    cost_group.add_command(summary)
    cost_group.add_command(breakdown)
    cost_group.add_command(configure)
    cost_group.add_command(reset)

    # Add the cost group to main
    main_group.add_command(cost_group)


@click.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed cost breakdown")
@click.option("--export", help="Export cost data to file (.json or .csv)")
@click.option("--days", type=int, help="Show costs for last N days")
@click.option("--months", type=int, help="Show costs for last N months")
@click.pass_context
def summary(
    ctx: click.Context,
    detailed: bool,
    export: Optional[str],
    days: Optional[int],
    months: Optional[int],
) -> None:
    """Show LLM cost summary and usage statistics."""
    try:
        cost_optimizer = get_cost_optimizer()

        if detailed:
            cost_optimizer.display_cost_summary()
        else:
            summary_data = cost_optimizer.get_cost_summary(days=days, months=months)

            if summary_data["total_requests"] == 0:
                print_info_panel("Cost Summary", "No cost data available.")
                return

            # Show basic summary
            total_cost = summary_data["total_cost"]
            total_requests = summary_data["total_requests"]
            daily_cost = summary_data.get("daily_cost", 0)
            monthly_cost = summary_data.get("monthly_cost", 0)

            print_info_panel(
                "Cost Summary",
                f"Total Cost: ${total_cost:.4f}\n"
                f"Total Requests: {total_requests}\n"
                f"Daily Cost: ${daily_cost:.4f}\n"
                f"Monthly Cost: ${monthly_cost:.4f}",
            )

        # Export if requested
        if export:
            export_path = Path(export)
            summary_data = cost_optimizer.get_cost_summary(days=days, months=months)

            if export_path.suffix.lower() == ".json":
                with open(export_path, "w") as f:
                    json.dump(summary_data, f, indent=2)
            elif export_path.suffix.lower() == ".csv":
                with open(export_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Metric", "Value"])
                    writer.writerow(
                        ["Total Cost", f"${summary_data['total_cost']:.4f}"]
                    )
                    writer.writerow(["Total Requests", summary_data["total_requests"]])
                    writer.writerow(
                        ["Daily Cost", f"${summary_data.get('daily_cost', 0):.4f}"]
                    )
                    writer.writerow(
                        ["Monthly Cost", f"${summary_data.get('monthly_cost', 0):.4f}"]
                    )

            print_success_panel("Cost Export", f"Cost data exported to {export_path}")

    except Exception as e:
        print_error_panel("Cost Summary Error", f"Failed to get cost summary: {e}")
        sys.exit(1)


@click.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed cost breakdown")
@click.option("--provider", "-p", help="Show breakdown for specific provider")
@click.option("--days", type=int, default=30, help="Show breakdown for last N days")
@click.option("--export", help="Export breakdown to file (.json or .csv)")
@click.pass_context
def breakdown(
    ctx: click.Context,
    detailed: bool,
    provider: Optional[str],
    days: int,
    export: Optional[str],
) -> None:
    """Show detailed cost breakdown.

    Provides a comprehensive breakdown of LLM costs by provider, model, and time period.
    """
    try:
        cost_optimizer = get_cost_optimizer()

        # Get cost breakdown for the specified period
        summary = cost_optimizer.get_cost_summary(days=days)

        if export:
            # Export breakdown data
            export_path = Path(export)

            if export_path.suffix.lower() == ".csv":
                # Convert to CSV format
                with open(export_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Provider", "Model", "Cost", "Requests", "Tokens"])

                    for prov, prov_data in summary.get("providers", {}).items():
                        for model, model_data in prov_data.get("models", {}).items():
                            writer.writerow(
                                [
                                    prov,
                                    model,
                                    model_data.get("cost", 0),
                                    model_data.get("requests", 0),
                                    model_data.get("tokens", 0),
                                ]
                            )
            else:
                # Export as JSON
                with open(export_path, "w") as f:
                    json.dump(summary, f, indent=2)

            print_success_panel(
                "Cost Breakdown Export", f"Breakdown exported to: {export_path}"
            )
            return

        # Display breakdown
        if provider:
            # Show breakdown for specific provider
            if provider in summary.get("providers", {}):
                provider_data = summary["providers"][provider]
                print_info_panel(
                    f"Cost Breakdown - {provider.title()}",
                    f"Total Cost: ${provider_data.get('cost', 0):.4f}\n"
                    f"Requests: {provider_data.get('requests', 0)}\n"
                    f"Tokens: {provider_data.get('tokens', 0):,}\n"
                    f"Average Cost per Request: ${provider_data.get('cost', 0) / max(provider_data.get('requests', 1), 1):.4f}",
                )

                if detailed and "models" in provider_data:
                    print_info_panel("Model Breakdown", "Cost by model:")
                    for model, model_data in provider_data["models"].items():
                        print_info_panel(
                            f"  {model}",
                            f"Cost: ${model_data.get('cost', 0):.4f}, "
                            f"Requests: {model_data.get('requests', 0)}, "
                            f"Tokens: {model_data.get('tokens', 0):,}",
                        )
            else:
                print_warning_panel(
                    "Provider Not Found", f"No data found for provider: {provider}"
                )
        else:
            # Show full breakdown
            print_info_panel(
                f"Cost Breakdown - Last {days} Days",
                f"Total Cost: ${summary.get('total_cost', 0):.4f}\n"
                f"Total Requests: {summary.get('total_requests', 0)}\n"
                f"Total Tokens: {summary.get('total_tokens', 0):,}",
            )

            if detailed and "providers" in summary:
                for prov, prov_data in summary["providers"].items():
                    print_info_panel(
                        f"Provider: {prov.title()}",
                        f"Cost: ${prov_data.get('cost', 0):.4f}\n"
                        f"Requests: {prov_data.get('requests', 0)}\n"
                        f"Tokens: {prov_data.get('tokens', 0):,}",
                    )

    except Exception as e:
        print_error_panel("Breakdown Error", f"Failed to get cost breakdown: {e}")
        sys.exit(1)


@click.command()
@click.option("--daily-limit", type=float, help="Set daily cost limit in USD")
@click.option("--monthly-limit", type=float, help="Set monthly cost limit in USD")
@click.option(
    "--per-request-limit", type=float, help="Set per-request cost limit in USD"
)
@click.option("--max-tokens", type=int, help="Set maximum tokens per request")
@click.option("--enable-tracking", is_flag=True, help="Enable cost tracking")
@click.option("--disable-tracking", is_flag=True, help="Disable cost tracking")
@click.option("--enable-optimization", is_flag=True, help="Enable token optimization")
@click.option("--disable-optimization", is_flag=True, help="Disable token optimization")
@click.option("--show", is_flag=True, help="Show current configuration")
@click.pass_context
def configure(
    ctx: click.Context,
    daily_limit: Optional[float],
    monthly_limit: Optional[float],
    per_request_limit: Optional[float],
    max_tokens: Optional[int],
    enable_tracking: bool,
    disable_tracking: bool,
    enable_optimization: bool,
    disable_optimization: bool,
    show: bool,
) -> None:
    """Configure cost optimization settings."""
    try:
        cost_optimizer = get_cost_optimizer()

        # Show current configuration if requested
        if show:
            config = cost_optimizer.config
            print_info_panel(
                "Current Cost Configuration",
                f"Daily Limit: ${config.max_daily_cost_usd:.2f}\n"
                f"Monthly Limit: ${config.max_monthly_cost_usd:.2f}\n"
                f"Per-Request Limit: ${config.max_cost_per_request_usd:.4f}\n"
                f"Max Tokens: {config.max_tokens_per_request}\n"
                f"Tracking Enabled: {getattr(config, 'enabled', True)}\n"
                f"Optimization Enabled: {getattr(config, 'enable_optimization', True)}",
            )
            return

        # Update configuration
        if daily_limit is not None:
            cost_optimizer.config.max_daily_cost_usd = daily_limit
            print_success_panel(
                "Daily Limit", f"Daily cost limit set to ${daily_limit:.2f}"
            )

        if monthly_limit is not None:
            cost_optimizer.config.max_monthly_cost_usd = monthly_limit
            print_success_panel(
                "Monthly Limit", f"Monthly cost limit set to ${monthly_limit:.2f}"
            )

        if per_request_limit is not None:
            cost_optimizer.config.max_cost_per_request_usd = per_request_limit
            print_success_panel(
                "Per-Request Limit",
                f"Per-request cost limit set to ${per_request_limit:.4f}",
            )

        if max_tokens is not None:
            cost_optimizer.config.max_tokens_per_request = max_tokens
            print_success_panel(
                "Token Limit", f"Maximum tokens per request set to {max_tokens}"
            )

        if enable_tracking:
            cost_optimizer.config.enable_cost_tracking = True
            print_success_panel("Tracking", "Cost tracking enabled")

        if disable_tracking:
            cost_optimizer.config.enable_cost_tracking = False
            print_success_panel("Tracking", "Cost tracking disabled")

        if enable_optimization:
            cost_optimizer.config.enable_token_optimization = True
            print_success_panel("Optimization", "Token optimization enabled")

        if disable_optimization:
            cost_optimizer.config.enable_token_optimization = False
            print_success_panel("Optimization", "Token optimization disabled")

        # Save configuration
        if hasattr(cost_optimizer, "_save_cost_history"):
            cost_optimizer._save_cost_history()

        print_info_panel(
            "Updated Configuration",
            f"Current settings:\n"
            f"• Daily limit: ${cost_optimizer.config.max_daily_cost_usd:.2f}\n"
            f"• Monthly limit: ${cost_optimizer.config.max_monthly_cost_usd:.2f}\n"
            f"• Per-request limit: ${cost_optimizer.config.max_cost_per_request_usd:.4f}\n"
            f"• Max tokens: {cost_optimizer.config.max_tokens_per_request}\n"
            f"• Cost tracking: {'enabled' if getattr(cost_optimizer.config, 'enable_cost_tracking', True) else 'disabled'}\n"
            f"• Token optimization: {'enabled' if getattr(cost_optimizer.config, 'enable_token_optimization', True) else 'disabled'}",
        )

    except Exception as e:
        print_error_panel(
            "Configuration Error", f"Failed to configure cost settings: {e}"
        )
        sys.exit(1)


@click.command()
@click.option("--force", "-f", is_flag=True, help="Force reset without confirmation")
@click.pass_context
def reset(ctx: click.Context, force: bool) -> None:
    """Reset cost history and statistics."""
    try:
        if not force:
            # Ask for confirmation
            confirm = click.confirm(
                "Are you sure you want to reset all cost history? This cannot be undone."
            )
            if not confirm:
                print_info_panel("Reset Cancelled", "Cost history reset cancelled.")
                return

        cost_optimizer = get_cost_optimizer()
        cost_optimizer.reset_cost_history()

        print_success_panel(
            "Reset Complete", "Cost history has been reset successfully."
        )

    except Exception as e:
        print_error_panel("Reset Error", f"Failed to reset cost history: {e}")
        sys.exit(1)


# Export function for CLI registration
cost_commands = register_cost_commands
