"""AI-powered change analysis for GitCo."""

import os
import re
from dataclasses import dataclass
from typing import Any, Optional, Union

import anthropic
import ollama
import openai
from rich.panel import Panel

from .config import Config, Repository
from .git_ops import GitRepository
from .utils import (
    console,
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
)


@dataclass
class SecurityUpdate:
    """Represents a detected security update."""

    type: str  # "vulnerability_fix", "authentication", "authorization", "encryption", "dependency"
    description: str
    severity: str  # "critical", "high", "medium", "low"
    cve_id: Optional[str] = None
    affected_components: Optional[list[str]] = None
    remediation_guidance: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.affected_components is None:
            self.affected_components = []


@dataclass
class Deprecation:
    """Represents a detected deprecation."""

    type: str  # "api_deprecation", "feature_deprecation", "dependency_deprecation", "config_deprecation"
    description: str
    severity: str  # "high", "medium", "low"
    replacement_suggestion: Optional[str] = None
    removal_date: Optional[str] = None
    affected_components: Optional[list[str]] = None
    migration_path: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.affected_components is None:
            self.affected_components = []


@dataclass
class BreakingChange:
    """Represents a detected breaking change."""

    type: str
    description: str
    severity: str  # "high", "medium", "low"
    affected_components: list[str]
    migration_guidance: Optional[str] = None


@dataclass
class ChangeAnalysis:
    """Result of AI change analysis."""

    summary: str
    breaking_changes: list[str]
    new_features: list[str]
    bug_fixes: list[str]
    security_updates: list[str]
    deprecations: list[str]
    recommendations: list[str]
    confidence: float
    detailed_breaking_changes: Optional[list[BreakingChange]] = None
    detailed_security_updates: Optional[list[SecurityUpdate]] = None
    detailed_deprecations: Optional[list[Deprecation]] = None


@dataclass
class AnalysisRequest:
    """Request for change analysis."""

    repository: Repository
    git_repo: GitRepository
    diff_content: str
    commit_messages: list[str]
    custom_prompt: Optional[str] = None


class SecurityDeprecationDetector:
    """Enhanced security update and deprecation detection."""

    def __init__(self) -> None:
        """Initialize the security and deprecation detector."""
        self.logger = get_logger()

        # Security update patterns
        self.security_patterns = {
            "vulnerability_fix": [
                r"CVE-\d{4}-\d+",
                r"vulnerability",
                r"security\s+fix",
                r"security\s+patch",
                r"security\s+update",
                r"buffer\s+overflow",
                r"sql\s+injection",
                r"xss",
                r"cross-site\s+scripting",
                r"authentication\s+bypass",
                r"privilege\s+escalation",
                r"remote\s+code\s+execution",
                r"rce",
                r"denial\s+of\s+service",
                r"dos",
                r"ddos",
            ],
            "authentication": [
                r"auth",
                r"authentication",
                r"login",
                r"password",
                r"token",
                r"jwt",
                r"oauth",
                r"session",
                r"csrf",
                r"csrf\s+token",
            ],
            "authorization": [
                r"authorization",
                r"permission",
                r"role",
                r"access\s+control",
                r"rbac",
                r"acl",
                r"privilege",
                r"admin",
                r"user\s+role",
            ],
            "encryption": [
                r"encrypt",
                r"decrypt",
                r"hash",
                r"sha",
                r"md5",
                r"bcrypt",
                r"pbkdf2",
                r"aes",
                r"rsa",
                r"ssl",
                r"tls",
                r"certificate",
                r"private\s+key",
                r"public\s+key",
            ],
            "dependency": [
                r"dependency\s+update",
                r"package\s+update",
                r"npm\s+audit",
                r"pip\s+audit",
                r"cargo\s+audit",
                r"go\s+mod\s+tidy",
                r"security\s+dependency",
            ],
        }

        # Deprecation patterns
        self.deprecation_patterns = {
            "api_deprecation": [
                r"@deprecated",
                r"DeprecationWarning",
                r"deprecated",
                r"deprecation",
                r"obsolete",
                r"legacy",
                r"old\s+api",
                r"removed",
                r"will\s+be\s+removed",
                r"sunset",
            ],
            "feature_deprecation": [
                r"feature\s+deprecated",
                r"functionality\s+deprecated",
                r"option\s+deprecated",
                r"setting\s+deprecated",
                r"parameter\s+deprecated",
            ],
            "dependency_deprecation": [
                r"dependency\s+deprecated",
                r"package\s+deprecated",
                r"library\s+deprecated",
                r"version\s+deprecated",
            ],
            "config_deprecation": [
                r"config\s+deprecated",
                r"setting\s+deprecated",
                r"option\s+deprecated",
                r"environment\s+variable\s+deprecated",
            ],
        }

        # Severity indicators
        self.critical_severity_patterns = [
            r"critical",
            r"severe",
            r"high\s+priority",
            r"urgent",
            r"immediate",
        ]

        self.high_severity_patterns = [
            r"high",
            r"important",
            r"significant",
            r"major",
        ]

        self.medium_severity_patterns = [
            r"medium",
            r"moderate",
            r"standard",
        ]

    def detect_security_updates(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[SecurityUpdate]:
        """Detect security updates in diff content and commit messages.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            List of detected security updates.
        """
        security_updates = []

        # Analyze commit messages for security indicators
        for message in commit_messages:
            security_updates.extend(self._analyze_commit_for_security(message))

        # Analyze diff content for security changes
        security_updates.extend(self._analyze_diff_for_security(diff_content))

        return security_updates

    def detect_deprecations(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[Deprecation]:
        """Detect deprecations in diff content and commit messages.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            List of detected deprecations.
        """
        deprecations = []

        # Analyze commit messages for deprecation indicators
        for message in commit_messages:
            deprecations.extend(self._analyze_commit_for_deprecation(message))

        # Analyze diff content for deprecation changes
        deprecations.extend(self._analyze_diff_for_deprecation(diff_content))

        return deprecations

    def _analyze_commit_for_security(self, message: str) -> list[SecurityUpdate]:
        """Analyze a commit message for security indicators.

        Args:
            message: Commit message to analyze.

        Returns:
            List of detected security updates.
        """
        security_updates = []
        message_lower = message.lower()

        # Check for CVE references
        cve_matches = re.findall(r"CVE-\d{4}-\d+", message, re.IGNORECASE)
        for cve_id in cve_matches:
            security_updates.append(
                SecurityUpdate(
                    type="vulnerability_fix",
                    description=f"Security vulnerability fix: {cve_id}",
                    severity="critical",
                    cve_id=cve_id,
                    affected_components=["unknown"],
                )
            )

        # Check for security patterns
        for security_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    severity = self._determine_security_severity(message_lower)
                    security_updates.append(
                        SecurityUpdate(
                            type=security_type,
                            description=f"Security update detected: {message}",
                            severity=severity,
                            affected_components=["unknown"],
                        )
                    )
                    break

        return security_updates

    def _analyze_commit_for_deprecation(self, message: str) -> list[Deprecation]:
        """Analyze a commit message for deprecation indicators.

        Args:
            message: Commit message to analyze.

        Returns:
            List of detected deprecations.
        """
        deprecations = []
        message_lower = message.lower()

        # Check for deprecation patterns
        for deprecation_type, patterns in self.deprecation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    severity = self._determine_deprecation_severity(message_lower)
                    deprecations.append(
                        Deprecation(
                            type=deprecation_type,
                            description=f"Deprecation detected: {message}",
                            severity=severity,
                            affected_components=["unknown"],
                        )
                    )
                    break

        return deprecations

    def _analyze_diff_for_security(self, diff_content: str) -> list[SecurityUpdate]:
        """Analyze diff content for security changes.

        Args:
            diff_content: Git diff content.

        Returns:
            List of detected security updates.
        """
        security_updates = []
        diff_lower = diff_content.lower()

        # Check for security-related file changes
        security_files = [
            "security",
            "auth",
            "authentication",
            "authorization",
            "encryption",
            "password",
            "token",
            "certificate",
            "key",
            "ssl",
            "tls",
        ]

        for security_file in security_files:
            if security_file in diff_lower:
                security_updates.append(
                    SecurityUpdate(
                        type="security_file_change",
                        description=f"Security-related file modified: {security_file}",
                        severity="medium",
                        affected_components=["security"],
                    )
                )

        # Check for specific security patterns in code
        for security_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, diff_lower, re.IGNORECASE):
                    severity = self._determine_security_severity(diff_lower)
                    security_updates.append(
                        SecurityUpdate(
                            type=security_type,
                            description=f"Security code change detected: {pattern}",
                            severity=severity,
                            affected_components=["code"],
                        )
                    )

        return security_updates

    def _analyze_diff_for_deprecation(self, diff_content: str) -> list[Deprecation]:
        """Analyze diff content for deprecation changes.

        Args:
            diff_content: Git diff content.

        Returns:
            List of detected deprecations.
        """
        deprecations = []
        diff_lower = diff_content.lower()

        # Check for deprecation patterns in code
        for deprecation_type, patterns in self.deprecation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, diff_lower, re.IGNORECASE):
                    severity = self._determine_deprecation_severity(diff_lower)
                    deprecations.append(
                        Deprecation(
                            type=deprecation_type,
                            description=f"Deprecation code change detected: {pattern}",
                            severity=severity,
                            affected_components=["code"],
                        )
                    )

        return deprecations

    def _determine_security_severity(self, text: str) -> str:
        """Determine the severity of a security update.

        Args:
            text: Text to analyze.

        Returns:
            Severity level.
        """
        text_lower = text.lower()

        if any(pattern in text_lower for pattern in self.critical_severity_patterns):
            return "critical"
        elif any(pattern in text_lower for pattern in self.high_severity_patterns):
            return "high"
        elif any(pattern in text_lower for pattern in self.medium_severity_patterns):
            return "medium"
        else:
            return "low"

    def _determine_deprecation_severity(self, text: str) -> str:
        """Determine the severity of a deprecation.

        Args:
            text: Text to analyze.

        Returns:
            Severity level.
        """
        text_lower = text.lower()

        if "removed" in text_lower or "breaking" in text_lower:
            return "high"
        elif "deprecated" in text_lower or "obsolete" in text_lower:
            return "medium"
        else:
            return "low"


