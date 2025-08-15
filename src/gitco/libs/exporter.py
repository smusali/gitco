"""Export functionality for GitCo."""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..utils.common import get_logger, print_error_panel, print_success_panel


def export_sync_results(
    sync_data: dict[str, Any], export_path: str, repo_name: Optional[str] = None
) -> None:
    """Export sync results to a JSON file.

    Args:
        sync_data: Dictionary containing sync results
        export_path: Path to export the JSON file
        repo_name: Optional repository name for single repo exports
    """
    try:
        # Prepare export data structure
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "sync_metadata": {
                "total_repositories": sync_data.get("total_repositories", 0),
                "successful_syncs": sync_data.get("successful_syncs", 0),
                "failed_syncs": sync_data.get("failed_syncs", 0),
                "total_time": sync_data.get("total_time", 0),
                "batch_mode": sync_data.get("batch_mode", False),
                "analysis_enabled": sync_data.get("analysis_enabled", False),
                "max_workers": sync_data.get("max_workers", 1),
            },
            "summary": {
                "overall_status": sync_data.get("overall_status", "unknown"),
                "total_repositories": sync_data.get("total_repositories", 0),
                "successful_syncs": sync_data.get("successful_syncs", 0),
                "failed_syncs": sync_data.get("failed_syncs", 0),
                "success_rate": sync_data.get("success_rate", 0.0),
                "total_duration": sync_data.get("total_duration", 0.0),
                "errors": sync_data.get("errors", []),
                "warnings": sync_data.get("warnings", []),
            },
            "repository_results": sync_data.get("repository_results", []),
        }

        # Add single repository info if provided
        if repo_name:
            export_data["single_repository"] = {
                "name": repo_name,
                "sync_result": (
                    sync_data.get("repository_results", [{}])[0]
                    if sync_data.get("repository_results")
                    else {}
                ),
            }

        # Write to file
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

        print_success_panel(
            "Export Successful",
            f"Sync report exported to: {export_path}",
        )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to export sync results: {e}")
        print_error_panel(
            "Export Failed",
            f"Failed to export sync results: {str(e)}",
        )


def export_discovery_results(recommendations: Any, export_path: str) -> None:
    """Export discovery results to a file.

    Args:
        recommendations: List of recommendation objects
        export_path: Path to export the file
    """
    try:
        # Convert recommendations to serializable format
        export_data = []
        for recommendation in recommendations:
            export_data.append(
                {
                    "issue": {
                        "number": recommendation.issue.number,
                        "title": recommendation.issue.title,
                        "state": recommendation.issue.state,
                        "labels": recommendation.issue.labels,
                        "html_url": recommendation.issue.html_url,
                        "created_at": recommendation.issue.created_at,
                        "updated_at": recommendation.issue.updated_at,
                    },
                    "repository": {
                        "name": recommendation.repository.name,
                        "fork": recommendation.repository.fork,
                        "upstream": recommendation.repository.upstream,
                        "language": recommendation.repository.language,
                    },
                    "skill_matches": [
                        {
                            "skill": match.skill,
                            "confidence": match.confidence,
                            "match_type": match.match_type,
                            "evidence": match.evidence,
                        }
                        for match in recommendation.skill_matches
                    ],
                    "overall_score": recommendation.overall_score,
                    "difficulty_level": recommendation.difficulty_level,
                    "estimated_time": recommendation.estimated_time,
                    "tags": recommendation.tags,
                }
            )

        # Write to file
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print_success_panel(
            "Export Successful",
            f"Discovery results exported to: {export_path}",
        )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to export discovery results: {e}")
        print_error_panel(
            "Export Failed",
            f"Failed to export results: {str(e)}",
        )


