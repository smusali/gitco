# Usage Guide

This guide covers how to use GitCo effectively for managing your OSS forks and discovering contribution opportunities.

## Basic Commands

### Initialize Configuration

Start by creating a configuration file with interactive guided setup:

```bash
# Interactive guided setup (recommended)
gitco init --interactive

# Non-interactive setup with defaults
gitco init

# Force overwrite existing configuration
gitco init --force

# Use custom template
gitco init --template custom.yml
```

This creates a `~/.gitco/config.yml` file in your home directory with guided setup options.

**Interactive Setup Features:**
- **Repository Configuration**: Add repositories with validation and skill matching
- **LLM Provider Setup**: Configure OpenAI, Anthropic integration
- **GitHub Integration**: Set up authentication with tokens or username/password
- **General Settings**: Configure default paths and batch processing options
- **Configuration Summary**: Review all settings before saving
- **Validation**: Automatic validation of repository formats and paths

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

GitCo includes comprehensive retry mechanisms for network operations:

- **Automatic Retry**: Network operations are automatically retried with configurable strategies
- **Exponential Backoff**: Smart retry delays that increase exponentially to prevent overwhelming servers
- **Jitter Support**: Random delay variations to prevent thundering herd problems
- **Recoverable Errors**: Detects and retries on timeouts, rate limits, connection issues, and server errors
- **Progress Tracking**: Shows retry attempts in progress bars and final summaries
- **Enhanced Reporting**: Displays retry information in success/failure messages

**Retry Strategies:**
- **Default**: 3 attempts with exponential backoff (1s, 2s, 4s)
- **Aggressive**: 5 attempts with faster backoff (0.5s, 1s, 2s, 4s, 8s)
- **Conservative**: 2 attempts with linear backoff (2s, 4s)

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
- Connection timeouts and DNS failures

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

# Show repository overview dashboard
gitco status --overview

# Filter repositories by health status
gitco status --overview --filter healthy
gitco status --overview --filter needs_attention
gitco status --overview --filter critical

# Sort repositories by metrics
gitco status --overview --sort health
gitco status --overview --sort activity
gitco status --overview --sort stars
gitco status --overview --sort forks
gitco status --overview --sort engagement

# Show detailed status information
gitco status --detailed

# Export status data
gitco status --export status.json
```

**Status Features:**

- **Overview Dashboard**: Comprehensive table view with health, sync, activity, and engagement metrics
- **Health Filtering**: Filter repositories by health status (healthy, needs_attention, critical)
- **Metric Sorting**: Sort by health score, activity, stars, forks, or engagement
- **Visual Indicators**: Emoji-based status indicators for quick visual assessment
- **Activity Bars**: Visual representation of recent commit activity
- **Summary Panels**: Key metrics displayed in organized panels
- **Alert System**: Automatic alerts for repositories needing attention

### Rate Limiting

GitCo includes comprehensive rate limiting for all API calls to prevent hitting API limits:

```bash
# Check rate limiting status for all providers
gitco github rate-limit-status

# Check status for specific provider
gitco github rate-limit-status --provider github
gitco github rate-limit-status --provider openai
gitco github rate-limit-status --provider anthropic

# Show detailed rate limiting information
gitco github rate-limit-status --detailed
```

**Rate Limiting Features:**

- **Automatic Rate Limiting**: Built-in rate limiting for GitHub, OpenAI, and Anthropic APIs
- **Provider-Specific Limits**: Different rate limits for each API provider
- **Smart Retry Logic**: Automatic retry with exponential backoff for rate limit errors
- **Real-time Monitoring**: Track requests per minute and hour
- **Header Parsing**: Parse rate limit headers from API responses
- **Graceful Handling**: Wait for rate limit resets when exceeded

**Rate Limits by Provider:**

- **GitHub**: 30 requests/minute, 5000 requests/hour
- **OpenAI**: 60 requests/minute, 1000 requests/hour
- **Anthropic**: 60 requests/minute, 1000 requests/hour
- **Default**: 60 requests/minute, 1000 requests/hour

# Show specific repository
gitco status --repo django

# Show detailed status
gitco status --detailed

### Activity Dashboard

View detailed activity metrics for your repositories:

```bash
# Show activity dashboard for all repositories
gitco activity

# Show activity for specific repository
gitco activity --repo django

# Show detailed activity information
gitco activity --detailed

