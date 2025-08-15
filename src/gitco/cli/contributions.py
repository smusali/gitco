"""Contribution tracking CLI commands for GitCo.

This module contains contribution-related commands:
sync-history, stats, recommendations, export, trending.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click

from ..libs.config import get_config_manager
from ..libs.exporter import export_contribution_data_to_csv
from ..libs.github_client import create_github_client
from ..utils.common import (
    print_error_panel,
    print_info_panel,
    print_success_panel,
    print_warning_panel,
)


def register_contributions_commands(main_group):
    """Register all contributions commands with the main CLI group."""
    # Create the contributions group
    contributions_group = click.Group(
        name="contributions", help="Manage contribution history and tracking."
    )
    contributions_group.add_command(sync_history)
    contributions_group.add_command(stats)
    contributions_group.add_command(recommendations)
    contributions_group.add_command(export)
    contributions_group.add_command(trending)

    # Add the contributions group to main
    main_group.add_command(contributions_group)


@click.command()
@click.option("--username", required=True, help="GitHub username to sync")
@click.option("--force", "-f", is_flag=True, help="Force sync even if recent")
@click.option("--days", type=int, help="Sync contributions from last N days")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def sync_history(
    ctx: click.Context, username: str, force: bool, days: Optional[int], quiet: bool
) -> None:
    """Sync contribution history from GitHub."""
    print_info_panel(
        "Syncing Contribution History",
        f"Fetching contributions for user: {username}",
    )

    try:
        # Load configuration
        config_manager = get_config_manager()
        config = config_manager.load_config()

        # Create GitHub client
        github_credentials = config_manager.get_github_credentials()
        github_client = create_github_client(
            token=github_credentials.get("token"),  # type: ignore
            username=github_credentials.get("username"),  # type: ignore
            password=github_credentials.get("password"),  # type: ignore
            base_url=config.settings.github_api_url,
        )

        # Test GitHub connection
        if not github_client.test_connection():
            print_error_panel(
                "GitHub Connection Failed",
                "Unable to connect to GitHub API. Please check your credentials.",
            )
            return

        # Create contribution tracker
        from ..libs.contribution_tracker import create_contribution_tracker

        tracker = create_contribution_tracker(config, github_client)

        # Sync contributions
        tracker.sync_contributions_from_github(username, force=force, days=days)

        print_success_panel(
            "Sync Completed",
            f"✅ Successfully synced contributions for {username}",
        )

    except Exception as e:
        print_error_panel(
            "Sync Failed",
            f"An error occurred during sync: {str(e)}",
        )
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--days", type=int, help="Show stats for last N days")
@click.option("--detailed", "-d", is_flag=True, help="Detailed statistics")
@click.option("--export", help="Export stats to file (.json or .csv)")
@click.option("--quiet", "-q", is_flag=True, help="Suppress output")
@click.pass_context
def stats(
    ctx: click.Context,
    days: Optional[int],
    detailed: bool,
    export: Optional[str],
    quiet: bool,
) -> None:
    """Show contribution statistics."""
    print_info_panel(
        "Calculating Contribution Statistics",
        "Analyzing your contribution history...",
    )

    try:
        # Load configuration
        config_manager = get_config_manager()
        config = config_manager.load_config()

        # Create GitHub client
        github_credentials = config_manager.get_github_credentials()
        github_client = create_github_client(
            token=github_credentials.get("token"),  # type: ignore
            username=github_credentials.get("username"),  # type: ignore
            password=github_credentials.get("password"),  # type: ignore
            base_url=config.settings.github_api_url,
        )

        # Create contribution tracker
        from ..libs.contribution_tracker import create_contribution_tracker

        tracker = create_contribution_tracker(config, github_client)

        # Get statistics
        stats = tracker.get_contribution_stats(days)

        # Display basic statistics
        print_success_panel(
            "Contribution Statistics",
            f"📊 Total Contributions: {stats.total_contributions}\n"
            f"📈 Open: {stats.open_contributions} | Closed: {stats.closed_contributions} | Merged: {stats.merged_contributions}\n"
            f"🏢 Repositories: {stats.repositories_contributed_to}\n"
            f"💡 Skills Developed: {len(stats.skills_developed)}\n"
            f"⭐ Average Impact Score: {stats.average_impact_score:.2f}",
        )

        # Enhanced impact metrics
        if hasattr(stats, "high_impact_contributions") and (
            stats.high_impact_contributions > 0
            or getattr(stats, "critical_contributions", 0) > 0
        ):
            impact_summary = f"🔥 High Impact: {stats.high_impact_contributions}"
            if (
                hasattr(stats, "critical_contributions")
                and stats.critical_contributions > 0
            ):
                impact_summary += f" | 🚀 Critical: {stats.critical_contributions}"
            print_info_panel("Impact Metrics", impact_summary)

        # Trending analysis
        if hasattr(stats, "contribution_velocity") and stats.contribution_velocity > 0:
            velocity_trend = "📈" if stats.contribution_velocity > 0.1 else "📊"
            print_info_panel(
                "Contribution Velocity",
                f"{velocity_trend} {stats.contribution_velocity:.2f} contributions/day (30d)",
            )

        # Show skills
        if stats.skills_developed:
            skills_list = ", ".join(sorted(stats.skills_developed))
            print_info_panel(
                "Skills Developed",
                f"🎯 {skills_list}",
            )

        # Show recent activity if available
        if hasattr(stats, "recent_activity") and stats.recent_activity:
            print_info_panel(
                "Recent Activity",
                f"🕒 Last {len(stats.recent_activity)} contributions:",
            )
            for i, contribution in enumerate(stats.recent_activity[:5], 1):
                print_info_panel(
                    f"{i}. {contribution.issue_title}",
                    f"Repository: {contribution.repository}\n"
                    f"Type: {contribution.contribution_type}\n"
                    f"Status: {contribution.status}\n"
                    f"Impact: {contribution.impact_score:.2f}\n"
                    f"Skills: {', '.join(contribution.skills_used)}",
                )

        # Export if requested
        if export:
            try:
                # Determine export format based on file extension
                export_path = Path(export)
                is_csv_export = export_path.suffix.lower() == ".csv"

                if is_csv_export:
                    # Get all contributions for CSV export
                    all_contributions = tracker.load_contribution_history()

                    # Filter by days if specified
                    if days:
                        cutoff_date = datetime.now() - timedelta(days=days)
                        all_contributions = [
                            c
                            for c in all_contributions
                            if datetime.fromisoformat(c.created_at) >= cutoff_date
                        ]

                    # Export to CSV
                    export_contribution_data_to_csv(all_contributions, export)
                else:
                    # JSON export
                    export_data = {
                        "exported_at": datetime.now().isoformat(),
                        "period_days": days,
                        "statistics": {
                            "total_contributions": stats.total_contributions,
                            "open_contributions": stats.open_contributions,
                            "closed_contributions": stats.closed_contributions,
                            "merged_contributions": stats.merged_contributions,
                            "repositories_contributed_to": stats.repositories_contributed_to,
                            "skills_developed": list(stats.skills_developed),
                            "total_impact_score": stats.total_impact_score,
                            "average_impact_score": stats.average_impact_score,
                            "contribution_timeline": getattr(
                                stats, "contribution_timeline", {}
                            ),
                        },
                        "recent_activity": [
                            {
                                "repository": c.repository,
                                "issue_number": c.issue_number,
                                "issue_title": c.issue_title,
                                "contribution_type": c.contribution_type,
                                "status": c.status,
                                "impact_score": c.impact_score,
                                "skills_used": c.skills_used,
                                "created_at": c.created_at,
                                "updated_at": c.updated_at,
                            }
                            for c in getattr(stats, "recent_activity", [])
                        ],
                    }

                    with open(export, "w", encoding="utf-8") as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)

                print_success_panel(
                    "Export Successful",
                    f"✅ Statistics exported to {export}",
                )

            except Exception as e:
                print_error_panel("Export Failed", f"Failed to export statistics: {e}")

    except Exception as e:
        print_error_panel(
            "Statistics Failed",
            f"An error occurred while calculating statistics: {str(e)}",
        )
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--skill", "-s", help="Filter by skill")
@click.option("--repository", "-r", help="Filter by repository")
@click.option("--limit", "-n", type=int, default=10, help="Number of recommendations")
@click.pass_context
def recommendations(
    ctx: click.Context, skill: Optional[str], repository: Optional[str], limit: int
) -> None:
    """Show contribution recommendations based on history."""
    print_info_panel(
        "Generating Recommendations",
        "Analyzing your contribution history for personalized recommendations...",
    )

    try:
        # Load configuration
        config_manager = get_config_manager()
        config = config_manager.load_config()

        # Create GitHub client
        github_credentials = config_manager.get_github_credentials()
        github_client = create_github_client(
            token=github_credentials.get("token"),  # type: ignore
            username=github_credentials.get("username"),  # type: ignore
            password=github_credentials.get("password"),  # type: ignore
            base_url=config.settings.github_api_url,
        )

        # Create contribution tracker
        from ..libs.contribution_tracker import create_contribution_tracker

        tracker = create_contribution_tracker(config, github_client)

        # Get user skills from contributions
        stats = tracker.get_contribution_stats()
        user_skills = list(stats.skills_developed)

        if not user_skills:
            print_warning_panel(
                "No Skills Found",
                "No skills detected in your contribution history. "
                "Try syncing your contributions first with 'gitco contributions sync-history'.",
            )
            return

        # Get recommendations
        recommendations = tracker.get_contribution_recommendations(user_skills)

        # Filter by skill if specified
        if skill:
            recommendations = [
                r
                for r in recommendations
                if skill.lower() in [s.lower() for s in r.skills_used]
            ]

        # Filter by repository if specified
        if repository:
            recommendations = [
                r for r in recommendations if repository.lower() in r.repository.lower()
            ]

        # Limit results
        recommendations = recommendations[:limit]

        if not recommendations:
            print_warning_panel(
                "No Recommendations",
                "No recommendations found with the current filters.",
            )
            return

        print_success_panel(
            "Contribution Recommendations",
            f"Found {len(recommendations)} recommendations based on your skills: {', '.join(user_skills)}",
        )

        for i, recommendation in enumerate(recommendations, 1):
            print_info_panel(
                f"{i}. {recommendation.issue_title}",
                f"Repository: {recommendation.repository}\n"
                f"Type: {recommendation.contribution_type}\n"
                f"Skills: {', '.join(recommendation.skills_used)}\n"
                f"Impact Score: {recommendation.impact_score:.2f}\n"
                f"URL: {recommendation.issue_url}",
            )

    except Exception as e:
        print_error_panel(
            "Recommendations Failed",
            f"An error occurred while generating recommendations: {str(e)}",
        )
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--days", type=int, help="Export contributions from last N days")
@click.option("--output", "-o", required=True, help="Output file path (.csv or .json)")
@click.option("--include-stats", "-s", is_flag=True, help="Include summary statistics")
@click.pass_context
def export(
    ctx: click.Context, days: Optional[int], output: str, include_stats: bool
) -> None:
    """Export contribution data to CSV or JSON format."""
    print_info_panel(
        "Exporting Contribution Data",
        f"Preparing contribution data for export to {output}...",
    )

    try:
        # Load configuration
        config_manager = get_config_manager()
        config = config_manager.load_config()

        # Create GitHub client
        github_credentials = config_manager.get_github_credentials()
        github_client = create_github_client(
            token=github_credentials.get("token"),  # type: ignore
            username=github_credentials.get("username"),  # type: ignore
            password=github_credentials.get("password"),  # type: ignore
            base_url=config.settings.github_api_url,
        )

        # Create contribution tracker
        from ..libs.contribution_tracker import create_contribution_tracker

        tracker = create_contribution_tracker(config, github_client)

        # Get all contributions
        all_contributions = tracker.load_contribution_history()

        # Filter by days if specified
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            all_contributions = [
                c
                for c in all_contributions
                if datetime.fromisoformat(c.created_at) >= cutoff_date
            ]

        if not all_contributions:
            print_warning_panel(
                "No Contributions Found",
                "No contributions found for the specified period.",
            )
            return

        # Determine export format based on file extension
        export_path = Path(output)
        is_csv_export = export_path.suffix.lower() == ".csv"

        if is_csv_export:
            # Export to CSV
            export_contribution_data_to_csv(all_contributions, output, include_stats)
        else:
            # Export to JSON
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "period_days": days,
                "total_contributions": len(all_contributions),
                "contributions": [
                    {
                        "repository": c.repository,
                        "issue_number": c.issue_number,
                        "issue_title": c.issue_title,
                        "issue_url": c.issue_url,
                        "contribution_type": c.contribution_type,
                        "status": c.status,
                        "created_at": c.created_at,
                        "updated_at": c.updated_at,
                        "skills_used": c.skills_used,
                        "impact_score": c.impact_score,
                        "labels": getattr(c, "labels", []),
                        "milestone": getattr(c, "milestone", None),
                        "assignees": getattr(c, "assignees", []),
                        "comments_count": getattr(c, "comments_count", 0),
                        "reactions_count": getattr(c, "reactions_count", 0),
                    }
                    for c in all_contributions
                ],
            }

            with open(output, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        print_success_panel(
            "Export Successful",
            f"✅ Contribution data exported to {output}",
        )

    except Exception as e:
        print_error_panel(
            "Export Failed",
            f"An error occurred while exporting contribution data: {str(e)}",
        )
        if ctx.obj.get("verbose"):
            raise


@click.command()
@click.option("--days", type=int, default=30, help="Analysis period in days")
@click.option("--export", help="Export trending analysis to file (.json or .csv)")
@click.pass_context
def trending(ctx: click.Context, days: Optional[int], export: Optional[str]) -> None:
    """Show detailed trending analysis of your contributions."""
    print_info_panel(
        "Analyzing Contribution Trends",
        f"Calculating trending analysis for the last {days} days...",
    )

    try:
        # Load configuration
        config_manager = get_config_manager()
        config = config_manager.load_config()

        # Create GitHub client
        github_credentials = config_manager.get_github_credentials()
        github_client = create_github_client(
            token=github_credentials.get("token"),  # type: ignore
            username=github_credentials.get("username"),  # type: ignore
            password=github_credentials.get("password"),  # type: ignore
            base_url=config.settings.github_api_url,
        )

        # Create contribution tracker
        from ..libs.contribution_tracker import create_contribution_tracker

        tracker = create_contribution_tracker(config, github_client)

        # Get statistics with enhanced metrics
        stats = tracker.get_contribution_stats(days)

        print_success_panel(
            "Trending Analysis",
            f"📊 Analysis period: {days} days\n"
            f"🚀 Contribution velocity: {getattr(stats, 'contribution_velocity', 0):.2f} contributions/day",
        )

        # Impact trends
        if hasattr(stats, "impact_trend_30d") and hasattr(stats, "impact_trend_7d"):
            if stats.impact_trend_30d != 0 or stats.impact_trend_7d != 0:
                trend_summary = ""
                if stats.impact_trend_30d != 0:
                    trend_icon = "📈" if stats.impact_trend_30d > 0 else "📉"
                    trend_summary += (
                        f"{trend_icon} 30d trend: {stats.impact_trend_30d:+.2f} "
                    )
                if stats.impact_trend_7d != 0:
                    trend_icon = "📈" if stats.impact_trend_7d > 0 else "📉"
                    trend_summary += (
                        f"{trend_icon} 7d trend: {stats.impact_trend_7d:+.2f}"
                    )
                print_info_panel("Impact Trends", trend_summary)

        # Skills analysis
        if hasattr(stats, "trending_skills") and stats.trending_skills:
            print_info_panel(
                "🚀 Trending Skills",
                f"Skills with growing usage: {', '.join(stats.trending_skills[:5])}",
            )

        if hasattr(stats, "declining_skills") and stats.declining_skills:
            print_info_panel(
                "📉 Declining Skills",
                f"Skills with declining usage: {', '.join(stats.declining_skills[:5])}",
            )

        # Export if requested
        if export:
            try:
                export_data = {
                    "exported_at": datetime.now().isoformat(),
                    "analysis_period_days": days,
                    "trending_analysis": {
                        "contribution_velocity": getattr(
                            stats, "contribution_velocity", 0
                        ),
                        "impact_trend_30d": getattr(stats, "impact_trend_30d", 0),
                        "impact_trend_7d": getattr(stats, "impact_trend_7d", 0),
                        "trending_skills": getattr(stats, "trending_skills", []),
                        "declining_skills": getattr(stats, "declining_skills", []),
                        "skill_growth_rate": getattr(stats, "skill_growth_rate", {}),
                    },
                }

                with open(export, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                print_success_panel(
                    "Export Successful",
                    f"✅ Trending analysis exported to {export}",
                )

            except Exception as e:
                print_error_panel(
                    "Export Failed", f"Failed to export trending analysis: {e}"
                )

    except Exception as e:
        print_error_panel(
            "Trending Analysis Failed",
            f"An error occurred while analyzing trends: {str(e)}",
        )
        if ctx.obj.get("verbose"):
            raise


# Export function for CLI registration
contributions_commands = register_contributions_commands
