"""Pattern-based detection for GitCo."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..utils.common import get_logger
from .patterns import (
    BREAKING_CHANGE_PATTERNS,
    CRITICAL_SECURITY_PATTERNS,
    DEPRECATION_PATTERNS,
    HIGH_DEPRECATION_PATTERNS,
    HIGH_SECURITY_PATTERNS,
    HIGH_SEVERITY_PATTERNS,
    MEDIUM_DEPRECATION_PATTERNS,
    MEDIUM_SECURITY_PATTERNS,
    MEDIUM_SEVERITY_PATTERNS,
    SECURITY_PATTERNS,
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


class BaseDetector(ABC):
    """Base class for all pattern-based detectors.

    This class provides common functionality and defines the interface that all
    detectors must implement. It includes shared methods for pattern matching,
    severity determination, and common detection patterns.
    """

    def __init__(self) -> None:
        """Initialize the base detector."""
        self.logger = get_logger()

    @abstractmethod
    def get_detector_name(self) -> str:
        """Get the name of the detector."""
        pass

    @abstractmethod
    def get_supported_types(self) -> list[str]:
        """Get the list of supported detection types."""
        pass

    def _match_patterns(
        self, text: str, patterns: dict[str, list[str]]
    ) -> list[tuple[str, str]]:
        """Match patterns in text and return matches with their types.

        Args:
            text: Text to search in.
            patterns: Dictionary of pattern types to regex patterns.

        Returns:
            List of tuples (type, matched_text).
        """
        matches = []
        text_lower = text.lower()

        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                try:
                    matches_found = re.finditer(pattern, text_lower, re.IGNORECASE)
                    for match in matches_found:
                        matches.append((pattern_type, match.group()))
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")

        return matches

    def _determine_severity(
        self, text: str, high_patterns: list[str], medium_patterns: list[str]
    ) -> str:
        """Determine severity based on patterns in text.

        Args:
            text: Text to analyze.
            high_patterns: Patterns indicating high severity.
            medium_patterns: Patterns indicating medium severity.

        Returns:
            Severity level: "high", "medium", or "low".
        """
        text_lower = text.lower()

        # Check for high severity patterns
        for pattern in high_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "high"

        # Check for medium severity patterns
        for pattern in medium_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "medium"

        return "low"

    def _extract_affected_components(self, text: str) -> list[str]:
        """Extract affected components from text.

        Args:
            text: Text to analyze.

        Returns:
            List of affected component names.
        """
        components = []

        # Look for file names, function names, class names, etc.
        file_patterns = [
            r"(\w+\.py)",
            r"(\w+\.js)",
            r"(\w+\.ts)",
            r"(\w+\.java)",
            r"(\w+\.go)",
            r"(\w+\.rs)",
        ]

        function_patterns = [
            r"def\s+(\w+)",
            r"function\s+(\w+)",
            r"(\w+)\s*\([^)]*\)",
        ]

        class_patterns = [
            r"class\s+(\w+)",
        ]

        all_patterns = file_patterns + function_patterns + class_patterns

        for pattern in all_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            components.extend(matches)

        # Remove duplicates and filter out common words
        common_words = {
            "def",
            "function",
            "class",
            "return",
            "pass",
            "None",
            "True",
            "False",
        }
        components = list(set(components) - common_words)

        return components if components else ["unknown"]

    def _log_detection(self, detector_type: str, count: int) -> None:
        """Log detection results.

        Args:
            detector_type: Type of detection performed.
            count: Number of items detected.
        """
        self.logger.info(f"{self.get_detector_name()} detected {count} {detector_type}")


class SecurityDeprecationDetector(BaseDetector):
    """Detector for security updates and deprecations."""

    def __init__(self) -> None:
        """Initialize the security and deprecation detector."""
        super().__init__()

        # Use imported patterns
        self.security_patterns = SECURITY_PATTERNS
        self.deprecation_patterns = DEPRECATION_PATTERNS

    def get_detector_name(self) -> str:
        """Get the name of the detector."""
        return "SecurityDeprecationDetector"

    def get_supported_types(self) -> list[str]:
        """Get the list of supported detection types."""
        return ["security_update", "deprecation"]

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

        # Analyze commit messages for security updates
        for message in commit_messages:
            security_updates.extend(self._analyze_commit_for_security(message))

        # Analyze diff content for security updates
        security_updates.extend(self._analyze_diff_for_security(diff_content))

        self._log_detection("security updates", len(security_updates))
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

        # Analyze commit messages for deprecations
        for message in commit_messages:
            deprecations.extend(self._analyze_commit_for_deprecation(message))

        # Analyze diff content for deprecations
        deprecations.extend(self._analyze_diff_for_deprecation(diff_content))

        self._log_detection("deprecations", len(deprecations))
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

        # Check for explicit CVE references
        cve_matches = re.findall(r"CVE-\d{4}-\d+", message, re.IGNORECASE)
        for cve_id in cve_matches:
            severity = self._determine_security_severity(message_lower)
            security_updates.append(
                SecurityUpdate(
                    type="vulnerability_fix",
                    description=f"Security vulnerability fix: {message}",
                    severity=severity,
                    cve_id=cve_id,
                    affected_components=self._extract_affected_components(message),
                )
            )

        # Check for security patterns using base class method
        matches = self._match_patterns(message, self.security_patterns)
        for security_type, _matched_text in matches:
            severity = self._determine_security_severity(message_lower)
            security_updates.append(
                SecurityUpdate(
                    type=security_type,
                    description=f"Security update detected: {message}",
                    severity=severity,
                    affected_components=self._extract_affected_components(message),
                )
            )

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

        # Check for deprecation patterns using base class method
        matches = self._match_patterns(message, self.deprecation_patterns)
        for deprecation_type, _matched_text in matches:
            severity = self._determine_deprecation_severity(message_lower)
            deprecations.append(
                Deprecation(
                    type=deprecation_type,
                    description=f"Deprecation detected: {message}",
                    severity=severity,
                    affected_components=self._extract_affected_components(message),
                )
            )

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
                        affected_components=self._extract_affected_components(
                            diff_content
                        ),
                    )
                )

        # Check for specific security patterns using base class method
        matches = self._match_patterns(diff_content, self.security_patterns)
        for security_type, matched_text in matches:
            severity = self._determine_security_severity(diff_lower)
            security_updates.append(
                SecurityUpdate(
                    type=security_type,
                    description=f"Security code change detected: {matched_text}",
                    severity=severity,
                    affected_components=self._extract_affected_components(diff_content),
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

        # Check for deprecation patterns using base class method
        matches = self._match_patterns(diff_content, self.deprecation_patterns)
        for deprecation_type, matched_text in matches:
            severity = self._determine_deprecation_severity(diff_lower)
            deprecations.append(
                Deprecation(
                    type=deprecation_type,
                    description=f"Deprecation code change detected: {matched_text}",
                    severity=severity,
                    affected_components=self._extract_affected_components(diff_content),
                )
            )

        return deprecations

    def _determine_security_severity(self, text: str) -> str:
        """Determine security severity based on text content.

        Args:
            text: Text to analyze.

        Returns:
            Severity level: "critical", "high", "medium", or "low".
        """
        return self._determine_severity(
            text,
            CRITICAL_SECURITY_PATTERNS + HIGH_SECURITY_PATTERNS,
            MEDIUM_SECURITY_PATTERNS,
        )

    def _determine_deprecation_severity(self, text: str) -> str:
        """Determine deprecation severity based on text content.

        Args:
            text: Text to analyze.

        Returns:
            Severity level: "high", "medium", or "low".
        """
        return self._determine_severity(
            text, HIGH_DEPRECATION_PATTERNS, MEDIUM_DEPRECATION_PATTERNS
        )


class BreakingChangeDetector(BaseDetector):
    """Enhanced breaking change detection using pattern analysis."""

    def __init__(self) -> None:
        """Initialize the breaking change detector."""
        super().__init__()

        # Use imported patterns
        self.breaking_patterns = BREAKING_CHANGE_PATTERNS
        self.high_severity_patterns = HIGH_SEVERITY_PATTERNS
        self.medium_severity_patterns = MEDIUM_SEVERITY_PATTERNS

    def get_detector_name(self) -> str:
        """Get the name of the detector."""
        return "BreakingChangeDetector"

    def get_supported_types(self) -> list[str]:
        """Get the list of supported detection types."""
        return [
            "api_signature",
            "configuration",
            "database",
            "dependencies",
            "deprecation",
            "security",
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

        self._log_detection("breaking changes", len(breaking_changes))
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

        # Check for explicit breaking change indicators
        if any(
            pattern.lower() in message_lower for pattern in self.high_severity_patterns
        ):
            breaking_changes.append(
                BreakingChange(
                    type="explicit_breaking_change",
                    description=f"Explicit breaking change mentioned: {message}",
                    severity="high",
                    affected_components=self._extract_affected_components(message),
                )
            )

        # Check for breaking change patterns using base class method
        matches = self._match_patterns(message, self.breaking_patterns)
        for change_type, _matched_text in matches:
            severity = self._determine_severity(
                message, self.high_severity_patterns, self.medium_severity_patterns
            )
            breaking_changes.append(
                BreakingChange(
                    type=change_type,
                    description=f"Breaking change detected: {message}",
                    severity=severity,
                    affected_components=self._extract_affected_components(message),
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
                    affected_components=self._extract_affected_components(filename),
                    migration_guidance="Review API usage and update method calls",
                )
            )

        # Check for configuration changes
        if self._has_configuration_changes(filename, str(changes)):
            breaking_changes.append(
                BreakingChange(
                    type="configuration_change",
                    description=f"Configuration changes detected in {filename}",
                    severity="medium",
                    affected_components=self._extract_affected_components(filename),
                    migration_guidance="Review configuration settings and update as needed",
                )
            )

        # Check for database changes
        if self._has_database_changes(filename, str(changes)):
            breaking_changes.append(
                BreakingChange(
                    type="database_change",
                    description=f"Database changes detected in {filename}",
                    severity="high",
                    affected_components=self._extract_affected_components(filename),
                    migration_guidance="Review database schema and migration scripts",
                )
            )

        # Check for dependency changes
        if self._has_dependency_changes(filename, str(changes)):
            breaking_changes.append(
                BreakingChange(
                    type="dependency_change",
                    description=f"Dependency changes detected in {filename}",
                    severity="medium",
                    affected_components=self._extract_affected_components(filename),
                    migration_guidance="Review dependency updates and test compatibility",
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
        # Use base class pattern matching
        matches = self._match_patterns(
            content, {"api_signature": self.breaking_patterns["api_signature"]}
        )
        return len(matches) > 0

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

        # Use base class pattern matching for content
        matches = self._match_patterns(
            content, {"configuration": self.breaking_patterns["configuration"]}
        )
        return len(matches) > 0

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

        # Use base class pattern matching for content
        matches = self._match_patterns(
            content, {"database": self.breaking_patterns["database"]}
        )
        return len(matches) > 0

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

        # Use base class pattern matching for content
        matches = self._match_patterns(
            content, {"dependencies": self.breaking_patterns["dependencies"]}
        )
        return len(matches) > 0
