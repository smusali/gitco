"""Tests for the prompts templates module."""

from gitco.detector import BreakingChange, Deprecation, SecurityUpdate
from gitco.prompts.templates import PromptManager


class TestPromptManager:
    """Test PromptManager class."""

    def test_prompt_manager_initialization(self) -> None:
        """Test PromptManager initialization."""
        manager = PromptManager()

        assert manager is not None
        assert hasattr(manager, "_system_prompt_template")
        assert hasattr(manager, "_analysis_prompt_template")

    def test_get_system_prompt(self) -> None:
        """Test get_system_prompt method."""
        manager = PromptManager()

        system_prompt = manager.get_system_prompt()

        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0

    def test_get_analysis_prompt_basic(self) -> None:
        """Test get_analysis_prompt with basic parameters."""
        manager = PromptManager()

        prompt = manager.get_analysis_prompt(
            repository_name="test-repo",
            repository_fork="https://github.com/user/fork",
            repository_upstream="https://github.com/original/repo",
            repository_skills=["python", "api"],
            commit_messages=["feat: add new feature"],
            diff_content="diff --git a/file.py b/file.py",
            diff_analysis="Added new function",
            breaking_changes=[],
            security_updates=[],
            deprecations=[],
        )

        assert isinstance(prompt, str)
        assert "test-repo" in prompt
        assert "feat: add new feature" in prompt

    def test_get_analysis_prompt_with_breaking_changes(self) -> None:
        """Test get_analysis_prompt with breaking changes."""
        manager = PromptManager()

        breaking_changes = [
            BreakingChange(
                type="api_change",
                description="Removed deprecated method",
                severity="high",
                affected_components=["api.py"],
                migration_guidance="Use new_method() instead",
            )
        ]

        prompt = manager.get_analysis_prompt(
            repository_name="breaking-repo",
            repository_fork="https://github.com/user/breaking",
            repository_upstream="https://github.com/original/breaking",
            repository_skills=["python"],
            commit_messages=["BREAKING CHANGE: removed old API"],
            diff_content="diff --git a/api.py b/api.py",
            diff_analysis="Removed deprecated method",
            breaking_changes=breaking_changes,
            security_updates=[],
            deprecations=[],
        )

        assert "breaking-repo" in prompt
        assert "Removed deprecated method" in prompt

    def test_get_analysis_prompt_with_security_updates(self) -> None:
        """Test get_analysis_prompt with security updates."""
        manager = PromptManager()

        security_updates = [
            SecurityUpdate(
                type="vulnerability_fix",
                description="Fixed SQL injection vulnerability",
                severity="critical",
                cve_id="CVE-2023-1234",
                affected_components=["database.py"],
                remediation_guidance="Update immediately",
            )
        ]

        prompt = manager.get_analysis_prompt(
            repository_name="security-repo",
            repository_fork="https://github.com/user/security",
            repository_upstream="https://github.com/original/security",
            repository_skills=["security"],
            commit_messages=["fix: resolve security vulnerability"],
            diff_content="diff --git a/database.py b/database.py",
            diff_analysis="Fixed SQL injection",
            breaking_changes=[],
            security_updates=security_updates,
            deprecations=[],
        )

        assert "security-repo" in prompt
        assert "CVE-2023-1234" in prompt

    def test_get_analysis_prompt_with_deprecations(self) -> None:
        """Test get_analysis_prompt with deprecations."""
        manager = PromptManager()

        deprecations = [
            Deprecation(
                type="api_deprecation",
                description="Deprecated old_config parameter",
                severity="medium",
                replacement_suggestion="Use new_config instead",
                removal_date="2024-12-31",
                affected_components=["config.py"],
                migration_path="Update configuration calls",
            )
        ]

        prompt = manager.get_analysis_prompt(
            repository_name="deprecation-repo",
            repository_fork="https://github.com/user/deprecation",
            repository_upstream="https://github.com/original/deprecation",
            repository_skills=["python"],
            commit_messages=["deprecated: old config parameter"],
            diff_content="diff --git a/config.py b/config.py",
            diff_analysis="Deprecated old parameter",
            breaking_changes=[],
            security_updates=[],
            deprecations=deprecations,
        )

        assert "deprecation-repo" in prompt
        assert "Use new_config instead" in prompt

    def test_get_analysis_prompt_with_custom_prompt(self) -> None:
        """Test get_analysis_prompt with custom prompt."""
        manager = PromptManager()

        custom_prompt = "Focus on performance implications of these changes"

        prompt = manager.get_analysis_prompt(
            repository_name="custom-repo",
            repository_fork="https://github.com/user/custom",
            repository_upstream="https://github.com/original/custom",
            repository_skills=["performance"],
            commit_messages=["perf: optimize algorithm"],
            diff_content="diff --git a/algorithm.py b/algorithm.py",
            diff_analysis="Optimized sorting algorithm",
            breaking_changes=[],
            security_updates=[],
            deprecations=[],
            custom_prompt=custom_prompt,
        )

        assert "custom-repo" in prompt
        assert custom_prompt in prompt

    def test_get_analysis_prompt_with_multiple_skills(self) -> None:
        """Test get_analysis_prompt with multiple skills."""
        manager = PromptManager()

        skills = ["python", "django", "postgresql", "redis", "celery"]

        prompt = manager.get_analysis_prompt(
            repository_name="multi-skill-repo",
            repository_fork="https://github.com/user/multi-skill",
            repository_upstream="https://github.com/original/multi-skill",
            repository_skills=skills,
            commit_messages=["feat: add comprehensive backend"],
            diff_content="diff --git a/backend/ b/backend/",
            diff_analysis="Added complete backend implementation",
            breaking_changes=[],
            security_updates=[],
            deprecations=[],
        )

        assert "multi-skill-repo" in prompt
        assert all(skill in prompt for skill in skills)

    def test_get_analysis_prompt_with_empty_commit_messages(self) -> None:
        """Test get_analysis_prompt with empty commit messages."""
        manager = PromptManager()

        prompt = manager.get_analysis_prompt(
            repository_name="empty-commits-repo",
            repository_fork="https://github.com/user/empty-commits",
            repository_upstream="https://github.com/original/empty-commits",
            repository_skills=[],
            commit_messages=[],
            diff_content="",
            diff_analysis="",
            breaking_changes=[],
            security_updates=[],
            deprecations=[],
        )

        assert "empty-commits-repo" in prompt
        assert isinstance(prompt, str)

    def test_get_analysis_prompt_with_large_diff(self) -> None:
        """Test get_analysis_prompt with large diff content."""
        manager = PromptManager()

        large_diff = "diff --git a/large_file.py b/large_file.py\n" * 100

        prompt = manager.get_analysis_prompt(
            repository_name="large-diff-repo",
            repository_fork="https://github.com/user/large-diff",
            repository_upstream="https://github.com/original/large-diff",
            repository_skills=["python"],
            commit_messages=["feat: major refactor"],
            diff_content=large_diff,
            diff_analysis="Large refactoring changes",
            breaking_changes=[],
            security_updates=[],
            deprecations=[],
        )

        assert "large-diff-repo" in prompt
        assert len(prompt) > len(large_diff)  # Should be processed

    def test_get_analysis_prompt_with_mixed_changes(self) -> None:
        """Test get_analysis_prompt with mixed types of changes."""
        manager = PromptManager()

        breaking_changes = [
            BreakingChange(
                type="api_change",
                description="Changed function signature",
                severity="high",
                affected_components=["api.py"],
                migration_guidance="Update function calls",
            )
        ]

        security_updates = [
            SecurityUpdate(
                type="vulnerability_fix",
                description="Fixed XSS vulnerability",
                severity="critical",
                affected_components=["web.py"],
                remediation_guidance="Update immediately",
            )
        ]

        deprecations = [
            Deprecation(
                type="feature_deprecation",
                description="Deprecated old feature",
                severity="medium",
                replacement_suggestion="Use new feature",
                affected_components=["feature.py"],
            )
        ]

        prompt = manager.get_analysis_prompt(
            repository_name="mixed-changes-repo",
            repository_fork="https://github.com/user/mixed-changes",
            repository_upstream="https://github.com/original/mixed-changes",
            repository_skills=["python", "security"],
            commit_messages=[
                "feat: breaking change",
                "fix: security issue",
                "deprecated: old feature",
            ],
            diff_content="diff --git a/api.py b/api.py\ndiff --git a/web.py b/web.py\ndiff --git a/feature.py b/feature.py",
            diff_analysis="Multiple types of changes",
            breaking_changes=breaking_changes,
            security_updates=security_updates,
            deprecations=deprecations,
        )

        assert "mixed-changes-repo" in prompt
        assert "Changed function signature" in prompt
        assert "Fixed XSS vulnerability" in prompt
        assert "Deprecated old feature" in prompt


