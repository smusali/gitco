# GitCo Frequently Asked Questions (FAQ)

Common questions and answers about GitCo, organized by category for easy reference.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Basic Usage](#basic-usage)
4. [Repository Management](#repository-management)
5. [Analysis and Discovery](#analysis-and-discovery)
6. [Health Monitoring](#health-monitoring)
7. [Contribution Tracking](#contribution-tracking)
8. [Backup and Recovery](#backup-and-recovery)
9. [Cost Management](#cost-management)
10. [GitHub Integration](#github-integration)
11. [Performance and Optimization](#performance-and-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Installation

### Q: How do I install GitCo?
**A:**
```bash
# Using pip (recommended)
pip install gitco

# Using pipx for isolated installation
pipx install gitco

# From source
git clone https://github.com/41technologies/gitco.git
cd gitco
pip install -e .
```

### Q: I get "command not found" after installation. What's wrong?
**A:** Add pip user bin to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Q: Which Python version do I need?
**A:** GitCo requires Python 3.9 or higher. Check with `python --version`.

### Q: Can I install GitCo in a virtual environment?
**A:** Yes, it's recommended:
```bash
python -m venv gitco-env
source gitco-env/bin/activate
pip install gitco
```

### Q: I get permission errors during installation. How do I fix this?
**A:**
```bash
# Install for current user only
pip install --user gitco

# Or use virtual environment
python -m venv ~/gitco-env
source ~/gitco-env/bin/activate
pip install gitco
```

---

## Configuration

### Q: How do I set up GitCo for the first time?
**A:** Run `gitco init --interactive` to create a configuration file at `~/.gitco/config.yml`.

### Q: Do I need to set up API keys?
**A:** API keys are optional but recommended for AI-powered features:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GITHUB_TOKEN="your-github-token"
```

### Q: How do I validate my configuration?
**A:**
```bash
# Basic validation
gitco config validate

# Detailed validation
gitco config validate-detailed --detailed

# Export validation report
gitco config validate-detailed --export validation-report.json
```

### Q: Can I use a custom configuration file?
**A:** Yes, use the `--config` option:
```bash
gitco --config /path/to/custom/config.yml sync
```

### Q: How do I configure multiple repositories?
**A:** Add them to your `~/.gitco/config.yml`:
```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async]
```

---

## Basic Usage

### Q: How do I sync my repositories?
**A:**
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

### Q: How do I check repository status?
**A:**
```bash
# Check all repositories
gitco status

# Detailed status
gitco status --detailed

# Overview dashboard
gitco status --overview

# Filter by health status
gitco status --filter healthy
```

### Q: How do I view repository activity?
**A:**
```bash
# Activity dashboard
gitco activity

# Detailed activity
gitco activity --detailed

# Activity for specific repository
gitco activity --repo django --detailed
```

---

## Repository Management

### Q: How do I add a new repository?
**A:** Add it to your configuration file:
```yaml
repositories:
  - name: new-project
    fork: username/new-project
    upstream: owner/new-project
    local_path: ~/code/new-project
    skills: [python, api, testing]
```

### Q: How do I manage upstream remotes?
**A:**
```bash
# Add upstream remote
gitco upstream add --repo django --url https://github.com/django/django.git

# Fetch from upstream
gitco upstream fetch --repo django

# Merge upstream changes
gitco upstream merge --repo django

# Validate upstream configuration
gitco upstream validate --repo django
```

### Q: How do I validate repositories?
**A:**
```bash
# Validate current directory
gitco validate-repo

# Validate specific path
gitco validate-repo --path ~/code/django

# Recursive validation
gitco validate-repo --path ~/code --recursive

# Detailed validation
gitco validate-repo --detailed
```

---

## Analysis and Discovery

### Q: How do I get AI analysis of changes?
**A:**
```bash
# Analyze specific repository
gitco analyze --repo django

# Analyze with custom prompt
gitco analyze --repo django --prompt "Focus on security changes"

# Analyze multiple repositories
gitco analyze --repos "django,fastapi,requests"

# Export analysis results
gitco analyze --repo django --export analysis.json
```

### Q: How do I find contribution opportunities?
**A:**
```bash
# Find all opportunities
gitco discover

# Find by skill
gitco discover --skill python

# Find by label
gitco discover --label "good first issue"

# Set confidence threshold
gitco discover --min-confidence 0.5

# Personalized recommendations
gitco discover --personalized --show-history
```

### Q: How do I filter discovery results?
**A:**
```bash
# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "bug"

# Set minimum confidence
gitco discover --min-confidence 0.7

# Limit results
gitco discover --limit 10

# Export results
gitco discover --export opportunities.json
```

---

## Health Monitoring

### Q: How do I check repository health?
**A:**
```bash
# Basic health check
gitco status

# Detailed health metrics
gitco status --detailed

# Filter by health status
gitco status --filter healthy
gitco status --filter needs_attention
gitco status --filter critical

# Sort by metrics
gitco status --sort health
gitco status --sort activity
```

### Q: How do I monitor repository activity?
**A:**
```bash
# Activity dashboard
gitco activity

# Detailed activity metrics
gitco activity --detailed

# Filter by activity level
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low

# Sort by activity metrics
gitco activity --sort activity
gitco activity --sort engagement
```

### Q: How do I export health and activity data?
**A:**
```bash
# Export health data
gitco status --export health.json

# Export activity data
gitco activity --export activity.json

# Export in CSV format
gitco status --export health.csv --output-format csv
```

---

## Contribution Tracking

### Q: How do I sync my contribution history?
**A:**
```bash
# Sync from GitHub
gitco contributions sync-history --username yourusername

# Force sync (even if recent)
gitco contributions sync-history --username yourusername --force
```

### Q: How do I view contribution statistics?
**A:**
```bash
# Basic stats
gitco contributions stats

# Stats for specific period
gitco contributions stats --days 30

# Export stats
gitco contributions stats --export stats.json
```

### Q: How do I get personalized recommendations?
**A:**
```bash
# Personalized recommendations
gitco contributions recommendations

# Filter by skill
gitco contributions recommendations --skill python

# Filter by repository
gitco contributions recommendations --repository django

# Limit recommendations
gitco contributions recommendations --limit 5
```

### Q: How do I export contribution data?
**A:**
```bash
# Export all contributions
gitco contributions export --output contributions.json

# Export recent contributions
gitco contributions export --days 30 --output recent-contributions.json

# Include summary statistics
gitco contributions export --output contributions.json --include-stats
```

---

## Backup and Recovery

### Q: How do I create backups?
**A:**
```bash
# Full backup
gitco backup create --type full --description "Weekly backup"

# Incremental backup
gitco backup create --type incremental --description "Daily backup"

# Config-only backup
gitco backup create --type config-only --description "Configuration backup"

# Backup specific repositories
gitco backup create --repos "django,fastapi" --description "Python repos backup"
```

### Q: How do I manage backups?
**A:**
```bash
# List all backups
gitco backup list

# Detailed backup information
gitco backup list --detailed

# Validate backup
gitco backup validate --backup-id backup-id

# Delete backup
gitco backup delete --backup-id backup-id --force
```

### Q: How do I restore from backup?
**A:**
```bash
# Restore from backup
gitco backup restore --backup-id backup-id

# Restore to specific directory
gitco backup restore --backup-id backup-id --target-dir ~/restored

# Skip configuration restoration
gitco backup restore --backup-id backup-id --no-config

# Overwrite existing files
gitco backup restore --backup-id backup-id --overwrite
```

---

## Cost Management

### Q: How do I check my API costs?
**A:**
```bash
# Basic cost summary
gitco cost summary

# Detailed cost breakdown
gitco cost summary --detailed

# Cost for specific period
gitco cost summary --days 30
gitco cost summary --months 3

# Export cost data
gitco cost summary --export costs.json
```

### Q: How do I set cost limits?
**A:**
```bash
# Set daily and monthly limits
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0

# Set per-request limit
gitco cost configure --per-request-limit 0.10

# Set token limits
gitco cost configure --max-tokens 4000
```

### Q: How do I optimize costs?
**A:**
```bash
# Enable token optimization
gitco cost configure --enable-optimization

# Enable cost tracking
gitco cost configure --enable-tracking

# View cost breakdown by provider
gitco cost breakdown --provider openai

# View cost breakdown by model
gitco cost breakdown --model gpt-3.5-turbo
```

---

## GitHub Integration

### Q: How do I test GitHub connection?
**A:**
```bash
# Test connection
gitco github test-connection

# Check rate limits
gitco github rate-limit-status

# Detailed rate limit information
gitco github rate-limit-status --detailed
```

### Q: How do I get repository information?
**A:**
```bash
# Get repository info
gitco github get-repo --repo django/django

# Get issues from repository
gitco github get-issues --repo django/django

# Get issues with filters
gitco github get-issues --repo django/django --labels "good first issue"
```

### Q: How do I get issues from multiple repositories?
**A:**
```bash
# Get issues from multiple repos
gitco github get-issues-multi --repos "django/django,fastapi/fastapi"

# Get issues with filters
gitco github get-issues-multi --repos "django/django,fastapi/fastapi" --labels "good first issue"

# Export results
gitco github get-issues-multi --repos "django/django,fastapi/fastapi" --export issues.json
```

---

## Performance and Optimization

### Q: How do I check performance metrics?
**A:**
```bash
# Performance metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json

# View logs
gitco logs --export logs.json
```

### Q: How do I optimize for automation?
**A:**
```bash
# Quiet mode for automation
gitco --quiet sync --batch

# Export for monitoring
gitco status --export status.json --output-format json

# Debug mode for troubleshooting
gitco --debug sync
```

### Q: How do I handle slow operations?
**A:**
```bash
# Reduce batch size in config
max_repos_per_batch: 2

# Increase timeouts
git_timeout: 600
github_timeout: 60

# Use quiet mode
gitco --quiet sync
```

---

## Troubleshooting

### Q: GitCo fails with import errors. What should I do?
**A:**
```bash
# Upgrade pip and reinstall
pip install --upgrade pip setuptools wheel
pip install --force-reinstall gitco

# Check Python version
python --version

# Use virtual environment
python -m venv gitco-env
source gitco-env/bin/activate
pip install gitco
```

### Q: I get permission errors when syncing repositories. How do I fix this?
**A:**
```bash
# Fix ownership
chown -R $(whoami):$(whoami) ~/code/django

# Fix permissions
chmod -R 755 ~/code/django

# Check Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Q: How do I resolve merge conflicts?
**A:**
```bash
# Abort current merge
gitco upstream merge --repo django --abort

# Resolve conflicts manually
cd ~/code/django
git status
# Edit conflicted files
git add .
git commit -m "Resolve merge conflicts"

# Use automatic resolution
gitco upstream merge --repo django --resolve --strategy ours
```

### Q: How do I handle rate limit errors?
**A:**
```bash
# Check rate limit status
gitco github rate-limit-status --detailed

# Wait for rate limit reset
gitco github rate-limit-status

# Increase delays in config
rate_limit_delay: 2.0
min_request_interval: 0.5
```

### Q: How do I debug issues?
**A:**
```bash
# Enable debug mode
gitco --debug --detailed-log sync

# Debug specific command
gitco --debug analyze --repo django

# Export debug logs
gitco --debug --log-file debug.log sync

# Verbose output
gitco --verbose sync
```

### Q: How do I reset cost tracking?
**A:**
```bash
# Reset cost history
gitco cost reset

# Force reset without confirmation
gitco cost reset --force

# Check cost usage
gitco cost summary --detailed
```

### Q: How do I validate my backup?
**A:**
```bash
# Validate backup
gitco backup validate --backup-id backup-id

# List backups
gitco backup list --detailed

# Test restore
gitco backup restore --backup-id backup-id --target-dir ~/test-restore
```

---

## Getting Help

### Q: Where can I get more help?
**A:**
- **Documentation:** Check the [CLI Reference](cli.md), [Configuration Guide](configuration.md), and [Usage Guide](usage.md)
- **GitHub Issues:** Report bugs and feature requests
- **Troubleshooting Guide:** See [Troubleshooting Guide](troubleshooting.md)
- **Community:** Join discussions and ask questions

### Q: How do I report a bug?
**A:** Include the following information:
```bash
# System information
gitco --version
python --version
git --version

# Configuration summary
gitco config status

# Recent logs
tail -n 100 ~/.gitco/gitco.log

# Performance metrics
gitco performance --export performance.json
```

This comprehensive FAQ covers the most common questions about GitCo. For more detailed information, refer to the specific documentation sections or report issues through the appropriate channels.
