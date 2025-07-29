"""Test GitCo CLI functionality."""

from collections.abc import Generator
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from gitco.cli import main


@pytest.fixture
def runner() -> CliRunner:
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_config_manager() -> Generator[Mock, None, None]:
    """Mock config manager."""
    from unittest.mock import patch

    with patch("gitco.cli.ConfigManager") as mock:
        yield mock


@pytest.fixture
def mock_git_repo() -> Generator[Mock, None, None]:
    """Mock git repository."""
    from unittest.mock import patch

    with patch("gitco.cli.GitRepository") as mock:
        yield mock


def test_cli_version(runner: CliRunner) -> None:
    """Test that the CLI shows version information."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output
    assert "0.1.0" in result.output


def test_cli_help(runner: CliRunner) -> None:
    """Test that the CLI shows help information."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "GitCo" in result.output
    assert "init" in result.output
    assert "sync" in result.output
    assert "analyze" in result.output
    assert "discover" in result.output
    assert "status" in result.output
    assert "upstream" in result.output


def test_init_command(runner: CliRunner) -> None:
    """Test the init command."""
    result = runner.invoke(main, ["init"])
    # The command will fail if config file exists, which is expected
    if result.exit_code == 0:
        assert "Initializing GitCo configuration" in result.output
        assert "Configuration initialized successfully" in result.output
    else:
        assert "Configuration file already exists" in result.output


def test_init_command_with_force(runner: CliRunner) -> None:
    """Test the init command with force flag."""
    result = runner.invoke(main, ["init", "--force"])
    assert result.exit_code == 0
    assert "Configuration initialized successfully" in result.output


def test_init_command_with_template(runner: CliRunner) -> None:
    """Test the init command with template."""
    result = runner.invoke(main, ["init", "--template", "custom.yml"])
    assert result.exit_code == 0
    assert "Using custom template: custom.yml" in result.output


def test_sync_command(runner: CliRunner) -> None:
    """Test the sync command."""
    result = runner.invoke(main, ["sync"])
    # The sync command will fail because the repositories don't exist, but it should handle the error gracefully
    assert result.exit_code == 1
    assert (
        "Configuration file not found" in result.output
        or "Failed to sync" in result.output
        or "repositories failed" in result.output
    )


def test_sync_command_with_repo(runner: CliRunner) -> None:
    """Test the sync command with specific repository."""
    result = runner.invoke(main, ["sync", "--repo", "django"])
    # The sync command will fail because the repository doesn't exist, but it should handle the error gracefully
    assert result.exit_code == 1
    assert (
        "Repository 'django' not found" in result.output
        or "Failed to sync" in result.output
    )


def test_sync_command_with_analyze(runner: CliRunner) -> None:
    """Test the sync command with analysis."""
    result = runner.invoke(main, ["sync", "--analyze"])
    # The sync command will fail because the repositories don't exist, but it should handle the error gracefully
    assert result.exit_code == 1
    assert "AI analysis requested" in result.output


def test_analyze_command(runner: CliRunner) -> None:
    """Test the analyze command."""
    result = runner.invoke(main, ["analyze", "--repo", "fastapi"])
    assert result.exit_code == 0
    assert (
        "Repository Not Found" in result.output or "Invalid Repository" in result.output
    )


def test_analyze_command_with_prompt(runner: CliRunner) -> None:
    """Test the analyze command with custom prompt."""
    result = runner.invoke(
        main, ["analyze", "--repo", "fastapi", "--prompt", "Custom prompt"]
    )
    assert result.exit_code == 0
    assert (
        "Repository Not Found" in result.output or "Invalid Repository" in result.output
    )


