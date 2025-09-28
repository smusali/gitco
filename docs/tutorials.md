# GitCo Tutorials

This guide provides essential tutorials and examples for using GitCo effectively.

## Getting Started Tutorial

### Prerequisites
- Python 3.9+ installed
- Git installed and configured
- GitHub account with access to repositories
- LLM API key (OpenAI)

### Step 1: Installation and Setup
```bash
# Install GitCo
pip install gitco

# Initialize with interactive setup
gitco init --interactive

# Set up API keys
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"
```

### Step 2: Configure Your First Repository
Edit `~/.gitco/config.yml`:
```yaml
repositories:
  - name: django
    fork: your-username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

settings:
  llm_provider: openai
  default_path: ~/code
```

### Step 3: Verify Your Setup
```bash
# Sync with a single repository
gitco sync --repo django

# Get AI analysis of changes
gitco analyze --repo django

# Find contribution opportunities
gitco discover
```

## Daily Workflow Tutorial

### Morning Routine
```bash
# Quick sync of all repositories
gitco sync --batch --quiet

# Check repository health
gitco status --overview

# Find new opportunities
gitco discover --limit 3
```

### Weekly Review
```bash
# Full sync with analysis
gitco sync --batch --analyze --export weekly-sync.json

# Activity analysis
gitco activity --detailed --export weekly-activity.json

# Contribution statistics
gitco contributions stats --days 7 --export weekly-stats.json
```

## Contribution Discovery Tutorial

### Basic Discovery
```bash
# Find all opportunities
gitco discover

# Find Python-specific opportunities
gitco discover --skill python

# Find beginner-friendly issues
gitco discover --label "good first issue"
```

### Personalized Discovery
```bash
# Sync your contribution history
gitco contributions sync-history --username yourusername

# Get personalized recommendations
gitco discover --personalized

# Show contribution history
gitco discover --show-history
```

## Automation Tutorial

### Cron Job Setup
```bash
# Add to crontab (crontab -e)
# Sync repositories every 6 hours
0 */6 * * * /usr/bin/gitco sync --batch --quiet --log /var/log/gitco/sync.log

# Daily health check at 9 AM
0 9 * * * /usr/bin/gitco status --overview --quiet --export /var/log/gitco/daily-status.json
```

### GitHub Actions Workflow
Create `.github/workflows/gitco-maintenance.yml`:
```yaml
name: GitCo Maintenance

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM
  workflow_dispatch:

jobs:
  gitco-sync:
    runs-on: ubuntu-latest
    steps:
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install GitCo
      run: pip install gitco

    - name: Setup environment
      run: |
        echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
        echo "GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}" >> $GITHUB_ENV

    - name: Sync repositories
      run: gitco sync --batch --quiet --export sync-results.json

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: gitco-sync-results
        path: sync-results.json
```

## Troubleshooting Tutorial

### Common Issues

#### Configuration Issues
```bash
# Validate configuration
gitco config validate

# Check configuration status
gitco config status
```

#### Git Operation Issues
```bash
# Check repository status
cd ~/code/django
git status

# Resolve conflicts manually
git merge --abort
git reset --hard HEAD
git clean -fd
```

#### API Rate Limiting
```bash
# Check rate limit status
gitco github rate-limit-status

# Wait for rate limit reset or use GitHub token
```

#### LLM API Issues
```bash
# Check API key
echo $OPENAI_API_KEY

# Check API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### Debug Mode
```bash
# Enable verbose output
gitco sync --verbose

# Enable detailed logging
gitco sync --detailed-log --log-file debug.log
```

## Best Practices

### Repository Organization
1. Use consistent naming conventions
2. Group repositories by technology
3. Tag repositories with relevant skills
4. Regular maintenance and sync

### Configuration Management
1. Keep configuration in version control
2. Use environment variables for sensitive data
3. Run configuration validation regularly
4. Create backups of your configuration

### Automation Best Practices
1. Start with a few repositories and expand gradually
2. Monitor logs regularly for issues
3. Set up alerts for sync failures
4. Create regular backups
5. Monitor API usage and performance

For more detailed examples and advanced workflows, see the [Examples Guide](examples.md) and [Workflows Guide](workflows.md).
