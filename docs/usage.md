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
