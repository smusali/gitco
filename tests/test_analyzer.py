"""Tests for the analyzer module."""

import os
from unittest.mock import Mock, patch

import pytest

from gitco.analyzer import (
    AnalysisRequest,
    AnthropicAnalyzer,
    ChangeAnalysis,
    ChangeAnalyzer,
    OllamaAnalyzer,
    OpenAIAnalyzer,
)


class TestChangeAnalysis:
    """Test ChangeAnalysis dataclass."""

    def test_change_analysis_creation(self) -> None:
        """Test creating a ChangeAnalysis instance."""
        analysis = ChangeAnalysis(
            summary="Test summary",
            breaking_changes=["Change 1"],
            new_features=["Feature 1"],
            bug_fixes=["Fix 1"],
            security_updates=["Security 1"],
            deprecations=["Deprecation 1"],
            recommendations=["Recommendation 1"],
            confidence=0.8,
        )

        assert analysis.summary == "Test summary"
        assert analysis.breaking_changes == ["Change 1"]
        assert analysis.new_features == ["Feature 1"]
        assert analysis.bug_fixes == ["Fix 1"]
        assert analysis.security_updates == ["Security 1"]
        assert analysis.deprecations == ["Deprecation 1"]
        assert analysis.recommendations == ["Recommendation 1"]
        assert analysis.confidence == 0.8


class TestAnalysisRequest:
    """Test AnalysisRequest dataclass."""

    def test_analysis_request_creation(self) -> None:
        """Test creating an AnalysisRequest instance."""
        mock_repo = Mock()
        mock_git_repo = Mock()

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=mock_git_repo,
            diff_content="test diff",
            commit_messages=["commit 1", "commit 2"],
            custom_prompt="test prompt",
        )

        assert request.repository == mock_repo
        assert request.git_repo == mock_git_repo
        assert request.diff_content == "test diff"
        assert request.commit_messages == ["commit 1", "commit 2"]
        assert request.custom_prompt == "test prompt"


class TestOpenAIAnalyzer:
    """Test OpenAIAnalyzer class."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_analyzer_initialization(self) -> None:
        """Test OpenAIAnalyzer initialization."""
        analyzer = OpenAIAnalyzer()
        assert analyzer.api_key == "test-key"
        assert analyzer.model == "gpt-3.5-turbo"

    def test_openai_analyzer_initialization_with_api_key(self) -> None:
        """Test OpenAIAnalyzer initialization with explicit API key."""
        analyzer = OpenAIAnalyzer(api_key="explicit-key", model="gpt-4")
        assert analyzer.api_key == "explicit-key"
        assert analyzer.model == "gpt-4"

    def test_openai_analyzer_initialization_no_api_key(self) -> None:
        """Test OpenAIAnalyzer initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIAnalyzer()

    def test_build_analysis_prompt(self) -> None:
        """Test building analysis prompt."""
        analyzer = OpenAIAnalyzer(api_key="test-key")
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python", "web"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff content",
            commit_messages=["commit 1", "commit 2"],
            custom_prompt="test prompt",
        )

        prompt = analyzer._build_analysis_prompt(request)
        assert "test-repo" in prompt
        assert "user/fork" in prompt
        assert "upstream/repo" in prompt
        assert "python, web" in prompt
        assert "test diff content" in prompt
        assert "commit 1" in prompt
        assert "commit 2" in prompt
        assert "test prompt" in prompt

    def test_get_system_prompt(self) -> None:
        """Test getting system prompt."""
        analyzer = OpenAIAnalyzer(api_key="test-key")
        prompt = analyzer._get_system_prompt()
        assert "expert software developer" in prompt
        assert "open source contributor" in prompt

    def test_parse_text_response(self) -> None:
        """Test parsing text response."""
        analyzer = OpenAIAnalyzer(api_key="test-key")
        response = """
        Summary: Test summary

        Breaking Changes:
        - Change 1
        - Change 2

        New Features:
        - Feature 1
        """

        result = analyzer._parse_text_response(response)
        assert result["summary"] == "Test summary"
        assert "Change 1" in result["breaking_changes"]
        assert "Change 2" in result["breaking_changes"]
        assert "Feature 1" in result["new_features"]

    @patch("openai.OpenAI")
    def test_analyze_changes_success(self, mock_openai: Mock) -> None:
        """Test successful change analysis."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = '{"summary": "Test", "confidence": 0.8}'
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = OpenAIAnalyzer(api_key="test-key")
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff",
            commit_messages=["test commit"],
        )

        result = analyzer.analyze_changes(request)
        assert result.summary == "Test"
        assert result.confidence == 0.8

    @patch("openai.OpenAI")
    def test_analyze_changes_failure(self, mock_openai: Mock) -> None:
        """Test failed change analysis."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        analyzer = OpenAIAnalyzer(api_key="test-key")
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff",
            commit_messages=["test commit"],
        )

        with pytest.raises(Exception, match="API Error"):
            analyzer.analyze_changes(request)


