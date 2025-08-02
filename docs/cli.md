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

### `gitco init`

Initialize GitCo configuration.

```bash
gitco init [OPTIONS]

Options:
  --interactive, -i        Interactive setup mode
  --non-interactive, -n    Non-interactive setup with defaults
  --force, -f              Force reinitialization
  --config-path <path>     Custom configuration path
```

**Examples:**
```bash
# Interactive setup
gitco init --interactive

# Non-interactive setup
gitco init --non-interactive

# Force reinitialization
gitco init --force
```

### `gitco sync`

Synchronize repositories with upstream.

```bash
gitco sync [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Sync specific repository
  --batch, -b              Batch sync all repositories
  --analyze, -a            Run analysis after sync
  --stash                  Stash local changes before sync
  --force, -f              Force sync even if conflicts
  --max-repos <count>      Maximum repositories per batch
  --export <file>          Export sync report
```

**Examples:**
```bash
# Sync all repositories
gitco sync

# Sync specific repository
gitco sync --repo django

# Sync with analysis
gitco sync --analyze

# Batch sync with export
gitco sync --batch --export sync-report.json
```

### `gitco analyze`

Analyze repository changes using AI.

```bash
gitco analyze [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Analyze specific repository
  --detailed, -d           Detailed analysis
  --prompt <text>          Custom analysis prompt
  --model <model>          LLM model to use
  --no-llm                 Skip LLM analysis
  --max-commits <count>    Maximum commits to analyze
  --export <file>          Export analysis results
```

**Examples:**
```bash
# Analyze repository
gitco analyze --repo django

# Detailed analysis with custom prompt
gitco analyze --repo django --detailed --prompt "Focus on security implications"

# Analyze without LLM
gitco analyze --repo django --no-llm
```

### `gitco discover`

Discover contribution opportunities.

```bash
gitco discover [OPTIONS]

Options:
  --skill <skill>          Filter by skill
  --label <label>          Filter by GitHub label
  --repos <repos>          Filter by repositories
  --min-confidence <float> Minimum confidence threshold (0.0-1.0)
  --limit <count>          Maximum results to return
  --personalized           Use personalized recommendations
  --export <file>          Export discovery results
```

**Examples:**
```bash
# Discover all opportunities
gitco discover

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Personalized recommendations
gitco discover --personalized --limit 10
```

---

## Configuration Commands

### `gitco config`

Manage configuration.

```bash
gitco config [COMMAND] [OPTIONS]

Commands:
  validate                 Validate configuration
  show                     Show current configuration
  edit                     Edit configuration file
  export                   Export configuration
  import                   Import configuration
```

**Examples:**
```bash
# Validate configuration
gitco config validate

# Show configuration
gitco config show

# Edit configuration
gitco config edit
```

### `gitco config validate`

Validate configuration file.

```bash
gitco config validate [OPTIONS]

Options:
  --detailed, -d           Detailed validation report
  --strict                 Strict validation mode
  --export <file>          Export validation report
```

**Examples:**
```bash
# Basic validation
gitco config validate

# Detailed validation
gitco config validate --detailed

# Export validation report
gitco config validate --export validation-report.json
```

---

## Repository Management Commands

### `gitco validate-repo`

Validate repository structure and configuration.

```bash
gitco validate-repo [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Validate specific repository
  --all, -a                Validate all repositories
  --detailed, -d           Detailed validation report
  --path <path>            Validate repository at path
  --recursive              Recursive validation
  --export <file>          Export validation report
```

**Examples:**
```bash
# Validate specific repository
gitco validate-repo --repo django

# Validate all repositories
gitco validate-repo --all

# Validate at specific path
gitco validate-repo --path ~/code/django
```

---

## Analysis Commands

### `gitco analyze`

Analyze repository changes using AI.

```bash
gitco analyze [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Analyze specific repository
  --repos <names>          Analyze multiple repositories
  --detailed, -d           Detailed analysis
  --prompt <text>          Custom analysis prompt
  --model <model>          LLM model to use
  --provider <provider>    LLM provider (openai, anthropic)
  --no-llm                 Skip LLM analysis
  --max-commits <count>    Maximum commits to analyze
  --export <file>          Export analysis results
```

