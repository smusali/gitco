# Usage Guide

This guide covers how to use GitCo effectively for managing your OSS forks and discovering contribution opportunities.

## Basic Commands

### Initialize Configuration

Start by creating a configuration file:

```bash
gitco init
```

This creates a `gitco-config.yml` file in your current directory.

**Note:** The CLI framework, configuration management, and logging system are implemented. Full functionality will be added in subsequent commits.

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

### Analyze Changes

Get AI-powered analysis of upstream changes:

```bash
# Analyze specific repository
gitco analyze --repo fastapi

# Analyze with custom prompt
gitco analyze --repo django --prompt "Focus on security changes"

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
```

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

Synchronize repositories with upstream changes.

**Options:**
- `--repo REPO`: Sync specific repository
- `--analyze`: Include AI analysis
- `--export FILE`: Export report to file
- `--quiet`: Suppress output
- `--log FILE`: Log to file
- `--batch`: Process all repositories

**Examples:**
```bash
gitco sync
gitco sync --repo django --analyze
gitco sync --export report.json
```

### `gitco analyze`

Analyze repository changes with AI.

**Options:**
- `--repo REPO`: Analyze specific repository
- `--prompt PROMPT`: Custom analysis prompt
- `--repos REPOS`: Analyze multiple repositories
- `--export FILE`: Export analysis to file

**Examples:**
```bash
gitco analyze --repo fastapi
gitco analyze --repo django --prompt "Security focus"
```

### `gitco discover`

Discover contribution opportunities.

**Options:**
- `--skill SKILL`: Filter by skill
- `--label LABEL`: Filter by label
- `--export FILE`: Export results to file
- `--limit N`: Limit number of results

**Examples:**
```bash
gitco discover
gitco discover --skill python --label "good first issue"
```

### `gitco status`

Show repository status.

**Options:**
- `--repo REPO`: Show specific repository
- `--detailed`: Show detailed information
- `--export FILE`: Export status to file

**Examples:**
```bash
gitco status
gitco status --repo django --detailed
```

## Configuration Examples

### Basic Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

settings:
  llm_provider: openai
  api_key_env: AETHERIUM_API_KEY
```

### Advanced Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm, database]
    
  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async]

settings:
  llm_provider: anthropic
  api_key_env: AETHERIUM_API_KEY
  analysis_enabled: true
  max_repos_per_batch: 5
```

## Workflow Examples

### Daily Workflow

```bash
# 1. Check status of all repositories
gitco status

# 2. Sync repositories with upstream
gitco sync --analyze

# 3. Discover new opportunities
gitco discover --skill python
```

### Weekly Workflow

```bash
# 1. Full sync with analysis
gitco sync --analyze --export weekly-sync.json

# 2. Comprehensive opportunity search
gitco discover --export opportunities.csv

# 3. Generate status report
gitco status --detailed --export status-report.json
```

### Automation Workflow

```bash
# Add to crontab for daily sync
0 9 * * * cd /path/to/project && gitco sync --quiet --log /var/log/gitco.log

# Weekly analysis
0 10 * * 1 cd /path/to/project && gitco analyze --batch --export analysis.json
```

## Tips and Best Practices

### Repository Management

1. **Keep repositories organized** in a consistent directory structure
2. **Use descriptive names** for repository identifiers
3. **Update skills regularly** as you learn new technologies
4. **Backup your configuration** before major changes

### Analysis Optimization

1. **Use specific prompts** for focused analysis
2. **Export results** for historical tracking
3. **Combine with other tools** for comprehensive insights
4. **Review analysis results** before acting on recommendations

### Discovery Strategy

1. **Start with broad searches** then narrow down
2. **Focus on your strongest skills** for better matches
3. **Track your contributions** to improve recommendations
4. **Set realistic goals** for contribution frequency

## Troubleshooting

### Common Issues

1. **Repository not found:**
   - Check local_path exists
   - Verify repository permissions

2. **API key errors:**
   - Verify environment variable is set
   - Check API key permissions

3. **Analysis failures:**
   - Check internet connectivity
   - Verify API key is valid

### Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md)
- Search [GitHub Issues](https://github.com/41technologies/gitco/issues)
- Create a new issue with detailed information

## Next Steps

- Explore [Advanced Configuration](configuration.md)
- Check [Troubleshooting Guide](troubleshooting.md) for common issues
- Contribute to the project via [Contributing Guide](../CONTRIBUTING.md) 