# Additional test cases for PromptManager class
def test_prompt_manager_with_custom_templates() -> None:
    """Test PromptManager with custom template initialization."""
    manager = PromptManager()

    # Test that templates are properly initialized
    system_prompt = manager.get_system_prompt()
    assert isinstance(system_prompt, str)
    assert len(system_prompt) > 0

    analysis_prompt = manager.get_analysis_prompt(
        repository_name="test-repo",
        repository_fork="https://github.com/user/test",
        repository_upstream="https://github.com/original/test",
        repository_skills=["python"],
        commit_messages=["test commit"],
        diff_content="test diff",
        diff_analysis="test analysis",
        breaking_changes=[],
        security_updates=[],
        deprecations=[],
    )
    assert isinstance(analysis_prompt, str)
    assert len(analysis_prompt) > 0


def test_prompt_manager_system_prompt_content() -> None:
    """Test PromptManager system prompt content."""
    manager = PromptManager()
    system_prompt = manager.get_system_prompt()

    # Check for key elements in system prompt
    assert "You are an expert software developer" in system_prompt
    assert "breaking change detection" in system_prompt
    assert "security analysis" in system_prompt


def test_prompt_manager_analysis_prompt_with_complex_breaking_changes() -> None:
    """Test PromptManager analysis prompt with complex breaking changes."""
    manager = PromptManager()

    complex_breaking_changes = [
        BreakingChange(
            type="database_schema_change",
            description="Modified database schema structure",
            severity="critical",
            affected_components=["models.py", "migrations/"],
            migration_guidance="Run database migrations and update ORM models",
        ),
        BreakingChange(
            type="authentication_change",
            description="Changed authentication mechanism",
            severity="high",
            affected_components=["auth.py", "middleware.py"],
            migration_guidance="Update authentication calls and middleware",
        ),
    ]

    prompt = manager.get_analysis_prompt(
        repository_name="complex-repo",
        repository_fork="https://github.com/user/complex",
        repository_upstream="https://github.com/original/complex",
        repository_skills=["python", "django", "database"],
        commit_messages=[
            "feat: database schema changes",
            "feat: authentication system update",
        ],
        diff_content="diff --git a/models.py b/models.py\ndiff --git a/auth.py b/auth.py",
        diff_analysis="Complex breaking changes in database and auth",
        breaking_changes=complex_breaking_changes,
        security_updates=[],
        deprecations=[],
    )

    assert "complex-repo" in prompt
    assert "Modified database schema structure" in prompt
    assert "Changed authentication mechanism" in prompt
    assert "Run database migrations" in prompt
    assert "Update authentication calls" in prompt