def export_contribution_data_to_csv(
    contributions: list[Any], export_path: str, include_stats: bool = True
) -> None:
    """Export contribution data to CSV format.

    Args:
        contributions: List of Contribution objects
        export_path: Path to export the CSV file
        include_stats: Whether to include summary statistics
    """
    try:
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "Repository",
                    "Issue Number",
                    "Issue Title",
                    "Issue URL",
                    "Contribution Type",
                    "Status",
                    "Created At",
                    "Updated At",
                    "Skills Used",
                    "Impact Score",
                    "Labels",
                    "Milestone",
                    "Assignees",
                    "Comments Count",
                    "Reactions Count",
                ]
            )

            # Write contribution data
            for contribution in contributions:
                writer.writerow(
                    [
                        contribution.repository,
                        contribution.issue_number,
                        contribution.issue_title,
                        contribution.issue_url,
                        contribution.contribution_type,
                        contribution.status,
                        contribution.created_at,
                        contribution.updated_at,
                        "; ".join(contribution.skills_used),
                        f"{contribution.impact_score:.3f}",
                        "; ".join(contribution.labels),
                        contribution.milestone or "",
                        "; ".join(contribution.assignees),
                        contribution.comments_count,
                        contribution.reactions_count,
                    ]
                )

        # If include_stats is True, create a separate stats CSV file
        if include_stats and contributions:
            stats_file = export_file.with_suffix(".stats.csv")
            with open(stats_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Calculate basic stats
                total_contributions = len(contributions)
                open_contributions = len(
                    [c for c in contributions if c.status == "open"]
                )
                closed_contributions = len(
                    [c for c in contributions if c.status == "closed"]
                )
                merged_contributions = len(
                    [c for c in contributions if c.status == "merged"]
                )

                repositories = {c.repository for c in contributions}
                skills = set()
                for c in contributions:
                    skills.update(c.skills_used)

                total_impact = sum(c.impact_score for c in contributions)
                avg_impact = (
                    total_impact / total_contributions if total_contributions > 0 else 0
                )

                # Write stats header
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Contributions", total_contributions])
                writer.writerow(["Open Contributions", open_contributions])
                writer.writerow(["Closed Contributions", closed_contributions])
                writer.writerow(["Merged Contributions", merged_contributions])
                writer.writerow(["Unique Repositories", len(repositories)])
                writer.writerow(["Unique Skills", len(skills)])
                writer.writerow(["Total Impact Score", f"{total_impact:.3f}"])
                writer.writerow(["Average Impact Score", f"{avg_impact:.3f}"])
                writer.writerow(["Export Date", datetime.now().isoformat()])

        print_success_panel(
            "CSV Export Successful",
            f"Contribution data exported to: {export_path}",
        )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to export contribution data: {e}")
        print_error_panel(
            "CSV Export Failed",
            f"Failed to export contribution data: {str(e)}",
        )


def export_health_data(
    repositories: Any, health_calculator: Any, export_path: str
) -> None:
    """Export health data to JSON format.

    Args:
        repositories: List of repository objects
        health_calculator: Health calculator instance
        export_path: Path to export the JSON file
    """
    try:
        # Calculate health metrics for all repositories
        health_data = []
        for repo in repositories:
            metrics = health_calculator.calculate_repository_health(repo)
            health_data.append(
                {
                    "name": repo.name,
                    "path": repo.local_path,
                    "health_score": metrics.health_score,
                    "health_status": metrics.health_status,
                    "activity_metrics": {
                        "commit_count": metrics.activity_metrics.commit_count,
                        "contributor_count": metrics.activity_metrics.contributor_count,
                        "last_commit_days": metrics.activity_metrics.last_commit_days,
                    },
                    "github_metrics": {
                        "stars": metrics.github_metrics.stars,
                        "forks": metrics.github_metrics.forks,
                        "issues": metrics.github_metrics.issues,
                        "language": metrics.github_metrics.language,
                    },
                    "sync_health": {
                        "status": metrics.sync_health.status,
                        "last_sync_days": metrics.sync_health.last_sync_days,
                    },
                    "engagement_metrics": {
                        "contributor_engagement": metrics.engagement_metrics.contributor_engagement,
                        "issue_activity": metrics.engagement_metrics.issue_activity,
                    },
                    "trending_metrics": {
                        "growth_rate": metrics.trending_metrics.growth_rate,
                        "activity_trend": metrics.trending_metrics.activity_trend,
                    },
                }
            )

        # Create summary
        summary = health_calculator.calculate_health_summary(repositories)

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "summary": {
                "total_repositories": summary.total_repositories,
                "excellent_health": summary.excellent_health,
                "good_health": summary.good_health,
                "fair_health": summary.fair_health,
                "poor_health": summary.poor_health,
                "critical_health": summary.critical_health,
                "average_health_score": summary.average_health_score,
                "trending_repositories": summary.trending_repositories,
                "declining_repositories": summary.declining_repositories,
            },
            "repositories": health_data,
        }

        # Write to file
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print_success_panel(
            "Export Successful",
            f"Health data exported to: {export_path}",
        )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to export health data: {e}")
        print_error_panel(
            "Export Failed",
            f"Failed to export health data: {str(e)}",
        )
