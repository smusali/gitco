"""AI-powered change analysis for GitCo."""

import os
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


@dataclass
class AnalysisRequest:
    """Request for change analysis."""

    repository: Repository
    git_repo: GitRepository
    diff_content: str
    commit_messages: list[str]
    custom_prompt: Optional[str] = None


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
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(request)

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
            analysis = self._parse_analysis_response(
                response.choices[0].message.content or ""
            )

            log_operation_success(
                "OpenAI change analysis",
                repo=request.repository.name,
                confidence=analysis.confidence,
            )

            return analysis

        except Exception as e:
            log_operation_failure(
                "OpenAI change analysis",
                e,
                repo=request.repository.name,
            )
            raise

    def _build_analysis_prompt(self, request: AnalysisRequest) -> str:
        """Build the analysis prompt for OpenAI.

        Args:
            request: Analysis request.

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

        prompt = f"""
Analyze the following changes for repository: {repo.name}
Repository: {repo.fork} -> {repo.upstream}
Skills: {', '.join(repo.skills)}

Changes Summary:
{commit_summary}

Diff Analysis:
{diff_analysis}

Diff Content:
{diff_content}

Please provide a comprehensive analysis of these changes, including:
1. Summary of changes - A clear, concise summary of what changed
2. Breaking changes - Any changes that could break existing code or APIs
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
        return """You are an expert software developer and open source contributor.
Your task is to analyze code changes and provide insights that help developers understand:
- What changed and why
- Potential impact on existing code
- Opportunities for contribution
- Security and stability implications

Be concise but thorough. Focus on actionable insights that help developers make informed decisions about contributing to the project."""

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
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(request)

            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system=self._get_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Parse the response - handle different content types
            response_text = ""
            if response.content:
                for content_block in response.content:
                    if hasattr(content_block, "text"):
                        response_text += content_block.text

            analysis = self._parse_analysis_response(response_text)

            log_operation_success(
                "Anthropic change analysis",
                repo=request.repository.name,
                confidence=analysis.confidence,
            )

            return analysis

        except Exception as e:
            log_operation_failure(
                "Anthropic change analysis",
                e,
                repo=request.repository.name,
            )
            raise

    def _build_analysis_prompt(self, request: AnalysisRequest) -> str:
        """Build the analysis prompt for Anthropic Claude.

        Args:
            request: Analysis request.

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

        prompt = f"""
Analyze the following changes for repository: {repo.name}
Repository: {repo.fork} -> {repo.upstream}
Skills: {', '.join(repo.skills)}

Changes Summary:
{commit_summary}

Diff Analysis:
{diff_analysis}

Diff Content:
{diff_content}

Please provide a comprehensive analysis of these changes, including:
1. Summary of changes - A clear, concise summary of what changed
2. Breaking changes - Any changes that could break existing code or APIs
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
        """Get the system prompt for Anthropic Claude.

        Returns:
            System prompt string.
        """
        return """You are an expert software developer and open source contributor.
Your task is to analyze code changes and provide insights that help developers understand:
- What changed and why
- Potential impact on existing code
- Opportunities for contribution
- Security and stability implications

Be concise but thorough. Focus on actionable insights that help developers make informed decisions about contributing to the project."""

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
            model: Ollama model name to use for analysis.
            host: Ollama server host URL.
            timeout: Request timeout in seconds.
        """
        self.model = model
        self.host = host
        self.timeout = timeout
        self.client = ollama.Client(host=host)
        self.logger = get_logger()

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
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(request)

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
            response_text = response.get("message", {}).get("content", "")
            analysis = self._parse_analysis_response(response_text)

            log_operation_success(
                "Ollama change analysis",
                repo=request.repository.name,
                confidence=analysis.confidence,
            )

            return analysis

        except Exception as e:
            log_operation_failure(
                "Ollama change analysis",
                e,
                repo=request.repository.name,
            )
            raise

    def _build_analysis_prompt(self, request: AnalysisRequest) -> str:
        """Build the analysis prompt for Ollama.

        Args:
            request: Analysis request.

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

        prompt = f"""
Analyze the following changes for repository: {repo.name}
Repository: {repo.fork} -> {repo.upstream}
Skills: {', '.join(repo.skills)}

Changes Summary:
{commit_summary}

Diff Analysis:
{diff_analysis}

Diff Content:
{diff_content}

Please provide a comprehensive analysis of these changes, including:
1. Summary of changes - A clear, concise summary of what changed
2. Breaking changes - Any changes that could break existing code or APIs
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
        return """You are an expert software developer and open source contributor.
Your task is to analyze code changes and provide insights that help developers understand:
- What changed and why
- Potential impact on existing code
- Opportunities for contribution
- Security and stability implications

Be concise but thorough. Focus on actionable insights that help developers make informed decisions about contributing to the project."""

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
    ) -> Optional[ChangeAnalysis]:
        """Analyze changes for a repository.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            custom_prompt: Optional custom analysis prompt.

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
            analyzer = self.get_analyzer(self.config.settings.llm_provider)
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
    ) -> Optional[ChangeAnalysis]:
        """Analyze a specific commit in detail.

        Args:
            repository: Repository configuration.
            git_repo: Git repository instance.
            commit_hash: Hash of the commit to analyze.
            custom_prompt: Optional custom analysis prompt.

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
            analyzer = self.get_analyzer(self.config.settings.llm_provider)
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

        # Breaking changes
        if analysis.breaking_changes:
            console.print("\n[bold red]⚠️  Breaking Changes:[/bold red]")
            for change in analysis.breaking_changes:
                console.print(f"  • {change}")

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

        # Security updates
        if analysis.security_updates:
            console.print("\n[bold red]🔒 Security Updates:[/bold red]")
            for update in analysis.security_updates:
                console.print(f"  • {update}")

        # Deprecations
        if analysis.deprecations:
            console.print("\n[bold orange]⚠️  Deprecations:[/bold orange]")
            for deprecation in analysis.deprecations:
                console.print(f"  • {deprecation}")

        # Recommendations
        if analysis.recommendations:
            console.print("\n[bold cyan]💡 Recommendations:[/bold cyan]")
            for rec in analysis.recommendations:
                console.print(f"  • {rec}")

        console.print()  # Add spacing