class BreakingChangeDetector:
    """Enhanced breaking change detection using pattern analysis."""

    def __init__(self) -> None:
        """Initialize the breaking change detector."""
        self.logger = get_logger()

        # Common breaking change patterns
        self.breaking_patterns = {
            "api_signature": [
                r"def\s+\w+\s*\([^)]*\)\s*->\s*[^:]+:",  # Function signature changes
                r"class\s+\w+\s*\([^)]*\):",  # Class definition changes
                r"@\w+\([^)]*\)",  # Decorator changes
            ],
            "configuration": [
                r"config\.",
                r"settings\.",
                r"\.env",
                r"\.ini",
                r"\.toml",
                r"\.yaml",
                r"\.yml",
            ],
            "database": [
                r"migration",
                r"schema",
                r"ALTER\s+TABLE",
                r"DROP\s+TABLE",
                r"CREATE\s+TABLE",
                r"INDEX",
            ],
            "dependencies": [
                r"requirements\.txt",
                r"pyproject\.toml",
                r"setup\.py",
                r"package\.json",
                r"Gemfile",
                r"go\.mod",
            ],
            "deprecation": [
                r"@deprecated",
                r"DeprecationWarning",
                r"deprecated",
                r"removed",
                r"obsolete",
            ],
            "security": [
                r"security",
                r"vulnerability",
                r"CVE-",
                r"authentication",
                r"authorization",
            ],
        }

        # High severity indicators
        self.high_severity_patterns = [
            r"BREAKING CHANGE",
            r"breaking change",
            r"major version",
            r"incompatible",
            r"removed",
            r"deleted",
        ]

        # Medium severity indicators
        self.medium_severity_patterns = [
            r"deprecated",
            r"deprecation",
            r"changed",
            r"modified",
            r"updated",
        ]

    def detect_breaking_changes(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[BreakingChange]:
        """Detect breaking changes in diff content and commit messages.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            List of detected breaking changes.
        """
        breaking_changes = []

        # Analyze commit messages for breaking change indicators
        for message in commit_messages:
            breaking_changes.extend(self._analyze_commit_message(message))

        # Analyze diff content for breaking changes
        breaking_changes.extend(self._analyze_diff_content(diff_content))

        return breaking_changes

    def _analyze_commit_message(self, message: str) -> list[BreakingChange]:
        """Analyze a commit message for breaking change indicators.

        Args:
            message: Commit message to analyze.

        Returns:
            List of detected breaking changes.
        """
        breaking_changes = []
        message_lower = message.lower()

        # Check for explicit breaking change indicators (highest priority)
        if any(
            pattern.lower() in message_lower for pattern in self.high_severity_patterns
        ):
            breaking_changes.append(
                BreakingChange(
                    type="explicit_breaking_change",
                    description=f"Explicit breaking change mentioned: {message}",
                    severity="high",
                    affected_components=["unknown"],
                )
            )

        # Check for deprecation indicators
        elif any(
            pattern.lower() in message_lower
            for pattern in self.breaking_patterns["deprecation"]
        ):
            breaking_changes.append(
                BreakingChange(
                    type="deprecation",
                    description=f"Deprecation mentioned: {message}",
                    severity="medium",
                    affected_components=["unknown"],
                )
            )

        # Check for security-related changes
        elif any(
            pattern.lower() in message_lower
            for pattern in self.breaking_patterns["security"]
        ):
            breaking_changes.append(
                BreakingChange(
                    type="security_change",
                    description=f"Security-related change: {message}",
                    severity="high",
                    affected_components=["security"],
                )
            )

        return breaking_changes

    def _analyze_diff_content(self, diff_content: str) -> list[BreakingChange]:
        """Analyze diff content for breaking changes.

        Args:
            diff_content: Git diff content.

        Returns:
            List of detected breaking changes.
        """
        breaking_changes = []

        # Parse diff content to extract file changes
        lines = diff_content.split("\n")
        current_file = None
        file_changes: dict[str, dict] = {}

        for line in lines:
            if line.startswith("diff --git"):
                # Extract filename
                parts = line.split()
                if len(parts) >= 3:
                    current_file = parts[2].replace("a/", "").replace("b/", "")
                    file_changes[current_file] = {"additions": 0, "deletions": 0}
            elif line.startswith("+") and current_file:
                file_changes[current_file]["additions"] += 1
            elif line.startswith("-") and current_file:
                file_changes[current_file]["deletions"] += 1

        # Analyze each file for breaking changes
        for filename, changes in file_changes.items():
            breaking_changes.extend(self._analyze_file_changes(filename, changes))

        return breaking_changes

    def _analyze_file_changes(
        self, filename: str, changes: dict
    ) -> list[BreakingChange]:
        """Analyze file changes for breaking changes.

        Args:
            filename: Name of the changed file.
            changes: Dictionary containing change information.

        Returns:
            List of detected breaking changes.
        """
        breaking_changes = []

        # Check for API signature changes
        if self._has_api_signature_changes(filename):
            breaking_changes.append(
                BreakingChange(
                    type="api_signature_change",
                    description=f"API signature changes detected in {filename}",
                    severity="high",
                    affected_components=["api"],
                    migration_guidance="Review API usage and update method calls",
                )
            )

        # Check for configuration changes
        if self._has_configuration_changes(filename, filename):
            breaking_changes.append(
                BreakingChange(
                    type="configuration_change",
                    description=f"Configuration changes detected in {filename}",
                    severity="medium",
                    affected_components=["configuration"],
                    migration_guidance="Update configuration files and environment variables",
                )
            )

        # Check for database changes
        if self._has_database_changes(filename, filename):
            breaking_changes.append(
                BreakingChange(
                    type="database_change",
                    description=f"Database schema changes detected in {filename}",
                    severity="high",
                    affected_components=["database"],
                    migration_guidance="Run database migrations and update queries",
                )
            )

        # Check for dependency changes
        if self._has_dependency_changes(filename, filename):
            breaking_changes.append(
                BreakingChange(
                    type="dependency_change",
                    description=f"Dependency changes detected in {filename}",
                    severity="medium",
                    affected_components=["dependencies"],
                    migration_guidance="Update dependencies and test compatibility",
                )
            )

        return breaking_changes

    def _has_api_signature_changes(self, content: str) -> bool:
        """Check if content contains API signature changes.

        Args:
            content: Content to check.

        Returns:
            True if API signature changes are detected.
        """
        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.breaking_patterns["api_signature"]
        )

    def _has_configuration_changes(self, filename: str, content: str) -> bool:
        """Check if content contains configuration changes.

        Args:
            filename: Name of the file.
            content: Content to check.

        Returns:
            True if configuration changes are detected.
        """
        # Check filename patterns
        config_patterns = [
            r"\.env",
            r"\.ini",
            r"\.toml",
            r"\.yaml",
            r"\.yml",
            r"config",
            r"settings",
        ]
        if any(
            re.search(pattern, filename, re.IGNORECASE) for pattern in config_patterns
        ):
            return True

        # Check content patterns
        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.breaking_patterns["configuration"]
        )

    def _has_database_changes(self, filename: str, content: str) -> bool:
        """Check if content contains database changes.

        Args:
            filename: Name of the file.
            content: Content to check.

        Returns:
            True if database changes are detected.
        """
        # Check filename patterns
        db_patterns = [
            r"migration",
            r"schema",
            r"\.sql",
            r"database",
        ]
        if any(re.search(pattern, filename, re.IGNORECASE) for pattern in db_patterns):
            return True

        # Check content patterns
        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.breaking_patterns["database"]
        )

    def _has_dependency_changes(self, filename: str, content: str) -> bool:
        """Check if content contains dependency changes.

        Args:
            filename: Name of the file.
            content: Content to check.

        Returns:
            True if dependency changes are detected.
        """
        # Check filename patterns
        dep_patterns = [
            r"requirements\.txt",
            r"pyproject\.toml",
            r"setup\.py",
            r"package\.json",
            r"Gemfile",
            r"go\.mod",
            r"Cargo\.toml",
        ]
        if any(re.search(pattern, filename, re.IGNORECASE) for pattern in dep_patterns):
            return True

        # Check content patterns
        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.breaking_patterns["dependencies"]
        )


