# Usage Guide

This guide covers how to use GitCo effectively for managing your OSS forks and discovering contribution opportunities.

## Basic Commands

### Initialize Configuration

Start by creating a configuration file:

```bash
gitco init
```

This creates a `gitco-config.yml` file in your current directory.

**Note:** The CLI framework, configuration management, logging system, and CI pipeline are implemented. Full functionality will be added in subsequent commits.

### Sync Repositories

Synchronize your repositories with upstream changes:

```bash
# Sync all repositories
gitco sync

# Sync specific repository
gitco sync --repo django

# Sync with detailed analysis
gitco sync --analyze

# Sync with export report
gitco sync --export report.json
```

**Error Recovery Features:**

GitCo includes robust error recovery mechanisms for network operations:

- **Automatic Retry**: Network operations are automatically retried up to 3 times for recoverable errors
- **Recoverable Errors**: Detects and retries on timeouts, rate limits, connection issues, and server errors
- **Progress Tracking**: Shows retry attempts in progress bars and final summaries
- **Enhanced Reporting**: Displays retry information in success/failure messages

Example output with retry information:
```
✅ django: Sync completed (retry: 2)
❌ fastapi: Failed to fetch upstream (retry: 3)
```

**Recoverable Error Types:**
- Network timeouts and connection failures
- Rate limiting and "too many requests" errors
- Server errors (5xx status codes)
- Temporary network issues

### Analyze Changes

Get AI-powered analysis of upstream changes:

```bash
# Analyze specific repository
gitco analyze --repo fastapi

# Analyze with custom prompt
gitco analyze --repo django --prompt "Focus on security changes"

# Analyze with specific LLM provider
gitco analyze --repo django --provider anthropic

# Analyze multiple repositories
gitco analyze --repos django,fastapi,requests
```

### Discover Opportunities

Find contribution opportunities across your repositories:

```bash
# Find all opportunities
gitco discover

# Find by skill
gitco discover --skill python

# Find by label
gitco discover --label "good first issue"

# Find by skill and label
gitco discover --skill python --label "help wanted"
```

### Check Status

View the status of your repositories:

```bash
# Show all repository statuses
gitco status

# Show specific repository
gitco status --repo django

# Show detailed status
gitco status --detailed

### Validate Repositories

Validate Git repositories and check their status:

```bash
# Validate current directory
gitco validate-repo

# Validate specific path
gitco validate-repo --path ~/code/django

# Find all repositories recursively
gitco validate-repo --recursive

# Get detailed repository information
gitco validate-repo --detailed

# Combine recursive search with detailed info
gitco validate-repo --recursive --detailed
```

### Safe Stashing and Change Management

GitCo provides comprehensive stashing functionality to safely handle local changes during operations. This ensures your work is never lost during sync operations.

#### Automatic Stashing

GitCo automatically detects and handles uncommitted changes:

```bash
# GitCo automatically stashes changes before sync operations
gitco sync --repo django

# Check if a repository has uncommitted changes
gitco validate-repo --path ~/code/django
```

#### How Automatic Stashing Works

1. **Detection**: Before any sync operation, GitCo checks for uncommitted changes
2. **Stashing**: If changes exist, they are automatically stashed with a descriptive message
3. **Operation**: The sync operation proceeds with a clean working directory
4. **Restoration**: After successful completion, stashed changes are automatically restored
5. **Recovery**: If the operation fails, GitCo attempts to restore the stash

#### Stash Management

While GitCo handles stashing automatically, you can manage stashes manually if needed:

```bash
# The system provides stash management through the GitRepository class
# Stashes are created with descriptive messages like "GitCo: Auto-stash before sync"
# Stash references are tracked and restored automatically
```

#### Key Features

- **Automatic Detection**: Detects uncommitted changes before any operation
- **Safe Stashing**: Creates stashes with descriptive messages for easy identification
- **Automatic Restoration**: Restores stashed changes after successful operations
- **Error Recovery**: Attempts to restore stashes even if operations fail
- **Stash Management**: Provides tools to list, apply, and drop stashes when needed

#### Best Practices

1. **Trust the automation**: GitCo's stashing is designed to be safe and reliable
2. **Check before operations**: Use `gitco validate-repo` to see repository status
3. **Review stashes**: If needed, use standard git commands to review stashes
4. **Backup important work**: Always commit important changes before major operations

## Advanced Usage

### Batch Operations

Process multiple repositories efficiently:

```bash
# Sync all repositories in batch
gitco sync --batch

# Analyze all repositories
gitco analyze --batch

# Discover across all repositories
gitco discover --batch
```

### Export and Reporting

Export data for external analysis:

```bash
# Export sync report
gitco sync --export sync-report.json

# Export discovery results
gitco discover --export opportunities.csv

# Export status report
gitco status --export status-report.json
```

### Automation

Use GitCo in automated workflows:

```bash
# Quiet mode for scripts
gitco sync --quiet

# Log to file
gitco sync --log sync.log

# Cron-friendly output
gitco sync --cron
```

## Command Reference

### `gitco init`

Initialize a new GitCo configuration.

**Options:**
- `--force`: Overwrite existing configuration
- `--template`: Use custom template

**Examples:**
```bash
gitco init
gitco init --force
```

### `gitco sync`