# Filter repositories by activity level
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low

# Sort repositories by activity metrics
gitco activity --sort activity
gitco activity --sort engagement
gitco activity --sort commits
gitco activity --sort contributors

# Show activity dashboard via status command
gitco status --activity
gitco status --activity --detailed
```

**Activity Dashboard Features:**

- **Commit Activity**: Track commits across different time periods (24h, 7d, 30d, 90d)
- **Contributor Analysis**: Monitor active contributors and total contributor counts
- **Issue & PR Tracking**: Track new and closed issues, open PRs, and engagement metrics
- **Activity Health**: Overall activity health assessment with scoring
- **Engagement Metrics**: Activity and engagement scoring with trend analysis
- **Activity Patterns**: Most active hours and days with temporal analysis
- **Trending Metrics**: Stars, forks, and views growth tracking
- **Activity Levels**: Classification of repositories by activity level (high, moderate, low)
- **Engagement Levels**: Distribution of repositories by engagement level
- **Trending Repositories**: Identification and display of trending repositories
- **Most Active Repositories**: Display of repositories with highest activity
- **Rich Visualization**: Comprehensive tables with detailed metrics and health panels

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

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Set minimum confidence score
gitco discover --min-confidence 0.5

# Limit results
gitco discover --limit 10

# Export discovery results
gitco discover --export opportunities.json
```

### Contribution Discovery

GitCo provides intelligent contribution opportunity discovery using skill-based matching algorithms. The discovery system analyzes GitHub issues across your configured repositories and matches them to your skills and interests.

#### Skill-Based Matching

The discovery engine uses multiple matching strategies:

**Exact Matches**: Direct skill matches in issue content
- Example: "python" matches issues containing "python", "django", "flask"
- Confidence: 1.0 (highest)

**Partial Matches**: Skill-related terms and synonyms
- Example: "javascript" matches "react", "vue", "node.js"
- Confidence: 0.6-0.8

**Related Matches**: Related technologies and frameworks
- Example: "api" matches "rest", "graphql", "openapi"
- Confidence: 0.4

**Language Matches**: Repository language alignment
- Example: Python skill matches Python repository
- Confidence: 0.2-0.3

#### Difficulty Detection

Issues are automatically categorized by difficulty:

**Beginner**: Good for newcomers
- Labels: "good first issue", "beginner-friendly", "help wanted"
- Content: Documentation, tutorials, simple fixes
- Time: Quick to medium

**Intermediate**: Requires some experience
- Labels: "enhancement", "feature", "improvement"
- Content: New features, refactoring, moderate complexity
- Time: Medium

**Advanced**: Complex changes
- Labels: "architecture", "performance", "security"
- Content: Major refactoring, optimization, security fixes
- Time: Long

#### Time Estimation

Issues are estimated by time commitment:

**Quick**: 1-2 hours
- Typo fixes, documentation updates, simple formatting
- Labels: "typo", "documentation", "style"

**Medium**: 1-2 days
- Feature additions, bug fixes, moderate refactoring
- Labels: "feature", "bug", "enhancement"

**Long**: 1-2 weeks
- Major features, architecture changes, complex refactoring
- Labels: "architecture", "major", "rewrite"

#### Confidence Scoring

Each recommendation includes a confidence score (0.0-1.0):

- **0.9-1.0**: Perfect match with your skills
- **0.7-0.8**: Strong match with multiple skill alignments
- **0.5-0.6**: Good match with some skill overlap
- **0.3-0.4**: Moderate match with related skills
- **0.1-0.2**: Weak match, mostly language-based

#### Filtering Options

**Skill Filtering**: Focus on specific skills
```bash
gitco discover --skill python
gitco discover --skill javascript --skill react
```

**Label Filtering**: Focus on specific issue types
```bash
gitco discover --label "good first issue"
gitco discover --label "help wanted" --label "bug"
```

**Confidence Threshold**: Set minimum confidence
```bash
gitco discover --min-confidence 0.7
```

**Result Limiting**: Control output size
```bash
gitco discover --limit 5
```

#### Export Functionality

Export discovery results for external analysis:

```bash
# Export to JSON
gitco discover --export opportunities.json

# Export with filtering
gitco discover --skill python --export python-opportunities.json
```

The exported JSON includes:
- Issue details (title, URL, labels, description)
- Repository information
- Skill matches with confidence scores
- Difficulty and time estimates
- Overall recommendation score

