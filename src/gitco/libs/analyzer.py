"""AI-powered change analysis for GitCo."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import openai
import requests
from rich.panel import Panel

from ..prompts import PromptManager
from ..utils.common import (
    console,
    get_logger,
)
from ..utils.exception import (
    ConnectionTimeoutError,
    NetworkTimeoutError,
    ReadTimeoutError,
    RequestTimeoutError,
)
from ..utils.rate_limiter import RateLimitedAPIClient, get_rate_limiter
from ..utils.retry import TIMEOUT_AWARE_RETRY_CONFIG, with_retry
from .config import Config, Repository
from .detector import (
    BreakingChange,
    BreakingChangeDetector,
    Deprecation,
    SecurityDeprecationDetector,
    SecurityUpdate,
)
from .git_ops import GitRepository


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

    def _get_api_name(self) -> str:
        """Get the name of the API being used.

        Returns:
            Name of the API.
        """
        api_name: str = "OpenAI"
        return api_name

    def analyze_changes(self, request: AnalysisRequest) -> ChangeAnalysis:
        """Analyze changes using AI.

        Args:
            request: Analysis request containing repository and change data.

        Returns:
            Analysis result with summary and categorized changes.

        Raises:
            Exception: If analysis fails.
        """
        try:
            # Detect breaking changes, security updates, and deprecations
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

            # Add detailed detections
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
        """Build the analysis prompt.

        Args:
            request: Analysis request.
            detected_breaking_changes: Detected breaking changes.
            detected_security_updates: Detected security updates.
            detected_deprecations: Detected deprecations.

        Returns:
            Formatted prompt for LLM analysis.
        """
        prompt = f"""Analyze the following changes for the repository {request.repository.name}:

Repository: {request.repository.name}
Repository Path: {request.repository.local_path}

Recent Commit Messages:
{chr(10).join(f"- {msg}" for msg in request.commit_messages)}

Code Changes (Diff):
{request.diff_content}

Detected Breaking Changes:
{chr(10).join(f"- {bc.description}" for bc in detected_breaking_changes) if detected_breaking_changes else "None detected"}

Detected Security Updates:
{chr(10).join(f"- {su.description}" for su in detected_security_updates) if detected_security_updates else "None detected"}

Detected Deprecations:
{chr(10).join(f"- {dep.description}" for dep in detected_deprecations) if detected_deprecations else "None detected"}

