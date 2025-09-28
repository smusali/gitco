"""GitCo - A simple CLI tool for intelligent OSS fork management and contribution discovery."""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "FortyOne Technologies Inc."
__email__ = "fortyone.technologies@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/41technologies/gitco"

# Import main classes for easier access
from .activity_dashboard import ActivityDashboard, ActivityMetrics
from .analyzer import ChangeAnalysis, ChangeAnalyzer
from .backup import BackupManager, BackupMetadata
from .config import Config, ConfigManager, Repository
from .contribution_tracker import Contribution, ContributionStats, ContributionTracker
from .detector import BreakingChangeDetector, SecurityDeprecationDetector
from .discovery import ContributionDiscovery
from .exporter import DataExporter
from .git_ops import GitOperations, GitRepository, GitRepositoryManager
from .github_client import GitHubClient, GitHubIssue, GitHubRepository
from .health_metrics import HealthMetrics, RepositoryHealthMetrics

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "Config",
    "Repository",
    "ConfigManager",
    "ChangeAnalyzer",
    "ChangeAnalysis",
    "BreakingChangeDetector",
    "SecurityDeprecationDetector",
    "GitOperations",
    "GitRepository",
    "GitRepositoryManager",
    "GitHubClient",
    "GitHubIssue",
    "GitHubRepository",
    "ContributionTracker",
    "Contribution",
    "ContributionStats",
    "ContributionDiscovery",
    "BackupManager",
    "BackupMetadata",
    "DataExporter",
    "ActivityDashboard",
    "ActivityMetrics",
    "HealthMetrics",
    "RepositoryHealthMetrics",
]