class TestAnthropicAnalyzer:
    """Test AnthropicAnalyzer class."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_anthropic_analyzer_initialization(self) -> None:
        """Test AnthropicAnalyzer initialization."""
        analyzer = AnthropicAnalyzer()
        assert analyzer.api_key == "test-key"
        assert analyzer.model == "claude-3-sonnet-20240229"

    def test_anthropic_analyzer_initialization_with_api_key(self) -> None:
        """Test AnthropicAnalyzer initialization with explicit API key."""
        analyzer = AnthropicAnalyzer(api_key="explicit-key", model="claude-3-haiku")
        assert analyzer.api_key == "explicit-key"
        assert analyzer.model == "claude-3-haiku"

    def test_anthropic_analyzer_initialization_no_api_key(self) -> None:
        """Test AnthropicAnalyzer initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key not provided"):
                AnthropicAnalyzer()

    def test_build_analysis_prompt(self) -> None:
        """Test building analysis prompt."""
        analyzer = AnthropicAnalyzer(api_key="test-key")
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python", "web"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff content",
            commit_messages=["commit 1", "commit 2"],
            custom_prompt="test prompt",
        )

        prompt = analyzer._build_analysis_prompt(request)
        assert "test-repo" in prompt
        assert "user/fork" in prompt
        assert "upstream/repo" in prompt
        assert "python, web" in prompt
        assert "test diff content" in prompt
        assert "commit 1" in prompt
        assert "commit 2" in prompt
        assert "test prompt" in prompt

    def test_get_system_prompt(self) -> None:
        """Test getting system prompt."""
        analyzer = AnthropicAnalyzer(api_key="test-key")
        prompt = analyzer._get_system_prompt()
        assert "expert software developer" in prompt
        assert "open source contributor" in prompt

    def test_parse_text_response(self) -> None:
        """Test parsing text response."""
        analyzer = AnthropicAnalyzer(api_key="test-key")
        response = """
        Summary: Test summary

        Breaking Changes:
        - Change 1
        - Change 2

        New Features:
        - Feature 1
        """

        result = analyzer._parse_text_response(response)
        assert result["summary"] == "Test summary"
        assert "Change 1" in result["breaking_changes"]
        assert "Change 2" in result["breaking_changes"]
        assert "Feature 1" in result["new_features"]

    @patch("anthropic.Anthropic")
    def test_analyze_changes_success(self, mock_anthropic: Mock) -> None:
        """Test successful change analysis."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '{"summary": "Test", "confidence": 0.8}'
        mock_client.messages.create.return_value = mock_response

        analyzer = AnthropicAnalyzer(api_key="test-key")
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff",
            commit_messages=["test commit"],
        )

        result = analyzer.analyze_changes(request)
        assert result.summary == "Test"
        assert result.confidence == 0.8

    @patch("anthropic.Anthropic")
    def test_analyze_changes_failure(self, mock_anthropic: Mock) -> None:
        """Test failed change analysis."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        analyzer = AnthropicAnalyzer(api_key="test-key")
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff",
            commit_messages=["test commit"],
        )

        with pytest.raises(Exception, match="API Error"):
            analyzer.analyze_changes(request)