Please provide a comprehensive analysis including:
1. Summary of changes
2. Breaking changes (if any)
3. New features
4. Bug fixes
5. Security updates
6. Deprecations
7. Recommendations for users/developers

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
}}"""

        if request.custom_prompt:
            prompt += f"\n\nAdditional Context: {request.custom_prompt}"

        return prompt

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM.

        Returns:
            System prompt for analysis.
        """
        return """You are an expert software developer and code reviewer with experience as an open source contributor. Your task is to analyze code changes and provide insights about their impact, breaking changes, new features, and recommendations.

Be thorough but concise. Focus on practical implications for developers and users. If you're unsure about something, mention it in the recommendations.

Always respond with valid JSON as specified in the user prompt."""

    def _parse_analysis_response(self, response: str) -> ChangeAnalysis:
        """Parse the LLM response into a structured analysis.

        Args:
            response: Raw response from LLM.

        Returns:
            Parsed analysis result.
        """
        try:
            parsed = self._parse_text_response(response)

            return ChangeAnalysis(
                summary=parsed.get("summary", "No summary provided"),
                breaking_changes=parsed.get("breaking_changes", []),
                new_features=parsed.get("new_features", []),
                bug_fixes=parsed.get("bug_fixes", []),
                security_updates=parsed.get("security_updates", []),
                deprecations=parsed.get("deprecations", []),
                recommendations=parsed.get("recommendations", []),
                confidence=parsed.get("confidence", 0.5),
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse LLM response: {e}")
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
        """Parse text response from LLM.

        Args:
            response: Raw text response.

        Returns:
            Parsed response as dictionary.
        """
        import json
        import re

        # Try to extract JSON from the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            try:
                json_result: dict[str, Any] = json.loads(json_match.group())
                return json_result
            except json.JSONDecodeError:
                pass

        # If JSON extraction fails, try to parse the entire response
        try:
            parse_result: dict[str, Any] = json.loads(response)
            return parse_result
        except json.JSONDecodeError:
            # Parse text format with sections
            result: dict[str, Any] = {
                "summary": "",
                "breaking_changes": [],
                "new_features": [],
                "bug_fixes": [],
                "security_updates": [],
                "deprecations": [],
                "recommendations": [],
                "confidence": 0.3,
            }

            # Extract summary
            summary_match = re.search(
                r"Summary:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if summary_match:
                result["summary"] = summary_match.group(1).strip()

            # Extract breaking changes
            breaking_match = re.search(
                r"Breaking Changes?:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if breaking_match:
                breaking_text = breaking_match.group(1).strip()
                result["breaking_changes"] = [
                    line.strip()[2:]
                    for line in breaking_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract new features
            features_match = re.search(
                r"New Features?:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if features_match:
                features_text = features_match.group(1).strip()
                result["new_features"] = [
                    line.strip()[2:]
                    for line in features_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract bug fixes
            bugs_match = re.search(
                r"Bug Fixes?:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if bugs_match:
                bugs_text = bugs_match.group(1).strip()
                result["bug_fixes"] = [
                    line.strip()[2:]
                    for line in bugs_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract security updates
            security_match = re.search(
                r"Security Updates?:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if security_match:
                security_text = security_match.group(1).strip()
                result["security_updates"] = [
                    line.strip()[2:]
                    for line in security_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract deprecations
            deprecations_match = re.search(
                r"Deprecations?:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if deprecations_match:
                deprecations_text = deprecations_match.group(1).strip()
                result["deprecations"] = [
                    line.strip()[2:]
                    for line in deprecations_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract recommendations
            recommendations_match = re.search(
                r"Recommendations?:\s*(.+?)(?=\n\n|\n[A-Z]|$)",
                response,
                re.DOTALL | re.IGNORECASE,
            )
            if recommendations_match:
                recommendations_text = recommendations_match.group(1).strip()
                result["recommendations"] = [
                    line.strip()[2:]
                    for line in recommendations_text.split("\n")
                    if line.strip().startswith("-")
                ]

            # Extract confidence
            confidence_match = re.search(
                r"Confidence:\s*(\d+\.?\d*)",
                response,
                re.IGNORECASE,
            )
            if confidence_match:
                try:
                    result["confidence"] = float(confidence_match.group(1))
                except ValueError:
                    pass

            return result


class OpenAIAnalyzer(BaseAnalyzer, RateLimitedAPIClient):
    """OpenAI GPT integration for change analysis."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        timeout: int = 30,
        connect_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
    ):
        """Initialize OpenAI analyzer.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
            model: OpenAI model to use for analysis.
            base_url: Custom base URL for OpenAI API.
            timeout: Request timeout in seconds
            connect_timeout: Connection timeout in seconds
            read_timeout: Read timeout in seconds
        """
        super().__init__(model)

        # Initialize rate limiter
        rate_limiter = get_rate_limiter("openai")
        RateLimitedAPIClient.__init__(self, rate_limiter)

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        self.base_url = base_url
        self.timeout = timeout
        self.connect_timeout = connect_timeout or timeout
        self.read_timeout = read_timeout or timeout

        # Initialize OpenAI client with timeout configuration
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    @with_retry(config=TIMEOUT_AWARE_RETRY_CONFIG)
    def _call_llm_api(self, prompt: str, system_prompt: str) -> str:
        """Call the LLM API with the given prompt.

        Args:
            prompt: The user prompt to send to the LLM.
            system_prompt: The system prompt to send to the LLM.

        Returns:
            The raw response from the LLM.

        Raises:
            NetworkTimeoutError: When network operation times out
            Exception: If the API call fails.
        """
        try:

            def make_openai_request() -> Any:
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=4000,
                    timeout=self.timeout,
                )

            response = self.make_rate_limited_request(make_openai_request)

            # Log token usage
            if hasattr(response, "usage") and response.usage:
                self.logger.debug(
                    f"OpenAI API call: {response.usage.total_tokens} tokens"
                )

            return response.choices[0].message.content or ""

        except requests.exceptions.ConnectTimeout as e:
            raise ConnectionTimeoutError(
                "Connection to OpenAI API timed out",
                self.connect_timeout,
                "OpenAI API chat completion",
            ) from e
        except requests.exceptions.ReadTimeout as e:
            raise ReadTimeoutError(
                "Read from OpenAI API timed out",
                self.read_timeout,
                "OpenAI API chat completion",
            ) from e
        except requests.exceptions.Timeout as e:
            raise RequestTimeoutError(
                "Request to OpenAI API timed out",
                self.timeout,
                "OpenAI API chat completion",
            ) from e
        except requests.exceptions.RequestException as e:
            raise NetworkTimeoutError(
                "Network error during OpenAI API request",
                self.timeout,
                "OpenAI API chat completion",
            ) from e
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            raise

    def _get_api_name(self) -> str:
        """Get the name of the API provider.

        Returns:
            The name of the API provider (OpenAI).
        """
        return "OpenAI"


class ChangeAnalyzer:
    """Main change analyzer that coordinates different LLM providers."""

    def __init__(self, config: Config):
        """Initialize change analyzer.

        Args:
            config: Configuration object.
        """
        self.config = config
        self.logger = get_logger()
        self.analyzers: dict[str, BaseAnalyzer] = {}
        self.breaking_change_detector = BreakingChangeDetector()
        self.security_deprecation_detector = SecurityDeprecationDetector()

    def get_analyzer(self, provider: str = "openai") -> BaseAnalyzer:
        """Get analyzer for the specified provider.

        Args:
            provider: Provider name (only "openai" is supported).

        Returns:
            Configured analyzer instance.

        Raises:
            ValueError: If provider is not supported.
        """
        if provider in self.analyzers:
            return self.analyzers[provider]

        if provider == "openai":
            openai_analyzer: BaseAnalyzer = OpenAIAnalyzer(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-3.5-turbo",
                base_url=self.config.settings.llm_openai_api_url,
                timeout=30,
                connect_timeout=None,
                read_timeout=None,
            )
            self.analyzers[provider] = openai_analyzer
            return openai_analyzer
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. Only 'openai' is supported."
            )

    def analyze_repository_changes(
        self,
        repository: Repository,
        git_repo: GitRepository,
        custom_prompt: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Optional[ChangeAnalysis]:
        """Analyze changes in a repository.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            custom_prompt: Custom prompt for analysis.
            provider: LLM provider to use.

        Returns:
            Analysis result or None if analysis fails.
        """
        try:
            # Get recent changes
            diff_content = git_repo.get_recent_changes()
            commit_messages = git_repo.get_recent_commit_messages()

            if not diff_content and not commit_messages:
                self.logger.info(f"No changes to analyze for {repository.name}")
                return None

            # Create analysis request
            request = AnalysisRequest(
                repository=repository,
                git_repo=git_repo,
                diff_content=diff_content,
                commit_messages=commit_messages,
                custom_prompt=custom_prompt,
            )

            # Get analyzer
            analyzer_provider = provider or self.config.settings.llm_provider
            analyzer = self.get_analyzer(analyzer_provider)

            # Perform analysis
            analysis = analyzer.analyze_changes(request)

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze changes for {repository.name}: {e}")
            return None

    def analyze_specific_commit(
        self,
        repository: Repository,
        git_repo: GitRepository,
        commit_hash: str,
        custom_prompt: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Optional[ChangeAnalysis]:
        """Analyze a specific commit.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            commit_hash: Hash of the commit to analyze.
            custom_prompt: Custom prompt for analysis.
            provider: LLM provider to use.

        Returns:
            Analysis result or None if analysis fails.
        """
        try:
            # Get commit-specific changes
            diff_content = git_repo.get_commit_diff(commit_hash)
            commit_info = git_repo.get_commit_info(commit_hash)
            commit_messages = [commit_info.get("message", "")]

            if not diff_content:
                self.logger.info(f"No changes found for commit {commit_hash}")
                return None

            # Create analysis request
            request = AnalysisRequest(
                repository=repository,
                git_repo=git_repo,
                diff_content=diff_content,
                commit_messages=commit_messages,
                custom_prompt=custom_prompt,
            )

            # Get analyzer
            analyzer_provider = provider or self.config.settings.llm_provider
            analyzer = self.get_analyzer(analyzer_provider)

            # Perform analysis
            analysis = analyzer.analyze_changes(request)

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
        """Get a summary of recent commits without LLM analysis.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            num_commits: Number of commits to analyze.

        Returns:
            Summary of recent commits.
        """
        try:
            commit_messages = git_repo.get_recent_commit_messages(num_commits)

            # Categorize commits
            categories = self._categorize_commits(commit_messages)

            return {
                "repository": repository.name,
                "total_commits": len(commit_messages),
                "has_changes": len(commit_messages) > 0,
                "categories": categories,
                "commit_messages": commit_messages,
                "summary": f"Analyzed {len(commit_messages)} recent commits",
            }

        except Exception as e:
            self.logger.error(
                f"Failed to get commit summary for {repository.name}: {e}"
            )
            return {
                "repository": repository.name,
                "error": str(e),
                "total_commits": 0,
                "has_changes": False,
                "categories": {},
                "commit_messages": [],
                "summary": "Failed to analyze commits",
            }

    def _categorize_commits(self, commit_messages: list[str]) -> dict[str, int]:
        """Categorize commit messages.

        Args:
            commit_messages: List of commit messages.

        Returns:
            Dictionary mapping categories to counts.
        """
        categories = {
            "feature": 0,
            "fix": 0,
            "docs": 0,
            "style": 0,
            "refactor": 0,
            "test": 0,
            "chore": 0,
            "breaking": 0,
            "security": 0,
            "other": 0,
        }

        for message in commit_messages:
            message_lower = message.lower()

            # Check for breaking changes
            if any(
                keyword in message_lower
                for keyword in ["breaking", "breaking change", "!"]
            ):
                categories["breaking"] += 1
            # Check for security updates
            elif any(
                keyword in message_lower
                for keyword in ["security", "vulnerability", "cve"]
            ):
                categories["security"] += 1
            # Check for features
            elif any(
                keyword in message_lower
                for keyword in ["feat:", "feature:", "add:", "new:"]
            ):
                categories["feature"] += 1
            # Check for fixes
            elif any(
                keyword in message_lower for keyword in ["fix:", "bug:", "issue:"]
            ):
                categories["fix"] += 1
            # Check for documentation
            elif any(
                keyword in message_lower
                for keyword in ["docs:", "documentation:", "readme:"]
            ):
                categories["docs"] += 1
            # Check for style changes
            elif any(
                keyword in message_lower for keyword in ["style:", "format:", "lint:"]
            ):
                categories["style"] += 1
            # Check for refactoring
            elif any(
                keyword in message_lower for keyword in ["refactor:", "refactoring:"]
            ):
                categories["refactor"] += 1
            # Check for tests
            elif any(
                keyword in message_lower for keyword in ["test:", "testing:", "spec:"]
            ):
                categories["test"] += 1
            # Check for chores
            elif any(
                keyword in message_lower
                for keyword in ["chore:", "maintenance:", "deps:"]
            ):
                categories["chore"] += 1
            # If no category matches, count as other
            else:
                categories["other"] += 1

        return categories

    def _analyze_diff_content(self, diff_content: str) -> str:
        """Analyze diff content for patterns.

        Args:
            diff_content: Git diff content.

        Returns:
            Analysis of diff patterns.
        """
        if not diff_content.strip():
            return "No diff content available."

        analysis = []

        # Count additions and deletions more accurately
        # Count lines that start with + (but not +++ which are diff headers)
        additions = 0
        deletions = 0
        for line in diff_content.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        analysis.append(f"Lines: +{additions} -{deletions}")

        # Count files changed
        file_count = diff_content.count("diff --git")
        if file_count > 0:
            analysis.append(f"Files changed: {file_count}")

        # Check for file types - count unique Python files
        py_files = set()
        for line in diff_content.split("\n"):
            if "diff --git" in line and ".py" in line:
                # Extract filename from diff line like "diff --git a/src/file1.py b/src/file1.py"
                parts = line.split()
                if len(parts) >= 3:
                    filename = parts[2].split("/")[-1]  # Get just the filename
                    if filename.endswith(".py"):
                        py_files.add(filename)

        py_count = len(py_files)
        if py_count > 0:
            analysis.append(f"py ({py_count})")
        if ".js" in diff_content or ".ts" in diff_content:
            analysis.append("JavaScript/TypeScript files modified")
        if ".md" in diff_content:
            analysis.append("Documentation files modified")
        if "requirements" in diff_content or "setup.py" in diff_content:
            analysis.append("Dependencies modified")

        # Check for specific change types
        if ".md" in diff_content or "README" in diff_content:
            analysis.append("Contains documentation changes")
        if any(
            config_file in diff_content
            for config_file in [
                ".yml",
                ".yaml",
                ".json",
                ".toml",
                "setup.py",
                "requirements",
            ]
        ):
            analysis.append("Contains configuration changes")
        if "test" in diff_content.lower():
            analysis.append("Contains test changes")

        return "; ".join(analysis)

    def display_analysis(self, analysis: ChangeAnalysis, repository_name: str) -> None:
        """Display analysis results in a formatted way.

        Args:
            analysis: Analysis result to display.
            repository_name: Name of the repository.
        """
        # Create summary panel
        summary_panel = Panel(
            analysis.summary,
            title=f"📊 Analysis Summary - {repository_name}",
            border_style="blue",
        )
        console.print(summary_panel)

        # Display breaking changes
        if analysis.breaking_changes:
            breaking_panel = Panel(
                "\n".join(f"• {change}" for change in analysis.breaking_changes),
                title="🚨 Breaking Changes",
                border_style="red",
            )
            console.print(breaking_panel)

        # Display new features
        if analysis.new_features:
            features_panel = Panel(
                "\n".join(f"• {feature}" for feature in analysis.new_features),
                title="✨ New Features",
                border_style="green",
            )
            console.print(features_panel)

        # Display bug fixes
        if analysis.bug_fixes:
            fixes_panel = Panel(
                "\n".join(f"• {fix}" for fix in analysis.bug_fixes),
                title="🐛 Bug Fixes",
                border_style="yellow",
            )
            console.print(fixes_panel)

        # Display security updates
        if analysis.security_updates:
            security_panel = Panel(
                "\n".join(f"• {update}" for update in analysis.security_updates),
                title="🔒 Security Updates",
                border_style="red",
            )
            console.print(security_panel)

        # Display deprecations
        if analysis.deprecations:
            deprecations_panel = Panel(
                "\n".join(f"• {dep}" for dep in analysis.deprecations),
                title="⚠️ Deprecations",
                border_style="yellow",
            )
            console.print(deprecations_panel)

        # Display recommendations
        if analysis.recommendations:
            recommendations_panel = Panel(
                "\n".join(f"• {rec}" for rec in analysis.recommendations),
                title="💡 Recommendations",
                border_style="cyan",
            )
            console.print(recommendations_panel)

        # Display confidence
        confidence_color = (
            "green"
            if analysis.confidence > 0.7
            else "yellow"
            if analysis.confidence > 0.4
            else "red"
        )
        confidence_panel = Panel(
            f"Confidence: {analysis.confidence:.1%}",
            title="🎯 Analysis Confidence",
            border_style=confidence_color,
        )
        console.print(confidence_panel)

    def detect_breaking_changes(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[BreakingChange]:
        """Detect breaking changes in code changes.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            List of detected breaking changes.
        """
        try:
            detector = BreakingChangeDetector()
            return detector.detect_breaking_changes(diff_content, commit_messages)
        except Exception as e:
            self.logger.error(f"Failed to detect breaking changes: {e}")
            return []

    def detect_security_updates(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[SecurityUpdate]:
        """Detect security updates in code changes.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            List of detected security updates.
        """
        try:
            detector = SecurityDeprecationDetector()
            return detector.detect_security_updates(diff_content, commit_messages)
        except Exception as e:
            self.logger.error(f"Failed to detect security updates: {e}")
            return []

    def detect_deprecations(
        self, diff_content: str, commit_messages: list[str]
    ) -> list[Deprecation]:
        """Detect deprecations in code changes.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            List of detected deprecations.
        """
        try:
            detector = SecurityDeprecationDetector()
            return detector.detect_deprecations(diff_content, commit_messages)
        except Exception as e:
            self.logger.error(f"Failed to detect deprecations: {e}")
            return []

    def analyze_changes_without_llm(
        self,
        repository: Repository,
        git_repo: GitRepository,
    ) -> dict[str, Any]:
        """Analyze changes without using LLM (pattern-based analysis).

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.

        Returns:
            Analysis result based on pattern detection.
        """
        try:
            # Get recent changes
            diff_content = git_repo.get_recent_changes()
            commit_messages = git_repo.get_recent_commit_messages()

            if not diff_content and not commit_messages:
                return {
                    "repository": repository.name,
                    "summary": "No changes to analyze",
                    "breaking_changes": [],
                    "new_features": [],
                    "bug_fixes": [],
                    "security_updates": [],
                    "deprecations": [],
                    "recommendations": [],
                    "confidence": 0.0,
                }

            # Detect patterns
            breaking_changes = self.detect_breaking_changes(
                diff_content, commit_messages
            )
            security_updates = self.detect_security_updates(
                diff_content, commit_messages
            )
            deprecations = self.detect_deprecations(diff_content, commit_messages)

            # Categorize commits
            categories = self._categorize_commits(commit_messages)

            # Generate summary
            summary_parts = []
            if categories["feature"] > 0:
                summary_parts.append(f"{categories['feature']} new features")
            if categories["fix"] > 0:
                summary_parts.append(f"{categories['fix']} bug fixes")
            if categories["breaking"] > 0:
                summary_parts.append(f"{categories['breaking']} breaking changes")
            if categories["security"] > 0:
                summary_parts.append(f"{categories['security']} security updates")

            summary = (
                f"Found {len(commit_messages)} commits with {', '.join(summary_parts)}"
                if summary_parts
                else f"Found {len(commit_messages)} commits"
            )

            # Generate recommendations
            recommendations = []
            if breaking_changes:
                recommendations.append(
                    "Review breaking changes carefully before upgrading"
                )
            if security_updates:
                recommendations.append(
                    "Security updates detected - consider upgrading soon"
                )
            if categories["docs"] == 0 and len(commit_messages) > 3:
                recommendations.append(
                    "Consider adding documentation for recent changes"
                )

            return {
                "repository": repository.name,
                "summary": summary,
                "breaking_changes": [bc.description for bc in breaking_changes],
                "new_features": [],
                "bug_fixes": [],
                "security_updates": [su.description for su in security_updates],
                "deprecations": [dep.description for dep in deprecations],
                "recommendations": recommendations,
                "confidence": 0.6 if breaking_changes or security_updates else 0.3,
                "categories": categories,
            }

        except Exception as e:
            self.logger.error(
                f"Failed to analyze changes without LLM for {repository.name}: {e}"
            )
            return {
                "repository": repository.name,
                "summary": "Analysis failed",
                "error": str(e),
                "breaking_changes": [],
                "new_features": [],
                "bug_fixes": [],
                "security_updates": [],
                "deprecations": [],
                "recommendations": ["Manual review recommended"],
                "confidence": 0.0,
            }

    def get_breaking_change_summary(
        self, diff_content: str, commit_messages: list[str]
    ) -> dict[str, Any]:
        """Get a summary of breaking changes.

        Args:
            diff_content: Git diff content.
            commit_messages: List of commit messages.

        Returns:
            Summary of breaking changes.
        """
        try:
            breaking_changes = self.detect_breaking_changes(
                diff_content, commit_messages
            )

            return {
                "changes": [bc.description for bc in breaking_changes],
                "count": len(breaking_changes),
                "high_priority_count": len(
                    [bc for bc in breaking_changes if bc.severity == "high"]
                ),
                "total_breaking_changes": len(breaking_changes),
                "severity": "high" if breaking_changes else "none",
                "recommendations": (
                    [
                        "Review breaking changes carefully",
                        "Test thoroughly before deploying",
                        "Update dependent code if necessary",
                    ]
                    if breaking_changes
                    else ["No breaking changes detected"]
                ),
            }

        except Exception as e:
            self.logger.error(f"Failed to get breaking change summary: {e}")
            return {
                "changes": [],
                "count": 0,
                "high_priority_count": 0,
                "total_breaking_changes": 0,
                "severity": "unknown",
                "error": str(e),
                "recommendations": ["Manual review recommended"],
            }
