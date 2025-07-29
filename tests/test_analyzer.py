"""Tests for the analyzer module."""

import os
from unittest.mock import Mock, patch

import pytest

from gitco.analyzer import (
    AnalysisRequest,
    AnthropicAnalyzer,
    ChangeAnalysis,
    ChangeAnalyzer,
    OpenAIAnalyzer,
)


class TestChangeAnalysis:
    """Test ChangeAnalysis dataclass."""

    def test_change_analysis_creation(self):
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

    def test_analysis_request_creation(self):
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
    def test_openai_analyzer_initialization(self):
        """Test OpenAIAnalyzer initialization."""
        analyzer = OpenAIAnalyzer()
        assert analyzer.api_key == "test-key"
        assert analyzer.model == "gpt-3.5-turbo"

    def test_openai_analyzer_initialization_with_api_key(self):
        """Test OpenAIAnalyzer initialization with explicit API key."""
        analyzer = OpenAIAnalyzer(api_key="explicit-key", model="gpt-4")
        assert analyzer.api_key == "explicit-key"
        assert analyzer.model == "gpt-4"

    def test_openai_analyzer_initialization_no_api_key(self):
        """Test OpenAIAnalyzer initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIAnalyzer()

    def test_build_analysis_prompt(self):
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

    def test_get_system_prompt(self):
        """Test getting system prompt."""
        analyzer = OpenAIAnalyzer(api_key="test-key")
        prompt = analyzer._get_system_prompt()
        assert "expert software developer" in prompt
        assert "open source contributor" in prompt

    def test_parse_text_response(self):
        """Test parsing text response."""
        analyzer = OpenAIAnalyzer(api_key="test-key")
        response = """
        Summary: Test summary
        Breaking Changes:
        - Change 1
        - Change 2
        New Features:
        - Feature 1
        Bug Fixes:
        - Fix 1
        Security Updates:
        - Security 1
        Deprecations:
        - Deprecation 1
        Recommendations:
        - Recommendation 1
        """

        data = analyzer._parse_text_response(response)
        assert data["summary"] == "Test summary"
        assert "Change 1" in data["breaking_changes"]
        assert "Change 2" in data["breaking_changes"]
        assert "Feature 1" in data["new_features"]
        assert "Fix 1" in data["bug_fixes"]
        assert "Security 1" in data["security_updates"]
        assert "Deprecation 1" in data["deprecations"]
        assert "Recommendation 1" in data["recommendations"]

    @patch("openai.OpenAI")
    def test_analyze_changes_success(self, mock_openai):
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
        assert isinstance(result, ChangeAnalysis)
        assert result.summary == "Test"
        assert result.confidence == 0.8

    @patch("openai.OpenAI")
    def test_analyze_changes_failure(self, mock_openai):
        """Test change analysis failure."""
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
    def test_anthropic_analyzer_initialization(self):
        """Test AnthropicAnalyzer initialization."""
        analyzer = AnthropicAnalyzer()
        assert analyzer.api_key == "test-key"
        assert analyzer.model == "claude-3-sonnet-20240229"

    def test_anthropic_analyzer_initialization_with_api_key(self):
        """Test AnthropicAnalyzer initialization with explicit API key."""
        analyzer = AnthropicAnalyzer(
            api_key="explicit-key", model="claude-3-opus-20240229"
        )
        assert analyzer.api_key == "explicit-key"
        assert analyzer.model == "claude-3-opus-20240229"

    def test_anthropic_analyzer_initialization_no_api_key(self):
        """Test AnthropicAnalyzer initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key not provided"):
                AnthropicAnalyzer()

    def test_build_analysis_prompt(self):
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

    def test_get_system_prompt(self):
        """Test getting system prompt."""
        analyzer = AnthropicAnalyzer(api_key="test-key")
        prompt = analyzer._get_system_prompt()
        assert "expert software developer" in prompt
        assert "open source contributor" in prompt

    def test_parse_text_response(self):
        """Test parsing text response."""
        analyzer = AnthropicAnalyzer(api_key="test-key")
        response = """
        Summary: Test summary
        Breaking Changes:
        - Change 1
        - Change 2
        New Features:
        - Feature 1
        Bug Fixes:
        - Fix 1
        Security Updates:
        - Security 1
        Deprecations:
        - Deprecation 1
        Recommendations:
        - Recommendation 1
        """

        data = analyzer._parse_text_response(response)
        assert data["summary"] == "Test summary"
        assert "Change 1" in data["breaking_changes"]
        assert "Change 2" in data["breaking_changes"]
        assert "Feature 1" in data["new_features"]
        assert "Fix 1" in data["bug_fixes"]
        assert "Security 1" in data["security_updates"]
        assert "Deprecation 1" in data["deprecations"]
        assert "Recommendation 1" in data["recommendations"]

    @patch("anthropic.Anthropic")
    def test_analyze_changes_success(self, mock_anthropic):
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
        assert isinstance(result, ChangeAnalysis)
        assert result.summary == "Test"
        assert result.confidence == 0.8

    @patch("anthropic.Anthropic")
    def test_analyze_changes_failure(self, mock_anthropic):
        """Test change analysis failure."""
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