class OpenAIAnalyzer:
    """OpenAI API integration for change analysis."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI analyzer.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: OpenAI model to use for analysis.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        self.logger = get_logger()
        self.breaking_detector = BreakingChangeDetector()
        self.security_deprecation_detector = SecurityDeprecationDetector()

    def analyze_changes(self, request: AnalysisRequest) -> ChangeAnalysis:
        """Analyze repository changes using OpenAI.

        Args:
            request: Analysis request containing repository and change data.

        Returns:
            Analysis result with categorized changes and recommendations.

        Raises:
            Exception: If analysis fails.
        """
        log_operation_start(
            "OpenAI change analysis",
            repo=request.repository.name,
            model=self.model,
        )

        try:
            # Use enhanced breaking change detection
            detected_breaking_changes = self.breaking_detector.detect_breaking_changes(
                request.diff_content, request.commit_messages
            )
            detected_security_updates = (
                self.security_deprecation_detector.detect_security_updates(
                    request.diff_content, request.commit_messages
                )
            )
            detected_deprecations = (
                self.security_deprecation_detector.detect_deprecations(
                    request.diff_content, request.commit_messages
                )
            )

            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(
                request,
                detected_breaking_changes,
                detected_security_updates,
                detected_deprecations,
            )

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            # Parse the response
            response_content = response.choices[0].message.content
            if response_content is None:
                raise ValueError("Empty response from OpenAI")
            analysis = self._parse_analysis_response(response_content)

            # Add detailed breaking changes to the analysis
            analysis.detailed_breaking_changes = detected_breaking_changes
            analysis.detailed_security_updates = detected_security_updates
            analysis.detailed_deprecations = detected_deprecations

            # Enhance breaking changes list with detected changes
            if detected_breaking_changes:
                enhanced_breaking_changes = analysis.breaking_changes.copy()
                for change in detected_breaking_changes:
                    enhanced_breaking_changes.append(
                        f"{change.type}: {change.description}"
                    )
                analysis.breaking_changes = enhanced_breaking_changes

            log_operation_success(
                "OpenAI change analysis",
                repo=request.repository.name,
                confidence=analysis.confidence,
            )

            return analysis

        except Exception as e:
            log_operation_failure(
                "OpenAI change analysis",
                repo=request.repository.name,
                error=e,
            )
            raise

    def _build_analysis_prompt(
        self,
        request: AnalysisRequest,
        detected_breaking_changes: list[BreakingChange],
        detected_security_updates: list[SecurityUpdate],
        detected_deprecations: list[Deprecation],
    ) -> str:
        """Build the analysis prompt for OpenAI.

        Args:
            request: Analysis request.
            detected_breaking_changes: List of detected breaking changes.
            detected_security_updates: List of detected security updates.
            detected_deprecations: List of detected deprecations.

        Returns:
            Formatted prompt string.
        """
        repo = request.repository
        diff_content = request.diff_content
        commit_messages = request.commit_messages

        # Build commit summary
        commit_summary = "\n".join([f"- {msg}" for msg in commit_messages])

        # Simple diff analysis
        diff_analysis = "Standard code changes"
        if diff_content:
            lines = diff_content.splitlines()
            file_count = sum(1 for line in lines if line.startswith("diff --git"))
            if file_count > 0:
                diff_analysis = f"Files changed: {file_count}"

        # Build breaking change context
        breaking_context = ""
        if detected_breaking_changes:
            breaking_context = "\n\nDetected Breaking Changes:\n"
            for change in detected_breaking_changes:
                breaking_context += (
                    f"- {change.type} ({change.severity}): {change.description}\n"
                )
                if change.migration_guidance:
                    breaking_context += f"  Migration: {change.migration_guidance}\n"

        # Build security update context
        security_context = ""
        if detected_security_updates:
            security_context = "\n\nDetected Security Updates:\n"
            for update in detected_security_updates:
                security_context += (
                    f"- {update.type} ({update.severity}): {update.description}\n"
                )
                if update.cve_id:
                    security_context += f"  CVE: {update.cve_id}\n"
                if update.affected_components:
                    security_context += (
                        f"  Affected: {', '.join(update.affected_components)}\n"
                    )
                if update.remediation_guidance:
                    security_context += (
                        f"  Remediation: {update.remediation_guidance}\n"
                    )

        # Build deprecation context
        deprecation_context = ""
        if detected_deprecations:
            deprecation_context = "\n\nDetected Deprecations:\n"
            for deprecation in detected_deprecations:
                deprecation_context += f"- {deprecation.type} ({deprecation.severity}): {deprecation.description}\n"
                if deprecation.replacement_suggestion:
                    deprecation_context += (
                        f"  Replacement: {deprecation.replacement_suggestion}\n"
                    )
                if deprecation.removal_date:
                    deprecation_context += (
                        f"  Removal Date: {deprecation.removal_date}\n"
                    )
                if deprecation.affected_components:
                    deprecation_context += (
                        f"  Affected: {', '.join(deprecation.affected_components)}\n"
                    )
                if deprecation.migration_path:
                    deprecation_context += (
                        f"  Migration Path: {deprecation.migration_path}\n"
                    )

        prompt = f"""
Analyze the following changes for repository: {repo.name}
Repository: {repo.fork} -> {repo.upstream}
Skills: {', '.join(repo.skills)}

Changes Summary:
{commit_summary}

Diff Analysis:
{diff_analysis}
{breaking_context}
{security_context}
{deprecation_context}

Diff Content:
{diff_content}

Please provide a comprehensive analysis of these changes, with special attention to breaking changes. Focus on:

BREAKING CHANGE DETECTION:
- API signature changes (function/class definitions, decorators)
- Configuration file modifications
- Database schema changes
- Dependency updates and version changes
- Deprecated features or removed functionality
- Security-related changes that might affect existing code

For each detected breaking change, provide:
- Clear description of what changed
- Impact assessment (high/medium/low severity)
- Migration guidance for affected code
- Testing recommendations

Please provide a comprehensive analysis of these changes, including:
1. Summary of changes - A clear, concise summary of what changed
2. Breaking changes - Any changes that could break existing code or APIs (be thorough)
3. New features - New functionality or capabilities added
4. Bug fixes - Issues that were resolved
5. Security updates - Security-related changes or vulnerabilities addressed
6. Deprecations - Any deprecated features or APIs
7. Recommendations - Suggestions for contributors or users

Focus on:
- Code quality and maintainability implications
- Performance impact of changes
- Potential areas for contribution
- Migration guidance if needed
- Testing recommendations

Format your response as JSON with the following structure:
{{
    "summary": "Brief summary of changes",
    "breaking_changes": ["list", "of", "breaking", "changes"],
    "new_features": ["list", "of", "new", "features"],
    "bug_fixes": ["list", "of", "bug", "fixes"],
    "security_updates": ["list", "of", "security", "updates"],
    "deprecations": ["list", "of", "deprecations"],
    "recommendations": ["list", "of", "recommendations"],
    "confidence": 0.85
}}
"""

        if request.custom_prompt:
            prompt += f"\nAdditional Context: {request.custom_prompt}"

        return prompt

    def _get_system_prompt(self) -> str:
        """Get the system prompt for OpenAI.

        Returns:
            System prompt string.
        """
        return """You are an expert software developer and open source contributor specializing in breaking change detection and security analysis.
