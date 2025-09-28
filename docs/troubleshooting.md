# GitCo Troubleshooting Guide

This guide helps you resolve common issues with GitCo and provides diagnostic commands for troubleshooting.

## Table of Contents

1. [Quick Diagnostic Commands](#quick-diagnostic-commands)
2. [Configuration Issues](#configuration-issues)
3. [Git Operations Issues](#git-operations-issues)
4. [API and Network Issues](#api-and-network-issues)
5. [Analysis and Discovery Issues](#analysis-and-discovery-issues)
6. [Performance Issues](#performance-issues)
7. [Backup and Recovery Issues](#backup-and-recovery-issues)
8. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## Quick Diagnostic Commands

### Basic System Checks

```bash
# Check GitCo installation
gitco --version
gitco --help

# Check Python environment
python --version
pip list | grep gitco

# Check Git configuration
git --version
git config --list

# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GITHUB_TOKEN

# Check configuration file
ls -la ~/.gitco/
cat ~/.gitco/config.yml
```

### GitCo-Specific Diagnostics

```bash
# Validate configuration
gitco config validate

# Check GitHub connection
gitco github connection-status

# Check rate limits
gitco github rate-limit-status

# Validate repositories
gitco validate-repo --detailed

# Check performance
gitco performance --detailed

# View logs
gitco logs --export logs.json
```

---

## Configuration Issues

### Invalid Configuration File

**Symptoms:** `gitco config validate` fails

**Solutions:**

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.gitco/config.yml'))"

# Validate configuration
gitco config validate --detailed

# Check for missing required fields
gitco config validate --strict
```

### Missing Environment Variables

**Symptoms:** API calls fail with authentication errors

**Solutions:**

```bash
# Check environment variables
env | grep -E "(OPENAI|ANTHROPIC|GITHUB)_API_KEY"

# Set missing variables
export OPENAI_API_KEY="your-key-here"
export GITHUB_TOKEN="your-token-here"

# Check API connections
gitco github connection-status
```

### Repository Path Issues

**Symptoms:** "Repository not found" or "Path does not exist"

**Solutions:**

```bash
# Check repository paths
ls -la ~/code/

# Validate repository structure
gitco validate-repo --repo django

# Fix repository paths in config
# Edit ~/.gitco/config.yml with correct paths
```

---

## Git Operations Issues

### Permission Denied

**Symptoms:** `Permission denied` when accessing repositories

**Solutions:**

```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) ~/code/

# Fix permissions
chmod -R 755 ~/code/

# Check Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Merge Conflicts

**Symptoms:** Sync fails with merge conflicts

**Solutions:**

```bash
# Abort current merge
cd ~/code/django
git merge --abort

# Stash changes and retry
gitco sync --repo django --stash

# Manual conflict resolution
cd ~/code/django
git status
# Edit conflicted files
git add .
git commit -m "Resolve merge conflicts"
```

### Upstream Remote Issues

**Symptoms:** "Upstream remote not found" or sync fails

**Solutions:**

```bash
# Check upstream configuration
gitco upstream validate --repo django

# Add upstream remote
gitco upstream add --repo django --url https://github.com/django/django.git

# Update upstream URL
gitco upstream update --repo django --url https://github.com/new-org/django.git
```

---

## API and Network Issues

### Rate Limit Errors

**Symptoms:** `Rate limit exceeded` or `403 Forbidden`

**Solutions:**

```bash
# Check rate limits
gitco github rate-limit-status

# Wait for rate limit reset
gitco github rate-limit-status --wait

# Use different token
export GITHUB_TOKEN="your-new-token"

# Increase delays in config
# Edit ~/.gitco/config.yml:
# rate_limit_delay: 2.0
```

### Network Timeouts

**Symptoms:** `Connection timeout` or `Request timeout`

**Solutions:**

```bash
# Check network connectivity
ping api.github.com
curl -I https://api.github.com

# Increase timeouts in config
# Edit ~/.gitco/config.yml:
# git_timeout: 600
# github_timeout: 60

# Use proxy if needed
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"
```

### API Authentication Failures

**Symptoms:** `401 Unauthorized` or `Invalid token`

**Solutions:**

```bash
# Check GitHub token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Regenerate token with correct scopes
# Go to GitHub Settings > Developer settings > Personal access tokens

# Check OpenAI token
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

---

## Analysis and Discovery Issues

### LLM Provider Errors

**Symptoms:** Analysis fails with API errors

**Solutions:**

```bash
# Check LLM provider configuration
gitco config validate

# Check OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Switch LLM provider
# Edit ~/.gitco/config.yml:
# settings:
#   llm_provider: anthropic

# Disable analysis temporarily
gitco analyze --repo django --no-llm
```


### Discovery Issues

**Symptoms:** No opportunities found or poor recommendations

**Solutions:**

```bash
# Check skill configuration
gitco config validate

# Update skills in config
# Edit ~/.gitco/config.yml with relevant skills

# Lower confidence threshold
gitco discover --min-confidence 0.3

# Check GitHub rate limits
gitco github rate-limit-status
```

---

## Performance Issues

### Slow Sync Operations

**Symptoms:** Sync takes too long or hangs

**Solutions:**

```bash
# Check repository sizes
du -sh ~/code/*

# Reduce batch size
gitco sync --batch --max-repos 2

# Use quiet mode
gitco --quiet sync

# Check system resources
top
df -h
```

### Memory Issues

**Symptoms:** Out of memory errors or crashes

**Solutions:**

```bash
# Check memory usage
free -h

# Reduce batch processing
# Edit ~/.gitco/config.yml:
# max_repos_per_batch: 1

# Use incremental backups
gitco backup create --type incremental

# Skip git history in backups
gitco backup create --no-git-history
```

### High CPU Usage

**Symptoms:** System becomes unresponsive during operations

**Solutions:**

```bash
# Monitor CPU usage
htop

# Reduce concurrency
# Edit ~/.gitco/config.yml:
# max_concurrent_operations: 1

# Use quiet mode
gitco --quiet sync

# Process repositories one by one
gitco sync --repo django
gitco sync --repo fastapi
```

---

## Backup and Recovery Issues

### Backup Creation Fails

**Symptoms:** Backup creation fails or is incomplete

**Solutions:**

```bash
# Check disk space
df -h

# Check backup directory permissions
ls -la ~/.gitco/backups/

# Create smaller backup
gitco backup create --type incremental --no-git-history

# Check backup validation
gitco backup validate --backup-id backup-id
```

### Restore Issues

**Symptoms:** Restore fails or is incomplete

**Solutions:**

```bash
# List available backups
gitco backup list --detailed

# Restore to different directory
gitco backup restore --backup-id backup-id --target-dir ~/restore-location

# Check restore permissions
ls -la ~/code/

# Force restore
gitco backup restore --backup-id backup-id --overwrite
```

### Backup Corruption

**Symptoms:** Backup validation fails

**Solutions:**

```bash
# Validate backup
gitco backup validate --backup-id backup-id

# Delete corrupted backup
gitco backup delete --backup-id backup-id --force

# Create new backup
gitco backup create --type full --description "Fresh backup"
```

---

## Advanced Troubleshooting

### Debug Mode

**Enable comprehensive debugging:**

```bash
# Enable debug mode
gitco --debug sync

# Log to file
gitco --debug --log-file debug.log sync

# Detailed logging
gitco --debug --detailed-log sync

# Export debug information
gitco --debug --export debug-info.json sync
```

### Performance Profiling

**Profile GitCo operations:**

```bash
# Check performance metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json

# Monitor system resources
top -p $(pgrep -f gitco)

# Check disk I/O
iotop -p $(pgrep -f gitco)
```

### Network Diagnostics

**Diagnose network issues:**

```bash
# Check GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Check OpenAI API
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check DNS resolution
nslookup api.github.com
nslookup api.openai.com

# Check connectivity
ping api.github.com
ping api.openai.com
```

### Log Analysis

**Analyze GitCo logs:**

```bash
# View recent logs
tail -n 100 ~/.gitco/gitco.log

# Search for errors
grep -i error ~/.gitco/gitco.log

# Search for specific operations
grep -i sync ~/.gitco/gitco.log

# Export logs for analysis
gitco logs --export logs.json
```

### System Resource Monitoring

**Monitor system resources during operations:**

```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h
du -sh ~/code/*

# Monitor network
iftop

# Monitor processes
ps aux | grep gitco
```

This troubleshooting guide covers the most common issues you might encounter with GitCo. For additional help, check the [FAQ](faq.md) or report issues through the appropriate channels.
