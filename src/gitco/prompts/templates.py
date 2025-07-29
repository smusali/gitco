"""Prompt templates for GitCo analysis."""

from typing import Optional

from jinja2 import Template

from gitco.detector import BreakingChange, Deprecation, SecurityUpdate


class PromptManager:
    """Manages prompt templates for LLM analysis."""

    def __init__(self) -> None:
        """Initialize the prompt manager."""
        self._system_prompt_template = Template(SYSTEM_PROMPT_TEMPLATE)
        self._analysis_prompt_template = Template(ANALYSIS_PROMPT_TEMPLATE)

    def get_system_prompt(self) -> str:
        """Get the system prompt for LLM analysis.

        Returns:
            Formatted system prompt string.
        """
        return str(self._system_prompt_template.render())

    def get_analysis_prompt(
        self,
        repository_name: str,
        repository_fork: str,
        repository_upstream: str,
        repository_skills: list[str],
        commit_messages: list[str],
        diff_content: str,
        diff_analysis: str,
        breaking_changes: list[BreakingChange],
        security_updates: list[SecurityUpdate],
        deprecations: list[Deprecation],
        custom_prompt: Optional[str] = None,
    ) -> str:
        """Get the analysis prompt for LLM analysis.

        Args:
            repository_name: Name of the repository.
            repository_fork: Fork URL.
            repository_upstream: Upstream URL.
            repository_skills: List of skills/tags.
            commit_messages: List of commit messages.
            diff_content: Git diff content.
            diff_analysis: Analysis of the diff.
            breaking_changes: List of detected breaking changes.
            security_updates: List of detected security updates.
            deprecations: List of detected deprecations.
            custom_prompt: Optional custom prompt to append.

        Returns:
            Formatted analysis prompt string.
        """
        # Build commit summary
        commit_summary = "\n".join([f"- {msg}" for msg in commit_messages])

        # Build breaking change context
        breaking_context = ""
        if breaking_changes:
            breaking_context = "\n\nDetected Breaking Changes:\n"
            for change in breaking_changes:
                breaking_context += (
                    f"- {change.type} ({change.severity}): {change.description}\n"
                )
                if hasattr(change, "migration_guidance") and change.migration_guidance:
                    breaking_context += f"  Migration: {change.migration_guidance}\n"

        # Build security update context
        security_context = ""
        if security_updates:
            security_context = "\n\nDetected Security Updates:\n"
            for update in security_updates:
                security_context += (
                    f"- {update.type} ({update.severity}): {update.description}\n"
                )
                if hasattr(update, "cve_id") and update.cve_id:
                    security_context += f"  CVE: {update.cve_id}\n"
                if update.affected_components:
                    security_context += (
                        f"  Affected: {', '.join(update.affected_components)}\n"
                    )
                if (
                    hasattr(update, "remediation_guidance")
                    and update.remediation_guidance
                ):
                    security_context += (
                        f"  Remediation: {update.remediation_guidance}\n"
                    )

        # Build deprecation context
        deprecation_context = ""
        if deprecations:
            deprecation_context = "\n\nDetected Deprecations:\n"
            for deprecation in deprecations:
                deprecation_context += f"- {deprecation.type} ({deprecation.severity}): {deprecation.description}\n"
                if (
                    hasattr(deprecation, "replacement_suggestion")
                    and deprecation.replacement_suggestion
                ):
                    deprecation_context += (
                        f"  Replacement: {deprecation.replacement_suggestion}\n"
                    )
                if hasattr(deprecation, "removal_date") and deprecation.removal_date:
                    deprecation_context += (
                        f"  Removal Date: {deprecation.removal_date}\n"
                    )
                if deprecation.affected_components:
                    deprecation_context += (
                        f"  Affected: {', '.join(deprecation.affected_components)}\n"
                    )
                if (
                    hasattr(deprecation, "migration_path")
                    and deprecation.migration_path
                ):
                    deprecation_context += (
                        f"  Migration: {deprecation.migration_path}\n"
                    )

        # Build skills context
        skills_context = ""
        if repository_skills:
            skills_context = f"Skills: {', '.join(repository_skills)}"
        else:
            skills_context = "Skills: Not specified"

        context = {
            "repository_name": repository_name,
            "repository_fork": repository_fork,
            "repository_upstream": repository_upstream,
            "repository_skills": skills_context,
            "commit_summary": commit_summary,
            "diff_analysis": diff_analysis,
            "breaking_context": breaking_context,
            "security_context": security_context,
            "deprecation_context": deprecation_context,
            "diff_content": diff_content,
            "custom_prompt": custom_prompt or "",
        }

        return str(self._analysis_prompt_template.render(**context))


# Template constants
SYSTEM_PROMPT_TEMPLATE = """You are an expert software developer and open source contributor specializing in breaking change detection and security analysis.
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

ANALYSIS_PROMPT_TEMPLATE = """Analyze the following changes for repository: {{ repository_name }}
Repository: {{ repository_fork }} -> {{ repository_upstream }}
Skills: {{ repository_skills }}

Changes Summary:
{{ commit_summary }}

Diff Analysis:
{{ diff_analysis }}{{ breaking_context }}{{ security_context }}{{ deprecation_context }}

Diff Content:
{{ diff_content }}

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
{
    "summary": "Brief summary of changes",
    "breaking_changes": ["list", "of", "breaking", "changes"],
    "new_features": ["list", "of", "new", "features"],
    "bug_fixes": ["list", "of", "bug", "fixes"],
    "security_updates": ["list", "of", "security", "updates"],
    "deprecations": ["list", "of", "deprecations"],
    "recommendations": ["list", "of", "recommendations"],
    "confidence": 0.85
}
{% if custom_prompt %}

Additional Context: {{ custom_prompt }}
{% endif %}"""
