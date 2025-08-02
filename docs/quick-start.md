# GitCo Quick Start Guide

Get up and running with GitCo in 5 minutes! This guide will help you set up GitCo and start managing your OSS forks effectively.

## Table of Contents

1. [Installation](#installation)
2. [Initial Setup](#initial-setup)
3. [Basic Configuration](#basic-configuration)
4. [First Sync](#first-sync)
5. [Analysis and Discovery](#analysis-and-discovery)
6. [Health Monitoring](#health-monitoring)
7. [Next Steps](#next-steps)

---

## Installation

### Prerequisites

- Python 3.9 or higher
- Git installed and configured
- GitHub account with personal access token

### Install GitCo

```bash
# Install from PyPI
pip install gitco

# Or install from source
git clone https://github.com/41technologies/gitco.git
cd gitco
pip install -e .
```

### Verify Installation

```bash
gitco --version
gitco --help
```

---

## Initial Setup

### 1. Initialize Configuration

```bash
# Interactive setup (recommended)
gitco init --interactive

# Or use defaults
gitco init --non-interactive
```

The interactive setup will guide you through:
- Repository configuration
- LLM provider selection
- GitHub integration
- Cost optimization settings

### 2. Set Environment Variables

```bash
# GitHub integration
export GITHUB_TOKEN="your-github-token"

# LLM provider (choose one)
export OPENAI_API_KEY="your-openai-api-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 3. Verify Setup

```bash
# Validate configuration
gitco config validate

# Test GitHub connection
gitco github test-connection
```

---

## Basic Configuration

### Manual Configuration

If you prefer manual configuration, create `~/.gitco/config.yml`:

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

settings:
  llm_provider: openai
  default_path: ~/code
  analysis_enabled: true
```

### Configuration Options

**Repository Fields:**
- `name`: Unique identifier
- `fork`: Your fork (username/repo)
- `upstream`: Original repository (owner/repo)
- `local_path`: Local clone path
- `skills`: Your relevant skills
- `analysis_enabled`: Enable AI analysis
- `sync_frequency`: Sync schedule (daily, weekly, monthly, manual)
- `language`: Primary programming language

**Settings Fields:**
- `llm_provider`: AI provider (openai, anthropic, custom)
- `default_path`: Default repository path
- `analysis_enabled`: Global AI analysis setting
- `max_repos_per_batch`: Batch processing limit
- `git_timeout`: Git operation timeout
- `rate_limit_delay`: API call delay

---

## First Sync

### 1. Clone Your Repositories

```bash
# Clone repositories to local paths
git clone https://github.com/username/django.git ~/code/django
```

### 2. Add Upstream Remotes

```bash
# Add upstream remote
gitco upstream add --repo django --url https://github.com/django/django.git

# Verify upstream configuration
gitco upstream validate --repo django
```

### 3. Perform First Sync

```bash
# Sync all repositories
gitco sync

# Or sync specific repository
gitco sync --repo django

# Sync with analysis
gitco sync --analyze
```

### 4. Check Status

```bash
# View repository status
gitco status

# Detailed health check
gitco status --detailed

# Overview dashboard
gitco status --overview
```

---

## Analysis and Discovery

### Change Analysis

```bash
# Analyze repository changes
gitco analyze --repo django

# Analyze with custom prompt
gitco analyze --repo django --prompt "Focus on security implications"

# Analyze multiple repositories
gitco analyze --repos "django,fastapi"
```

### Contribution Discovery

```bash
# Discover all opportunities
gitco discover

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Set confidence threshold
gitco discover --min-confidence 0.5

# Personalized recommendations
gitco discover --personalized --show-history
```

### Activity Monitoring

```bash
# View activity dashboard
gitco activity

# Detailed activity metrics
gitco activity --detailed

# Activity for specific repository
gitco activity --repo django --detailed
```

---

## Health Monitoring

### Repository Health

```bash
# Basic health check
gitco status

# Filter by health status
gitco status --filter healthy
gitco status --filter needs_attention
gitco status --filter critical

# Sort by metrics
gitco status --sort health
gitco status --sort activity
gitco status --sort stars
```

### Activity Monitoring

```bash
# Activity dashboard
gitco activity

# Filter by activity level
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low

# Sort by activity metrics
gitco activity --sort activity
gitco activity --sort engagement
```

### Export Data

```bash
# Export health data
gitco status --export health.json

# Export activity data
gitco activity --export activity.json

# Export discovery results
gitco discover --export opportunities.json
```

---

## Next Steps

### Daily Workflow

```bash
# Daily sync
gitco sync

# Check health
gitco status

# Find opportunities
gitco discover --limit 5
```

### Weekly Workflow

```bash
# Sync with analysis
gitco sync --analyze

# Detailed health report
gitco status --detailed --export weekly-health.json

# Activity analysis
gitco activity --detailed --export weekly-activity.json
```

### Advanced Features

**Contribution Tracking:**
```bash
# Sync contribution history
gitco contributions sync-history --username yourusername

# View contribution stats
gitco contributions stats

# Get recommendations
gitco contributions recommendations
```

**Backup and Recovery:**
```bash
# Create backup
gitco backup create --type full --description "Weekly backup"

# List backups
gitco backup list

# Restore from backup
gitco backup restore --backup-id backup-id
```

**Cost Management:**
```bash
# View cost summary
gitco cost summary

# Configure cost limits
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0

# Cost breakdown
gitco cost breakdown --provider openai
```

**GitHub Integration:**
```bash
# Check rate limits
gitco github rate-limit-status

# Get repository info
gitco github get-repo --repo django/django

# Get issues from multiple repos
gitco github get-issues-multi --repos "django/django,fastapi/fastapi"
```

### Automation

**Quiet Mode:**
```bash
# Quiet sync for automation
gitco --quiet sync --batch

# Export for monitoring
gitco status --export status.json --output-format json
```

**GitHub Actions:**
```yaml
name: GitCo Sync
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install GitCo
        run: pip install gitco
      - name: Sync repositories
        run: |
          export GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
          export OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
          gitco --quiet sync --batch --export sync-report.json
```

### Troubleshooting

**Common Issues:**
```bash
# Validate configuration
gitco config validate

# Test GitHub connection
gitco github test-connection

# Check rate limits
gitco github rate-limit-status

# Debug mode
gitco --debug sync
```

**Get Help:**
```bash
# Comprehensive help
gitco help

# Command-specific help
gitco sync --help
gitco analyze --help
gitco discover --help
```

---

## Configuration Examples

### Minimal Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django

settings:
  llm_provider: openai
  default_path: ~/code
```

### Advanced Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]
    analysis_enabled: true
    sync_frequency: daily
    language: python

  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async]
    analysis_enabled: true
    sync_frequency: weekly
    language: python

settings:
  llm_provider: anthropic
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 5
  git_timeout: 300
  rate_limit_delay: 1.0
  log_level: INFO

  # GitHub settings
  github_token_env: GITHUB_TOKEN
  github_api_url: https://api.github.com

  # Rate limiting
  github_rate_limit_per_minute: 30
  github_rate_limit_per_hour: 5000
  llm_rate_limit_per_minute: 60
  llm_rate_limit_per_hour: 1000

  # Cost optimization
  enable_cost_tracking: true
  enable_token_optimization: true
  max_tokens_per_request: 4000
  max_cost_per_request_usd: 0.10
  max_daily_cost_usd: 5.0
  max_monthly_cost_usd: 50.0
```

---

## What's Next?

Now that you have GitCo set up, explore these resources:

- **[CLI Reference](cli.md)** - Complete command reference
- **[Configuration Guide](configuration.md)** - Detailed configuration options
- **[Usage Guide](usage.md)** - Comprehensive usage examples
- **[Features Guide](features.md)** - Detailed feature overview
- **[Tutorials Guide](tutorials.md)** - Step-by-step tutorials
- **[Workflows Guide](workflows.md)** - User persona-based workflows
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions
- **[FAQ](faq.md)** - Frequently asked questions

GitCo is designed to make OSS contribution management simple, intelligent, and rewarding. Start contributing more effectively today! 🚀