**Examples:**
```bash
# Analyze repository
gitco analyze --repo django

# Analyze with custom prompt
gitco analyze --repo django --prompt "Focus on security implications"

# Analyze multiple repositories
gitco analyze --repos "django,fastapi"

# Use specific model
gitco analyze --repo django --model gpt-3.5-turbo
```

---

## Discovery Commands

### `gitco discover`

Discover contribution opportunities.

```bash
gitco discover [OPTIONS]

Options:
  --skill <skill>          Filter by skill
  --label <label>          Filter by GitHub label
  --repos <repos>          Filter by repositories
  --min-confidence <float> Minimum confidence threshold (0.0-1.0)
  --limit <count>          Maximum results to return
  --personalized           Use personalized recommendations
  --show-history           Show contribution history
  --export <file>          Export discovery results
```

**Examples:**
```bash
# Discover all opportunities
gitco discover

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Personalized recommendations
gitco discover --personalized --limit 10

# Export results
gitco discover --export opportunities.json
```

---

## Status and Health Commands

### `gitco status`

Check repository health and status.

```bash
gitco status [OPTIONS]

Options:
  --detailed, -d           Detailed status report
  --overview, -o           Overview status
  --filter <status>        Filter by status (healthy, needs_attention, critical)
  --sort <field>           Sort by field (health, activity, stars)
  --export <file>          Export status report
```

**Examples:**
```bash
# Check all repositories
gitco status

# Detailed status
gitco status --detailed

# Filter by health
gitco status --filter healthy

# Export status
gitco status --export status.json
```

---

## Activity Commands

### `gitco activity`

View repository activity dashboard.

```bash
gitco activity [OPTIONS]

Options:
  --repo, -r <name>        Activity for specific repository
  --detailed, -d           Detailed activity report
  --filter <level>         Filter by activity level (high, moderate, low)
  --sort <field>           Sort by field (activity, engagement, commits)
  --export <file>          Export activity report
```

**Examples:**
```bash
# View activity dashboard
gitco activity

# Detailed activity
gitco activity --detailed

# Activity for specific repository
gitco activity --repo django

# Export activity
gitco activity --export activity.json
```

---

## Contribution Tracking Commands

### `gitco contributions`

Manage contribution tracking.

```bash
gitco contributions [COMMAND] [OPTIONS]

Commands:
  sync-history             Sync contribution history
  stats                    View contribution statistics
  recommendations          Get personalized recommendations
  trending                 View trending analysis
  export                   Export contribution data
```

### `gitco contributions sync-history`

Sync contribution history from GitHub.

```bash
gitco contributions sync-history [OPTIONS]

Options:
  --username <username>    GitHub username
  --force                  Force sync even if recent
  --days <count>           Sync contributions from last N days
```

**Examples:**
```bash
# Sync contribution history
gitco contributions sync-history --username yourusername

# Force sync
gitco contributions sync-history --username yourusername --force
```

### `gitco contributions stats`

View contribution statistics.

```bash
gitco contributions stats [OPTIONS]

Options:
  --days <count>           Statistics for last N days
  --detailed, -d           Detailed statistics
  --export <file>          Export statistics
```

**Examples:**
```bash
# View statistics
gitco contributions stats

# Statistics for last 30 days
gitco contributions stats --days 30

# Export statistics
gitco contributions stats --export stats.json
```

---

## GitHub Integration Commands

### `gitco github`

GitHub integration commands.

```bash
gitco github [COMMAND] [OPTIONS]

Commands:
  test-connection          Test GitHub connection
  rate-limit-status        Check rate limit status
  get-repo                 Get repository information
  get-issues               Get repository issues
  get-issues-multi         Get issues from multiple repositories
```

### `gitco github test-connection`

Test GitHub API connection.

```bash
gitco github test-connection [OPTIONS]

Options:
  --detailed, -d           Detailed connection test
```

