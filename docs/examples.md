# GitCo Examples

This guide provides comprehensive examples and real-world scenarios for using GitCo effectively. Each example includes complete code snippets, expected outputs, and practical use cases.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Configuration Examples](#configuration-examples)
3. [Workflow Examples](#workflow-examples)
4. [Automation Examples](#automation-examples)
5. [Integration Examples](#integration-examples)
6. [Advanced Examples](#advanced-examples)

---

## Basic Examples

### Example 1: First-Time Setup

**Scenario**: Setting up GitCo for the first time with a Python project.

```bash
# 1. Install GitCo
pip install gitco

# 2. Initialize with interactive setup
gitco init --interactive

# Interactive prompts:
# Repository name: django
# Fork URL: https://github.com/yourusername/django
# Upstream URL: https://github.com/django/django
# Local path: ~/code/django
# Skills: python, web, orm

# 3. Set environment variables
export OPENAI_API_KEY="sk-your-openai-key"
export GITHUB_TOKEN="ghp-your-github-token"

# 4. First sync
gitco sync --repo django

# Expected output:
# ✅ Successfully synced repository: django
# 📦 Uncommitted changes were stashed and restored
```

### Example 2: Multi-Repository Setup

**Scenario**: Managing multiple repositories in different programming languages.

```yaml
# ~/.gitco/config.yml
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

  - name: react
    fork: username/react
    upstream: facebook/react
    local_path: ~/code/react
    skills: [javascript, react, frontend]

  - name: vue
    fork: username/vue
    upstream: vuejs/vue
    local_path: ~/code/vue
    skills: [javascript, vue, frontend]

settings:
  llm_provider: openai
  api_key_env: OPENAI_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

```bash
# Sync all repositories
gitco sync --batch

# Expected output:
# ✅ Successfully synced all 4 repositories!
# All repositories are now up to date with their upstream sources.
```

### Example 3: AI-Powered Analysis

**Scenario**: Analyzing changes in a repository with AI insights.

```bash
# Analyze a specific repository
gitco analyze --repo django

# Expected output:
# 🤖 AI Analysis for django
#
# 📊 Summary:
# This update introduces significant improvements to Django's ORM performance
# and adds new middleware capabilities. The changes include both new features
# and breaking changes that require attention.
#
# ⚠️  Breaking Changes:
# - Deprecated old middleware API in favor of new async-compatible interface
# - Changed default behavior of QuerySet.filter() to be more strict
# - Removed support for Python 3.8
#
# ✨ New Features:
# - Added async ORM support with new async/await syntax
# - Introduced new middleware system with better performance
# - Added support for database connection pooling
#
# 🐛 Bug Fixes:
# - Fixed memory leak in query builder
# - Resolved issue with database connection timeouts
# - Fixed race condition in middleware processing
#
# 🔒 Security Updates:
# - Updated dependencies to address CVE-2023-1234
# - Enhanced input validation in form processing
# - Improved CSRF protection mechanisms
#
# 💡 Recommendations:
# - Update your middleware implementations to use the new API
# - Review and update any custom QuerySet methods
# - Test thoroughly with your existing codebase
# - Consider upgrading Python version if still using 3.8
```

### Example 4: Contribution Discovery

**Scenario**: Finding contribution opportunities based on skills and interests.

```bash
# Find Python opportunities
gitco discover --skill python --limit 5

# Expected output:
# 🎯 Found 5 contribution opportunities!
#
# Recommendation #1
# ┌─────────────────────────────────────────────────────────────┐
# │ #1234: Add async support to middleware system             │
# │ 🔗 https://github.com/django/django/issues/1234          │
# │ 📁 Repository: django                                     │
# │ 💻 Language: Python                                       │
# │ 🎯 Excellent Match | Score: 0.85 | 🎯 Intermediate | ⏱️ Medium │
# │ 🎯 Skill Matches:                                          │
# │   🎯 python (95%) [exact]                                 │
# │   📝 async (78%) [partial]                                │
# │   🔗 middleware (82%) [related]                           │
# └─────────────────────────────────────────────────────────────┘
#
# Recommendation #2
# ┌─────────────────────────────────────────────────────────────┐
# │ #5678: Improve API documentation                          │
# │ 🔗 https://github.com/fastapi/fastapi/issues/5678       │
# │ 📁 Repository: fastapi                                    │
# │ 💻 Language: Python                                       │
# │ ⭐ Good Match | Score: 0.72 | 🎯 Beginner | ⏱️ Quick    │
# │ 🎯 Skill Matches:                                          │
# │   🎯 python (88%) [exact]                                 │
# │   📝 api (75%) [partial]                                  │
# │   📝 documentation (70%) [related]                        │
# └─────────────────────────────────────────────────────────────┘
```

---

## Configuration Examples

### Example 1: Minimal Configuration

**Scenario**: Simple setup for a single repository.

```yaml
# ~/.gitco/config.yml
repositories:
  - name: my-project
    fork: username/my-project
    upstream: original/my-project
    local_path: ~/code/my-project
    skills: [python]

settings:
  llm_provider: openai
  api_key_env: OPENAI_API_KEY
  analysis_enabled: true
```

### Example 2: Advanced Configuration

**Scenario**: Comprehensive setup with multiple providers and advanced settings.

```yaml
# ~/.gitco/config.yml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]
    analysis_enabled: true

  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async]
    analysis_enabled: true

  - name: react
    fork: username/react
    upstream: facebook/react
    local_path: ~/code/react
    skills: [javascript, react, frontend]
    analysis_enabled: false  # Disable analysis for this repo

settings:
  # LLM Configuration
  llm_provider: openai
  api_key_env: OPENAI_API_KEY
  fallback_provider: anthropic
  fallback_api_key_env: ANTHROPIC_API_KEY

  # GitHub Configuration
  github_api_url: https://api.github.com
  github_token_env: GITHUB_TOKEN
  github_username: yourusername

  # Path Configuration
  default_path: ~/code
  backup_path: ~/.gitco/backups

  # Processing Configuration
  max_repos_per_batch: 8
  git_timeout: 300
  api_timeout: 60

  # Analysis Configuration
  analysis_enabled: true
  analysis_confidence_threshold: 0.7
  max_analysis_tokens: 4000

  # Discovery Configuration
  discovery_max_results: 20
  discovery_min_confidence: 0.3
  discovery_cache_duration: 3600

  # Logging Configuration
  log_level: INFO
  log_file: ~/.gitco/gitco.log
  max_log_size: 10  # MB
  log_backups: 5
```

### Example 3: Environment-Specific Configuration

**Scenario**: Different configurations for development and production.

```yaml
# ~/.gitco/config-dev.yml (Development)
repositories:
  - name: django-dev
    fork: username/django
    upstream: django/django
    local_path: ~/code/django-dev
    skills: [python, web, orm]

settings:
  llm_provider: openai
  api_key_env: OPENAI_API_KEY_DEV
  analysis_enabled: true
  max_repos_per_batch: 2
  log_level: DEBUG
```

```yaml
# ~/.gitco/config-prod.yml (Production)
repositories:
  - name: django-prod
    fork: username/django
    upstream: django/django
    local_path: ~/code/django-prod
    skills: [python, web, orm]

settings:
  llm_provider: anthropic
  api_key_env: ANTHROPIC_API_KEY_PROD
  analysis_enabled: true
  max_repos_per_batch: 10
  log_level: WARNING
```

```bash
# Use different configurations
gitco --config ~/.gitco/config-dev.yml sync
gitco --config ~/.gitco/config-prod.yml sync
```

---

## Workflow Examples

### Example 1: Daily Development Workflow

**Scenario**: Daily routine for a developer maintaining multiple forks.

```bash
#!/bin/bash
# daily-workflow.sh

echo "🔄 Starting daily GitCo workflow..."

# 1. Quick sync of all repositories
echo "📦 Syncing repositories..."
gitco sync --batch --quiet

# 2. Check for any issues
echo "🏥 Checking repository health..."
gitco status --overview

# 3. Find new opportunities
echo "🔍 Discovering opportunities..."
gitco discover --limit 3

# 4. Generate daily report
echo "📊 Generating daily report..."
gitco status --export daily-report-$(date +%Y%m%d).json

echo "✅ Daily workflow completed!"
```

### Example 2: Weekly Review Workflow

**Scenario**: Comprehensive weekly review of all repositories.

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

# 5. Create backup
echo "💾 Creating backup..."
gitco backup create --type full --description "Weekly backup"

echo "✅ Weekly review completed!"
```

### Example 3: Release Preparation Workflow

**Scenario**: Preparing for a major release by analyzing all changes.

```bash
#!/bin/bash
# release-prep.sh

RELEASE_VERSION="4.2.0"
REPOSITORIES="django,fastapi,requests"

echo "🚀 Preparing for release $RELEASE_VERSION..."

# 1. Sync all repositories
echo "📦 Syncing repositories..."
gitco sync --batch

# 2. Analyze changes in each repository
echo "🤖 Analyzing changes..."
for repo in ${REPOSITORIES//,/ }; do
    echo "Analyzing $repo..."
    gitco analyze --repo $repo --export ${repo}-${RELEASE_VERSION}-analysis.json
done

# 3. Generate release notes
echo "📝 Generating release notes..."
for repo in ${REPOSITORIES//,/ }; do
    echo "## $repo Changes" >> release-notes-${RELEASE_VERSION}.md
    cat ${repo}-${RELEASE_VERSION}-analysis.json | jq -r '.summary' >> release-notes-${RELEASE_VERSION}.md
    echo "" >> release-notes-${RELEASE_VERSION}.md
done

# 4. Check for breaking changes
echo "⚠️  Checking for breaking changes..."
for repo in ${REPOSITORIES//,/ }; do
    breaking_changes=$(cat ${repo}-${RELEASE_VERSION}-analysis.json | jq -r '.breaking_changes[]?')
    if [ ! -z "$breaking_changes" ]; then
        echo "Breaking changes in $repo:" >> breaking-changes-${RELEASE_VERSION}.md
        echo "$breaking_changes" >> breaking-changes-${RELEASE_VERSION}.md
    fi
done

echo "✅ Release preparation completed!"
```

---

## Automation Examples

### Example 1: Cron Job Automation

**Scenario**: Automated daily sync using cron.

```bash
# Add to crontab (crontab -e)
# Sync repositories every 6 hours
0 */6 * * * /usr/bin/gitco sync --batch --quiet --log /var/log/gitco/sync.log

# Daily health check at 9 AM
0 9 * * * /usr/bin/gitco status --overview --quiet --export /var/log/gitco/daily-status.json

# Weekly analysis on Sundays at 10 AM
0 10 * * 0 /usr/bin/gitco sync --batch --analyze --export /var/log/gitco/weekly-analysis.json
```

### Example 2: GitHub Actions Workflow

**Scenario**: Automated GitCo maintenance in GitHub Actions.

```yaml
# .github/workflows/gitco-maintenance.yml
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

    - name: Generate status report
      run: |
        gitco status --overview --export status-report.json

    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: gitco-results
        path: |
          sync-results.json
          status-report.json
```

### Example 3: Manual Systemd Service Setup

**Scenario**: Creating systemd service files manually for automated GitCo maintenance.

**Note**: GitCo does not provide built-in service installation. This example shows how to create systemd service files manually.

```ini
# /etc/systemd/system/gitco.service
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

```ini
# /etc/systemd/system/gitco.timer
[Unit]
Description=Run GitCo sync every 6 hours
Requires=gitco.service

[Timer]
OnCalendar=*-*-* 00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable and start the service
sudo systemctl enable gitco.timer
sudo systemctl start gitco.timer
sudo systemctl status gitco.timer
```

---

## Integration Examples

### Example 1: CI/CD Pipeline Integration

**Scenario**: Integrating GitCo into a CI/CD pipeline.

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  gitco-analysis:
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

    - name: Analyze changes
      run: |
        gitco analyze --repo my-project --export analysis.json

    - name: Check for breaking changes
      run: |
        if jq -e '.breaking_changes | length > 0' analysis.json; then
          echo "⚠️  Breaking changes detected!"
          cat analysis.json | jq -r '.breaking_changes[]'
          exit 1
        fi

    - name: Upload analysis
      uses: actions/upload-artifact@v3
      with:
        name: gitco-analysis
        path: analysis.json
```

### Example 2: Slack Integration

**Scenario**: Sending GitCo reports to Slack.

```python
# slack-integration.py
import requests
import json
import subprocess
from datetime import datetime

def send_slack_message(webhook_url, message):
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

def run_gitco_analysis():
    # Run GitCo analysis
    result = subprocess.run([
        "gitco", "sync", "--batch", "--analyze",
        "--export", "analysis.json"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        # Read analysis results
        with open("analysis.json", "r") as f:
            analysis = json.load(f)

        # Format message for Slack
        message = f"""
🤖 GitCo Daily Analysis - {datetime.now().strftime('%Y-%m-%d')}

📊 Summary:
• Repositories synced: {analysis.get('total_repositories', 0)}
• Successful syncs: {analysis.get('successful', 0)}
• Failed syncs: {analysis.get('failed', 0)}

🔍 Key Changes:
"""

        for repo_result in analysis.get('repository_results', []):
            if repo_result.get('success'):
                message += f"✅ {repo_result['name']}: Synced successfully\n"
            else:
                message += f"❌ {repo_result['name']}: {repo_result.get('message', 'Failed')}\n"

        return message
    else:
        return f"❌ GitCo analysis failed: {result.stderr}"

# Usage
webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
message = run_gitco_analysis()
send_slack_message(webhook_url, message)
```

### Example 3: Email Integration

**Scenario**: Sending GitCo reports via email.

```python
# email-integration.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import json
from datetime import datetime

def send_email_report(sender_email, sender_password, recipient_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()

def generate_gitco_report():
    # Run GitCo status
    result = subprocess.run([
        "gitco", "status", "--detailed", "--export", "status.json"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        with open("status.json", "r") as f:
            status = json.load(f)

        # Generate HTML report
        html_body = f"""
        <html>
        <body>
        <h1>GitCo Status Report - {datetime.now().strftime('%Y-%m-%d')}</h1>

        <h2>Repository Summary</h2>
        <ul>
        <li>Total Repositories: {status.get('total_repositories', 0)}</li>
        <li>Healthy Repositories: {status.get('healthy_repositories', 0)}</li>
        <li>Repositories Needing Attention: {status.get('needs_attention_repositories', 0)}</li>
        <li>Critical Repositories: {status.get('critical_repositories', 0)}</li>
        </ul>

        <h2>Repository Details</h2>
        """

        for repo in status.get('repository_results', []):
            health_status = repo.get('health_status', 'unknown')
            status_emoji = {
                'excellent': '🟢',
                'good': '🟢',
                'fair': '🟡',
                'poor': '🟠',
                'critical': '🔴'
            }.get(health_status, '⚪')

            html_body += f"""
            <div style="margin: 10px 0; padding: 10px; border: 1px solid #ccc;">
            <h3>{status_emoji} {repo.get('name', 'Unknown')}</h3>
            <p><strong>Health:</strong> {health_status.title()}</p>
            <p><strong>Sync Status:</strong> {repo.get('sync_status', 'Unknown')}</p>
            <p><strong>Last Commit:</strong> {repo.get('last_commit_days_ago', 'Unknown')} days ago</p>
            </div>
            """

        html_body += """
        </body>
        </html>
        """

        return html_body
    else:
        return f"<p>❌ GitCo status check failed: {result.stderr}</p>"

# Usage
sender_email = "your-email@gmail.com"
sender_password = "your-app-password"
recipient_email = "recipient@example.com"

subject = f"GitCo Status Report - {datetime.now().strftime('%Y-%m-%d')}"
body = generate_gitco_report()

send_email_report(sender_email, sender_password, recipient_email, subject, body)
```

---

## Advanced Examples

### Example 1: Multi-Repository Ecosystem Management

**Scenario**: Managing a complete Python ecosystem with multiple related repositories.

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

# Check for breaking changes across ecosystem
echo "⚠️  Checking for breaking changes..."
breaking_changes=0
for repo in "${repos[@]}"; do
    if [ -f "${repo}-analysis.json" ]; then
        changes=$(jq -r '.breaking_changes | length' "${repo}-analysis.json")
        if [ "$changes" -gt 0 ]; then
            echo "Breaking changes found in $repo:"
            jq -r '.breaking_changes[]' "${repo}-analysis.json"
            breaking_changes=$((breaking_changes + changes))
        fi
    fi
done

if [ $breaking_changes -gt 0 ]; then
    echo "⚠️  Total breaking changes: $breaking_changes"
else
    echo "✅ No breaking changes detected"
fi

echo "✅ Python ecosystem management completed!"
```

### Example 2: Cross-Platform Development Workflow

**Scenario**: Managing repositories across different platforms and technologies.

```bash
#!/bin/bash
# cross-platform-workflow.sh

echo "🔄 Cross-platform development workflow..."

# Define platform-specific repositories
declare -A platforms=(
    ["web"]="django,fastapi,react,vue"
    ["mobile"]="react-native,flutter,swift"
    ["desktop"]="electron,qt,wxpython"
    ["api"]="fastapi,django-rest,graphql"
)

for platform in "${!platforms[@]}"; do
    echo "📱 Managing $platform repositories..."

    # Get repositories for this platform
    repos=${platforms[$platform]}

    # Sync platform-specific repositories
    for repo in ${repos//,/ }; do
        gitco sync --repo $repo --quiet
    done

    # Analyze platform-specific changes
    gitco analyze --repos $repos --export ${platform}-analysis.json

    # Find platform-specific opportunities
    gitco discover --skill $platform --limit 5 --export ${platform}-opportunities.json
done

# Generate cross-platform report
gitco status --overview --export cross-platform-status.json

# Analyze cross-platform trends
echo "📊 Analyzing cross-platform trends..."
for platform in "${!platforms[@]}"; do
    echo "Platform: $platform"
    if [ -f "${platform}-analysis.json" ]; then
        jq -r '.summary' "${platform}-analysis.json"
    fi
done

echo "✅ Cross-platform workflow completed!"
```

### Example 3: Open Source Maintainer Workflow

**Scenario**: Comprehensive workflow for open source maintainers.

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

# 6. Check for security issues
echo "🔒 Checking for security issues..."
for repo in $(gitco config status | grep -o '[a-zA-Z0-9-]*' | head -10); do
    gitco analyze --repo $repo --prompt "Focus on security vulnerabilities and CVE updates" --export ${repo}-security.json
done

# 7. Generate community health report
echo "📈 Generating community health report..."
cat > community-health-report.md << EOF
# Community Health Report - $(date +%Y-%m-%d)

## Repository Status
$(gitco status --overview --quiet)

## Recent Activity
$(gitco activity --detailed --quiet)

## Issues Needing Attention
$(gitco discover --label "bug" --limit 10 --quiet)

## Security Analysis
$(for file in *-security.json; do
    if [ -f "$file" ]; then
        repo=$(echo $file | sed 's/-security.json//')
        echo "### $repo"
        jq -r '.security_updates[]?' "$file" 2>/dev/null || echo "No security issues found"
    fi
done)
EOF

echo "✅ Maintainer workflow completed!"
```

### Example 4: Advanced Integration

**Scenario**: Advanced integration with monitoring and alerting.

```python
# enterprise-integration.py
import subprocess
import json
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitCoMonitor:
    def __init__(self, config_path, webhook_url=None):
        self.config_path = config_path
        self.webhook_url = webhook_url

    def run_gitco_command(self, command, export_file=None):
        """Run a GitCo command and return results"""
        cmd = ["gitco", "--config", self.config_path] + command

        if export_file:
            cmd.extend(["--export", export_file])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def sync_repositories(self):
        """Sync all repositories"""
        logger.info("Starting repository sync...")
        success, stdout, stderr = self.run_gitco_command(["sync", "--batch", "--quiet"])

        if success:
            logger.info("Repository sync completed successfully")
            return True
        else:
            logger.error(f"Repository sync failed: {stderr}")
            self.send_alert("Repository sync failed", stderr)
            return False

    def check_health(self):
        """Check repository health"""
        logger.info("Checking repository health...")
        success, stdout, stderr = self.run_gitco_command(
            ["status", "--detailed"], "health-report.json"
        )

        if success:
            with open("health-report.json", "r") as f:
                health_data = json.load(f)

            # Check for critical issues
            critical_repos = []
            for repo in health_data.get("repository_results", []):
                if repo.get("health_status") == "critical":
                    critical_repos.append(repo.get("name"))

            if critical_repos:
                self.send_alert(
                    "Critical repositories detected",
                    f"Repositories needing immediate attention: {', '.join(critical_repos)}"
                )

            return health_data
        else:
            logger.error(f"Health check failed: {stderr}")
            return None

    def analyze_changes(self):
        """Analyze changes in repositories"""
        logger.info("Analyzing repository changes...")
        success, stdout, stderr = self.run_gitco_command(
            ["sync", "--batch", "--analyze"], "analysis-report.json"
        )

        if success:
            with open("analysis-report.json", "r") as f:
                analysis_data = json.load(f)

            # Check for breaking changes
            breaking_changes = []
            for repo_result in analysis_data.get("repository_results", []):
                if repo_result.get("breaking_changes"):
                    breaking_changes.append({
                        "repository": repo_result.get("name"),
                        "changes": repo_result.get("breaking_changes")
                    })

            if breaking_changes:
                self.send_alert(
                    "Breaking changes detected",
                    f"Breaking changes found in {len(breaking_changes)} repositories"
                )

            return analysis_data
        else:
            logger.error(f"Analysis failed: {stderr}")
            return None

    def discover_opportunities(self):
        """Discover contribution opportunities"""
        logger.info("Discovering contribution opportunities...")
        success, stdout, stderr = self.run_gitco_command(
            ["discover", "--limit", "10"], "opportunities.json"
        )

        if success:
            with open("opportunities.json", "r") as f:
                opportunities = json.load(f)

            # Log high-priority opportunities
            high_priority = [opp for opp in opportunities if opp.get("overall_score", 0) > 0.8]
            if high_priority:
                logger.info(f"Found {len(high_priority)} high-priority opportunities")

            return opportunities
        else:
            logger.error(f"Opportunity discovery failed: {stderr}")
            return None

    def send_alert(self, title, message):
        """Send alert via external webhook (requires external setup)"""
        if self.webhook_url:
            payload = {
                "text": f"🚨 **{title}**\n{message}",
                "timestamp": datetime.now().isoformat()
            }
            try:
                requests.post(self.webhook_url, json=payload, timeout=10)
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")

    def generate_report(self):
        """Generate comprehensive monitoring report"""
        logger.info("Generating monitoring report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "sync_status": self.sync_repositories(),
            "health_data": self.check_health(),
            "analysis_data": self.analyze_changes(),
            "opportunities": self.discover_opportunities()
        }

        # Save report
        with open("monitoring-report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("Monitoring report generated successfully")
        return report

# Usage
if __name__ == "__main__":
    gitco_monitor = GitCoMonitor(
        config_path="~/.gitco/config.yml",
        webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    )

    report = gitco_monitor.generate_report()
    print("GitCo monitoring workflow completed!")
```

These examples demonstrate the flexibility and power of GitCo for various use cases, from simple daily workflows to complex external integrations. Each example includes complete code snippets and expected outputs to help users understand and implement similar solutions.

**Note**: Webhook integrations, email notifications, and external alerting systems are not built into GitCo. These examples show how to integrate GitCo with external services and tools.
