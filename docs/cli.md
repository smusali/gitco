# GitCo CLI Reference

This document provides a comprehensive reference for all GitCo CLI commands, options, and usage patterns. The CLI has been organized into modular command groups for better maintainability and usability.

## Table of Contents

1. [Overview](#overview)
2. [Global Options](#global-options)
3. [Command Groups](#command-groups)
4. [Shell Completion](#shell-completion)
5. [Examples](#examples)

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

## Command Groups

GitCo commands are organized into logical groups for better organization and maintainability:

### [Core Commands](cli/core.md)
Main functionality commands: init, sync, analyze, discover, status, activity, logs, performance, version, help, completion, validate-repo.

**Most commonly used commands:**
- `gitco init` - Initialize configuration
- `gitco sync` - Synchronize repositories
- `gitco analyze` - Analyze changes with AI
- `gitco discover` - Find contribution opportunities
- `gitco status` - Check repository health
- `gitco activity` - View activity dashboard

### [Configuration Commands](cli/config.md)
Configuration management: validate, show, edit, export, import.

**Examples:**
- `gitco config validate` - Validate configuration
- `gitco config show` - Show current configuration
- `gitco config edit` - Edit configuration file

### [Upstream Management Commands](cli/upstream.md)
Upstream repository management: add, remove, update, validate, fetch, merge.

**Examples:**
- `gitco upstream add` - Add upstream remote
- `gitco upstream fetch` - Fetch from upstream
- `gitco upstream merge` - Merge upstream changes

### [GitHub Integration Commands](cli/github.md)
GitHub API operations: connection-status, rate-limit-status, get-repo, get-issues, get-issues-multi.

**Examples:**
- `gitco github connection-status` - Test GitHub connection
- `gitco github get-issues` - Get repository issues
- `gitco github rate-limit-status` - Check rate limits

### [Contribution Tracking Commands](cli/contributions.md)
Contribution history and tracking: sync-history, stats, recommendations, export, trending.

**Examples:**
- `gitco contributions sync-history` - Sync contribution history
- `gitco contributions stats` - View statistics
- `gitco contributions recommendations` - Get personalized recommendations

### [Backup and Recovery Commands](cli/backup.md)
Backup management: create, list, restore, validate, delete, cleanup.

**Examples:**
- `gitco backup create` - Create backup
- `gitco backup list` - List backups
- `gitco backup restore` - Restore from backup


---

## Shell Completion

### Installation

GitCo provides shell completion for bash and zsh.

**Bash:**
```bash
# Generate and install completion script
gitco completion --shell bash --install

# Or manually add to ~/.bashrc
gitco completion --shell bash >> ~/.bashrc
```

**Zsh:**
```bash
# Generate and install completion script
gitco completion --shell zsh --install

# Or manually add to ~/.zshrc
gitco completion --shell zsh >> ~/.zshrc
```

**Manual Installation:**
```bash
# Generate completion script to file
gitco completion --shell bash --output ~/.gitco-completion.bash

# Then source it in your shell configuration
echo "source ~/.gitco-completion.bash" >> ~/.bashrc
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


---

For detailed information about specific command groups, see the individual documentation files linked above. For configuration details, see the [Configuration Guide](configuration.md) and for usage patterns, see the [Usage Guide](usage.md).