**Examples:**
```bash
# Test connection
gitco github test-connection

# Detailed test
gitco github test-connection --detailed
```

### `gitco github rate-limit-status`

Check GitHub API rate limits.

```bash
gitco github rate-limit-status [OPTIONS]

Options:
  --detailed, -d           Detailed rate limit information
  --wait                   Wait for rate limit reset
```

**Examples:**
```bash
# Check rate limits
gitco github rate-limit-status

# Detailed information
gitco github rate-limit-status --detailed
```

---

## Upstream Management Commands

### `gitco upstream`

Manage upstream repository connections.

```bash
gitco upstream [COMMAND] [OPTIONS]

Commands:
  add                      Add upstream remote
  remove                   Remove upstream remote
  update                   Update upstream URL
  validate                 Validate upstream configuration
  fetch                    Fetch from upstream
  merge                    Merge upstream changes
```

### `gitco upstream add`

Add upstream remote to repository.

```bash
gitco upstream add [OPTIONS]

Options:
  --repo, -r <name>        Repository name
  --url <url>              Upstream repository URL
  --name <name>            Remote name (default: upstream)
```

**Examples:**
```bash
# Add upstream remote
gitco upstream add --repo django --url https://github.com/django/django.git
```

### `gitco upstream validate`

Validate upstream configuration.

```bash
gitco upstream validate [OPTIONS]

Options:
  --repo, -r <name>        Validate specific repository
  --detailed, -d           Detailed validation
```

**Examples:**
```bash
# Validate upstream
gitco upstream validate --repo django

# Detailed validation
gitco upstream validate --repo django --detailed
```

---

## Backup and Recovery Commands

### `gitco backup`

Manage backups and recovery.

```bash
gitco backup [COMMAND] [OPTIONS]

Commands:
  create                   Create backup
  list                     List backups
  restore                  Restore from backup
  validate                 Validate backup
  delete                   Delete backup
  cleanup                  Clean up old backups
```

### `gitco backup create`

Create a new backup.

```bash
gitco backup create [OPTIONS]

Options:
  --type <type>            Backup type (full, incremental, config-only)
  --description <text>     Backup description
  --repos <names>          Backup specific repositories
  --no-git-history         Skip git history
  --compression <level>    Compression level (0-9)
```

**Examples:**
```bash
# Create full backup
gitco backup create --type full --description "Weekly backup"

# Create incremental backup
gitco backup create --type incremental --description "Daily backup"

# Backup specific repositories
gitco backup create --repos "django,fastapi" --description "Python repos"
```

### `gitco backup list`

List available backups.

```bash
gitco backup list [OPTIONS]

Options:
  --detailed, -d           Detailed backup information
  --sort <field>           Sort by field (date, size, type)
```

**Examples:**
```bash
# List backups
gitco backup list

# Detailed list
gitco backup list --detailed
```

### `gitco backup restore`

Restore from backup.

```bash
gitco backup restore [OPTIONS]

Options:
  --backup-id <id>         Backup ID to restore
  --target-dir <path>      Target directory for restoration
  --overwrite              Overwrite existing files
  --no-config              Skip configuration restoration
```

**Examples:**
```bash
# Restore from backup
gitco backup restore --backup-id backup-2024-01-15

# Restore to specific directory
gitco backup restore --backup-id backup-2024-01-15 --target-dir ~/restored
```

---

## Cost Management Commands

### `gitco cost`

Manage cost tracking and optimization.

```bash
gitco cost [COMMAND] [OPTIONS]

Commands:
  summary                  View cost summary
  breakdown                View cost breakdown
  configure                Configure cost settings
  reset                    Reset cost tracking
```

### `gitco cost summary`

View cost summary.

```bash
gitco cost summary [OPTIONS]

Options:
  --detailed, -d           Detailed cost breakdown
  --days <count>           Cost for last N days
  --months <count>         Cost for last N months
  --export <file>          Export cost data
```

**Examples:**
```bash
# View cost summary
gitco cost summary

# Detailed summary
gitco cost summary --detailed

# Export cost data
gitco cost summary --export costs.json
```

