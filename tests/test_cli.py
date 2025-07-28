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
    assert "upstream" in result.output


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
    # The sync command will fail because the repositories don't exist, but it should handle the error gracefully
    assert result.exit_code == 1
    assert (
        "Configuration file not found" in result.output
        or "Failed to sync" in result.output
        or "repositories failed" in result.output
    )


def test_sync_command_with_repo(runner):
    """Test the sync command with specific repository."""
    result = runner.invoke(main, ["sync", "--repo", "django"])
    # The sync command will fail because the repository doesn't exist, but it should handle the error gracefully
    assert result.exit_code == 1
    assert (
        "Repository 'django' not found" in result.output
        or "Failed to sync" in result.output
    )


def test_sync_command_with_analyze(runner):
    """Test the sync command with analysis."""
    result = runner.invoke(main, ["sync", "--analyze"])
    # The sync command will fail because the repositories don't exist, but it should handle the error gracefully
    assert result.exit_code == 1
    assert "AI analysis will be implemented in Commit 22" in result.output


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
    """Test the status command with detailed information."""
    result = runner.invoke(main, ["status", "--detailed"])
    assert result.exit_code == 0
    assert "Detailed mode enabled" in result.output


def test_upstream_group_help(runner):
    """Test the upstream command group help."""
    result = runner.invoke(main, ["upstream", "--help"])
    assert result.exit_code == 0
    assert "Manage upstream remotes for repositories" in result.output
    assert "add" in result.output
    assert "remove" in result.output
    assert "update" in result.output
    assert "validate" in result.output
    assert "fetch" in result.output


def test_upstream_add_command(runner):
    """Test the upstream add command."""
    result = runner.invoke(
        main,
        [
            "upstream",
            "add",
            "--repo",
            "/path/to/repo",
            "--url",
            "git@github.com:original/repo.git",
        ],
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_add_command_missing_repo(runner):
    """Test the upstream add command with missing repo parameter."""
    result = runner.invoke(
        main, ["upstream", "add", "--url", "git@github.com:original/repo.git"]
    )
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_add_command_missing_url(runner):
    """Test the upstream add command with missing url parameter."""
    result = runner.invoke(main, ["upstream", "add", "--repo", "/path/to/repo"])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_remove_command(runner):
    """Test the upstream remove command."""
    result = runner.invoke(main, ["upstream", "remove", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_remove_command_missing_repo(runner):
    """Test the upstream remove command with missing repo parameter."""
    result = runner.invoke(main, ["upstream", "remove"])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_update_command(runner):
    """Test the upstream update command."""
    result = runner.invoke(
        main,
        [
            "upstream",
            "update",
            "--repo",
            "/path/to/repo",
            "--url",
            "git@github.com:new/repo.git",
        ],
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_update_command_missing_repo(runner):
    """Test the upstream update command with missing repo parameter."""
    result = runner.invoke(
        main, ["upstream", "update", "--url", "git@github.com:new/repo.git"]
    )
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_update_command_missing_url(runner):
    """Test the upstream update command with missing url parameter."""
    result = runner.invoke(main, ["upstream", "update", "--repo", "/path/to/repo"])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_validate_command(runner):
    """Test the upstream validate command."""
    result = runner.invoke(
        main, ["upstream", "validate-upstream", "--repo", "/path/to/repo"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_validate_command_missing_repo(runner):
    """Test the upstream validate command with missing repo parameter."""
    result = runner.invoke(main, ["upstream", "validate-upstream"])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_fetch_command(runner):
    """Test the upstream fetch command."""
    result = runner.invoke(main, ["upstream", "fetch", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_fetch_command_missing_repo(runner):
    """Test the upstream fetch command with missing repo parameter."""
    result = runner.invoke(main, ["upstream", "fetch"])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_help_command(runner):
    """Test the help command."""
    result = runner.invoke(main, ["help"])
    assert result.exit_code == 0
    assert "GitCo Help" in result.output
    assert "Basic Commands" in result.output
    assert "Examples" in result.output


def test_verbose_flag(runner):
    """Test the verbose flag."""
    result = runner.invoke(main, ["--verbose", "help"])
    assert result.exit_code == 0
    # Verbose output should include more detailed logging
    assert "GitCo Help" in result.output


def test_quiet_flag(runner):
    """Test the quiet flag."""
    result = runner.invoke(main, ["--quiet", "help"])
    assert result.exit_code == 0
    # Quiet output should be minimal
    assert "GitCo Help" in result.output


def test_command_help(runner):
    """Test help for specific commands."""
    commands = ["init", "sync", "analyze", "discover", "status", "upstream"]
    for command in commands:
        result = runner.invoke(main, [command, "--help"])
        assert result.exit_code == 0
        assert command in result.output


def test_invalid_command(runner):
    """Test invalid command handling."""
    result = runner.invoke(main, ["invalid-command"])
    assert result.exit_code != 0
    assert "No such command" in result.output


def test_upstream_merge_command(runner):
    """Test the upstream merge command."""
    result = runner.invoke(main, ["upstream", "merge", "--repo", "/path/to/repo"])
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_missing_repo(runner):
    """Test the upstream merge command with missing repo parameter."""
    result = runner.invoke(main, ["upstream", "merge"])
    assert result.exit_code != 0
    assert "Missing option" in result.output


def test_upstream_merge_command_with_branch(runner):
    """Test the upstream merge command with branch parameter."""
    result = runner.invoke(
        main, ["upstream", "merge", "--repo", "/path/to/repo", "--branch", "develop"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_with_strategy(runner):
    """Test the upstream merge command with strategy parameter."""
    result = runner.invoke(
        main, ["upstream", "merge", "--repo", "/path/to/repo", "--strategy", "theirs"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_abort(runner):
    """Test the upstream merge command with abort flag."""
    result = runner.invoke(
        main, ["upstream", "merge", "--repo", "/path/to/repo", "--abort"]
    )
    # Should fail because the repository path doesn't exist
    assert result.exit_code == 1
    assert "Invalid repository path" in result.output


def test_upstream_merge_command_resolve(runner):
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


def test_upstream_merge_command_help(runner):
    """Test help for the upstream merge command."""
    result = runner.invoke(main, ["upstream", "merge", "--help"])
    assert result.exit_code == 0
    assert "Merge upstream changes into current branch" in result.output
    assert "--repo" in result.output
    assert "--branch" in result.output
    assert "--strategy" in result.output
    assert "--abort" in result.output
    assert "--resolve" in result.output