Your task is to analyze code changes and provide insights that help developers understand:
- What changed and why
- Potential impact on existing code
- Breaking changes that require immediate attention
- Security updates and vulnerability fixes
- Deprecations and migration paths
- Opportunities for contribution
- Security and stability implications

Be thorough in detecting breaking changes, security updates, and deprecations. Look for:

BREAKING CHANGES:
- API signature modifications
- Configuration file changes
- Database schema updates
- Dependency version changes
- Deprecated or removed functionality

SECURITY UPDATES:
- CVE references and vulnerability fixes
- Authentication and authorization changes
- Encryption and security algorithm updates
- Security-related dependency updates
- Input validation and sanitization improvements
- Session management and token handling changes

DEPRECATIONS:
- API deprecations with replacement suggestions
- Feature deprecations with migration paths
- Dependency deprecations with upgrade guidance
- Configuration deprecations with new format instructions
- Removal dates and sunset schedules

Pay special attention to:
- Critical security vulnerabilities (CVE-YYYY-NNNN)
- High-priority security patches
- Authentication bypass fixes
- Authorization improvements
- Encryption algorithm updates
- Input validation enhancements
- Session security improvements

For deprecations, identify:
- What is being deprecated
- When it will be removed
- What to use instead
- Migration steps required

Be concise but thorough. Focus on actionable insights that help developers make informed decisions about contributing to the project, migrating their code, and addressing security concerns."""

    def _parse_analysis_response(self, response: str) -> ChangeAnalysis:
        """Parse OpenAI response into structured analysis.

        Args:
            response: Raw response from OpenAI.

        Returns:
            Structured analysis result.
        """
        try:
            # Try to extract JSON from response
            import json
            import re

            # Find JSON in the response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback to manual parsing
                data = self._parse_text_response(response)

            return ChangeAnalysis(
                summary=data.get("summary", "Analysis completed"),
                breaking_changes=data.get("breaking_changes", []),
                new_features=data.get("new_features", []),
                bug_fixes=data.get("bug_fixes", []),
                security_updates=data.get("security_updates", []),
                deprecations=data.get("deprecations", []),
                recommendations=data.get("recommendations", []),
                confidence=data.get("confidence", 0.5),
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse OpenAI response: {e}")
            # Return a basic analysis
            return ChangeAnalysis(
                summary="Analysis completed (parsing failed)",
                breaking_changes=[],
                new_features=[],
                bug_fixes=[],
                security_updates=[],
                deprecations=[],
                recommendations=["Review changes manually"],
                confidence=0.3,
            )

    def _parse_text_response(self, response: str) -> dict[str, Any]:
        """Parse text response when JSON parsing fails.

        Args:
            response: Text response from OpenAI.

        Returns:
            Parsed data dictionary.
        """
        # Simple text parsing as fallback
        lines = response.split("\n")
        data: dict[str, Any] = {
            "summary": "Analysis completed",
            "breaking_changes": [],
            "new_features": [],
            "bug_fixes": [],
            "security_updates": [],
            "deprecations": [],
            "recommendations": [],
            "confidence": 0.5,
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for summary line
            if "summary" in line.lower() and ":" in line:
                summary_part = line.split(":", 1)
                if len(summary_part) > 1:
                    data["summary"] = summary_part[1].strip()
                current_section = "summary"
            elif (
                "breaking" in line.lower() and "change" in line.lower() and ":" in line
            ):
                current_section = "breaking_changes"
            elif "new" in line.lower() and "feature" in line.lower() and ":" in line:
                current_section = "new_features"
            elif "bug" in line.lower() and "fix" in line.lower() and ":" in line:
                current_section = "bug_fixes"
            elif (
                "security" in line.lower() and "update" in line.lower() and ":" in line
            ):
                current_section = "security_updates"
            elif "deprecat" in line.lower() and ":" in line:
                current_section = "deprecations"
            elif "recommend" in line.lower() and ":" in line:
                current_section = "recommendations"
            elif line.startswith("-") or line.startswith("*"):
                if current_section and current_section != "summary":
                    item = line[1:].strip()
                    if item:  # Only add non-empty items
                        if current_section in data and isinstance(
                            data[current_section], list
                        ):
                            data[current_section].append(item)

        return data


class AnthropicAnalyzer:
    """Anthropic Claude API integration for change analysis."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"
    ):
        """Initialize Anthropic analyzer.

        Args:
            api_key: Anthropic API key. If None, will try to get from environment.
            model: Anthropic model to use for analysis.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )

        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = get_logger()
        self.breaking_detector = BreakingChangeDetector()
        self.security_deprecation_detector = SecurityDeprecationDetector()

    def analyze_changes(self, request: AnalysisRequest) -> ChangeAnalysis:
        """Analyze repository changes using Anthropic Claude.

        Args:
            request: Analysis request containing repository and change data.

        Returns:
            Analysis result with categorized changes and recommendations.

        Raises:
            Exception: If analysis fails.
        """
        log_operation_start(
            "Anthropic change analysis",
            repo=request.repository.name,
            model=self.model,
        )

        try:
            # Use enhanced breaking change detection
            detected_breaking_changes = self.breaking_detector.detect_breaking_changes(
                request.diff_content, request.commit_messages
            )
            detected_security_updates = (
                self.security_deprecation_detector.detect_security_updates(
                    request.diff_content, request.commit_messages
                )
            )
            detected_deprecations = (
                self.security_deprecation_detector.detect_deprecations(
                    request.diff_content, request.commit_messages
                )
            )

            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(
                request,
                detected_breaking_changes,
                detected_security_updates,
                detected_deprecations,
            )

            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Parse the response
            first_content = response.content[0]
            if not hasattr(first_content, "text"):
                raise ValueError(
                    "Invalid response content from Anthropic - no text attribute"
                )

            response_content = first_content.text
            if not isinstance(response_content, str):
                raise ValueError(
                    "Invalid response content from Anthropic - text is not a string"
                )
            analysis = self._parse_analysis_response(response_content)

            # Add detailed breaking changes to the analysis
            analysis.detailed_breaking_changes = detected_breaking_changes
            analysis.detailed_security_updates = detected_security_updates
            analysis.detailed_deprecations = detected_deprecations

            # Enhance breaking changes list with detected changes
            if detected_breaking_changes:
                enhanced_breaking_changes = analysis.breaking_changes.copy()
                for change in detected_breaking_changes:
                    enhanced_breaking_changes.append(
                        f"{change.type}: {change.description}"
                    )
                analysis.breaking_changes = enhanced_breaking_changes

            log_operation_success(
                "Anthropic change analysis",
                repo=request.repository.name,
                confidence=analysis.confidence,
            )

            return analysis

        except Exception as e:
            log_operation_failure(
                "Anthropic change analysis",
                repo=request.repository.name,
                error=e,
            )
            raise

    def _build_analysis_prompt(
        self,
        request: AnalysisRequest,
        detected_breaking_changes: list[BreakingChange],
        detected_security_updates: list[SecurityUpdate],
        detected_deprecations: list[Deprecation],
    ) -> str:
        """Build the analysis prompt for Anthropic.

        Args:
            request: Analysis request.
            detected_breaking_changes: List of detected breaking changes.
            detected_security_updates: List of detected security updates.
            detected_deprecations: List of detected deprecations.

        Returns:
            Formatted prompt string.
        """
        repo = request.repository
        diff_content = request.diff_content
        commit_messages = request.commit_messages

        # Build commit summary
        commit_summary = "\n".join([f"- {msg}" for msg in commit_messages])

        # Simple diff analysis
        diff_analysis = "Standard code changes"
        if diff_content:
            lines = diff_content.splitlines()
            file_count = sum(1 for line in lines if line.startswith("diff --git"))
            if file_count > 0:
                diff_analysis = f"Files changed: {file_count}"

        # Build breaking change context
        breaking_context = ""
        if detected_breaking_changes:
            breaking_context = "\n\nDetected Breaking Changes:\n"
            for change in detected_breaking_changes:
                breaking_context += (
                    f"- {change.type} ({change.severity}): {change.description}\n"
                )
                if change.migration_guidance:
                    breaking_context += f"  Migration: {change.migration_guidance}\n"

        # Build security update context
        security_context = ""
        if detected_security_updates:
            security_context = "\n\nDetected Security Updates:\n"
            for update in detected_security_updates:
                security_context += (
                    f"- {update.type} ({update.severity}): {update.description}\n"
                )
                if update.cve_id:
                    security_context += f"  CVE: {update.cve_id}\n"
                if update.affected_components:
                    security_context += (
                        f"  Affected: {', '.join(update.affected_components)}\n"
                    )
                if update.remediation_guidance:
                    security_context += (
                        f"  Remediation: {update.remediation_guidance}\n"
                    )

        # Build deprecation context
        deprecation_context = ""
        if detected_deprecations:
            deprecation_context = "\n\nDetected Deprecations:\n"
            for deprecation in detected_deprecations:
                deprecation_context += f"- {deprecation.type} ({deprecation.severity}): {deprecation.description}\n"
                if deprecation.replacement_suggestion:
                    deprecation_context += (
                        f"  Replacement: {deprecation.replacement_suggestion}\n"
                    )
                if deprecation.removal_date:
                    deprecation_context += (
                        f"  Removal Date: {deprecation.removal_date}\n"
                    )
                if deprecation.affected_components:
                    deprecation_context += (
                        f"  Affected: {', '.join(deprecation.affected_components)}\n"
                    )
                if deprecation.migration_path:
                    deprecation_context += (
                        f"  Migration Path: {deprecation.migration_path}\n"
                    )

        prompt = f"""
