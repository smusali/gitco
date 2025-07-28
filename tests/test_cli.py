"""Test GitCo CLI functionality."""

import pytest
from click.testing import CliRunner
from gitco.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_cli_version(runner):
    """Test that the CLI shows version information."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output
    assert "0.1.0" in result.output


def test_cli_help(runner):
    """Test that the CLI shows help information."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "GitCo" in result.output
    assert "init" in result.output
    assert "sync" in result.output
    assert "analyze" in result.output
    assert "discover" in result.output
    assert "status" in result.output


def test_init_command(runner):
    """Test the init command."""
    result = runner.invoke(main, ["init"])
    # The command will fail if config file exists, which is expected
    if result.exit_code == 0:
        assert "Initializing GitCo configuration" in result.output
        assert "Configuration initialized successfully" in result.output
    else:
        assert "Configuration file already exists" in result.output


def test_init_command_with_force(runner):
    """Test the init command with force flag."""
    result = runner.invoke(main, ["init", "--force"])
    assert result.exit_code == 0
    assert "Configuration initialized successfully" in result.output


def test_init_command_with_template(runner):
    """Test the init command with template."""
    result = runner.invoke(main, ["init", "--template", "custom.yml"])
    assert result.exit_code == 0
    assert "Using custom template: custom.yml" in result.output


def test_sync_command(runner):
    """Test the sync command."""
    result = runner.invoke(main, ["sync"])
    assert result.exit_code == 0
    assert "Synchronizing repositories" in result.output
    assert "Repository synchronization completed" in result.output


def test_sync_command_with_repo(runner):
    """Test the sync command with specific repository."""
    result = runner.invoke(main, ["sync", "--repo", "django"])
    assert result.exit_code == 0
    assert "Syncing repository: django" in result.output


def test_sync_command_with_analyze(runner):
    """Test the sync command with analysis."""
    result = runner.invoke(main, ["sync", "--analyze"])
    assert result.exit_code == 0
    assert "AI analysis enabled" in result.output


def test_analyze_command(runner):
    """Test the analyze command."""
    result = runner.invoke(main, ["analyze", "--repo", "fastapi"])
    assert result.exit_code == 0
    assert "Analyzing repository changes" in result.output
    assert "Analyzing repository: fastapi" in result.output
    assert "Analysis completed" in result.output


def test_analyze_command_with_prompt(runner):
    """Test the analyze command with custom prompt."""
    result = runner.invoke(
        main, ["analyze", "--repo", "django", "--prompt", "Security focus"]
    )
    assert result.exit_code == 0
    assert "Using custom prompt: Security focus" in result.output


def test_discover_command(runner):
    """Test the discover command."""
    result = runner.invoke(main, ["discover"])
    assert result.exit_code == 0
    assert "Discovering contribution opportunities" in result.output
    assert "Discovery completed" in result.output


def test_discover_command_with_skill(runner):
    """Test the discover command with skill filter."""
    result = runner.invoke(main, ["discover", "--skill", "python"])
    assert result.exit_code == 0
    assert "Filtering by skill: python" in result.output


def test_discover_command_with_label(runner):
    """Test the discover command with label filter."""
    result = runner.invoke(main, ["discover", "--label", "good first issue"])
    assert result.exit_code == 0
    assert "Filtering by label: good first issue" in result.output


def test_status_command(runner):
    """Test the status command."""
    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "Checking repository status" in result.output
    assert "Status check completed" in result.output


def test_status_command_with_repo(runner):
    """Test the status command with specific repository."""
    result = runner.invoke(main, ["status", "--repo", "django"])
    assert result.exit_code == 0
    assert "Checking status for: django" in result.output


def test_status_command_with_detailed(runner):
    """Test the status command with detailed flag."""
    result = runner.invoke(main, ["status", "--detailed"])
    assert result.exit_code == 0
    assert "Detailed mode enabled" in result.output


def test_help_command(runner):
    """Test the help command."""
    result = runner.invoke(main, ["help"])
    assert result.exit_code == 0
    assert "GitCo Help" in result.output
    assert "init" in result.output
    assert "sync" in result.output
    assert "analyze" in result.output
    assert "discover" in result.output
    assert "status" in result.output


def test_verbose_flag(runner):
    """Test the verbose flag."""
    result = runner.invoke(main, ["--verbose", "init"])
    # The command may fail if config file exists, which is expected
    if result.exit_code == 0:
        assert "Configuration initialized successfully" in result.output
    else:
        assert "Configuration file already exists" in result.output


def test_quiet_flag(runner):
    """Test the quiet flag."""
    result = runner.invoke(main, ["--quiet", "init"])
    # The command may fail if config file exists, which is expected
    if result.exit_code == 0:
        assert "Configuration initialized successfully" in result.output
    else:
        assert "Configuration file already exists" in result.output


def test_command_help(runner):
    """Test help for individual commands."""
    result = runner.invoke(main, ["sync", "--help"])
    assert result.exit_code == 0
    assert "Synchronize repositories with upstream changes" in result.output
    assert "--repo" in result.output
    assert "--analyze" in result.output


def test_invalid_command(runner):
    """Test handling of invalid commands."""
    result = runner.invoke(main, ["invalid-command"])
    assert result.exit_code != 0
    assert "No such command" in result.output