#### Best Practices

1. **Start Broad**: Run `gitco discover` without filters to see all opportunities
2. **Use Skill Filters**: Focus on your strongest skills first
3. **Check Confidence**: Higher confidence scores indicate better matches
4. **Consider Difficulty**: Start with beginner issues if you're new to a project
5. **Export Results**: Save interesting opportunities for later review
6. **Combine Filters**: Use multiple filters for targeted discovery

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

### Automation and Quiet Mode

GitCo supports automated workflows with comprehensive quiet mode functionality:

#### Quiet Mode Usage

```bash
# Basic quiet mode - suppresses all user-facing output
gitco sync --quiet

# Quiet mode with logging to file
gitco sync --quiet --log sync.log

# Quiet mode for other commands
gitco analyze --repo django --quiet
gitco discover --skill python --quiet
gitco status --quiet
gitco contributions stats --quiet

# Cron job example (sync every 6 hours)
0 */6 * * * gitco sync --quiet --log /var/log/gitco-sync.log
```

#### Quiet Mode Features

**What's Suppressed:**
- Progress bars and spinners
- Success, error, info, and warning panels
- Console messages and status updates
- Repository operation details

**What's Preserved:**
- Logging functionality (when `--log` is specified)
- Error reporting for critical issues
- Exit codes for script integration
- File exports and data output

**Use Cases:**
- **Cron jobs**: Automated repository synchronization
- **CI/CD pipelines**: Integration with build systems
- **Scripts**: Programmatic usage without user interaction
- **Monitoring**: Background operations with log-based monitoring

#### Automation Examples

**Cron Job Setup:**
```bash
# Add to crontab for daily sync
0 2 * * * gitco sync --quiet --log /var/log/gitco/daily-sync.log

# Add to crontab for hourly discovery
0 * * * * gitco discover --skill python --quiet --export /tmp/opportunities.json
```

**Script Integration:**
```bash
#!/bin/bash
# Sync repositories and check for failures
if gitco sync --quiet --log sync.log; then
    echo "Sync completed successfully"
else
    echo "Sync failed - check sync.log for details"
    exit 1
fi
```

**CI/CD Pipeline:**
```yaml
# GitHub Actions example
- name: Sync repositories
  run: |
    gitco sync --quiet --log sync.log
    if [ $? -ne 0 ]; then
      echo "Sync failed - uploading logs"
      # Upload logs for debugging
    fi
```

### Getting Help

GitCo provides comprehensive help with contextual examples and organized documentation:

```bash
# Get comprehensive help with contextual examples
gitco help
```

**Help Features:**

**Organized Command Categories:**
- **Setup & Configuration**: init, config validate, config status
- **Repository Management**: sync, status, activity, validate-repo
- **AI-Powered Analysis**: analyze, discover
- **Contribution Tracking**: contributions sync-history, stats, recommendations, export, trending
- **GitHub Integration**: github test-connection, get-repo, get-issues, get-issues-multi
- **Upstream Management**: upstream add, remove, update, validate, fetch, merge
- **Backup & Recovery**: backup create, list, restore, validate, delete, cleanup
- **Utilities**: logs, help

**Contextual Examples:**
- **For New Users**: Guided setup, configuration validation, basic sync
- **For Regular Maintenance**: Sync with analysis, status checks, activity monitoring
- **For Contribution Discovery**: Skill-based filtering, label filtering, personalized recommendations
- **For Advanced Users**: Parallel sync, specific LLM providers, trend analysis
- **For Automation**: Quiet mode, logging, export functionality

**Configuration Examples:**
- YAML configuration file examples with syntax highlighting
- Environment variable setup examples
- Repository configuration with skills and settings

**Common Workflows:**
- **Daily Maintenance**: Sync with analysis, status overview, discovery
- **Weekly Review**: Detailed activity, contribution stats, incremental backup
- **Monthly Analysis**: Trending analysis, data export, backup cleanup

**Tips and Best Practices:**
- Start with 2-3 repositories
- Use skills for better discovery
- Set up automated syncs
- Regular backups
- Monitor repository health
- Export data for analysis
- Use quiet mode for automation
- Check logs for debugging

**Troubleshooting:**
- Configuration validation
- Git conflict resolution
- API rate limit handling
- LLM error resolution
- Command-specific help
- Configuration status checks
- GitHub connectivity testing
- Repository validation

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