Analyze the following changes for repository: {repo.name}
Repository: {repo.fork} -> {repo.upstream}
Skills: {', '.join(repo.skills)}

Changes Summary:
{commit_summary}

Diff Analysis:
{diff_analysis}
{breaking_context}
{security_context}
{deprecation_context}

Diff Content:
{diff_content}

Please provide a comprehensive analysis of these changes, with special attention to breaking changes. Focus on:

BREAKING CHANGE DETECTION:
- API signature changes (function/class definitions, decorators)
- Configuration file modifications
- Database schema changes
- Dependency updates and version changes
- Deprecated features or removed functionality
- Security-related changes that might affect existing code

For each detected breaking change, provide:
- Clear description of what changed
- Impact assessment (high/medium/low severity)
- Migration guidance for affected code
- Testing recommendations

Please provide a comprehensive analysis of these changes, including:
1. Summary of changes - A clear, concise summary of what changed
2. Breaking changes - Any changes that could break existing code or APIs (be thorough)
3. New features - New functionality or capabilities added
4. Bug fixes - Issues that were resolved
5. Security updates - Security-related changes or vulnerabilities addressed
6. Deprecations - Any deprecated features or APIs
7. Recommendations - Suggestions for contributors or users

Focus on:
- Code quality and maintainability implications
- Performance impact of changes
- Potential areas for contribution
- Migration guidance if needed
- Testing recommendations

Format your response as JSON with the following structure:
{{
    "summary": "Brief summary of changes",
    "breaking_changes": ["list", "of", "breaking", "changes"],
    "new_features": ["list", "of", "new", "features"],
    "bug_fixes": ["list", "of", "bug", "fixes"],
    "security_updates": ["list", "of", "security", "updates"],
    "deprecations": ["list", "of", "deprecations"],
    "recommendations": ["list", "of", "recommendations"],
    "confidence": 0.85
}}
"""

        if request.custom_prompt:
            prompt += f"\nAdditional Context: {request.custom_prompt}"

        return prompt

    def _get_system_prompt(self) -> str:
        """Get the system prompt for Anthropic.

        Returns:
            System prompt string.
        """
        return """You are an expert software developer and open source contributor specializing in breaking change detection and security analysis.
Your task is to analyze code changes and provide insights that help developers understand:
- What changed and why
- Potential impact on existing code
- Breaking changes that require immediate attention
- Security updates and vulnerability fixes
- Deprecations and migration paths
- Opportunities for contribution
- Security and stability implications

Be thorough in detecting breaking changes, security updates, and deprecations. Look for:

BREAKING CHANGES:
- API signature modifications
- Configuration file changes
- Database schema updates
- Dependency version changes
- Deprecated or removed functionality

SECURITY UPDATES:
- CVE references and vulnerability fixes
- Authentication and authorization changes
- Encryption and security algorithm updates
- Security-related dependency updates
- Input validation and sanitization improvements
- Session management and token handling changes

DEPRECATIONS:
- API deprecations with replacement suggestions
- Feature deprecations with migration paths
- Dependency deprecations with upgrade guidance
- Configuration deprecations with new format instructions
- Removal dates and sunset schedules

Pay special attention to:
- Critical security vulnerabilities (CVE-YYYY-NNNN)
- High-priority security patches
- Authentication bypass fixes
- Authorization improvements
- Encryption algorithm updates
- Input validation enhancements
- Session security improvements

For deprecations, identify:
- What is being deprecated
- When it will be removed
- What to use instead
- Migration steps required

