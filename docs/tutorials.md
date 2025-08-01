# GitCo Tutorials

This guide provides comprehensive tutorials and examples for using GitCo effectively. Each tutorial includes step-by-step instructions, real-world scenarios, and best practices.

## Table of Contents

1. [Getting Started Tutorial](#getting-started-tutorial)
2. [Repository Management Tutorial](#repository-management-tutorial)
3. [AI-Powered Analysis Tutorial](#ai-powered-analysis-tutorial)
4. [Contribution Discovery Tutorial](#contribution-discovery-tutorial)
5. [Advanced Workflows](#advanced-workflows)
6. [Automation Tutorial](#automation-tutorial)
7. [Troubleshooting Tutorial](#troubleshooting-tutorial)

---

## Getting Started Tutorial

### Prerequisites

Before starting, ensure you have:
- Python 3.9+ installed
- Git installed and configured
- GitHub account with access to repositories
- LLM API key (OpenAI or Anthropic)

### Step 1: Installation

```bash
# Install GitCo
pip install gitco

# Verify installation
gitco --version
```

### Step 2: Initial Setup

```bash
# Start interactive setup
gitco init --interactive
```

The interactive setup will guide you through:

1. **Repository Configuration**
   ```
   Enter repository name: django
   Enter fork URL: https://github.com/yourusername/django
   Enter upstream URL: https://github.com/django/django
   Enter local path: ~/code/django
   Enter skills (comma-separated): python, web, orm
   ```

2. **LLM Provider Setup**
   ```
   Select LLM provider: openai
   Enter API key environment variable: OPENAI_API_KEY
   ```

3. **GitHub Integration**
   ```
   Enter GitHub username: yourusername
   Enter GitHub token environment variable: GITHUB_TOKEN
   ```

### Step 3: Environment Setup

Create a `.env` file in your project directory:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key-here
GITHUB_TOKEN=your-github-token-here
```

Or set environment variables:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export GITHUB_TOKEN="your-github-token-here"
```

### Step 4: First Sync

```bash
# Sync your first repository
gitco sync --repo django

# Expected output:
# ✅ Successfully synced repository: django
# 📦 Uncommitted changes were stashed and restored
```

### Step 5: Verify Configuration

```bash
# Validate your configuration
gitco config validate

# Check configuration status
gitco config status
```

---

## Repository Management Tutorial

### Managing Multiple Repositories

#### Adding New Repositories

Edit your configuration file (`~/.gitco/config.yml`):

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

  - name: requests
    fork: username/requests
    upstream: psf/requests
    local_path: ~/code/requests
    skills: [python, http, networking]
```

#### Batch Synchronization

```bash
# Sync all repositories
gitco sync --batch

# Sync with parallel processing
gitco sync --batch --max-workers 4

# Sync with analysis
gitco sync --batch --analyze
```

#### Individual Repository Management

```bash
# Sync specific repository
gitco sync --repo django

# Check repository status
gitco status --repo django

# View repository activity
gitco activity --repo django --detailed
```

### Repository Health Monitoring

#### Health Dashboard

```bash
# Overview of all repositories
gitco status --overview

# Detailed health information
gitco status --detailed

# Filter by health status
gitco status --filter healthy
gitco status --filter needs_attention
gitco status --filter critical
```

#### Activity Monitoring

```bash
# Activity dashboard
gitco activity --detailed

# Filter by activity level
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low

# Sort by activity metrics
gitco activity --sort activity
gitco activity --sort engagement
```

### Example: Managing a Python Ecosystem

```bash
# 1. Add Python repositories
gitco init --interactive
# Add: django, fastapi, requests, pytest, black

# 2. Sync all repositories
gitco sync --batch --analyze

# 3. Check health status
gitco status --overview

# 4. Monitor activity
gitco activity --detailed

# 5. Export status report
gitco status --export python-ecosystem-status.json
```

---

## AI-Powered Analysis Tutorial

### Basic Analysis

#### Single Repository Analysis

```bash
# Analyze changes in a repository
gitco analyze --repo django

# Expected output:
# 🤖 AI Analysis for django
# 📊 Summary: Added new middleware support and improved ORM performance
# ⚠️  Breaking Changes: Deprecated old middleware API
# ✨ New Features: Added async ORM support
# 🐛 Bug Fixes: Fixed memory leak in query builder
# 🔒 Security: Updated dependencies for CVE-2023-1234
```

#### Custom Analysis Prompts

```bash
# Focus on security changes
gitco analyze --repo django --prompt "Focus on security updates and vulnerabilities"

# Focus on performance improvements
gitco analyze --repo fastapi --prompt "Analyze performance improvements and optimizations"

# Focus on API changes
gitco analyze --repo requests --prompt "Identify API breaking changes and new endpoints"
```

#### Multi-Repository Analysis

```bash
# Analyze multiple repositories
gitco analyze --repos django,fastapi,requests

# Export analysis results
gitco analyze --repo django --export analysis-report.json
```

### Advanced Analysis Features

#### Provider-Specific Analysis

```bash
# Use OpenAI GPT-4
gitco analyze --repo django --provider openai

# Use Anthropic Claude
gitco analyze --repo fastapi --provider anthropic
```

#### Analysis with Context

```bash
# Analyze with custom context
gitco analyze --repo django --prompt "Focus on changes that affect my Django application's authentication system"
```

### Example: Analyzing a Major Release

```bash
# 1. Sync repository to get latest changes
gitco sync --repo django

# 2. Analyze the changes
gitco analyze --repo django --prompt "Focus on breaking changes and migration requirements"

# 3. Export detailed analysis
gitco analyze --repo django --export django-4.2-analysis.json

# 4. Review the analysis
cat django-4.2-analysis.json | jq '.breaking_changes'
```

---

## Contribution Discovery Tutorial

### Basic Discovery

#### Finding Opportunities

```bash
# Find all opportunities
gitco discover

# Find Python-specific opportunities
gitco discover --skill python

# Find beginner-friendly issues
gitco discover --label "good first issue"

# Find high-priority issues
gitco discover --label "high priority"
```

#### Filtered Discovery

```bash
# Find opportunities matching multiple criteria
gitco discover --skill python --label "bug"

# Find opportunities in specific repositories
gitco discover --skill python --limit 10

# Find opportunities with minimum confidence
gitco discover --min-confidence 0.7
```

### Personalized Discovery

#### Contribution History Analysis

```bash
# Sync your contribution history
gitco contributions sync-history --username yourusername

# View contribution statistics
gitco contributions stats

# Get personalized recommendations
gitco discover --personalized

# Show contribution history
gitco discover --show-history
```

#### Skill-Based Matching

```bash
# Find opportunities matching your skills
gitco discover --skill python,api

# Find opportunities for skill development
gitco discover --skill javascript --min-confidence 0.3
```

### Example: Finding Your Next Contribution

```bash
# 1. Sync your contribution history
gitco contributions sync-history --username yourusername

# 2. Find personalized opportunities
gitco discover --personalized --limit 5

# 3. Export opportunities for review
gitco discover --personalized --export opportunities.json

# 4. Review trending analysis
gitco contributions trending --days 30
```

---

## Advanced Workflows

### Daily Maintenance Workflow

```bash
#!/bin/bash
# daily-maintenance.sh

echo "🔄 Starting daily GitCo maintenance..."

# 1. Sync all repositories
echo "📦 Syncing repositories..."
gitco sync --batch --quiet --log daily-sync.log

# 2. Check repository health
echo "🏥 Checking repository health..."
gitco status --overview --quiet

# 3. Find new opportunities
echo "🔍 Discovering opportunities..."
gitco discover --limit 3 --quiet

# 4. Generate daily report
echo "📊 Generating daily report..."
gitco status --export daily-report-$(date +%Y%m%d).json

echo "✅ Daily maintenance completed!"
```

### Weekly Review Workflow

```bash
#!/bin/bash
# weekly-review.sh

echo "📅 Starting weekly GitCo review..."

# 1. Full sync with analysis
echo "🤖 Syncing with AI analysis..."
gitco sync --batch --analyze --export weekly-sync.json

# 2. Activity analysis
echo "📈 Analyzing activity patterns..."
gitco activity --detailed --export weekly-activity.json

# 3. Contribution statistics
echo "📊 Generating contribution stats..."
gitco contributions stats --days 7 --export weekly-stats.json

# 4. Trending analysis
echo "📈 Analyzing trends..."
gitco contributions trending --days 7 --export weekly-trends.json

echo "✅ Weekly review completed!"
```

### Monthly Analysis Workflow

```bash
#!/bin/bash
# monthly-analysis.sh

echo "📊 Starting monthly GitCo analysis..."

# 1. Comprehensive health check
echo "🏥 Comprehensive health check..."
gitco status --detailed --export monthly-health.json

# 2. Activity dashboard
echo "📈 Activity dashboard..."
gitco activity --detailed --export monthly-activity.json

# 3. Contribution analysis
echo "📊 Contribution analysis..."
gitco contributions stats --days 30 --export monthly-contributions.json

# 4. Trending analysis
echo "📈 Trending analysis..."
gitco contributions trending --days 30 --export monthly-trends.json

# 5. Create backup
echo "💾 Creating backup..."
gitco backup create --type full --description "Monthly backup"

echo "✅ Monthly analysis completed!"
```

---

## Automation Tutorial

### Cron Job Setup

#### Daily Sync

Add to your crontab (`crontab -e`):

```bash
# Sync repositories every 6 hours
0 */6 * * * /usr/bin/gitco sync --batch --quiet --log /var/log/gitco/sync.log

# Daily health check at 9 AM
0 9 * * * /usr/bin/gitco status --overview --quiet --export /var/log/gitco/daily-status.json

# Weekly analysis on Sundays at 10 AM
0 10 * * 0 /usr/bin/gitco sync --batch --analyze --export /var/log/gitco/weekly-analysis.json
```

#### GitHub Actions Workflow

Create `.github/workflows/gitco-maintenance.yml`:

```yaml
name: GitCo Maintenance

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM
  workflow_dispatch:  # Manual trigger

jobs:
  gitco-sync:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install GitCo
      run: |
        pip install gitco

    - name: Setup environment
      run: |
        echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> $GITHUB_ENV
        echo "GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}" >> $GITHUB_ENV

    - name: Sync repositories
      run: |
        gitco sync --batch --quiet --export sync-results.json

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: gitco-sync-results
        path: sync-results.json
```

### Manual Systemd Service Setup

**Note**: GitCo does not provide built-in service installation. You can create systemd service files manually for automated execution.

Create `/etc/systemd/system/gitco.service`:

```ini
[Unit]
Description=GitCo Repository Sync Service
After=network.target

[Service]
Type=oneshot
User=yourusername
Environment=OPENAI_API_KEY=your-api-key
Environment=GITHUB_TOKEN=your-github-token
ExecStart=/usr/bin/gitco sync --batch --quiet --log /var/log/gitco/sync.log
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/gitco.timer`:

```ini
[Unit]
Description=Run GitCo sync every 6 hours
Requires=gitco.service

[Timer]
OnCalendar=*-*-* 00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start the service:

```bash
sudo systemctl enable gitco.timer
sudo systemctl start gitco.timer
sudo systemctl status gitco.timer
```

**Alternative**: Use cron jobs (see above) for simpler automation without systemd.

---

## Troubleshooting Tutorial

### Common Issues and Solutions

#### Configuration Issues

**Problem**: Configuration validation fails
```bash
$ gitco config validate
❌ Configuration has 3 error(s)
```

**Solution**:
```bash
# Check configuration file
cat ~/.gitco/config.yml

# Fix common issues:
# 1. Ensure all required fields are present
# 2. Validate repository URLs
# 3. Check local paths exist
# 4. Verify API keys are set

# Re-validate
gitco config validate
```

#### Git Operation Issues

**Problem**: Sync fails with git errors
```bash
$ gitco sync --repo django
❌ Failed to sync repository 'django': Git operation failed
```

**Solution**:
```bash
# Check repository status
cd ~/code/django
git status

# Resolve conflicts manually
git merge --abort
git reset --hard HEAD
git clean -fd

# Try sync again
gitco sync --repo django
```

#### API Rate Limiting

**Problem**: GitHub API rate limit exceeded
```bash
$ gitco discover
❌ GitHub API rate limit exceeded
```

**Solution**:
```bash
# Check rate limit status
gitco github rate-limit-status

# Wait for rate limit reset
# Or use GitHub token with higher limits

# Retry with exponential backoff
gitco discover --min-confidence 0.1
```

#### LLM API Issues

**Problem**: LLM analysis fails
```bash
$ gitco analyze --repo django
❌ LLM API error: Invalid API key
```

**Solution**:
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Update API key if needed
export OPENAI_API_KEY="new-api-key"
```

### Debug Mode

Enable verbose logging for debugging:

```bash
# Enable verbose output
gitco sync --verbose

# Enable detailed logging
gitco sync --detailed-log --log-file debug.log

# Check log file
tail -f debug.log
```

### Recovery Procedures

#### Repository Recovery

```bash
# 1. Check repository status
gitco status --repo problematic-repo

# 2. Backup current state
gitco backup create --repos ~/code/problematic-repo

# 3. Reset repository
cd ~/code/problematic-repo
git reset --hard HEAD
git clean -fd

# 4. Re-sync
gitco sync --repo problematic-repo
```

#### Configuration Recovery

```bash
# 1. Backup current configuration
cp ~/.gitco/config.yml ~/.gitco/config.yml.backup

# 2. Reinitialize configuration
gitco init --force

# 3. Restore repositories from backup
# Edit ~/.gitco/config.yml to add your repositories back
```

### Performance Optimization

#### Batch Processing Optimization

```bash
# Use optimal worker count
gitco sync --batch --max-workers 4

# Monitor system resources
htop

# Adjust based on system capabilities
gitco sync --batch --max-workers 2  # For slower systems
```

#### API Usage Optimization

```bash
# Use cost optimization
gitco cost configure --enable-optimization

# Set cost limits
gitco cost configure --daily-limit 5.0

# Monitor costs
gitco cost summary
```

---

## Best Practices

### Repository Organization

1. **Use Consistent Naming**: Use descriptive repository names
2. **Group by Technology**: Organize repositories by programming language or framework
3. **Tag with Skills**: Add relevant skills to each repository for better discovery
4. **Regular Maintenance**: Sync repositories regularly to avoid large changes

### Configuration Management

1. **Version Control**: Keep your configuration file in version control
2. **Environment Variables**: Use environment variables for sensitive data
3. **Regular Validation**: Run configuration validation regularly
4. **Backup Configuration**: Create backups of your configuration

### Automation Best Practices

1. **Start Small**: Begin with a few repositories and expand gradually
2. **Monitor Logs**: Check logs regularly for issues
3. **Set Up Alerts**: Configure alerts for sync failures
4. **Regular Backups**: Create regular backups of your repositories
5. **Cost Monitoring**: Monitor API usage costs

### Contribution Workflow

1. **Regular Discovery**: Run discovery regularly to find new opportunities
2. **Skill Development**: Use discovery to identify skill development opportunities
3. **Track Progress**: Use contribution tracking to monitor your progress
4. **Export Data**: Export data for external analysis and reporting

### Security Best Practices

1. **Secure API Keys**: Store API keys securely and rotate them regularly
2. **Access Control**: Use GitHub tokens with minimal required permissions
3. **Audit Logs**: Review logs regularly for suspicious activity
4. **Backup Security**: Secure your backup files and configurations

---

## Advanced Examples

### Multi-Repository Ecosystem Management

```bash
#!/bin/bash
# manage-python-ecosystem.sh

# Define Python ecosystem repositories
repos=("django" "fastapi" "requests" "pytest" "black" "flake8")

echo "🐍 Managing Python ecosystem..."

# Sync all repositories
for repo in "${repos[@]}"; do
    echo "📦 Syncing $repo..."
    gitco sync --repo $repo --quiet
done

# Analyze changes
echo "🤖 Analyzing changes..."
gitco sync --batch --analyze --export python-ecosystem-analysis.json

# Find opportunities
echo "🔍 Finding opportunities..."
gitco discover --skill python --limit 10 --export python-opportunities.json

# Generate ecosystem report
echo "📊 Generating ecosystem report..."
gitco status --overview --export python-ecosystem-status.json

echo "✅ Python ecosystem management completed!"
```

### Cross-Platform Development Workflow

```bash
#!/bin/bash
# cross-platform-workflow.sh

echo "🔄 Cross-platform development workflow..."

# Sync repositories for different platforms
platforms=("web" "mobile" "desktop" "api")

for platform in "${platforms[@]}"; do
    echo "📱 Managing $platform repositories..."

    # Sync platform-specific repositories
    gitco sync --batch --quiet

    # Analyze platform-specific changes
    gitco analyze --repos $(gitco config status | grep $platform | awk '{print $1}' | tr '\n' ',')

    # Find platform-specific opportunities
    gitco discover --skill $platform --limit 5
done

# Generate cross-platform report
gitco status --overview --export cross-platform-status.json

echo "✅ Cross-platform workflow completed!"
```

### Open Source Maintainer Workflow

```bash
#!/bin/bash
# maintainer-workflow.sh

echo "👨‍💻 Open source maintainer workflow..."

# 1. Sync all maintained repositories
echo "📦 Syncing maintained repositories..."
gitco sync --batch --analyze

# 2. Check repository health
echo "🏥 Checking repository health..."
gitco status --detailed

# 3. Find issues to address
echo "🔍 Finding issues to address..."
gitco discover --label "bug" --limit 20

# 4. Monitor community activity
echo "👥 Monitoring community activity..."
gitco activity --detailed

# 5. Generate maintainer report
echo "📊 Generating maintainer report..."
gitco status --export maintainer-report.json
gitco activity --export maintainer-activity.json

echo "✅ Maintainer workflow completed!"
```

This comprehensive tutorial guide provides step-by-step instructions for all major GitCo workflows, from basic setup to advanced automation. Each tutorial includes real-world examples and best practices to help users get the most out of GitCo.
