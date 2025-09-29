# GitCo Quick Start Guide

Get up and running with GitCo in 5 minutes! This guide will help you set up GitCo and start managing your OSS forks effectively.

## Prerequisites

- Python 3.9 or higher
- Git installed and configured
- GitHub account with personal access token
- LLM API key (OpenAI) - optional but recommended

## Installation

```bash
pip install gitco
```

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

### 2. Set Environment Variables

```bash
# LLM provider
export OPENAI_API_KEY="your-openai-api-key"

# GitHub authentication is automatic using your existing Git credentials!
# No additional GitHub API keys are required.
```

### 3. Configure Your First Repository

Edit `~/.gitco/config.yml`:
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
```

### 4. Verify Setup

```bash
# Validate configuration
gitco config validate

# Check GitHub connection
gitco github connection-status
```

## Basic Usage

### Sync Repositories

```bash
# Sync all repositories
gitco sync

# Sync specific repository
gitco sync --repo django

# Sync with analysis
gitco sync --analyze
```

### Analyze Changes

```bash
# Analyze changes in a repository
gitco analyze --repo django

# Get detailed analysis
gitco analyze --repo django --detailed
```

### Discover Opportunities

```bash
# Find all opportunities
gitco discover

# Find Python-specific opportunities
gitco discover --skill python

# Find beginner-friendly issues
gitco discover --label "good first issue"
```

### Check Repository Health

```bash
# Check all repositories
gitco status

# Detailed health report
gitco status --detailed
```

## Next Steps

- **Learn more**: Check out the [Usage Guide](usage.md) for detailed workflows
- **Configure advanced settings**: See the [Configuration Guide](configuration.md)
- **Explore features**: Read the [Features Guide](features.md)
- **Get help**: Visit the [FAQ](faq.md) or [Troubleshooting Guide](troubleshooting.md)
