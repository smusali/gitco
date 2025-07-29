"""AI-powered change analysis for GitCo."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import anthropic
import ollama
import openai
import requests
from rich.panel import Panel

from .config import Config, Repository
from .detector import (
    BreakingChange,
    BreakingChangeDetector,
    Deprecation,
    SecurityDeprecationDetector,
    SecurityUpdate,
)
from .git_ops import GitRepository
from .prompts import PromptManager
from .utils import (
    console,
    get_logger,
)


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


class BaseAnalyzer(ABC):
    """Base class for all LLM analyzers.

    This class provides common functionality and defines the interface that all
    LLM analyzers must implement. It includes shared methods for building prompts,
    parsing responses, and handling common analysis patterns.
    """

    def __init__(self, model: str = "default"):
        """Initialize the base analyzer.

        Args:
            model: Model name to use for analysis.
        """
        self.model = model
        self.logger = get_logger()
        self.breaking_detector = BreakingChangeDetector()
        self.security_deprecation_detector = SecurityDeprecationDetector()
        self.prompt_manager = PromptManager()

    @abstractmethod
    def _call_llm_api(self, prompt: str, system_prompt: str) -> str:
        """Call the LLM API with the given prompt.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: The system prompt to send to the LLM.

        Returns:
            The raw response from the LLM.

        Raises:
            Exception: If the API call fails.
        """
        pass

    @abstractmethod
    def _get_api_name(self) -> str:
        """Get the name of the API provider.

        Returns:
            The name of the API provider (e.g., "OpenAI", "Anthropic", "Ollama").
        """
        pass

    def analyze_changes(self, request: AnalysisRequest) -> ChangeAnalysis:
        """Analyze repository changes using the LLM.

        Args:
            request: Analysis request containing repository and change data.

        Returns:
            Analysis result with categorized changes and recommendations.

        Raises:
            Exception: If analysis fails.
        """
        try:
            # Detect patterns first
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

            # Build analysis prompt
            prompt = self._build_analysis_prompt(
                request,
                detected_breaking_changes,
                detected_security_updates,
                detected_deprecations,
            )

            # Get system prompt
            system_prompt = self._get_system_prompt()

            # Call LLM API
            response = self._call_llm_api(prompt, system_prompt)

            # Parse response
            analysis = self._parse_analysis_response(response)

            # Add detailed detection results
            analysis.detailed_breaking_changes = detected_breaking_changes
            analysis.detailed_security_updates = detected_security_updates
            analysis.detailed_deprecations = detected_deprecations

            return analysis

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise

    def _build_analysis_prompt(
        self,
        request: AnalysisRequest,
        detected_breaking_changes: list[BreakingChange],
        detected_security_updates: list[SecurityUpdate],
        detected_deprecations: list[Deprecation],
    ) -> str:
        """Build the analysis prompt for the LLM.

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

        # Simple diff analysis
        diff_analysis = "Standard code changes"
        if diff_content:
            lines = diff_content.splitlines()
            file_count = sum(1 for line in lines if line.startswith("diff --git"))
            if file_count > 0:
                diff_analysis = f"Files changed: {file_count}"

        return self.prompt_manager.get_analysis_prompt(
            repository_name=repo.name,
            repository_fork=repo.fork,
            repository_upstream=repo.upstream,
            repository_skills=repo.skills,
            commit_messages=commit_messages,
            diff_content=diff_content,
            diff_analysis=diff_analysis,
            breaking_changes=detected_breaking_changes,
            security_updates=detected_security_updates,
            deprecations=detected_deprecations,
            custom_prompt=request.custom_prompt,
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM.

        Returns:
            System prompt string.
        """
        return self.prompt_manager.get_system_prompt()

    def _parse_analysis_response(self, response: str) -> ChangeAnalysis:
        """Parse LLM response into structured analysis.

        Args:
            response: Raw response from the LLM.

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
            self.logger.warning(f"Failed to parse {self._get_api_name()} response: {e}")
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
            response: Text response from the LLM.

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


class OpenAIAnalyzer(BaseAnalyzer):
    """OpenAI API integration for change analysis."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI analyzer.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: OpenAI model to use for analysis.
        """
        super().__init__(model)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        self.client = openai.OpenAI(api_key=self.api_key)

    def _call_llm_api(self, prompt: str, system_prompt: str) -> str:
        """Call the LLM API with the given prompt.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: The system prompt to send to the LLM.

        Returns:
            The raw response from the LLM.

        Raises:
            Exception: If the API call fails.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=4000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise

    def _get_api_name(self) -> str:
        """Get the name of the API provider.

        Returns:
            The name of the API provider (e.g., "OpenAI", "Anthropic", "Ollama").
        """
        return "OpenAI"


class AnthropicAnalyzer(BaseAnalyzer):
    """Anthropic Claude API integration for change analysis."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"
    ):
        """Initialize Anthropic analyzer.

        Args:
            api_key: Anthropic API key. If None, will try to get from environment.
            model: Anthropic model to use for analysis.
        """
        super().__init__(model)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _call_llm_api(self, prompt: str, system_prompt: str) -> str:
        """Call the LLM API with the given prompt.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: The system prompt to send to the LLM.

        Returns:
            The raw response from the LLM.

        Raises:
            Exception: If the API call fails.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            # Check if the first content block is a TextBlock
            if response.content and hasattr(response.content[0], "text"):
                return str(response.content[0].text)
            else:
                raise Exception("Unexpected response format from Anthropic API")
        except Exception as e:
            self.logger.error(f"Anthropic API call failed: {e}")
            raise

    def _get_api_name(self) -> str:
        """Get the name of the API provider.

        Returns:
            The name of the API provider (e.g., "OpenAI", "Anthropic", "Ollama").
        """
        return "Anthropic"


class OllamaAnalyzer(BaseAnalyzer):
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
        super().__init__(model)
        self.host = host
        self.timeout = timeout
        self.client = ollama.Client(host=host)

    def _call_llm_api(self, prompt: str, system_prompt: str) -> str:
        """Call the LLM API with the given prompt.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: The system prompt to send to the LLM.

        Returns:
            The raw response from the LLM.

        Raises:
            Exception: If the API call fails.
        """
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            response_data = response.json()
            if isinstance(response_data, dict) and "response" in response_data:
                return str(response_data["response"])
            else:
                raise Exception("Unexpected response format from Ollama API")
        except Exception as e:
            self.logger.error(f"Ollama API call failed: {e}")
            raise

    def _get_api_name(self) -> str:
        """Get the name of the API provider.

        Returns:
            The name of the API provider (e.g., "OpenAI", "Anthropic", "Ollama").
        """
        return "Ollama"


class ChangeAnalyzer:
    """Main change analyzer that coordinates analysis operations."""

    def __init__(self, config: Config):
        """Initialize change analyzer.

        Args:
            config: GitCo configuration.
        """
        self.config = config
        self.logger = get_logger()
        self.analyzers: dict[str, BaseAnalyzer] = {}
        self.security_deprecation_detector = SecurityDeprecationDetector()
        self.breaking_change_detector = BreakingChangeDetector()

    def get_analyzer(self, provider: str = "openai") -> BaseAnalyzer:
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

    def detect_breaking_changes(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[BreakingChange]:
        """Detect breaking changes using the breaking change detector.

        Args:
            diff_content: Git diff content to analyze.
            commit_messages: List of commit messages to analyze.

        Returns:
            List of detected breaking changes.
        """
        return self.breaking_change_detector.detect_breaking_changes(
            diff_content, commit_messages
        )

    def detect_security_updates(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[SecurityUpdate]:
        """Detect security updates using the security deprecation detector.

        Args:
            diff_content: Git diff content to analyze.
            commit_messages: List of commit messages to analyze.

        Returns:
            List of detected security updates.
        """
        return self.security_deprecation_detector.detect_security_updates(
            diff_content, commit_messages
        )

    def detect_deprecations(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[Deprecation]:
        """Detect deprecations using the security deprecation detector.

        Args:
            diff_content: Git diff content to analyze.
            commit_messages: List of commit messages to analyze.

        Returns:
            List of detected deprecations.
        """
        return self.security_deprecation_detector.detect_deprecations(
            diff_content, commit_messages
        )

    def analyze_changes_without_llm(
        self,
        repository: Repository,
        git_repo: GitRepository,
    ) -> dict[str, Any]:
        """Analyze changes using only pattern detection (no LLM required).

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.

        Returns:
            Dictionary containing analysis results from pattern detection.
        """
        try:
            # Get recent changes
            diff_content = git_repo.get_recent_changes()
            commit_messages = git_repo.get_recent_commit_messages()

            if not diff_content and not commit_messages:
                self.logger.info(
                    f"No changes to analyze for repository: {repository.name}"
                )
                return {}

            # Use pattern detection
            breaking_changes = self.detect_breaking_changes(
                diff_content, commit_messages
            )
            security_updates = self.detect_security_updates(
                diff_content, commit_messages
            )
            deprecations = self.detect_deprecations(diff_content, commit_messages)

            return {
                "repository": repository.name,
                "breaking_changes": breaking_changes,
                "security_updates": security_updates,
                "deprecations": deprecations,
                "total_issues": len(breaking_changes)
                + len(security_updates)
                + len(deprecations),
                "has_critical_issues": any(
                    change.severity == "high" for change in breaking_changes
                )
                or any(
                    update.severity in ["critical", "high"]
                    for update in security_updates
                ),
                "analysis_method": "pattern_detection",
            }

        except Exception as e:
            self.logger.error(f"Failed to analyze repository {repository.name}: {e}")
            return {}

    def get_breaking_change_summary(
        self, diff_content: str, commit_messages: list[str]
    ) -> dict[str, Any]:
        """Get a summary of breaking changes detected.

        Args:
            diff_content: Git diff content to analyze.
            commit_messages: List of commit messages to analyze.

        Returns:
            Dictionary containing breaking change summary.
        """
        breaking_changes = self.detect_breaking_changes(diff_content, commit_messages)

        # Group by severity
        severity_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}

        for change in breaking_changes:
            severity_counts[change.severity] = (
                severity_counts.get(change.severity, 0) + 1
            )
            type_counts[change.type] = type_counts.get(change.type, 0) + 1

        return {
            "total_breaking_changes": len(breaking_changes),
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "high_priority_count": len(
                [c for c in breaking_changes if c.severity == "high"]
            ),
            "changes": breaking_changes,
        }
