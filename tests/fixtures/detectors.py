"""Fixtures for detector tests."""

from gitco.detector import BreakingChange, Deprecation, SecurityUpdate


def sample_diff_content() -> str:
    """Sample diff content for testing."""
    return """diff --git a/src/main.py b/src/main.py
index 1234567..abcdefg 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
-def old_function():
+def new_function(param: str) -> str:
     return "Hello"

def another_function():
    pass
"""


def sample_commit_messages() -> list[str]:
    """Sample commit messages for testing."""
    return [
        "BREAKING CHANGE: update function signature",
        "feat: add new parameter to process_data",
        "fix: security vulnerability CVE-2023-1234",
        "deprecate: old API function",
    ]


def sample_breaking_changes() -> list[BreakingChange]:
    """Sample breaking changes for testing."""
    return [
        BreakingChange(
            type="api_signature",
            description="Function signature changed",
            severity="high",
            affected_components=["main.py"],
            migration_guidance="Update function calls to include new parameter",
        ),
        BreakingChange(
            type="configuration",
            description="Configuration file format changed",
            severity="medium",
            affected_components=["config.yaml"],
            migration_guidance="Update configuration format",
        ),
    ]


def sample_security_updates() -> list[SecurityUpdate]:
    """Sample security updates for testing."""
    return [
        SecurityUpdate(
            type="vulnerability_fix",
            description="Fix SQL injection vulnerability",
            severity="high",
            cve_id="CVE-2023-1234",
            affected_components=["auth.py"],
            remediation_guidance="Update authentication logic",
        ),
        SecurityUpdate(
            type="authentication",
            description="Improve password validation",
            severity="medium",
            affected_components=["auth.py"],
            remediation_guidance="Use stronger password requirements",
        ),
    ]


def sample_deprecations() -> list[Deprecation]:
    """Sample deprecations for testing."""
    return [
        Deprecation(
            type="api_deprecation",
            description="Deprecate old API function",
            severity="medium",
            replacement_suggestion="Use new_function instead",
            removal_date="2024-12-31",
            affected_components=["api.py"],
            migration_path="Update imports and function calls",
        ),
        Deprecation(
            type="feature_deprecation",
            description="Deprecate legacy feature",
            severity="low",
            replacement_suggestion="Use new feature",
            affected_components=["legacy.py"],
            migration_path="Migrate to new feature",
        ),
    ]


def sample_diff_with_api_changes() -> str:
    """Sample diff with API signature changes."""
    return """diff --git a/api.py b/api.py
index 1234567..abcdefg 100644
--- a/api.py
+++ b/api.py
@@ -1,3 +1,3 @@
-def process_data(data):
+def new_function(param: str) -> str:
     return "Hello"
"""


def sample_diff_with_config_changes() -> str:
    """Sample diff with configuration changes."""
    return """diff --git a/config.yaml b/config.yaml
index 1234567..abcdefg 100644
--- a/config.yaml
+++ b/config.yaml
@@ -1,3 +1,3 @@
-DEFAULT_TIMEOUT = 30
+DEFAULT_TIMEOUT = 60
"""


def sample_diff_with_database_changes() -> str:
    """Sample diff with database changes."""
    return """diff --git a/migration.sql b/migration.sql
index 1234567..abcdefg 100644
--- a/migration.sql
+++ b/migration.sql
@@ -1,3 +1,5 @@
+CREATE TABLE users (
+    id INTEGER PRIMARY KEY,
+    name TEXT NOT NULL
+);
"""


def sample_diff_with_dependency_changes() -> str:
    """Sample diff with dependency changes."""
    return """diff --git a/requirements.txt b/requirements.txt
index 1234567..abcdefg 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,3 +1,3 @@
-requests==2.25.1
+requests==2.28.0
"""