class TestOllamaAnalyzer:
    """Test OllamaAnalyzer class."""

    def test_ollama_analyzer_initialization(self) -> None:
        """Test OllamaAnalyzer initialization."""
        analyzer = OllamaAnalyzer()
        assert analyzer.model == "llama2"
        assert analyzer.host == "http://localhost:11434"
        assert analyzer.timeout == 120

    def test_ollama_analyzer_initialization_with_custom_params(self) -> None:
        """Test OllamaAnalyzer initialization with custom parameters."""
        analyzer = OllamaAnalyzer(
            model="codellama", host="http://localhost:8080", timeout=60
        )
        assert analyzer.model == "codellama"
        assert analyzer.host == "http://localhost:8080"
        assert analyzer.timeout == 60

    def test_build_analysis_prompt(self) -> None:
        """Test building analysis prompt."""
        analyzer = OllamaAnalyzer()
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python", "web"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff content",
            commit_messages=["commit 1", "commit 2"],
            custom_prompt="test prompt",
        )

        prompt = analyzer._build_analysis_prompt(request)
        assert "test-repo" in prompt
        assert "user/fork" in prompt
        assert "upstream/repo" in prompt
        assert "python, web" in prompt
        assert "test diff content" in prompt
        assert "commit 1" in prompt
        assert "commit 2" in prompt
        assert "test prompt" in prompt

    def test_get_system_prompt(self) -> None:
        """Test getting system prompt."""
        analyzer = OllamaAnalyzer()
        prompt = analyzer._get_system_prompt()
        assert "expert software developer" in prompt
        assert "open source contributor" in prompt

    def test_parse_text_response(self) -> None:
        """Test parsing text response."""
        analyzer = OllamaAnalyzer()
        response = """
        Summary: Test summary

        Breaking Changes:
        - Change 1
        - Change 2

        New Features:
        - Feature 1
        """

        result = analyzer._parse_text_response(response)
        assert result["summary"] == "Test summary"
        assert "Change 1" in result["breaking_changes"]
        assert "Change 2" in result["breaking_changes"]
        assert "Feature 1" in result["new_features"]

    @patch("ollama.Client")
    def test_analyze_changes_success(self, mock_ollama_client: Mock) -> None:
        """Test successful change analysis."""
        mock_client = Mock()
        mock_ollama_client.return_value = mock_client

        mock_response = {
            "message": {
                "content": '{"summary": "Test summary", "breaking_changes": ["Change 1"], "new_features": [], "bug_fixes": [], "security_updates": [], "deprecations": [], "recommendations": [], "confidence": 0.8}'
            }
        }
        mock_client.chat.return_value = mock_response

        analyzer = OllamaAnalyzer()
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff",
            commit_messages=["test commit"],
        )

        result = analyzer.analyze_changes(request)

        assert result.summary == "Test summary"
        assert result.breaking_changes == ["Change 1"]
        assert result.confidence == 0.8
        mock_client.chat.assert_called_once()

    @patch("ollama.Client")
    def test_analyze_changes_failure(self, mock_ollama_client: Mock) -> None:
        """Test failed change analysis."""
        mock_client = Mock()
        mock_ollama_client.return_value = mock_client
        mock_client.chat.side_effect = Exception("API Error")

        analyzer = OllamaAnalyzer()
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.fork = "user/fork"
        mock_repo.upstream = "upstream/repo"
        mock_repo.skills = ["python"]

        request = AnalysisRequest(
            repository=mock_repo,
            git_repo=Mock(),
            diff_content="test diff",
            commit_messages=["test commit"],
        )

        with pytest.raises(Exception, match="API Error"):
            analyzer.analyze_changes(request)

    def test_parse_analysis_response_json_success(self) -> None:
        """Test parsing JSON response successfully."""
        analyzer = OllamaAnalyzer()
        response = (
            '{"summary": "Test", "breaking_changes": ["Change"], "confidence": 0.9}'
        )

        result = analyzer._parse_analysis_response(response)
        assert result.summary == "Test"
        assert result.breaking_changes == ["Change"]
        assert result.confidence == 0.9

    def test_parse_analysis_response_json_failure(self) -> None:
        """Test parsing JSON response with fallback to text parsing."""
        analyzer = OllamaAnalyzer()
        response = "Invalid JSON response with summary: Test summary"

        result = analyzer._parse_analysis_response(response)
        assert result.summary == "Test summary"
        assert result.confidence == 0.5