Be concise but thorough. Focus on actionable insights that help developers make informed decisions about contributing to the project, migrating their code, and addressing security concerns."""

    def _parse_analysis_response(self, response: str) -> ChangeAnalysis:
        """Parse Anthropic response into structured analysis.

        Args:
            response: Raw response from Anthropic.

        Returns:
            Structured analysis result.
        """
        try:
            # Try to extract JSON from response
            import json
            import re

            # Find JSON in the response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback to manual parsing
                data = self._parse_text_response(response)

            return ChangeAnalysis(
                summary=data.get("summary", "Analysis completed"),
                breaking_changes=data.get("breaking_changes", []),
                new_features=data.get("new_features", []),
                bug_fixes=data.get("bug_fixes", []),
                security_updates=data.get("security_updates", []),
                deprecations=data.get("deprecations", []),
                recommendations=data.get("recommendations", []),
                confidence=data.get("confidence", 0.5),
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse Anthropic response: {e}")
            # Return a basic analysis
            return ChangeAnalysis(
                summary="Analysis completed (parsing failed)",
                breaking_changes=[],
                new_features=[],
                bug_fixes=[],
                security_updates=[],
                deprecations=[],
                recommendations=["Review changes manually"],
                confidence=0.3,
            )

    def _parse_text_response(self, response: str) -> dict[str, Any]:
        """Parse text response when JSON parsing fails.

        Args:
            response: Text response from Anthropic.

        Returns:
            Parsed data dictionary.
        """
        # Simple text parsing as fallback
        lines = response.split("\n")
        data: dict[str, Any] = {
            "summary": "Analysis completed",
            "breaking_changes": [],
            "new_features": [],
            "bug_fixes": [],
            "security_updates": [],
            "deprecations": [],
            "recommendations": [],
            "confidence": 0.5,
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for summary line
            if "summary" in line.lower() and ":" in line:
                summary_part = line.split(":", 1)
                if len(summary_part) > 1:
                    data["summary"] = summary_part[1].strip()
                current_section = "summary"
            elif (
                "breaking" in line.lower() and "change" in line.lower() and ":" in line
            ):
                current_section = "breaking_changes"
            elif "new" in line.lower() and "feature" in line.lower() and ":" in line:
                current_section = "new_features"
            elif "bug" in line.lower() and "fix" in line.lower() and ":" in line:
                current_section = "bug_fixes"
            elif (
                "security" in line.lower() and "update" in line.lower() and ":" in line
            ):
                current_section = "security_updates"
            elif "deprecat" in line.lower() and ":" in line:
                current_section = "deprecations"
            elif "recommend" in line.lower() and ":" in line:
                current_section = "recommendations"
            elif line.startswith("-") or line.startswith("*"):
                if current_section and current_section != "summary":
                    item = line[1:].strip()
                    if item:  # Only add non-empty items
                        if current_section in data and isinstance(
                            data[current_section], list
                        ):
                            data[current_section].append(item)

        return data


class OllamaAnalyzer:
    """Ollama local LLM integration for change analysis."""

    def __init__(
        self,
        model: str = "llama2",
        host: str = "http://localhost:11434",
        timeout: int = 120,
    ):
        """Initialize Ollama analyzer.

        Args:
            model: Ollama model to use for analysis.
            host: Ollama server host.
            timeout: Request timeout in seconds.
        """
        self.model = model
        self.host = host
        self.timeout = timeout
        self.client = ollama.Client(host=host)
        self.logger = get_logger()
        self.breaking_detector = BreakingChangeDetector()
        self.security_deprecation_detector = SecurityDeprecationDetector()

    def analyze_changes(self, request: AnalysisRequest) -> ChangeAnalysis:
        """Analyze repository changes using Ollama.

        Args:
            request: Analysis request containing repository and change data.

        Returns:
            Analysis result with categorized changes and recommendations.

        Raises:
            Exception: If analysis fails.
        """
        log_operation_start(
            "Ollama change analysis",
            repo=request.repository.name,
            model=self.model,
        )

        try:
            # Use enhanced breaking change detection
            detected_breaking_changes = self.breaking_detector.detect_breaking_changes(
                request.diff_content, request.commit_messages
            )
            detected_security_updates = (
                self.security_deprecation_detector.detect_security_updates(
                    request.diff_content, request.commit_messages
                )
            )
            detected_deprecations = (
                self.security_deprecation_detector.detect_deprecations(
                    request.diff_content, request.commit_messages
                )
            )

            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(
                request,
                detected_breaking_changes,
                detected_security_updates,
                detected_deprecations,
            )

            # Call Ollama API
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                options={
                    "temperature": 0.3,
                    "num_predict": 2000,
                },
            )

            # Parse the response
            response_content = response.message.content
            if response_content is None:
                raise ValueError("Empty response from Ollama")
            analysis = self._parse_analysis_response(response_content)

            # Add detailed breaking changes to the analysis
            analysis.detailed_breaking_changes = detected_breaking_changes
            analysis.detailed_security_updates = detected_security_updates
            analysis.detailed_deprecations = detected_deprecations

            # Enhance breaking changes list with detected changes
            if detected_breaking_changes:
                enhanced_breaking_changes = analysis.breaking_changes.copy()
                for change in detected_breaking_changes:
                    enhanced_breaking_changes.append(
                        f"{change.type}: {change.description}"
                    )
                analysis.breaking_changes = enhanced_breaking_changes

            log_operation_success(
                "Ollama change analysis",
                repo=request.repository.name,
                confidence=analysis.confidence,
            )

            return analysis

        except Exception as e:
            log_operation_failure(
                "Ollama change analysis",
                repo=request.repository.name,
                error=e,
            )
            raise

    def _build_analysis_prompt(
        self,
        request: AnalysisRequest,
        detected_breaking_changes: list[BreakingChange],
        detected_security_updates: list[SecurityUpdate],
        detected_deprecations: list[Deprecation],
    ) -> str:
        """Build the analysis prompt for Ollama.

        Args:
            request: Analysis request.
            detected_breaking_changes: List of detected breaking changes.
            detected_security_updates: List of detected security updates.
            detected_deprecations: List of detected deprecations.

        Returns:
            Formatted prompt string.
        """
        repo = request.repository
        diff_content = request.diff_content
        commit_messages = request.commit_messages

        # Build commit summary
        commit_summary = "\n".join([f"- {msg}" for msg in commit_messages])

        # Simple diff analysis
        diff_analysis = "Standard code changes"
        if diff_content:
            lines = diff_content.splitlines()
            file_count = sum(1 for line in lines if line.startswith("diff --git"))
            if file_count > 0:
                diff_analysis = f"Files changed: {file_count}"

        # Build breaking change context
        breaking_context = ""
        if detected_breaking_changes:
            breaking_context = "\n\nDetected Breaking Changes:\n"
            for change in detected_breaking_changes:
                breaking_context += (
                    f"- {change.type} ({change.severity}): {change.description}\n"
                )
                if change.migration_guidance:
                    breaking_context += f"  Migration: {change.migration_guidance}\n"

        # Build security update context
        security_context = ""
        if detected_security_updates:
            security_context = "\n\nDetected Security Updates:\n"
            for update in detected_security_updates:
                security_context += (
                    f"- {update.type} ({update.severity}): {update.description}\n"
                )
                if update.cve_id:
                    security_context += f"  CVE: {update.cve_id}\n"
                if update.affected_components:
                    security_context += (
                        f"  Affected: {', '.join(update.affected_components)}\n"
                    )
                if update.remediation_guidance:
                    security_context += (
                        f"  Remediation: {update.remediation_guidance}\n"
                    )

        # Build deprecation context
        deprecation_context = ""
        if detected_deprecations:
            deprecation_context = "\n\nDetected Deprecations:\n"
            for deprecation in detected_deprecations:
                deprecation_context += f"- {deprecation.type} ({deprecation.severity}): {deprecation.description}\n"
                if deprecation.replacement_suggestion:
                    deprecation_context += (
                        f"  Replacement: {deprecation.replacement_suggestion}\n"
                    )
                if deprecation.removal_date:
                    deprecation_context += (
                        f"  Removal Date: {deprecation.removal_date}\n"
                    )
                if deprecation.affected_components:
                    deprecation_context += (
                        f"  Affected: {', '.join(deprecation.affected_components)}\n"
                    )
                if deprecation.migration_path:
                    deprecation_context += (
                        f"  Migration Path: {deprecation.migration_path}\n"
                    )

        prompt = f"""
Analyze the following changes for repository: {repo.name}
Repository: {repo.fork} -> {repo.upstream}
Skills: {', '.join(repo.skills)}

Changes Summary:
{commit_summary}

Diff Analysis:
{diff_analysis}
{breaking_context}
{security_context}
{deprecation_context}

Diff Content:
{diff_content}

Please provide a comprehensive analysis of these changes, with special attention to breaking changes. Focus on:

BREAKING CHANGE DETECTION:
- API signature changes (function/class definitions, decorators)
- Configuration file modifications
- Database schema changes
- Dependency updates and version changes
- Deprecated features or removed functionality
- Security-related changes that might affect existing code

For each detected breaking change, provide:
- Clear description of what changed
- Impact assessment (high/medium/low severity)
- Migration guidance for affected code
- Testing recommendations

Please provide a comprehensive analysis of these changes, including:
1. Summary of changes - A clear, concise summary of what changed
2. Breaking changes - Any changes that could break existing code or APIs (be thorough)
3. New features - New functionality or capabilities added
4. Bug fixes - Issues that were resolved
5. Security updates - Security-related changes or vulnerabilities addressed
6. Deprecations - Any deprecated features or APIs
7. Recommendations - Suggestions for contributors or users

Focus on:
- Code quality and maintainability implications
- Performance impact of changes
- Potential areas for contribution
- Migration guidance if needed
- Testing recommendations

Format your response as JSON with the following structure:
{{
    "summary": "Brief summary of changes",
    "breaking_changes": ["list", "of", "breaking", "changes"],
    "new_features": ["list", "of", "new", "features"],
    "bug_fixes": ["list", "of", "bug", "fixes"],
    "security_updates": ["list", "of", "security", "updates"],
    "deprecations": ["list", "of", "deprecations"],
    "recommendations": ["list", "of", "recommendations"],
    "confidence": 0.85
}}
"""

        if request.custom_prompt:
            prompt += f"\nAdditional Context: {request.custom_prompt}"

        return prompt

    def _get_system_prompt(self) -> str:
        """Get the system prompt for Ollama.

        Returns:
            System prompt string.
        """
        return """You are an expert software developer and open source contributor specializing in breaking change detection and security analysis.
Your task is to analyze code changes and provide insights that help developers understand:
- What changed and why
- Potential impact on existing code
- Breaking changes that require immediate attention
- Security updates and vulnerability fixes
- Deprecations and migration paths
- Opportunities for contribution
- Security and stability implications

Be thorough in detecting breaking changes, security updates, and deprecations. Look for:

BREAKING CHANGES:
- API signature modifications
- Configuration file changes
- Database schema updates
- Dependency version changes
- Deprecated or removed functionality

SECURITY UPDATES:
- CVE references and vulnerability fixes
- Authentication and authorization changes
- Encryption and security algorithm updates
- Security-related dependency updates
- Input validation and sanitization improvements
- Session management and token handling changes

DEPRECATIONS:
- API deprecations with replacement suggestions
- Feature deprecations with migration paths
- Dependency deprecations with upgrade guidance
- Configuration deprecations with new format instructions
- Removal dates and sunset schedules

Pay special attention to:
- Critical security vulnerabilities (CVE-YYYY-NNNN)
- High-priority security patches
- Authentication bypass fixes
- Authorization improvements
- Encryption algorithm updates
- Input validation enhancements
- Session security improvements

For deprecations, identify:
- What is being deprecated
- When it will be removed
- What to use instead
- Migration steps required

