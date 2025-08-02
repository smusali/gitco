# GitCo Usage Guide

This guide provides comprehensive usage examples and workflows for GitCo, covering all major features and common use cases.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Workflows](#basic-workflows)
3. [Repository Management](#repository-management)
4. [Analysis and Discovery](#analysis-and-discovery)
5. [Health Monitoring](#health-monitoring)
6. [Contribution Tracking](#contribution-tracking)
7. [Backup and Recovery](#backup-and-recovery)
8. [Cost Management](#cost-management)
9. [Automation](#automation)
10. [Advanced Workflows](#advanced-workflows)
11. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Initial Setup

1. **Install GitCo:**
   ```bash
   pip install gitco
   ```

2. **Initialize Configuration:**
   ```bash
   gitco init --interactive
   ```

3. **Set Environment Variables:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export GITHUB_TOKEN="your-github-token"
   ```

4. **Verify Setup:**
   ```bash
   gitco config validate
   gitco github test-connection
   ```

### Basic Configuration

Create a minimal configuration file at `~/.gitco/config.yml`:

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

---

## Basic Workflows

### Daily Repository Sync

**Sync all repositories:**
```bash
gitco sync
```

**Sync specific repository:**
```bash
gitco sync --repo django
```

**Sync with analysis:**
```bash
gitco sync --analyze
```

**Batch sync with export:**
```bash
gitco sync --batch --export sync-report.json
```

### Repository Health Check

**Check all repositories:**
```bash
gitco status
```

**Detailed health report:**
```bash
gitco status --detailed
```

**Overview dashboard:**
```bash
gitco status --overview
```

**Filter by health status:**
```bash
gitco status --filter healthy
gitco status --filter needs_attention
gitco status --filter critical
```

### Activity Monitoring

**View activity dashboard:**
```bash
gitco activity
```

**Detailed activity for specific repository:**
```bash
gitco activity --repo django --detailed
```

**Filter by activity level:**
```bash
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low
```

---

## Repository Management

### Adding New Repositories

**Manual addition to config:**
```yaml
repositories:
  - name: new-project
    fork: username/new-project
    upstream: owner/new-project
    local_path: ~/code/new-project
    skills: [python, api, testing]
    analysis_enabled: true
    sync_frequency: daily
    language: python
```

**Validate new repository:**
```bash
gitco validate-repo --path ~/code/new-project
```

### Upstream Management

**Add upstream remote:**
```bash
gitco upstream add --repo django --url https://github.com/django/django.git
```

**Fetch from upstream:**
```bash
gitco upstream fetch --repo django
```

**Merge upstream changes:**
```bash
gitco upstream merge --repo django
```

**Resolve conflicts:**
```bash
gitco upstream merge --repo django --resolve --strategy ours
```

**Validate upstream configuration:**
```bash
gitco upstream validate --repo django
```

### Repository Validation

**Validate current directory:**
```bash
gitco validate-repo
```

**Validate specific path:**
```bash
gitco validate-repo --path ~/code/django
```

**Recursive validation:**
```bash
gitco validate-repo --path ~/code --recursive
```

**Detailed validation:**
```bash
gitco validate-repo --detailed
```

---

## Analysis and Discovery

### Change Analysis

**Analyze repository changes:**
```bash
gitco analyze --repo django
```

**Analyze with custom prompt:**
```bash
gitco analyze --repo django --prompt "Focus on security implications"
```

**Analyze with specific provider:**
```bash
gitco analyze --repo django --provider anthropic
```

**Analyze multiple repositories:**
```bash
gitco analyze --repos "django,fastapi,requests"
```

**Export analysis results:**
```bash
gitco analyze --repo django --export analysis.json
```

### Contribution Discovery

**Discover all opportunities:**
```bash
gitco discover
```

**Filter by skill:**
```bash
gitco discover --skill python
gitco discover --skill javascript
```

**Filter by label:**
```bash
gitco discover --label "good first issue"
gitco discover --label "bug"
```

**Set confidence threshold:**
```bash
gitco discover --min-confidence 0.5
```

**Limit results:**
```bash
gitco discover --limit 10
```

**Personalized recommendations:**
```bash
gitco discover --personalized --show-history
```

**Export discovery results:**
```bash
gitco discover --export opportunities.json
```

---

## Health Monitoring

### Repository Health

**Basic health check:**
```bash
gitco status
```

**Detailed health metrics:**
```bash
gitco status --detailed
```

**Health overview dashboard:**
```bash
gitco status --overview
```

**Filter by health status:**
```bash
gitco status --filter healthy
gitco status --filter needs_attention
gitco status --filter critical
```

**Sort by metrics:**
```bash
gitco status --sort health
gitco status --sort activity
gitco status --sort stars
gitco status --sort forks
```

**Export health data:**
```bash
gitco status --export health-report.json
```

### Activity Monitoring

**Activity dashboard:**
```bash
gitco activity
```

**Detailed activity metrics:**
```bash
gitco activity --detailed
```

**Activity for specific repository:**
```bash
gitco activity --repo django --detailed
```

**Filter by activity level:**
```bash
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low
```

**Sort by activity metrics:**
```bash
gitco activity --sort activity
gitco activity --sort engagement
gitco activity --sort commits
gitco activity --sort contributors
```

**Export activity data:**
```bash
gitco activity --export activity-report.json
```

---

## Contribution Tracking

### Sync Contribution History

**Sync from GitHub:**
```bash
gitco contributions sync-history --username yourusername
```

**Force sync (even if recent):**
```bash
gitco contributions sync-history --username yourusername --force
```

### View Contribution Statistics

**Basic stats:**
```bash
gitco contributions stats
```

**Stats for specific period:**
```bash
gitco contributions stats --days 30
```

**Export stats:**
```bash
gitco contributions stats --export stats.json
```

### Get Recommendations

**Personalized recommendations:**
```bash
gitco contributions recommendations
```

**Filter by skill:**
```bash
gitco contributions recommendations --skill python
```

**Filter by repository:**
```bash
gitco contributions recommendations --repository django
```

**Limit recommendations:**
```bash
gitco contributions recommendations --limit 5
```

### Export Contribution Data

**Export all contributions:**
```bash
gitco contributions export --output contributions.json
```

**Export recent contributions:**
```bash
gitco contributions export --days 30 --output recent-contributions.json
```

**Include summary statistics:**
```bash
gitco contributions export --output contributions.json --include-stats
```

### Trending Analysis

**View trending analysis:**
```bash
gitco contributions trending
```

**Custom analysis period:**
```bash
gitco contributions trending --days 60
```

**Export trending data:**
```bash
gitco contributions trending --export trending.json
```

---

## Backup and Recovery

### Create Backups

**Full backup:**
```bash
gitco backup create --type full --description "Monthly backup"
```

**Incremental backup:**
```bash
gitco backup create --type incremental --description "Daily backup"
```

**Config-only backup:**
```bash
gitco backup create --type config-only --description "Configuration backup"
```

**Backup specific repositories:**
```bash
gitco backup create --repos "django,fastapi" --description "Python repos backup"
```

**Exclude git history (smaller backup):**
```bash
gitco backup create --no-git-history --compression 9
```

### Manage Backups

**List all backups:**
```bash
gitco backup list
```

**Detailed backup information:**
```bash
gitco backup list --detailed
```

**Validate backup:**
```bash
gitco backup validate --backup-id backup-2024-01-15
```

**Delete backup:**
```bash
gitco backup delete --backup-id backup-2024-01-15
```

**Force delete:**
```bash
gitco backup delete --backup-id backup-2024-01-15 --force
```

### Restore Backups

**Restore from backup:**
```bash
gitco backup restore --backup-id backup-2024-01-15
```

**Restore to specific directory:**
```bash
gitco backup restore --backup-id backup-2024-01-15 --target-dir ~/restored
```

**Skip configuration restoration:**
```bash
gitco backup restore --backup-id backup-2024-01-15 --no-config
```

**Overwrite existing files:**
```bash
gitco backup restore --backup-id backup-2024-01-15 --overwrite
```

### Cleanup Old Backups

**Cleanup old backups:**
```bash
gitco backup cleanup
```

**Keep more backups:**
```bash
gitco backup cleanup --keep 10
```

---

## Cost Management

### View Cost Summary

**Basic cost summary:**
```bash
gitco cost summary
```

**Detailed cost breakdown:**
```bash
gitco cost summary --detailed
```

**Cost for specific period:**
```bash
gitco cost summary --days 30
gitco cost summary --months 3
```

**Export cost data:**
```bash
gitco cost summary --export costs.json
```

### Configure Cost Settings

**Set cost limits:**
```bash
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0
```

**Set per-request limit:**
```bash
gitco cost configure --per-request-limit 0.10
```

**Set token limits:**
```bash
gitco cost configure --max-tokens 4000
```

**Enable/disable tracking:**
```bash
gitco cost configure --enable-tracking
gitco cost configure --disable-tracking
```

**Enable/disable optimization:**
```bash
gitco cost configure --enable-optimization
gitco cost configure --disable-optimization
```

### Cost Breakdown

**Breakdown by model:**
```bash
gitco cost breakdown --model gpt-3.5-turbo
```

**Breakdown by provider:**
```bash
gitco cost breakdown --provider openai
```

**Custom time period:**
```bash
gitco cost breakdown --days 60
```

### Reset Cost History

**Reset cost tracking:**
```bash
gitco cost reset
```

**Force reset:**
```bash
gitco cost reset --force
```

---

## Automation

### Quiet Mode Operations

**Quiet sync for automation:**
```bash
gitco --quiet sync --batch
```

**Quiet analysis:**
```bash
gitco --quiet analyze --repo django
```

**Quiet status check:**
```bash
gitco --quiet status --filter critical
```

### Export for External Tools

**Export status for monitoring:**
```bash
gitco status --export status.json --output-format json
```

**Export health data:**
```bash
gitco status --export health.csv --output-format csv
```

**Export activity data:**
```bash
gitco activity --export activity.json
```

### Logging for Automation

**Enable detailed logging:**
```bash
gitco --log-file gitco.log --detailed-log sync
```

**Set log level:**
```bash
gitco --log-level DEBUG sync
```

**Log rotation:**
```bash
gitco --max-log-size 50 --log-backups 10 sync
```

### CI/CD Integration

**GitHub Actions workflow:**
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
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: sync-report
          path: sync-report.json
```

---

## Advanced Workflows

### Multi-Repository Analysis

**Analyze multiple repositories:**
```bash
gitco analyze --repos "django,fastapi,requests" --export analysis.json
```

**Batch sync with analysis:**
```bash
gitco sync --batch --analyze --export batch-analysis.json
```

### Advanced Discovery

**High-confidence opportunities:**
```bash
gitco discover --min-confidence 0.8 --limit 5
```

**Skill-specific discovery:**
```bash
gitco discover --skill python --label "good first issue" --limit 10
```

**Personalized recommendations:**
```bash
gitco discover --personalized --show-history --limit 10
```

### Health Monitoring Workflow

**Daily health check:**
```bash
gitco status --overview --filter needs_attention
```

**Weekly detailed health report:**
```bash
gitco status --detailed --export weekly-health.json
```

**Activity monitoring:**
```bash
gitco activity --filter high --sort activity
```

### Backup Strategy

**Daily incremental backups:**
```bash
gitco backup create --type incremental --description "Daily backup $(date)"
```

**Weekly full backups:**
```bash
gitco backup create --type full --description "Weekly backup $(date)"
```

**Monthly cleanup:**
```bash
gitco backup cleanup --keep 30
```

### Cost Optimization Workflow

**Monitor costs:**
```bash
gitco cost summary --detailed
```

**Set conservative limits:**
```bash
gitco cost configure --daily-limit 2.0 --monthly-limit 20.0
```

**Track usage patterns:**
```bash
gitco cost breakdown --days 30
```

### GitHub Integration Workflow

**Check rate limits:**
```bash
gitco github rate-limit-status --detailed
```

**Test connection:**
```bash
gitco github test-connection
```

**Get repository info:**
```bash
gitco github get-repo --repo django/django
```

**Get issues from multiple repos:**
```bash
gitco github get-issues-multi --repos "django/django,fastapi/fastapi" --labels "good first issue"
```

---

## Troubleshooting

### Common Issues

**Configuration validation:**
```bash
gitco config validate
gitco config validate-detailed --detailed
```

**GitHub connection test:**
```bash
gitco github test-connection
```

**Repository validation:**
```bash
gitco validate-repo --detailed
```

**Rate limit check:**
```bash
gitco github rate-limit-status
```

### Debug Mode

**Enable debug logging:**
```bash
gitco --debug --detailed-log sync
```

**Debug specific command:**
```bash
gitco --debug analyze --repo django
```

**Export debug logs:**
```bash
gitco --debug --log-file debug.log sync
```

### Performance Issues

**Check performance metrics:**
```bash
gitco performance --detailed
```

**View logs:**
```bash
gitco logs --export logs.json
```

**Monitor resource usage:**
```bash
gitco performance --export performance.json
```

### Cost Issues

**Check cost usage:**
```bash
gitco cost summary --detailed
```

**Reset cost tracking:**
```bash
gitco cost reset --force
```

**Configure cost limits:**
```bash
gitco cost configure --daily-limit 1.0 --monthly-limit 10.0
```

### Backup Issues

**Validate backup:**
```bash
gitco backup validate --backup-id backup-id
```

**List backups:**
```bash
gitco backup list --detailed
```

**Test restore:**
```bash
gitco backup restore --backup-id backup-id --target-dir ~/test-restore
```

This comprehensive usage guide covers all major GitCo workflows and provides practical examples for common use cases. The guide is designed to help users effectively utilize GitCo's features for intelligent OSS fork management and contribution discovery.
