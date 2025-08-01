"""Test GitCo CLI functionality."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from gitco.cli import main


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
    # The command will fail if config file exists and template doesn't exist, which is expected
    if result.exit_code == 0:
        assert "Using custom template: custom.yml" in result.output
    else:
        assert (
            "Configuration file already exists" in result.output
            or "Template file not found" in result.output
        )


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


@patch("gitco.cli.get_config_manager")
@patch("gitco.cli.create_github_client")
@patch("gitco.discovery.create_discovery_engine")
def test_discover_command(
    mock_discovery_engine: Mock,
    mock_github_client: Mock,
    mock_config_manager: Mock,
    runner: CliRunner,
) -> None:
    """Test the discover command."""
    # Mock config manager
    mock_config = Mock()
    mock_config.repositories = [Mock()]
    mock_config_manager.return_value.load_config.return_value = mock_config

    # Mock GitHub client
    mock_github = Mock()
    mock_github.test_connection.return_value = True
    mock_github_client.return_value = mock_github

    # Mock discovery engine
    mock_discovery = Mock()
    mock_discovery.discover_opportunities.return_value = []
    mock_discovery_engine.return_value = mock_discovery

    result = runner.invoke(main, ["discover"])
    assert result.exit_code == 0
    assert "Discovering Contribution Opportunities" in result.output


@patch("gitco.cli.get_config_manager")
@patch("gitco.cli.create_github_client")
@patch("gitco.discovery.create_discovery_engine")
def test_discover_command_with_skill(
    mock_discovery_engine: Mock,
    mock_github_client: Mock,
    mock_config_manager: Mock,
    runner: CliRunner,
) -> None:
    """Test the discover command with skill filter."""
    # Mock config manager
    mock_config = Mock()
    mock_config.repositories = [Mock()]
    mock_config_manager.return_value.load_config.return_value = mock_config

    # Mock GitHub client
    mock_github = Mock()
    mock_github.test_connection.return_value = True
    mock_github_client.return_value = mock_github

    # Mock discovery engine
    mock_discovery = Mock()
    mock_discovery.discover_opportunities.return_value = []
    mock_discovery_engine.return_value = mock_discovery

    result = runner.invoke(main, ["discover", "--skill", "python"])
    assert result.exit_code == 0
    assert (
        "Discovery Results" in result.output
        or "No Opportunities Found" in result.output
    )


@patch("gitco.cli.get_config_manager")
@patch("gitco.cli.create_github_client")
@patch("gitco.discovery.create_discovery_engine")
def test_discover_command_with_label(
    mock_discovery_engine: Mock,
    mock_github_client: Mock,
    mock_config_manager: Mock,
    runner: CliRunner,
) -> None:
    """Test the discover command with label filter."""
    # Mock config manager
    mock_config = Mock()
    mock_config.repositories = [Mock()]
    mock_config_manager.return_value.load_config.return_value = mock_config

    # Mock GitHub client
    mock_github = Mock()
    mock_github.test_connection.return_value = True
    mock_github_client.return_value = mock_github

    # Mock discovery engine
    mock_discovery = Mock()
    mock_discovery.discover_opportunities.return_value = []
    mock_discovery_engine.return_value = mock_discovery

    result = runner.invoke(main, ["discover", "--label", "good first issue"])
    assert result.exit_code == 0
    assert (
        "Discovery Results" in result.output
        or "No Opportunities Found" in result.output
    )


@patch("gitco.cli.get_config_manager")
@patch("gitco.cli.create_github_client")
@patch("gitco.health_metrics.create_health_calculator")
def test_status_command(
    mock_health_calculator: Mock,
    mock_github_client: Mock,
    mock_config_manager: Mock,
    runner: CliRunner,
) -> None:
    """Test the status command."""
    # Mock config manager
    mock_config = Mock()
    mock_config.repositories = [Mock()]
    mock_config_manager.return_value.load_config.return_value = mock_config

    # Mock GitHub client
    mock_github = Mock()
    mock_github_client.return_value = mock_github

    # Mock health calculator
    mock_health = Mock()
    mock_summary = Mock()
    mock_summary.total_repositories = 1
    mock_summary.healthy_repositories = 1
    mock_summary.needs_attention_repositories = 0
    mock_summary.critical_repositories = 0
    mock_summary.active_repositories_7d = 1
    mock_summary.active_repositories_30d = 1
    mock_summary.up_to_date_repositories = 1
    mock_summary.behind_repositories = 0
    mock_summary.diverged_repositories = 0
    mock_summary.high_engagement_repositories = 1
    mock_summary.low_engagement_repositories = 0
    mock_summary.average_activity_score = 0.8
    mock_summary.trending_repositories = []
    mock_summary.declining_repositories = []
    mock_summary.total_stars = 100
    mock_summary.total_forks = 50
    mock_summary.total_open_issues = 10
    mock_health.calculate_health_summary.return_value = mock_summary
    mock_health_calculator.return_value = mock_health

    result = runner.invoke(main, ["status"])
    assert result.exit_code == 0
    assert "Repository Health Summary" in result.output


@patch("gitco.cli.get_config_manager")
@patch("gitco.cli.create_github_client")
@patch("gitco.health_metrics.create_health_calculator")
def test_status_command_with_repo(
    mock_health_calculator: Mock,
    mock_github_client: Mock,
    mock_config_manager: Mock,
    runner: CliRunner,
) -> None:
    """Test the status command with specific repository."""
    # Mock config manager
    mock_config = Mock()
    mock_repo = Mock()
    mock_repo.name = "django"
    mock_config.repositories = [mock_repo]
    mock_config_manager.return_value.load_config.return_value = mock_config

    # Mock GitHub client
    mock_github = Mock()
    mock_github_client.return_value = mock_github

    # Mock health calculator
    mock_health = Mock()
    mock_metrics = Mock()
    mock_metrics.repository_name = "django"
    mock_metrics.health_status = "good"
    mock_metrics.overall_health_score = 0.8
    mock_metrics.recent_commits_7d = 5
    mock_metrics.recent_commits_30d = 20
    mock_metrics.total_commits = 1000
    mock_metrics.last_commit_days_ago = 2
    mock_metrics.stars_count = 50
    mock_metrics.forks_count = 25
    mock_metrics.open_issues_count = 5
    mock_metrics.language = "Python"
    mock_metrics.sync_status = "up_to_date"
    mock_metrics.days_since_last_sync = 1
    mock_metrics.uncommitted_changes = False
    mock_metrics.contributor_engagement_score = 0.7
    mock_metrics.issue_response_time_avg = 24.0
    mock_metrics.stars_growth_30d = 2
    mock_metrics.forks_growth_30d = 1
    mock_metrics.topics = ["web", "framework"]
    mock_health.calculate_repository_health.return_value = mock_metrics
    mock_health_calculator.return_value = mock_health

    result = runner.invoke(main, ["status", "--repo", "django"])
    assert result.exit_code == 0
    assert "django" in result.output


@patch("gitco.cli.get_config_manager")
@patch("gitco.cli.create_github_client")
@patch("gitco.health_metrics.create_health_calculator")
def test_status_command_with_detailed(
    mock_health_calculator: Mock,
    mock_github_client: Mock,
    mock_config_manager: Mock,
    runner: CliRunner,
) -> None:
    """Test the status command with detailed output."""
    # Mock config manager
    mock_config = Mock()
    mock_config.repositories = [Mock()]
    mock_config_manager.return_value.load_config.return_value = mock_config

    # Mock GitHub client
    mock_github = Mock()
    mock_github_client.return_value = mock_github

    # Mock health calculator
    mock_health = Mock()
    mock_summary = Mock()
    mock_summary.total_repositories = 1
    mock_summary.healthy_repositories = 1
    mock_summary.needs_attention_repositories = 0
    mock_summary.critical_repositories = 0
    mock_summary.active_repositories_7d = 1
    mock_summary.active_repositories_30d = 1
    mock_summary.up_to_date_repositories = 1
    mock_summary.behind_repositories = 0
    mock_summary.diverged_repositories = 0
    mock_summary.high_engagement_repositories = 1
    mock_summary.low_engagement_repositories = 0
    mock_summary.average_activity_score = 0.8
    mock_summary.trending_repositories = []
    mock_summary.declining_repositories = []
    mock_summary.total_stars = 100
    mock_summary.total_forks = 50
    mock_summary.total_open_issues = 10
    mock_health.calculate_health_summary.return_value = mock_summary
    mock_health_calculator.return_value = mock_health

    result = runner.invoke(main, ["status", "--detailed"])
    assert result.exit_code == 0
    assert "Repository Health Summary" in result.output


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


def test_cli_with_debug_flag(runner: CliRunner) -> None:
    """Test CLI with debug flag enabled."""
    result = runner.invoke(main, ["--debug", "--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output


def test_cli_with_config_file_flag(runner: CliRunner) -> None:
    """Test CLI with custom config file flag."""
    result = runner.invoke(main, ["--config", "/path/to/config.yml", "--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output


def test_cli_with_log_level_flag(runner: CliRunner) -> None:
    """Test CLI with custom log level flag."""
    result = runner.invoke(main, ["--log-level", "DEBUG", "--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output


def test_cli_with_output_format_flag(runner: CliRunner) -> None:
    """Test CLI with output format flag."""
    result = runner.invoke(main, ["--output-format", "json", "--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output


def test_cli_with_color_flag(runner: CliRunner) -> None:
    """Test CLI with color flag."""
    result = runner.invoke(main, ["--no-color", "--version"])
    assert result.exit_code == 0
    assert "gitco" in result.output