Be concise but thorough. Focus on actionable insights that help developers make informed decisions about contributing to the project, migrating their code, and addressing security concerns."""

    def _parse_analysis_response(self, response: str) -> ChangeAnalysis:
        """Parse Ollama response into structured analysis.

        Args:
            response: Raw response from Ollama.

        Returns:
            Structured analysis result.
        """
        try:
            # Try to extract JSON from response
            import json
            import re

            # Find JSON in the response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback to manual parsing
                data = self._parse_text_response(response)

            return ChangeAnalysis(
                summary=data.get("summary", "Analysis completed"),
                breaking_changes=data.get("breaking_changes", []),
                new_features=data.get("new_features", []),
                bug_fixes=data.get("bug_fixes", []),
                security_updates=data.get("security_updates", []),
                deprecations=data.get("deprecations", []),
                recommendations=data.get("recommendations", []),
                confidence=data.get("confidence", 0.5),
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse Ollama response: {e}")
            # Return a basic analysis
            return ChangeAnalysis(
                summary="Analysis completed (parsing failed)",
                breaking_changes=[],
                new_features=[],
                bug_fixes=[],
                security_updates=[],
                deprecations=[],
                recommendations=["Review changes manually"],
                confidence=0.3,
            )

    def _parse_text_response(self, response: str) -> dict[str, Any]:
        """Parse text response when JSON parsing fails.

        Args:
            response: Text response from Ollama.

        Returns:
            Parsed data dictionary.
        """
        # Simple text parsing as fallback
        lines = response.split("\n")
        data: dict[str, Any] = {
            "summary": "Analysis completed",
            "breaking_changes": [],
            "new_features": [],
            "bug_fixes": [],
            "security_updates": [],
            "deprecations": [],
            "recommendations": [],
            "confidence": 0.5,
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for summary line
            if "summary" in line.lower() and ":" in line:
                summary_part = line.split(":", 1)
                if len(summary_part) > 1:
                    data["summary"] = summary_part[1].strip()
                current_section = "summary"
            elif (
                "breaking" in line.lower() and "change" in line.lower() and ":" in line
            ):
                current_section = "breaking_changes"
            elif "new" in line.lower() and "feature" in line.lower() and ":" in line:
                current_section = "new_features"
            elif "bug" in line.lower() and "fix" in line.lower() and ":" in line:
                current_section = "bug_fixes"
            elif (
                "security" in line.lower() and "update" in line.lower() and ":" in line
            ):
                current_section = "security_updates"
            elif "deprecat" in line.lower() and ":" in line:
                current_section = "deprecations"
            elif "recommend" in line.lower() and ":" in line:
                current_section = "recommendations"
            elif line.startswith("-") or line.startswith("*"):
                if current_section and current_section != "summary":
                    item = line[1:].strip()
                    if item:  # Only add non-empty items
                        if current_section in data and isinstance(
                            data[current_section], list
                        ):
                            data[current_section].append(item)

        return data


class ChangeAnalyzer:
    """Main change analyzer that coordinates analysis operations."""

    def __init__(self, config: Config):
        """Initialize change analyzer.

        Args:
            config: GitCo configuration.
        """
        self.config = config
        self.logger = get_logger()
        self.analyzers: dict[
            str, Union[OpenAIAnalyzer, AnthropicAnalyzer, OllamaAnalyzer]
        ] = {}
        self.security_deprecation_detector = SecurityDeprecationDetector()

    def get_analyzer(
        self, provider: str = "openai"
    ) -> Union[OpenAIAnalyzer, AnthropicAnalyzer, OllamaAnalyzer]:
        """Get analyzer for specified provider.

        Args:
            provider: LLM provider name.

        Returns:
            Configured analyzer instance.

        Raises:
            ValueError: If provider is not supported.
        """
        if provider not in self.analyzers:
            if provider == "openai":
                api_key = os.getenv(self.config.settings.api_key_env)
                self.analyzers[provider] = OpenAIAnalyzer(api_key=api_key)
            elif provider == "anthropic":
                api_key = os.getenv(self.config.settings.api_key_env)
                self.analyzers[provider] = AnthropicAnalyzer(api_key=api_key)
            elif provider == "ollama":
                # Get Ollama configuration from settings
                ollama_host = getattr(
                    self.config.settings, "ollama_host", "http://localhost:11434"
                )
                ollama_model = getattr(self.config.settings, "ollama_model", "llama2")
                self.analyzers[provider] = OllamaAnalyzer(
                    model=ollama_model, host=ollama_host
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

        return self.analyzers[provider]

    def analyze_repository_changes(
        self,
        repository: Repository,
        git_repo: GitRepository,
        custom_prompt: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Optional[ChangeAnalysis]:
        """Analyze changes for a repository.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            custom_prompt: Optional custom analysis prompt.
            provider: Optional LLM provider to use (overrides config default).

        Returns:
            Analysis result or None if analysis is disabled.
        """
        if not self.config.settings.analysis_enabled or not repository.analysis_enabled:
            self.logger.info(f"Analysis disabled for repository: {repository.name}")
            return None

        try:
            # Get recent changes
            diff_content = git_repo.get_recent_changes()
            commit_messages = git_repo.get_recent_commit_messages()

            if not diff_content and not commit_messages:
                self.logger.info(
                    f"No changes to analyze for repository: {repository.name}"
                )
                return None

            # Create analysis request
            request = AnalysisRequest(
                repository=repository,
                git_repo=git_repo,
                diff_content=diff_content,
                commit_messages=commit_messages,
                custom_prompt=custom_prompt,
            )

            # Get analyzer and perform analysis
            selected_provider = provider or self.config.settings.llm_provider
            analyzer = self.get_analyzer(selected_provider)
            return analyzer.analyze_changes(request)

        except Exception as e:
            self.logger.error(f"Failed to analyze repository {repository.name}: {e}")
            return None

    def analyze_specific_commit(
        self,
        repository: Repository,
        git_repo: GitRepository,
        commit_hash: str,
        custom_prompt: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Optional[ChangeAnalysis]:
        """Analyze a specific commit in detail.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            commit_hash: Hash of the commit to analyze.
            custom_prompt: Optional custom analysis prompt.
            provider: Optional LLM provider to use (overrides config default).

        Returns:
            Analysis result or None if analysis fails.
        """
        if not self.config.settings.analysis_enabled or not repository.analysis_enabled:
            self.logger.info(f"Analysis disabled for repository: {repository.name}")
            return None

        try:
            # Get detailed commit analysis
            commit_analysis = git_repo.get_commit_diff_analysis(commit_hash)
            if not commit_analysis:
                self.logger.warning(f"Could not get analysis for commit {commit_hash}")
                return None

            # Create analysis request with commit-specific data
            request = AnalysisRequest(
                repository=repository,
                git_repo=git_repo,
                diff_content=commit_analysis.get("diff_content", ""),
                commit_messages=[commit_analysis.get("message", "")],
                custom_prompt=custom_prompt,
            )

            # Get analyzer and perform analysis
            selected_provider = provider or self.config.settings.llm_provider
            analyzer = self.get_analyzer(selected_provider)
            analysis = analyzer.analyze_changes(request)

            # Enhance analysis with commit metadata
            if analysis:
                analysis.summary = f"Commit {commit_hash[:8]}: {analysis.summary}"
                if commit_analysis.get("files_changed"):
                    analysis.recommendations.append(
                        f"Files changed: {', '.join(commit_analysis['files_changed'][:5])}"
                    )
                if commit_analysis.get("insertions") or commit_analysis.get(
                    "deletions"
                ):
                    analysis.recommendations.append(
                        f"Lines: +{commit_analysis.get('insertions', 0)} -{commit_analysis.get('deletions', 0)}"
                    )

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze commit {commit_hash}: {e}")
            return None

    def get_commit_summary(
        self,
        repository: Repository,
        git_repo: GitRepository,
        num_commits: int = 5,
    ) -> dict[str, Any]:
        """Get a summary of recent commits without full AI analysis.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            num_commits: Number of recent commits to summarize.

        Returns:
            Dictionary containing commit summary information.
        """
        try:
            commit_messages = git_repo.get_recent_commit_messages(num_commits)
            diff_content = git_repo.get_recent_changes(num_commits)

            # Basic analysis without AI
            summary = {
                "repository": repository.name,
                "total_commits": len(commit_messages),
                "commit_messages": commit_messages,
                "has_changes": bool(diff_content),
                "change_summary": self._analyze_diff_content(diff_content),
                "last_commit": commit_messages[0] if commit_messages else None,
                "commit_types": self._categorize_commits(commit_messages),
            }

            return summary

        except Exception as e:
            self.logger.error(
                f"Failed to get commit summary for {repository.name}: {e}"
            )
            return {}

    def _categorize_commits(self, commit_messages: list[str]) -> dict[str, int]:
        """Categorize commits by type based on commit message patterns.

        Args:
            commit_messages: List of commit messages.

        Returns:
            Dictionary with commit categories and counts.
        """
        categories = {
            "feature": 0,
            "fix": 0,
            "docs": 0,
            "refactor": 0,
            "test": 0,
            "chore": 0,
            "other": 0,
        }

        for message in commit_messages:
            message_lower = message.lower()

            # Use more specific patterns to avoid double counting
            if message_lower.startswith("feat:") or "feature:" in message_lower:
                categories["feature"] += 1
            elif message_lower.startswith("fix:") or "bug:" in message_lower:
                categories["fix"] += 1
            elif (
                message_lower.startswith("doc:")
                or "docs:" in message_lower
                or "readme" in message_lower
            ):
                categories["docs"] += 1
            elif message_lower.startswith("refactor:") or "clean" in message_lower:
                categories["refactor"] += 1
            elif message_lower.startswith("test:") or "spec" in message_lower:
                categories["test"] += 1
            elif (
                message_lower.startswith("chore:")
                or "update" in message_lower
                or "bump" in message_lower
            ):
                categories["chore"] += 1
            else:
                categories["other"] += 1

        return categories

    def _analyze_diff_content(self, diff_content: str) -> str:
        """Analyze diff content to provide better context for AI analysis.

        Args:
            diff_content: Raw diff content.

        Returns:
            Analysis summary of the diff content.
        """
        if not diff_content:
            return "No diff content available."

        lines = diff_content.splitlines()
        analysis_parts = []

        # Count file types
        file_extensions: dict[str, int] = {}
        total_files = 0
        total_insertions = 0
        total_deletions = 0

        for line in lines:
            if line.startswith("diff --git"):
                total_files += 1
                # Extract file extension
                parts = line.split()
                if len(parts) >= 3:
                    filename = parts[2]
                    if "." in filename:
                        ext = filename.split(".")[-1]
                        file_extensions[ext] = file_extensions.get(ext, 0) + 1
            elif line.startswith("+") and not line.startswith("+++"):
                total_insertions += 1
            elif line.startswith("-") and not line.startswith("---"):
                total_deletions += 1

        # Build analysis summary
        if total_files > 0:
            analysis_parts.append(f"Files changed: {total_files}")

        if total_insertions > 0 or total_deletions > 0:
            analysis_parts.append(f"Lines: +{total_insertions} -{total_deletions}")

        if file_extensions:
            top_extensions = sorted(
                file_extensions.items(), key=lambda x: x[1], reverse=True
            )[:3]
            ext_summary = ", ".join(
                [f"{ext} ({count})" for ext, count in top_extensions]
            )
            analysis_parts.append(f"File types: {ext_summary}")

        # Look for specific patterns
        if any("test" in line.lower() for line in lines):
            analysis_parts.append("Contains test changes")

        if any("doc" in line.lower() or "readme" in line.lower() for line in lines):
            analysis_parts.append("Contains documentation changes")

        if any("config" in line.lower() or "setup" in line.lower() for line in lines):
            analysis_parts.append("Contains configuration changes")

        return " | ".join(analysis_parts) if analysis_parts else "Standard code changes"

    def display_analysis(self, analysis: ChangeAnalysis, repository_name: str) -> None:
        """Display analysis results in a formatted way.

        Args:
            analysis: Analysis result to display.
            repository_name: Name of the analyzed repository.
        """
        console.print(
            f"\n[bold blue]Analysis Results for {repository_name}[/bold blue]"
        )
        console.print(f"Confidence: {analysis.confidence:.1%}\n")

        # Summary
        if analysis.summary:
            console.print(Panel(analysis.summary, title="Summary", border_style="blue"))

        # Detailed breaking changes
        if analysis.detailed_breaking_changes:
            console.print("\n[bold red]🚨 Detailed Breaking Changes:[/bold red]")
            for change in analysis.detailed_breaking_changes:
                # Color code by severity
                breaking_severity_color_map: dict[str, str] = {
                    "high": "red",
                    "medium": "yellow",
                    "low": "blue",
                }
                breaking_severity_color: str = breaking_severity_color_map.get(
                    change.severity, "white"
                )

                console.print(
                    f"  • [{breaking_severity_color}]{change.type}[/{breaking_severity_color}] ({change.severity.upper()}): {change.description}"
                )
                if change.affected_components and change.affected_components != [
                    "unknown"
                ]:
                    console.print(
                        f"    Affected: {', '.join(change.affected_components)}"
                    )
                if change.migration_guidance:
                    console.print(f"    Migration: {change.migration_guidance}")

        # Detailed security updates
        if analysis.detailed_security_updates:
            console.print("\n[bold red]🔒 Detailed Security Updates:[/bold red]")
            for update in analysis.detailed_security_updates:
                # Color code by severity
                security_severity_color_map: dict[str, str] = {
                    "critical": "bright_red",
                    "high": "red",
                    "medium": "yellow",
                    "low": "blue",
                }
                security_severity_color: str = security_severity_color_map.get(
                    update.severity, "white"
                )

                console.print(
                    f"  • [{security_severity_color}]{update.type}[/{security_severity_color}] ({update.severity.upper()}): {update.description}"
                )
                if update.cve_id:
                    console.print(f"    CVE: [bold red]{update.cve_id}[/bold red]")
                if update.affected_components and update.affected_components != [
                    "unknown"
                ]:
                    console.print(
                        f"    Affected: {', '.join(update.affected_components)}"
                    )
                if update.remediation_guidance:
                    console.print(f"    Remediation: {update.remediation_guidance}")

        # Detailed deprecations
        if analysis.detailed_deprecations:
            console.print("\n[bold orange]⚠️  Detailed Deprecations:[/bold orange]")
            for deprecation in analysis.detailed_deprecations:
                # Color code by severity
                deprecation_severity_color_map: dict[str, str] = {
                    "high": "red",
                    "medium": "yellow",
                    "low": "blue",
                }
                deprecation_severity_color: str = deprecation_severity_color_map.get(
                    deprecation.severity, "white"
                )

                console.print(
                    f"  • [{deprecation_severity_color}]{deprecation.type}[/{deprecation_severity_color}] ({deprecation.severity.upper()}): {deprecation.description}"
                )
                if deprecation.replacement_suggestion:
                    console.print(
                        f"    Replacement: [green]{deprecation.replacement_suggestion}[/green]"
                    )
                if deprecation.removal_date:
                    console.print(
                        f"    Removal Date: [yellow]{deprecation.removal_date}[/yellow]"
                    )
                if (
                    deprecation.affected_components
                    and deprecation.affected_components != ["unknown"]
                ):
                    console.print(
                        f"    Affected: {', '.join(deprecation.affected_components)}"
                    )
                if deprecation.migration_path:
                    console.print(f"    Migration Path: {deprecation.migration_path}")

        # Breaking changes (legacy format)
        if analysis.breaking_changes:
            console.print("\n[bold red]⚠️  Breaking Changes:[/bold red]")
            for breaking_change in analysis.breaking_changes:
                console.print(f"  • {breaking_change}")

        # New features
        if analysis.new_features:
            console.print("\n[bold green]✨ New Features:[/bold green]")
            for feature in analysis.new_features:
                console.print(f"  • {feature}")

        # Bug fixes
        if analysis.bug_fixes:
            console.print("\n[bold yellow]🐛 Bug Fixes:[/bold yellow]")
            for fix in analysis.bug_fixes:
                console.print(f"  • {fix}")

        # Security updates (legacy format)
        if analysis.security_updates:
            console.print("\n[bold red]🔒 Security Updates:[/bold red]")
            for security_update in analysis.security_updates:
                console.print(f"  • {security_update}")

        # Deprecations (legacy format)
        if analysis.deprecations:
            console.print("\n[bold orange]⚠️  Deprecations:[/bold orange]")
            for deprecation_item in analysis.deprecations:
                console.print(f"  • {deprecation_item}")

        # Recommendations
        if analysis.recommendations:
            console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
            for rec in analysis.recommendations:
                console.print(f"  • {rec}")

        console.print()  # Add spacing