class TestChangeAnalyzer:
    """Test ChangeAnalyzer class."""

    def test_change_analyzer_initialization(self):
        """Test ChangeAnalyzer initialization."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)
        assert analyzer.config == mock_config
        assert analyzer.analyzers == {}

    def test_get_analyzer_openai(self):
        """Test getting OpenAI analyzer."""
        mock_config = Mock()
        mock_config.settings.api_key_env = "TEST_API_KEY"
        with patch.dict(os.environ, {"TEST_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            openai_analyzer = analyzer.get_analyzer("openai")
            assert isinstance(openai_analyzer, OpenAIAnalyzer)
            assert openai_analyzer.api_key == "test-key"

    def test_get_analyzer_anthropic(self):
        """Test getting Anthropic analyzer."""
        mock_config = Mock()
        mock_config.settings.api_key_env = "TEST_API_KEY"
        with patch.dict(os.environ, {"TEST_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            anthropic_analyzer = analyzer.get_analyzer("anthropic")
            assert isinstance(anthropic_analyzer, AnthropicAnalyzer)
            assert anthropic_analyzer.api_key == "test-key"

    def test_get_analyzer_unsupported_provider(self):
        """Test getting unsupported analyzer."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)
        with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported"):
            analyzer.get_analyzer("unsupported")

    def test_analyze_repository_changes_disabled(self):
        """Test repository analysis when disabled."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = False
        mock_repo = Mock()
        mock_repo.analysis_enabled = True

        analyzer = ChangeAnalyzer(mock_config)
        result = analyzer.analyze_repository_changes(mock_repo, Mock())
        assert result is None

    def test_analyze_repository_changes_no_changes(self):
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
    def test_analyze_repository_changes_success(self, mock_openai_analyzer):
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

    def test_analyze_repository_changes_exception(self):
        """Test repository analysis with exception."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True
        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_repo.name = "test-repo"
        mock_git_repo = Mock()
        mock_git_repo.get_recent_changes.side_effect = Exception("Git error")

        analyzer = ChangeAnalyzer(mock_config)
        result = analyzer.analyze_repository_changes(mock_repo, mock_git_repo)
        assert result is None

    def test_display_analysis(self):
        """Test displaying analysis results."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)
        analysis = ChangeAnalysis(
            summary="Test summary",
            breaking_changes=["Breaking change"],
            new_features=["New feature"],
            bug_fixes=["Bug fix"],
            security_updates=["Security update"],
            deprecations=["Deprecation"],
            recommendations=["Recommendation"],
            confidence=0.8,
        )

        # This test just ensures the method doesn't raise an exception
        analyzer.display_analysis(analysis, "test-repo")
