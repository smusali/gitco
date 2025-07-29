"""Tests for the analyzer module."""

import os
from unittest.mock import Mock, patch

import pytest

from gitco.analyzer import (
    AnalysisRequest,
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
            custom_prompt="custom prompt",
        )

        prompt = analyzer._build_analysis_prompt(request)

        assert "test-repo" in prompt
        assert "user/fork" in prompt
        assert "upstream/repo" in prompt
        assert "python, web" in prompt
        assert "test diff content" in prompt
        assert "commit 1" in prompt
        assert "commit 2" in prompt
        assert "custom prompt" in prompt

    def test_get_system_prompt(self):
        """Test getting system prompt."""
        analyzer = OpenAIAnalyzer(api_key="test-key")
        prompt = analyzer._get_system_prompt()

        assert "expert software developer" in prompt
        assert "open source contributor" in prompt
        assert "analyze code changes" in prompt

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
        """

        data = analyzer._parse_text_response(response)

        # The parsing should now work correctly
        assert data["summary"] == "Test summary"
        assert "Change 1" in data["breaking_changes"]
        assert "Change 2" in data["breaking_changes"]
        assert "Feature 1" in data["new_features"]
        assert "Fix 1" in data["bug_fixes"]

    @patch("openai.OpenAI")
    def test_analyze_changes_success(self, mock_openai):
        """Test successful change analysis."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = """
        {
            "summary": "Test summary",
            "breaking_changes": ["Change 1"],
            "new_features": ["Feature 1"],
            "bug_fixes": ["Fix 1"],
            "security_updates": ["Security 1"],
            "deprecations": ["Deprecation 1"],
            "recommendations": ["Recommendation 1"],
            "confidence": 0.85
        }
        """

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

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
            commit_messages=["commit 1"],
        )

        analysis = analyzer.analyze_changes(request)

        assert analysis.summary == "Test summary"
        assert analysis.breaking_changes == ["Change 1"]
        assert analysis.new_features == ["Feature 1"]
        assert analysis.bug_fixes == ["Fix 1"]
        assert analysis.security_updates == ["Security 1"]
        assert analysis.deprecations == ["Deprecation 1"]
        assert analysis.recommendations == ["Recommendation 1"]
        assert analysis.confidence == 0.85

    @patch("openai.OpenAI")
    def test_analyze_changes_failure(self, mock_openai):
        """Test change analysis failure."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

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
            commit_messages=["commit 1"],
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
        mock_config.settings.api_key_env = "OPENAI_API_KEY"

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            openai_analyzer = analyzer.get_analyzer("openai")

            assert isinstance(openai_analyzer, OpenAIAnalyzer)
            assert openai_analyzer.api_key == "test-key"

    def test_get_analyzer_unsupported_provider(self):
        """Test getting unsupported analyzer."""
        mock_config = Mock()
        analyzer = ChangeAnalyzer(mock_config)

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            analyzer.get_analyzer("unsupported")

    def test_analyze_repository_changes_disabled(self):
        """Test analysis when disabled."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = False

        analyzer = ChangeAnalyzer(mock_config)
        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_git_repo = Mock()

        result = analyzer.analyze_repository_changes(
            repository=mock_repo,
            git_repo=mock_git_repo,
        )

        assert result is None

    def test_analyze_repository_changes_no_changes(self):
        """Test analysis when no changes are found."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True

        analyzer = ChangeAnalyzer(mock_config)
        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_git_repo = Mock()
        mock_git_repo.get_recent_changes.return_value = ""
        mock_git_repo.get_recent_commit_messages.return_value = []

        result = analyzer.analyze_repository_changes(
            repository=mock_repo,
            git_repo=mock_git_repo,
        )

        assert result is None

    @patch("gitco.analyzer.OpenAIAnalyzer")
    def test_analyze_repository_changes_success(self, mock_openai_analyzer):
        """Test successful repository analysis."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True
        mock_config.settings.llm_provider = "openai"
        mock_config.settings.api_key_env = "OPENAI_API_KEY"

        mock_analyzer = Mock()
        mock_analysis = Mock()
        mock_openai_analyzer.return_value = mock_analyzer
        mock_analyzer.analyze_changes.return_value = mock_analysis

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            analyzer = ChangeAnalyzer(mock_config)
            mock_repo = Mock()
            mock_repo.analysis_enabled = True
            mock_git_repo = Mock()
            mock_git_repo.get_recent_changes.return_value = "test diff"
            mock_git_repo.get_recent_commit_messages.return_value = ["commit 1"]

            result = analyzer.analyze_repository_changes(
                repository=mock_repo,
                git_repo=mock_git_repo,
            )

            assert result == mock_analysis
            mock_analyzer.analyze_changes.assert_called_once()

    def test_analyze_repository_changes_exception(self):
        """Test repository analysis with exception."""
        mock_config = Mock()
        mock_config.settings.analysis_enabled = True

        analyzer = ChangeAnalyzer(mock_config)
        mock_repo = Mock()
        mock_repo.analysis_enabled = True
        mock_repo.name = "test-repo"
        mock_git_repo = Mock()
        mock_git_repo.get_recent_changes.side_effect = Exception("Git error")

        result = analyzer.analyze_repository_changes(
            repository=mock_repo,
            git_repo=mock_git_repo,
        )

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

        # This should not raise any exceptions
        analyzer.display_analysis(analysis, "test-repo")