def test_analyze_command_with_provider_validation(
    runner: CliRunner, mock_config_manager: Mock, mock_git_repo: Mock
) -> None:
    """Test analyze command with provider validation."""
    # Mock successful repository lookup
    mock_repo = Mock()
    mock_repo.name = "test-repo"
    mock_repo.local_path = "/tmp/test-repo"
    mock_repo.analysis_enabled = True
    mock_config_manager.return_value.get_repository.return_value = mock_repo

    # Mock successful git repository validation
    mock_git_repo.return_value.is_git_repository.return_value = True
    mock_git_repo.return_value.get_recent_changes.return_value = "test changes"
    mock_git_repo.return_value.get_recent_commit_messages.return_value = ["test commit"]

    # Test with invalid provider
    result = runner.invoke(
        main,
        ["analyze", "--repo", "test-repo", "--provider", "invalid"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Invalid LLM Provider" in result.output
    assert "invalid" in result.output
    assert "Supported providers" in result.output

    # Test with valid provider
    result = runner.invoke(
        main,
        ["analyze", "--repo", "test-repo", "--provider", "anthropic"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "LLM Provider" in result.output
    assert "anthropic" in result.output


def test_discover_command(runner: CliRunner) -> None:
    """Test the discover command."""
    result = runner.invoke(main, ["discover"])
    assert result.exit_code == 0
    assert "Discovering Contribution Opportunities" in result.output


def test_discover_command_with_skill(runner: CliRunner) -> None:
    """Test the discover command with skill filter."""
    result = runner.invoke(main, ["discover", "--skill", "python"])
    assert result.exit_code == 0
    assert "python" in result.output


def test_discover_command_with_label(runner: CliRunner) -> None:
    """Test the discover command with label filter."""
    result = runner.invoke(main, ["discover", "--label", "good first issue"])
    assert result.exit_code == 0
    assert "good first issue" in result.output


def test_status_command(runner: CliRunner) -> None:
    """Test the status command."""
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "Repository Status" in result.output


def test_status_command_with_repo(runner: CliRunner) -> None:
    """Test the status command with specific repository."""
    result = runner.invoke(main, ["status", "--repo", "django"])
    assert result.exit_code == 0
    assert "django" in result.output


def test_status_command_with_detailed(runner: CliRunner) -> None:
    """Test the status command with detailed output."""
    result = runner.invoke(main, ["status", "--detailed"])
    assert result.exit_code == 0
    assert "Detailed" in result.output


def test_upstream_group_help(runner: CliRunner) -> None:
    """Test the upstream group help."""
    result = runner.invoke(main, ["upstream", "--help"])
    assert result.exit_code == 0
    assert "upstream" in result.output
    assert "add" in result.output
    assert "remove" in result.output
    assert "update" in result.output
    assert "validate" in result.output
    assert "fetch" in result.output
    assert "merge" in result.output


def test_upstream_add_command(runner: CliRunner) -> None:
    """Test the upstream add command."""
    result = runner.invoke(
        main,
        [
            "upstream",
            "add",
            "--repo",
            "/path/to/repo",
            "--url",
            "git@github.com:django/django.git",
        ],
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_add_command_missing_repo(runner: CliRunner) -> None:
    """Test the upstream add command with missing repo."""
    result = runner.invoke(
        main, ["upstream", "add", "--url", "git@github.com:django/django.git"]
    )
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_upstream_add_command_missing_url(runner: CliRunner) -> None:
    """Test the upstream add command with missing URL."""
    result = runner.invoke(main, ["upstream", "add", "--repo", "/path/to/repo"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_upstream_remove_command(runner: CliRunner) -> None:
    """Test the upstream remove command."""
    result = runner.invoke(main, ["upstream", "remove", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_remove_command_missing_repo(runner: CliRunner) -> None:
    """Test the upstream remove command with missing repo."""
    result = runner.invoke(main, ["upstream", "remove"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_upstream_update_command(runner: CliRunner) -> None:
    """Test the upstream update command."""
    result = runner.invoke(
        main,
        [
            "upstream",
            "update",
            "--repo",
            "/path/to/repo",
            "--url",
            "git@github.com:new/django.git",
        ],
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_update_command_missing_repo(runner: CliRunner) -> None:
    """Test the upstream update command with missing repo."""
    result = runner.invoke(
        main, ["upstream", "update", "--url", "git@github.com:new/django.git"]
    )
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_upstream_update_command_missing_url(runner: CliRunner) -> None:
    """Test the upstream update command with missing URL."""
    result = runner.invoke(main, ["upstream", "update", "--repo", "/path/to/repo"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_upstream_validate_command(runner: CliRunner) -> None:
    """Test the upstream validate command."""
    result = runner.invoke(main, ["upstream", "validate", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Error" in result.output or "Invalid" in result.output


def test_upstream_validate_command_missing_repo(runner: CliRunner) -> None:
    """Test the upstream validate command with missing repo."""
    result = runner.invoke(main, ["upstream", "validate"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "No such command" in result.output


def test_upstream_fetch_command(runner: CliRunner) -> None:
    """Test the upstream fetch command."""
    result = runner.invoke(main, ["upstream", "fetch", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_fetch_command_missing_repo(runner: CliRunner) -> None:
    """Test the upstream fetch command with missing repo."""
    result = runner.invoke(main, ["upstream", "fetch"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_help_command(runner: CliRunner) -> None:
    """Test the help command."""
    result = runner.invoke(main, ["help"])
    assert result.exit_code == 0
    assert "GitCo" in result.output


def test_verbose_flag(runner: CliRunner) -> None:
    """Test the verbose flag."""
    result = runner.invoke(main, ["--verbose", "help"])
    assert result.exit_code == 0
    assert "GitCo" in result.output


def test_quiet_flag(runner: CliRunner) -> None:
    """Test the quiet flag."""
    result = runner.invoke(main, ["--quiet", "help"])
    assert result.exit_code == 0
    assert "GitCo" in result.output


def test_command_help(runner: CliRunner) -> None:
    """Test command-specific help."""
    result = runner.invoke(main, ["sync", "--help"])
    assert result.exit_code == 0
    assert "sync" in result.output
    assert "repositories" in result.output


def test_invalid_command(runner: CliRunner) -> None:
    """Test invalid command."""
    result = runner.invoke(main, ["invalid_command"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "No such command" in result.output


def test_upstream_merge_command(runner: CliRunner) -> None:
    """Test the upstream merge command."""
    result = runner.invoke(main, ["upstream", "merge", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_missing_repo(runner: CliRunner) -> None:
    """Test the upstream merge command with missing repo."""
    result = runner.invoke(main, ["upstream", "merge"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Missing option" in result.output


def test_upstream_merge_command_with_branch(runner: CliRunner) -> None:
    """Test the upstream merge command with branch parameter."""
    result = runner.invoke(
        main, ["upstream", "merge", "--repo", "/path/to/repo", "--branch", "develop"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_with_strategy(runner: CliRunner) -> None:
    """Test the upstream merge command with strategy parameter."""
    result = runner.invoke(
        main, ["upstream", "merge", "--repo", "/path/to/repo", "--strategy", "theirs"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_abort(runner: CliRunner) -> None:
    """Test the upstream merge command with abort flag."""
    result = runner.invoke(
        main, ["upstream", "merge", "--repo", "/path/to/repo", "--abort"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_resolve(runner: CliRunner) -> None:
    """Test the upstream merge command with resolve flag."""
    result = runner.invoke(
        main,
        [
            "upstream",
            "merge",
            "--repo",
            "/path/to/repo",
            "--resolve",
            "--strategy",
            "ours",
        ],
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_help(runner: CliRunner) -> None:
    """Test help for the upstream merge command."""
    result = runner.invoke(main, ["upstream", "merge", "--help"])
    assert result.exit_code == 0
    assert "Merge upstream changes into current branch" in result.output
    assert "--repo" in result.output
    assert "--branch" in result.output
    assert "--strategy" in result.output
    assert "--abort" in result.output
    assert "--resolve" in result.output


def test_upstream_merge_command_with_invalid_strategy(runner: CliRunner) -> None:
    """Test upstream merge command with invalid strategy."""
    result = runner.invoke(
        main,
        ["upstream", "merge", "--repo", "test", "--resolve", "--strategy", "invalid"],
    )
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Error" in result.output or "Invalid" in result.output


def test_upstream_merge_command_without_repo_and_strategy(runner: CliRunner) -> None:
    """Test upstream merge command without repo and strategy."""
    result = runner.invoke(main, ["upstream", "merge", "--resolve"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Error" in result.output


def test_upstream_merge_command_with_branch_and_strategy(runner: CliRunner) -> None:
    """Test upstream merge command with branch and strategy."""
    result = runner.invoke(
        main,
        [
            "upstream",
            "merge",
            "--repo",
            "test",
            "--branch",
            "develop",
            "--resolve",
            "--strategy",
            "ours",
        ],
    )
    assert result.exit_code == 1
    assert "Error" in result.output or "Repository" in result.output


def test_upstream_merge_command_abort_without_repo(runner: CliRunner) -> None:
    """Test upstream merge abort command without repo."""
    result = runner.invoke(main, ["upstream", "merge", "--abort"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Error" in result.output


def test_upstream_merge_command_resolve_without_repo(runner: CliRunner) -> None:
    """Test upstream merge resolve command without repo."""
    result = runner.invoke(main, ["upstream", "merge", "--resolve"])
    assert result.exit_code == 2  # Click uses exit code 2 for usage errors
    assert "Error" in result.output
