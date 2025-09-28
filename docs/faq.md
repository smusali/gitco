# GitCo Frequently Asked Questions (FAQ)

Common questions and answers about GitCo, organized by category for easy reference.

## Table of Contents

1. [Configuration](#configuration)
2. [Basic Usage](#basic-usage)
3. [Repository Management](#repository-management)
4. [Analysis and Discovery](#analysis-and-discovery)
5. [Health Monitoring](#health-monitoring)
6. [Contribution Tracking](#contribution-tracking)
7. [Backup and Recovery](#backup-and-recovery)
8. [GitHub Integration](#github-integration)
9. [Performance and Optimization](#performance-and-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Configuration

### Q: How do I set up GitCo for the first time?
**A:** Run `gitco init --interactive` to create a configuration file at `~/.gitco/config.yml`.

### Q: Do I need to set up API keys?
**A:** API keys are optional but recommended for AI-powered features:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"
```

### Q: How do I validate my configuration?
**A:**
```bash
# Basic validation
gitco config validate

# Detailed validation
gitco config validate --detailed

# Export validation report
gitco config validate --export validation-report.json
```

### Q: Can I use a custom configuration file?
**A:** Yes, use the `--config` option:
```bash
gitco --config ~/.gitco/custom-config.yml sync
```

### Q: How do I add a new repository to my configuration?
**A:** Edit `~/.gitco/config.yml` and add a new entry:
```yaml
repositories:
  - name: new-project
    fork: username/new-project
    upstream: owner/new-project
    local_path: ~/code/new-project
    skills: [python, api, development]
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
```

### Q: How do I analyze changes in a repository?
**A:**
```bash
# Basic analysis
gitco analyze --repo django

# Detailed analysis
gitco analyze --repo django --detailed

# Custom analysis prompt
gitco analyze --repo django --prompt "Focus on security implications"
```

### Q: How do I find contribution opportunities?
**A:**
```bash
# Find all opportunities
gitco discover

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Personalized recommendations
gitco discover --personalized
```

### Q: How do I check repository health?
**A:**
```bash
# Check all repositories
gitco status

# Detailed health report
gitco status --detailed

# Filter by health status
gitco status --filter healthy
```

---

## Repository Management

### Q: How do I add an upstream remote to a repository?
**A:**
```bash
gitco upstream add --repo django --url https://github.com/django/django.git
```

### Q: How do I validate a repository?
**A:**
```bash
# Validate specific repository
gitco validate-repo --repo django

# Validate all repositories
gitco validate-repo --all

# Detailed validation
gitco validate-repo --repo django --detailed
```

### Q: How do I update an upstream URL?
**A:**
```bash
gitco upstream update --repo django --url https://github.com/new-org/django.git
```

### Q: What if I have merge conflicts during sync?
**A:** GitCo will automatically stash your changes and attempt to resolve conflicts. You can configure merge strategies in your config:
```yaml
settings:
  merge_strategy: ours  # or 'theirs', 'manual'
```

---

## Analysis and Discovery

### Q: Which LLM providers are supported?
**A:** GitCo supports OpenAI (GPT-3.5, GPT-4).

### Q: How do I configure the LLM provider?
**A:** Update your configuration:
```yaml
settings:
  llm_provider: openai
```


### Q: How accurate are the discovery recommendations?
**A:** Discovery accuracy depends on your skill configuration and the quality of issue labels. You can adjust confidence thresholds:
```bash
gitco discover --min-confidence 0.7
```

---

## Health Monitoring

### Q: What health metrics does GitCo track?
**A:** GitCo tracks repository activity, commit frequency, issue response times, pull request merge rates, and overall repository health scores.

### Q: How do I export health data?
**A:**
```bash
# Export health data
gitco status --export health.json

# Export activity data
gitco activity --export activity.json
```

### Q: How do I filter repositories by health status?
**A:**
```bash
# Show only healthy repositories
gitco status --filter healthy

# Show repositories needing attention
gitco status --filter needs_attention

# Show critical repositories
gitco status --filter critical
```

---

## Contribution Tracking

### Q: How do I sync my contribution history?
**A:**
```bash
gitco contributions sync-history --username yourusername
```

### Q: How do I view my contribution statistics?
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
# Get recommendations based on history
gitco contributions recommendations

# Filter by skill
gitco contributions recommendations --skill python

# Limit results
gitco contributions recommendations --limit 5
```

---

## Backup and Recovery

### Q: How do I create a backup?
**A:**
```bash
# Full backup
gitco backup create --type full --description "Weekly backup"

# Incremental backup
gitco backup create --type incremental --description "Daily backup"
```

### Q: How do I restore from a backup?
**A:**
```bash
# List available backups
gitco backup list

# Restore from backup
gitco backup restore --backup-id backup-id
```

### Q: How do I manage backup storage?
**A:**
```bash
# Clean up old backups
gitco backup cleanup

# Keep more backups
gitco backup cleanup --keep 10
```

---


## GitHub Integration

### Q: How do I check my GitHub connection?
**A:**
```bash
gitco github connection-status
```

### Q: How do I check rate limits?
**A:**
```bash
gitco github rate-limit-status
```

### Q: How do I get repository information?
**A:**
```bash
gitco github get-repo --repo django/django
```

---

## Performance and Optimization

### Q: How do I optimize sync performance?
**A:**
```bash
# Use batch processing
gitco sync --batch

# Adjust batch size
gitco sync --batch --max-repos 5

# Use quiet mode for automation
gitco --quiet sync
```

### Q: How do I monitor performance?
**A:**
```bash
# Check performance metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json
```

### Q: How do I handle large repositories?
**A:** GitCo automatically handles large repositories, but you can optimize:
```bash
# Skip git history in backups
gitco backup create --no-git-history

# Use incremental backups
gitco backup create --type incremental
```

---

## Troubleshooting

### Q: I get "command not found" after installation. What's wrong?
**A:** Add pip user bin to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
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

### Q: My configuration validation fails. What should I check?
**A:**
```bash
# Check configuration file syntax
gitco config validate

# Check environment variables
echo $OPENAI_API_KEY
echo $GITHUB_TOKEN

# Check GitHub connection
gitco github connection-status
```

### Q: I get rate limit errors. How do I fix this?
**A:**
```bash
# Check current rate limits
gitco github rate-limit-status

# Wait for rate limit reset or use a different token
export GITHUB_TOKEN="your-new-token"
```

### Q: Analysis is taking too long. How do I speed it up?
**A:**
```bash
# Use a faster model
gitco analyze --repo django --model gpt-3.5-turbo

# Limit analysis scope
gitco analyze --repo django --max-commits 10

# Disable detailed analysis
gitco analyze --repo django --no-detailed
```

### Q: How do I enable debug logging?
**A:**
```bash
# Enable debug mode
gitco --debug sync

# Log to file
gitco --debug --log-file debug.log sync

# Detailed logging
gitco --debug --detailed-log sync
```

### Q: How do I get help for a specific command?
**A:**
```bash
# General help
gitco --help

# Command-specific help
gitco sync --help
gitco analyze --help
gitco discover --help
```
