# GitCo Troubleshooting Guide

This guide helps you resolve common issues with GitCo and provides diagnostic commands for troubleshooting.

## Table of Contents

1. [Quick Diagnostic Commands](#quick-diagnostic-commands)
2. [Installation Problems](#installation-problems)
3. [Configuration Issues](#configuration-issues)
4. [Git Operations Issues](#git-operations-issues)
5. [API and Network Issues](#api-and-network-issues)
6. [Analysis and Discovery Issues](#analysis-and-discovery-issues)
7. [Performance Issues](#performance-issues)
8. [Cost Management Issues](#cost-management-issues)
9. [Backup and Recovery Issues](#backup-and-recovery-issues)
10. [Advanced Troubleshooting](#advanced-troubleshooting)

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

# Test GitHub connection
gitco github test-connection

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

## Installation Problems

### Command Not Found

**Symptoms:** `gitco: command not found`

**Solutions:**

```bash
# Reinstall GitCo
pip install --force-reinstall gitco

# Add pip user bin to PATH
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Use pipx for isolated installation
pipx install gitco

# Check installation location
which gitco
pip show gitco
```

### Import Errors

**Symptoms:** `ModuleNotFoundError` or `ImportError`

**Solutions:**

```bash
# Install dependencies
pip install -r requirements.txt

# Check Python version (requires 3.9+)
python --version

# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install gitco

# Upgrade pip
pip install --upgrade pip
pip install --force-reinstall gitco
```

### Permission Errors

**Symptoms:** Permission denied errors during installation

**Solutions:**

```bash
# Install for current user only
pip install --user gitco

# Fix permissions
sudo chown -R $USER:$USER ~/.local/bin
chmod +x ~/.local/bin/gitco

# Use virtual environment
python -m venv ~/gitco-env
source ~/gitco-env/bin/activate
pip install gitco
```

---

## Configuration Issues

### Invalid YAML Syntax

**Symptoms:** YAML parsing errors

**Solutions:**

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('~/.gitco/config.yml'))"

# Convert tabs to spaces
expand -t 2 ~/.gitco/config.yml > ~/.gitco/config.yml.tmp
mv ~/.gitco/config.yml.tmp ~/.gitco/config.yml

# Check for hidden characters
cat -A ~/.gitco/config.yml

# Use GitCo validation
gitco config validate
```

### Missing Required Fields

**Symptoms:** Configuration validation errors

**Solutions:**

```bash
# Run detailed validation
gitco config validate-detailed --detailed

# Check required fields
gitco config validate-detailed --export validation-report.json

# Recreate configuration
gitco init --force
```

### Repository Not Found

**Symptoms:** Repository path errors or missing repositories

**Solutions:**

```bash
# Check if paths exist
ls -la ~/code/django

# Check repository status
cd ~/code/django && git status

# Clone missing repositories
git clone https://github.com/username/django.git ~/code/django

# Validate repository
gitco validate-repo --path ~/code/django
```

### Invalid URLs

**Symptoms:** URL validation errors

**Solutions:**

```bash
# Check URL format
gitco config validate

# Use proper URL format
# ✅ Correct: https://github.com/username/repo
# ❌ Incorrect: github.com/username/repo

# Test URL accessibility
curl -I https://github.com/username/repo
```

---

## Git Operations Issues

### Permission Denied

**Symptoms:** Permission errors during Git operations

**Solutions:**

```bash
# Fix repository permissions
chmod -R 755 ~/code/django

# Check Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Fix SSH keys
ssh-add ~/.ssh/id_rsa
ssh -T git@github.com
```

### Merge Conflicts

**Symptoms:** Merge conflict errors during sync

**Solutions:**

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

### Upstream Remote Issues

**Symptoms:** Upstream remote not found or invalid

**Solutions:**

```bash
# Check upstream configuration
gitco upstream validate --repo django

# Add upstream remote
gitco upstream add --repo django --url https://github.com/django/django.git

# Update upstream URL
gitco upstream update --repo django --url https://github.com/new/django.git

# Remove and re-add upstream
gitco upstream remove --repo django
gitco upstream add --repo django --url https://github.com/django/django.git
```

### Stash Issues

**Symptoms:** Stash conflicts or failed stash operations

**Solutions:**

```bash
# Check stash status
cd ~/code/django
git stash list

# Apply specific stash
git stash apply stash@{0}

# Drop problematic stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

---

## API and Network Issues

### Missing API Keys

**Symptoms:** API authentication errors

**Solutions:**

```bash
# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GITHUB_TOKEN="your-github-token"

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user

# Check environment variables
env | grep -E "(OPENAI|ANTHROPIC|GITHUB)_API_KEY"
```

### Rate Limit Exceeded

**Symptoms:** Rate limit errors from APIs

**Solutions:**

```bash
# Check rate limit status
gitco github rate-limit-status --detailed

# Wait for rate limit reset
gitco github rate-limit-status

# Reduce request frequency
# Edit config.yml to increase delays
rate_limit_delay: 2.0
min_request_interval: 0.5
```

### Network Timeout

**Symptoms:** Connection timeout errors

**Solutions:**

```bash
# Increase timeout values
# Edit config.yml
github_timeout: 60
git_timeout: 600

# Check network connectivity
ping api.github.com
ping api.openai.com

# Use proxy if needed
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"
```

### GitHub API Issues

**Symptoms:** GitHub API errors or authentication failures

**Solutions:**

```bash
# Test GitHub connection
gitco github test-connection

# Check token permissions
curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user

# Regenerate token with proper permissions
# Go to GitHub Settings > Developer settings > Personal access tokens

# Test specific repository access
gitco github get-repo --repo django/django
```

---

## Analysis and Discovery Issues

### LLM API Errors

**Symptoms:** Analysis failures or LLM API errors

**Solutions:**

```bash
# Test LLM provider
gitco analyze --repo django --provider openai

# Check API key
echo $OPENAI_API_KEY

# Test API directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}' \
     https://api.openai.com/v1/chat/completions

# Switch providers
gitco analyze --repo django --provider anthropic
```

### Discovery Failures

**Symptoms:** Discovery command fails or returns no results

**Solutions:**

```bash
# Check GitHub connection
gitco github test-connection

# Test discovery with different filters
gitco discover --skill python
gitco discover --label "good first issue"
gitco discover --min-confidence 0.1

# Check rate limits
gitco github rate-limit-status

# Enable debug mode
gitco --debug discover
```

### Cost Limit Exceeded

**Symptoms:** Cost limit errors during analysis

**Solutions:**

```bash
# Check cost usage
gitco cost summary --detailed

# Reset cost limits
gitco cost configure --daily-limit 10.0 --monthly-limit 100.0

# Disable cost tracking temporarily
gitco cost configure --disable-tracking

# Reset cost history
gitco cost reset --force
```

---

## Performance Issues

### Slow Operations

**Symptoms:** Commands take too long to complete

**Solutions:**

```bash
# Check performance metrics
gitco performance --detailed

# Reduce batch size
# Edit config.yml
max_repos_per_batch: 2

# Increase timeouts
git_timeout: 600
github_timeout: 60

# Use quiet mode for automation
gitco --quiet sync --batch
```

### Memory Issues

**Symptoms:** Out of memory errors or high memory usage

**Solutions:**

```bash
# Check system resources
free -h
top

# Reduce concurrent operations
max_repos_per_batch: 1

# Clear caches
gitco cost reset --force

# Use smaller models
# Edit config.yml to use smaller LLM models
```

### High CPU Usage

**Symptoms:** Excessive CPU usage during operations

**Solutions:**

```bash
# Monitor CPU usage
htop

# Reduce concurrent workers
max_repos_per_batch: 1

# Use quiet mode
gitco --quiet sync

# Check for background processes
ps aux | grep gitco
```

---

## Cost Management Issues

### Unexpected Costs

**Symptoms:** Higher than expected API costs

**Solutions:**

```bash
# Check cost breakdown
gitco cost breakdown --detailed

# Set stricter limits
gitco cost configure --daily-limit 2.0 --monthly-limit 20.0

# Enable token optimization
gitco cost configure --enable-optimization

# Reduce token limits
gitco cost configure --max-tokens 2000
```

### Cost Tracking Disabled

**Symptoms:** Cost tracking not working

**Solutions:**

```bash
# Enable cost tracking
gitco cost configure --enable-tracking

# Check cost log file
ls -la ~/.gitco/cost_log.json

# Reset cost tracking
gitco cost reset --force

# Check configuration
gitco config validate
```

### Cost Export Issues

**Symptoms:** Cost export fails or returns empty data

**Solutions:**

```bash
# Export cost data
gitco cost summary --export costs.json

# Check export format
gitco cost summary --export costs.csv

# Verify file permissions
ls -la costs.json

# Check file content
cat costs.json
```

---

## Backup and Recovery Issues

### Backup Creation Fails

**Symptoms:** Backup creation errors

**Solutions:**

```bash
# Check disk space
df -h

# Use smaller backup type
gitco backup create --type config-only

# Exclude git history
gitco backup create --no-git-history

# Check permissions
ls -la ~/.gitco/

# Use different compression
gitco backup create --compression 1
```

### Backup Restoration Fails

**Symptoms:** Backup restoration errors

**Solutions:**

```bash
# Validate backup
gitco backup validate --backup-id backup-id

# List available backups
gitco backup list --detailed

# Restore to different location
gitco backup restore --backup-id backup-id --target-dir ~/restored

# Overwrite existing files
gitco backup restore --backup-id backup-id --overwrite
```

### Backup Corruption

**Symptoms:** Backup validation fails

**Solutions:**

```bash
# Validate backup integrity
gitco backup validate --backup-id backup-id

# Delete corrupted backup
gitco backup delete --backup-id backup-id --force

# Create new backup
gitco backup create --type full --description "Replacement backup"
```

---

## Advanced Troubleshooting

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Enable debug logging
gitco --debug --detailed-log sync

# Debug specific command
gitco --debug analyze --repo django

# Export debug logs
gitco --debug --log-file debug.log sync
```

### Verbose Output

Get detailed output for troubleshooting:

```bash
# Verbose mode
gitco --verbose sync

# Detailed validation
gitco config validate-detailed --detailed

# Detailed status
gitco status --detailed
```

### Log Analysis

Analyze logs for issues:

```bash
# View logs
gitco logs --export logs.json

# Check log file
tail -f ~/.gitco/gitco.log

# Analyze performance logs
gitco performance --export performance.json
```

### Network Diagnostics

Diagnose network connectivity issues:

```bash
# Test API endpoints
curl -I https://api.github.com
curl -I https://api.openai.com

# Check DNS resolution
nslookup api.github.com
nslookup api.openai.com

# Test with different network
# Try from different network or VPN
```

### Configuration Reset

Reset configuration to defaults:

```bash
# Backup current config
cp ~/.gitco/config.yml ~/.gitco/config.yml.backup

# Reinitialize configuration
gitco init --force

# Restore specific settings
# Manually edit ~/.gitco/config.yml
```

### Environment Issues

Resolve environment-related issues:

```bash
# Check Python environment
which python
python --version
pip list

# Use virtual environment
python -m venv gitco-env
source gitco-env/bin/activate
pip install gitco

# Check system dependencies
git --version
curl --version
```

---

## Getting Help

### Self-Service Resources

```bash
# Comprehensive help
gitco help

# Command-specific help
gitco sync --help
gitco analyze --help
gitco discover --help

# Configuration help
gitco config --help
```

### Diagnostic Information

When reporting issues, include:

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

### Community Support

- **GitHub Issues:** Report bugs and feature requests
- **Documentation:** Check the [CLI Reference](cli.md) and [FAQ](faq.md)
- **Configuration Guide:** Review [Configuration Guide](configuration.md)
- **Usage Examples:** See [Usage Guide](usage.md)

This comprehensive troubleshooting guide covers the most common issues and provides practical solutions for resolving GitCo problems. For additional help, refer to the specific documentation sections or report issues through the appropriate channels.