def test_prompt_manager_analysis_prompt_with_multiple_security_updates() -> None:
    """Test PromptManager analysis prompt with multiple security updates."""
    manager = PromptManager()

    security_updates = [
        SecurityUpdate(
            type="dependency_vulnerability",
            description="Fixed SQL injection vulnerability in ORM",
            severity="critical",
            affected_components=["orm.py", "queries.py"],
            cve_id="CVE-2023-1234",
            remediation_guidance="Update to latest ORM version and sanitize inputs",
        ),
        SecurityUpdate(
            type="authentication_vulnerability",
            description="Fixed session hijacking vulnerability",
            severity="high",
            affected_components=["session.py", "cookies.py"],
            cve_id="CVE-2023-5678",
            remediation_guidance="Implement secure session management",
        ),
    ]

    prompt = manager.get_analysis_prompt(
        repository_name="security-repo",
        repository_fork="https://github.com/user/security",
        repository_upstream="https://github.com/original/security",
        repository_skills=["python", "security", "authentication"],
        commit_messages=[
            "fix: SQL injection vulnerability",
            "fix: session hijacking vulnerability",
        ],
        diff_content="diff --git a/orm.py b/orm.py\ndiff --git a/session.py b/session.py",
        diff_analysis="Multiple security fixes",
        breaking_changes=[],
        security_updates=security_updates,
        deprecations=[],
    )

    assert "security-repo" in prompt
    assert "Fixed SQL injection vulnerability" in prompt
    assert "Fixed session hijacking vulnerability" in prompt
    assert "CVE-2023-1234" in prompt
    assert "CVE-2023-5678" in prompt
    assert "Update to latest ORM version" in prompt
    assert "Implement secure session management" in prompt


def test_prompt_manager_analysis_prompt_with_comprehensive_deprecations() -> None:
    """Test PromptManager analysis prompt with comprehensive deprecations."""
    manager = PromptManager()

    deprecations = [
        Deprecation(
            type="api_deprecation",
            description="Deprecated old API endpoints",
            severity="medium",
            affected_components=["api/v1/", "controllers/"],
            replacement_suggestion="Use new API v2 endpoints",
            removal_date="v3.0",
        ),
        Deprecation(
            type="feature_deprecation",
            description="Deprecated legacy authentication system",
            severity="high",
            affected_components=["auth/legacy.py", "middleware/legacy.py"],
            replacement_suggestion="Migrate to OAuth 2.0 system",
            removal_date="v2.5",
        ),
    ]

    prompt = manager.get_analysis_prompt(
        repository_name="deprecation-repo",
        repository_fork="https://github.com/user/deprecation",
        repository_upstream="https://github.com/original/deprecation",
        repository_skills=["python", "api", "authentication"],
        commit_messages=[
            "deprecated: old API endpoints",
            "deprecated: legacy auth system",
        ],
        diff_content="diff --git a/api/v1/ b/api/v1/\ndiff --git a/auth/legacy.py b/auth/legacy.py",
        diff_analysis="Comprehensive deprecation changes",
        breaking_changes=[],
        security_updates=[],
        deprecations=deprecations,
    )

    assert "deprecation-repo" in prompt
    assert "Deprecated old API endpoints" in prompt
    assert "Deprecated legacy authentication system" in prompt
    assert "Use new API v2 endpoints" in prompt
    assert "Migrate to OAuth 2.0 system" in prompt
    assert "v3.0" in prompt
    assert "v2.5" in prompt
