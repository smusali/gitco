# GitCo CLI Reference

This document provides a comprehensive reference for all GitCo CLI commands, options, and usage patterns.

## Table of Contents

1. [Overview](#overview)
2. [Global Options](#global-options)
3. [Core Commands](#core-commands)
4. [Configuration Commands](#configuration-commands)
5. [Repository Management Commands](#repository-management-commands)
6. [Analysis Commands](#analysis-commands)
7. [Discovery Commands](#discovery-commands)
8. [Status and Health Commands](#status-and-health-commands)
9. [Activity Commands](#activity-commands)
10. [Contribution Tracking Commands](#contribution-tracking-commands)
11. [GitHub Integration Commands](#github-integration-commands)
12. [Upstream Management Commands](#upstream-management-commands)
13. [Backup and Recovery Commands](#backup-and-recovery-commands)
14. [Cost Management Commands](#cost-management-commands)
15. [Utility Commands](#utility-commands)
16. [Shell Completion](#shell-completion)
17. [Examples](#examples)

---

## Overview

GitCo is a comprehensive CLI tool for intelligent OSS fork management and contribution discovery. It provides automated synchronization, AI-powered analysis, and intelligent contribution discovery across multiple repositories.

### Basic Usage

```bash
# Get help
gitco --help

# Check version
gitco --version

# Initialize configuration
gitco init

# Sync repositories
gitco sync

# Analyze changes
gitco analyze --repo <repository>

# Discover opportunities
gitco discover
```

---

## Global Options

All GitCo commands support these global options:

### Output Control

```bash
--verbose, -v          Enable verbose output
--quiet, -q            Suppress output (quiet mode)
--debug                Enable debug mode
--no-color             Disable colored output
```

### Logging Options

```bash
--log-file <file>      Log to file
--detailed-log         Use detailed log format with function names and line numbers
--max-log-size <MB>    Maximum log file size in MB before rotation (default: 10)
--log-backups <count>  Number of backup log files to keep (default: 5)
--log-level <level>    Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### Configuration Options

```bash
--config, -c <path>    Path to configuration file (default: ~/.gitco/config.yml)
--output-format <fmt>  Output format for commands (text, json, csv)
```

### Examples

```bash
# Verbose sync with logging
gitco --verbose --log-file sync.log sync

# Quiet mode for automation
gitco --quiet sync --batch

# Debug mode with detailed logging
gitco --debug --detailed-log analyze --repo django

# Custom configuration file
gitco --config ~/.gitco/custom-config.yml sync
```

---

## Core Commands

### `init` - Initialize Configuration

Initialize GitCo configuration and setup.

```bash
gitco init [OPTIONS]
```

**Options:**
- `--force, -f` - Overwrite existing configuration
- `--template, -t <template>` - Use custom template for configuration
- `--interactive, -i` - Use interactive guided setup
- `--non-interactive, -n` - Use non-interactive setup with defaults

**Examples:**
```bash
# Interactive setup
gitco init --interactive

# Non-interactive with defaults
gitco init --non-interactive

# Force overwrite existing config
gitco init --force
```

### `sync` - Synchronize Repositories

Synchronize repositories with upstream changes.

```bash
gitco sync [OPTIONS]
```

**Options:**
- `--repo, -r <repo>` - Sync specific repository
- `--analyze, -a` - Include AI analysis of changes
- `--export, -e <file>` - Export report to file
- `--batch, -b` - Process all repositories in batch
- `--max-workers, -w <workers>` - Maximum concurrent workers for batch processing (default: 4)

**Examples:**
```bash
# Sync all repositories
gitco sync

# Sync specific repository with analysis
gitco sync --repo django --analyze

# Batch sync with export
gitco sync --batch --export sync-report.json
```

### `analyze` - Analyze Repository Changes

Analyze changes in repositories using AI.

```bash
gitco analyze [OPTIONS]
```

**Options:**
- `--repo, -r <repo>` - Repository to analyze (required)
- `--prompt, -p <prompt>` - Custom analysis prompt
- `--provider <provider>` - LLM provider to use (openai, anthropic)
- `--repos <repos>` - Analyze multiple repositories (comma-separated)
- `--export, -e <file>` - Export analysis to file

**Examples:**
```bash
# Analyze specific repository
gitco analyze --repo django

# Analyze with custom prompt
gitco analyze --repo django --prompt "Focus on security implications"

# Analyze multiple repositories
gitco analyze --repos "django,flask,fastapi"
```

### `discover` - Discover Contribution Opportunities

Discover contribution opportunities based on skills and preferences.

```bash
gitco discover [OPTIONS]
```

**Options:**
- `--skill, -s <skill>` - Filter by skill
- `--label, -l <label>` - Filter by label
- `--export, -e <file>` - Export results to file
- `--limit, -n <limit>` - Limit number of results
- `--min-confidence, -c <score>` - Minimum confidence score (0.0-1.0, default: 0.1)
- `--personalized, -p` - Include personalized recommendations based on contribution history
- `--show-history, -h` - Show contribution history analysis

**Examples:**
```bash
# Discover Python opportunities
gitco discover --skill python

# Discover with minimum confidence
gitco discover --skill python --min-confidence 0.5

# Personalized recommendations
gitco discover --personalized --show-history
```

### `status` - Repository Status and Health

Show repository status and health metrics.

```bash
gitco status [OPTIONS]
```

**Options:**
- `--repo, -r <repo>` - Show specific repository
- `--detailed, -d` - Show detailed information
- `--export, -e <file>` - Export status to file
- `--overview, -o` - Show repository overview dashboard
- `--activity, -a` - Show repository activity dashboard
- `--filter, -f <status>` - Filter repositories by status (healthy, needs_attention, critical)
- `--sort, -s <metric>` - Sort repositories by metric (health, activity, stars, forks)

**Examples:**
```bash
# Show all repository status
gitco status

# Show detailed status for specific repository
gitco status --repo django --detailed

# Show overview dashboard
gitco status --overview
```

### `activity` - Repository Activity Dashboard

Show repository activity metrics and trends.

```bash
gitco activity [OPTIONS]
```

**Options:**
- `--repo, -r <repo>` - Show activity for specific repository
- `--detailed, -d` - Show detailed activity information
- `--export, -e <file>` - Export activity data to file
- `--filter, -f <level>` - Filter repositories by activity level (high, moderate, low)
- `--sort, -s <metric>` - Sort repositories by metric (activity, engagement, commits, contributors)

**Examples:**
```bash
# Show activity for all repositories
gitco activity

# Show detailed activity for specific repository
gitco activity --repo django --detailed

# Filter by activity level
gitco activity --filter high
```

---

## Configuration Commands

### `config` - Configuration Management

Manage GitCo configuration.

```bash
gitco config <subcommand> [OPTIONS]
```

#### `config validate` - Validate Configuration

Validate the current configuration.

```bash
gitco config validate
```

#### `config status` - Configuration Status

Show configuration status and validation results.

```bash
gitco config status
```

#### `config validate-detailed` - Detailed Validation

Show detailed validation report.

```bash
gitco config validate-detailed [OPTIONS]
```

**Options:**
- `--detailed, -d` - Show detailed validation report
- `--export, -e <file>` - Export validation report to file

---

## Repository Management Commands

### `validate-repo` - Validate Repository

Validate repository structure and configuration.

```bash
gitco validate-repo [OPTIONS]
```

**Options:**
- `--path, -p <path>` - Path to validate (default: current directory)
- `--recursive, -r` - Recursively find repositories
- `--detailed, -d` - Show detailed repository information

**Examples:**
```bash
# Validate current directory
gitco validate-repo

# Validate specific path recursively
gitco validate-repo --path ~/code --recursive
```

---

## GitHub Integration Commands

### `github` - GitHub API Integration

GitHub API integration commands.

```bash
gitco github <subcommand> [OPTIONS]
```

#### `github rate-limit-status` - Rate Limit Status

Show GitHub API rate limit status.

```bash
gitco github rate-limit-status [OPTIONS]
```

**Options:**
- `--provider, -p <provider>` - Show status for specific provider (github, openai, anthropic)
- `--detailed, -d` - Show detailed rate limiting information

#### `github test-connection` - Test Connection

Test GitHub API connection.

```bash
gitco github test-connection
```

#### `github get-repo` - Get Repository Info

Get repository information from GitHub.

```bash
gitco github get-repo --repo <owner/repo>
```

#### `github get-issues` - Get Repository Issues

Get issues from a repository.

```bash
gitco github get-issues [OPTIONS] --repo <owner/repo>
```

**Options:**
- `--state, -s <state>` - Issue state (open, closed, all, default: open)
- `--labels, -l <labels>` - Filter by labels (comma-separated)
- `--exclude-labels, -e <labels>` - Exclude labels (comma-separated)
- `--assignee, -a <assignee>` - Filter by assignee
- `--milestone, -m <milestone>` - Filter by milestone
- `--limit, -n <limit>` - Maximum number of issues
- `--created-after <date>` - Filter issues created after date (YYYY-MM-DD)
- `--updated-after <date>` - Filter issues updated after date (YYYY-MM-DD)
- `--detailed, -d` - Show detailed issue information

#### `github get-issues-multi` - Get Issues from Multiple Repositories

Get issues from multiple repositories.

```bash
gitco github get-issues-multi [OPTIONS] --repos <repos>
```

**Options:**
- `--state, -s <state>` - Issue state (open, closed, all, default: open)
- `--labels, -l <labels>` - Filter by labels (comma-separated)
- `--exclude-labels, -e <labels>` - Exclude labels (comma-separated)
- `--assignee, -a <assignee>` - Filter by assignee
- `--milestone, -m <milestone>` - Filter by milestone
- `--limit-per-repo <limit>` - Maximum issues per repository
- `--total-limit <limit>` - Maximum total issues across all repositories
- `--created-after <date>` - Filter issues created after date (YYYY-MM-DD)
- `--updated-after <date>` - Filter issues updated after date (YYYY-MM-DD)
- `--detailed, -d` - Show detailed issue information
- `--export <file>` - Export results to JSON file

---

## Upstream Management Commands

### `upstream` - Upstream Repository Management

Manage upstream repository connections.

```bash
gitco upstream <subcommand> [OPTIONS]
```

#### `upstream add` - Add Upstream Repository

Add upstream repository for a local repository.

```bash
gitco upstream add --repo <repo> --url <url>
```

#### `upstream remove` - Remove Upstream Repository

Remove upstream repository configuration.

```bash
gitco upstream remove --repo <repo>
```

#### `upstream update` - Update Upstream URL

Update upstream repository URL.

```bash
gitco upstream update --repo <repo> --url <url>
```

#### `upstream validate` - Validate Upstream Configuration

Validate upstream repository configuration.

```bash
gitco upstream validate --repo <repo>
```

#### `upstream fetch` - Fetch from Upstream

Fetch latest changes from upstream.

```bash
gitco upstream fetch --repo <repo>
```

#### `upstream merge` - Merge Upstream Changes

Merge upstream changes into local repository.

```bash
gitco upstream merge [OPTIONS] --repo <repo>
```

**Options:**
- `--branch, -b <branch>` - Branch to merge (default: default branch)
- `--strategy, -s <strategy>` - Conflict resolution strategy (ours, theirs, manual, default: ours)
- `--abort, -a` - Abort current merge
- `--resolve` - Resolve conflicts automatically

---

## Contribution Tracking Commands

### `contributions` - Contribution History Management

Manage contribution history and tracking.

```bash
gitco contributions <subcommand> [OPTIONS]
```

#### `contributions sync-history` - Sync Contribution History

Sync contribution history from GitHub.

```bash
gitco contributions sync-history --username <username> [OPTIONS]
```

**Options:**
- `--force, -f` - Force sync even if recent
- `--quiet, -q` - Suppress output

#### `contributions stats` - Contribution Statistics

Show contribution statistics.

```bash
gitco contributions stats [OPTIONS]
```

**Options:**
- `--days, -d <days>` - Show stats for last N days
- `--export, -e <file>` - Export stats to file (.json or .csv)
- `--quiet, -q` - Suppress output

#### `contributions recommendations` - Get Recommendations

Get personalized contribution recommendations.

```bash
gitco contributions recommendations [OPTIONS]
```

**Options:**
- `--skill, -s <skill>` - Filter by skill
- `--repository, -r <repository>` - Filter by repository
- `--limit, -n <limit>` - Number of recommendations (default: 10)

#### `contributions export` - Export Contributions

Export contribution data.

```bash
gitco contributions export [OPTIONS] --output <file>
```

**Options:**
- `--days, -d <days>` - Export contributions from last N days
- `--include-stats, -s` - Include summary statistics

#### `contributions trending` - Trending Analysis

Show trending contribution analysis.

```bash
gitco contributions trending [OPTIONS]
```

**Options:**
- `--days, -d <days>` - Analysis period in days (default: 30)
- `--export, -e <file>` - Export trending analysis to file (.json or .csv)

---

## Backup and Recovery Commands

### `backup` - Backup and Recovery Management

Manage backup and recovery operations.

```bash
gitco backup <subcommand> [OPTIONS]
```

#### `backup create` - Create Backup

Create a new backup.

```bash
gitco backup create [OPTIONS]
```

**Options:**
- `--repos, -r <repos>` - Comma-separated list of repository paths
- `--config, -c <config>` - Path to configuration file
- `--type, -t <type>` - Backup type (full, incremental, config-only, default: full)
- `--description, -d <description>` - Description of the backup
- `--no-git-history` - Exclude git history to reduce size
- `--compression <level>` - Compression level (0-9, default: 6)
- `--quiet, -q` - Suppress output

#### `backup list` - List Backups

List available backups.

```bash
gitco backup list [OPTIONS]
```

**Options:**
- `--detailed, -d` - Show detailed information

#### `backup restore` - Restore Backup

Restore from a backup.

```bash
gitco backup restore [OPTIONS] --backup-id <id>
```

**Options:**
- `--target-dir, -t <dir>` - Target directory for restoration
- `--no-config` - Skip configuration restoration
- `--overwrite, -f` - Overwrite existing files
- `--quiet, -q` - Suppress output

#### `backup validate` - Validate Backup

Validate a backup.

```bash
gitco backup validate --backup-id <id>
```

#### `backup delete` - Delete Backup

Delete a backup.

```bash
gitco backup delete [OPTIONS] --backup-id <id>
```

**Options:**
- `--force, -f` - Force deletion without confirmation

#### `backup cleanup` - Cleanup Old Backups

Cleanup old backups.

```bash
gitco backup cleanup [OPTIONS]
```

**Options:**
- `--keep, -k <count>` - Number of backups to keep (default: 5)

---

## Cost Management Commands

### `cost` - Cost Management

Manage LLM API costs and optimization.

```bash
gitco cost <subcommand> [OPTIONS]
```

#### `cost summary` - Cost Summary

Show cost summary and statistics.

```bash
gitco cost summary [OPTIONS]
```

**Options:**
- `--detailed, -d` - Show detailed cost breakdown
- `--export, -e <file>` - Export cost data to file (.json or .csv)
- `--days <days>` - Show costs for last N days
- `--months <months>` - Show costs for last N months

#### `cost configure` - Configure Cost Settings

Configure cost tracking and optimization settings.

```bash
gitco cost configure [OPTIONS]
```

**Options:**
- `--daily-limit <limit>` - Set daily cost limit in USD
- `--monthly-limit <limit>` - Set monthly cost limit in USD
- `--per-request-limit <limit>` - Set per-request cost limit in USD
- `--max-tokens <tokens>` - Set maximum tokens per request
- `--enable-tracking` - Enable cost tracking
- `--disable-tracking` - Disable cost tracking
- `--enable-optimization` - Enable token optimization
- `--disable-optimization` - Disable token optimization

#### `cost reset` - Reset Cost History

Reset cost tracking history.

```bash
gitco cost reset [OPTIONS]
```

**Options:**
- `--force, -f` - Force reset without confirmation

#### `cost breakdown` - Cost Breakdown

Show detailed cost breakdown by model and provider.

```bash
gitco cost breakdown [OPTIONS]
```

**Options:**
- `--model, -m <model>` - Show costs for specific model
- `--provider, -p <provider>` - Show costs for specific provider
- `--days, -d <days>` - Show costs for last N days (default: 30)

---

## Utility Commands

### `logs` - View Logs

View application logs and performance data.

```bash
gitco logs [OPTIONS]
```

**Options:**
- `--export, -e <file>` - Export performance summary to file (.json or .csv)
- `--format, -f <format>` - Export format (json, csv, default: json)

### `performance` - Performance Metrics

Show performance metrics and statistics.

```bash
gitco performance [OPTIONS]
```

**Options:**
- `--detailed, -d` - Show detailed performance metrics
- `--export, -e <file>` - Export performance data to file (.json or .csv)
- `--format, -f <format>` - Export format (json, csv, default: json)

### `help` - Show Help

Show detailed help information.

```bash
gitco help
```

### `completion` - Shell Completion

Generate shell completion scripts.

```bash
gitco completion --shell <shell> [OPTIONS]
```

**Options:**
- `--shell, -s <shell>` - Shell type (bash, zsh, required)
- `--output, -o <file>` - Output file path (default: auto-detect)
- `--install, -i` - Install completion script

**Examples:**
```bash
# Generate bash completion
gitco completion --shell bash

# Generate zsh completion and install
gitco completion --shell zsh --install
```

---

## Examples

### Basic Workflow

```bash
# Initialize configuration
gitco init --interactive

# Sync repositories
gitco sync

# Analyze changes
gitco analyze --repo django

# Discover opportunities
gitco discover --skill python

# Check status
gitco status
```

### Advanced Workflow

```bash
# Sync with analysis and export
gitco sync --analyze --export sync-report.json

# Discover personalized opportunities
gitco discover --personalized --show-history

# Check detailed health status
gitco status --detailed --overview

# View activity dashboard
gitco activity --detailed

# Create backup
gitco backup create --type full --description "Pre-update backup"

# Check cost usage
gitco cost summary --detailed
```

### Automation Workflow

```bash
# Quiet sync for CI/CD
gitco --quiet sync --batch

# Export status for monitoring
gitco status --export status.json --output-format json

# Check rate limits
gitco github rate-limit-status --detailed

# Validate configuration
gitco config validate
```

### Contribution Tracking

```bash
# Sync contribution history
gitco contributions sync-history --username yourusername

# View contribution stats
gitco contributions stats --days 30

# Get personalized recommendations
gitco contributions recommendations --skill python

# Export contribution data
gitco contributions export --output contributions.json --include-stats
```

### Backup and Recovery

```bash
# Create full backup
gitco backup create --type full --description "Monthly backup"

# List backups
gitco backup list --detailed

# Restore from backup
gitco backup restore --backup-id backup-2024-01-15

# Cleanup old backups
gitco backup cleanup --keep 5
```

### Cost Management

```bash
# View cost summary
gitco cost summary --detailed

# Configure cost limits
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0

# View cost breakdown
gitco cost breakdown --provider openai --days 30

# Reset cost history
gitco cost reset --force
```