### `gitco cost configure`

Configure cost settings.

```bash
gitco cost configure [OPTIONS]

Options:
  --daily-limit <amount>   Daily cost limit
  --monthly-limit <amount> Monthly cost limit
  --per-request-limit <amount> Per-request cost limit
  --enable-tracking        Enable cost tracking
  --disable-tracking       Disable cost tracking
  --enable-optimization    Enable cost optimization
  --disable-optimization   Disable cost optimization
  --show                   Show current configuration
```

**Examples:**
```bash
# Set cost limits
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0

# Enable optimization
gitco cost configure --enable-optimization

# Show configuration
gitco cost configure --show
```

---

## Utility Commands

### `gitco help`

Get help for commands.

```bash
gitco help [COMMAND]

Examples:
  gitco help               Show general help
  gitco help sync          Show help for sync command
  gitco help analyze       Show help for analyze command
```

### `gitco version`

Show GitCo version.

```bash
gitco version

# Output example:
# GitCo version 0.1.0
```

### `gitco performance`

View performance metrics.

```bash
gitco performance [OPTIONS]

Options:
  --detailed, -d           Detailed performance metrics
  --export <file>          Export performance data
```

**Examples:**
```bash
# View performance metrics
gitco performance

# Detailed metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json
```

### `gitco logs`

View and manage logs.

```bash
gitco logs [OPTIONS]

Options:
  --export <file>          Export logs
  --lines <count>          Number of lines to show
  --follow, -f             Follow log file
```

**Examples:**
```bash
# Export logs
gitco logs --export logs.json

# Show last 100 lines
gitco logs --lines 100
```

---

## Shell Completion

### Installation

GitCo provides shell completion for bash, zsh, and fish.

**Bash:**
```bash
# Add to ~/.bashrc
eval "$(gitco --generate-completion bash)"
```

**Zsh:**
```bash
# Add to ~/.zshrc
eval "$(gitco --generate-completion zsh)"
```

**Fish:**
```bash
# Add to ~/.config/fish/config.fish
gitco --generate-completion fish | source
```

### Completion Features

- **Command Completion**: Complete command names
- **Option Completion**: Complete command options
- **Repository Completion**: Complete repository names from configuration
- **Skill Completion**: Complete skill names
- **Label Completion**: Complete GitHub label names

---

## Examples

### Daily Workflow

```bash
# Morning routine
gitco sync --batch --quiet
gitco status --overview
gitco discover --limit 3

# Weekly review
gitco sync --batch --analyze --export weekly-sync.json
gitco activity --detailed --export weekly-activity.json
gitco contributions stats --days 7 --export weekly-stats.json
```

### Repository Management

```bash
# Add new repository
gitco upstream add --repo new-project --url https://github.com/owner/new-project.git

# Validate repository
gitco validate-repo --repo new-project

# Sync with analysis
gitco sync --repo new-project --analyze
```

### Analysis and Discovery

```bash
# Analyze changes
gitco analyze --repo django --detailed --prompt "Focus on security implications"

# Discover opportunities
gitco discover --skill python --label "good first issue" --limit 10

# Personalized recommendations
gitco contributions sync-history --username yourusername
gitco discover --personalized --limit 5
```

### Automation

```bash
# Quiet mode for automation
gitco --quiet sync --batch --export sync-report.json

# Export status for monitoring
gitco status --export status.json --output-format json

# Debug mode for troubleshooting
gitco --debug analyze --repo django
```

### Backup and Recovery

```bash
# Create backup
gitco backup create --type full --description "Weekly backup"

# List backups
gitco backup list --detailed

# Restore from backup
gitco backup restore --backup-id backup-2024-01-15
```

### Cost Management

```bash
# View cost summary
gitco cost summary --detailed

# Set cost limits
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0

# Reset cost tracking
gitco cost reset --force
```

This comprehensive CLI reference covers all GitCo commands and options. For more detailed information about specific features, see the [Usage Guide](usage.md) and [Configuration Guide](configuration.md).