class TestChangeAnalyzer:
    """Test ChangeAnalyzer class."""

    def test_change_analyzer_initialization(self) -> None:
        """Test ChangeAnalyzer initialization."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)
        assert analyzer.config == mock_config
        assert analyzer.analyzers == {}

    def test_get_analyzer_openai(self) -> None:
        """Test getting OpenAI analyzer."""
        mock_config = Mock()
        mock_config.settings.api_key_env = "TEST_API_KEY"
        with patch.dict(os.environ, {"TEST_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            openai_analyzer = analyzer.get_analyzer("openai")
            assert isinstance(openai_analyzer, OpenAIAnalyzer)
            assert openai_analyzer.api_key == "test-key"

    def test_get_analyzer_anthropic(self) -> None:
        """Test getting Anthropic analyzer."""
        mock_config = Mock()
        mock_config.settings.api_key_env = "TEST_API_KEY"
        with patch.dict(os.environ, {"TEST_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            anthropic_analyzer = analyzer.get_analyzer("anthropic")
            assert isinstance(anthropic_analyzer, AnthropicAnalyzer)
            assert anthropic_analyzer.api_key == "test-key"

    def test_get_analyzer_ollama(self) -> None:
        """Test getting Ollama analyzer."""
        mock_config = Mock()
        mock_config.settings.ollama_host = "http://localhost:8080"
        mock_config.settings.ollama_model = "codellama"

        with patch("gitco.analyzer.OllamaAnalyzer") as mock_ollama_analyzer:
            mock_analyzer_instance = Mock()
            mock_ollama_analyzer.return_value = mock_analyzer_instance

            analyzer = ChangeAnalyzer(mock_config)
            ollama_analyzer = analyzer.get_analyzer("ollama")

            assert isinstance(ollama_analyzer, Mock)
            mock_ollama_analyzer.assert_called_once_with(
                model="codellama", host="http://localhost:8080"
            )

    def test_get_analyzer_ollama_defaults(self) -> None:
        """Test getting Ollama analyzer with default settings."""
        mock_config = Mock()
        mock_config.settings.ollama_host = "http://localhost:11434"
        mock_config.settings.ollama_model = "llama2"

        with patch("gitco.analyzer.OllamaAnalyzer") as mock_ollama_analyzer:
            mock_analyzer_instance = Mock()
            mock_ollama_analyzer.return_value = mock_analyzer_instance

            analyzer = ChangeAnalyzer(mock_config)
            ollama_analyzer = analyzer.get_analyzer("ollama")

            assert isinstance(ollama_analyzer, Mock)
            mock_ollama_analyzer.assert_called_once_with(
                model="llama2", host="http://localhost:11434"
            )

    def test_get_analyzer_unsupported_provider(self) -> None:
        """Test getting unsupported analyzer."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)
        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            analyzer.get_analyzer("unsupported")

    def test_analyze_repository_changes_disabled(self) -> None:
        """Test repository analysis when disabled."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = False
        mock_repo = Mock()
        mock_repo.analysis_enabled = True

        analyzer = ChangeAnalyzer(mock_config)
        result = analyzer.analyze_repository_changes(mock_repo, Mock())
        assert result is None

    def test_analyze_repository_changes_no_changes(self) -> None:
        """Test repository analysis with no changes."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True
        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_git_repo = Mock()
        mock_git_repo.get_recent_changes.return_value = ""
        mock_git_repo.get_recent_commit_messages.return_value = []

        analyzer = ChangeAnalyzer(mock_config)
        result = analyzer.analyze_repository_changes(mock_repo, mock_git_repo)
        assert result is None

    @patch("gitco.analyzer.OpenAIAnalyzer")
    def test_analyze_repository_changes_success(
        self, mock_openai_analyzer: Mock
    ) -> None:
        """Test successful repository analysis."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True
        mock_config.settings.llm_provider = "openai"
        mock_config.settings.api_key_env = "TEST_API_KEY"

        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_repo.name = "test-repo"
        mock_git_repo = Mock()
        mock_git_repo.get_recent_changes.return_value = "test diff"
        mock_git_repo.get_recent_commit_messages.return_value = ["test commit"]

        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze_changes.return_value = ChangeAnalysis(
            summary="Test analysis",
            breaking_changes=[],
            new_features=[],
            bug_fixes=[],
            security_updates=[],
            deprecations=[],
            recommendations=[],
            confidence=0.8,
        )
        mock_openai_analyzer.return_value = mock_analyzer_instance

        with patch.dict(os.environ, {"TEST_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            result = analyzer.analyze_repository_changes(mock_repo, mock_git_repo)
            assert result is not None
            assert result.summary == "Test analysis"

    def test_analyze_repository_changes_exception(self) -> None:
        """Test repository analysis with exception."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True
        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_git_repo = Mock()
        mock_git_repo.get_recent_changes.side_effect = Exception("Test error")

        analyzer = ChangeAnalyzer(mock_config)
        result = analyzer.analyze_repository_changes(mock_repo, mock_git_repo)
        assert result is None

    def test_display_analysis(self) -> None:
        """Test displaying analysis results."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)

        analysis = ChangeAnalysis(
            summary="Test summary",
            breaking_changes=["Change 1"],
            new_features=["Feature 1"],
            bug_fixes=["Fix 1"],
            security_updates=["Security 1"],
            deprecations=["Deprecation 1"],
            recommendations=["Recommendation 1"],
            confidence=0.8,
        )

        # This should not raise any exceptions
        analyzer.display_analysis(analysis, "test-repo")
