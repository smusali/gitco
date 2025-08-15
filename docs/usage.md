# GitCo Usage Guide

This guide provides comprehensive usage examples and workflows for GitCo, covering all major features and common use cases.

## Table of Contents

1. [Basic Workflows](#basic-workflows)
2. [Repository Management](#repository-management)
3. [Analysis and Discovery](#analysis-and-discovery)
4. [Health Monitoring](#health-monitoring)
5. [Contribution Tracking](#contribution-tracking)
6. [Backup and Recovery](#backup-and-recovery)
7. [Cost Management](#cost-management)
8. [Automation](#automation)
9. [Advanced Workflows](#advanced-workflows)

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

**Detailed activity metrics:**
```bash
gitco activity --detailed
```

**Activity for specific repository:**
```bash
gitco activity --repo django --detailed
```

---

## Repository Management

### Repository Validation

**Validate repository structure:**
```bash
gitco validate-repo --repo django
```

**Validate all repositories:**
```bash
gitco validate-repo --all
```

**Detailed validation report:**
```bash
gitco validate-repo --repo django --detailed --export validation.json
```

### Upstream Management

**Add upstream remote:**
```bash
gitco upstream add --repo django --url https://github.com/django/django.git
```

**Verify upstream configuration:**
```bash
gitco upstream validate --repo django
```

**Update upstream URL:**
```bash
gitco upstream update --repo django --url https://github.com/new-org/django.git
```

**Remove upstream remote:**
```bash
gitco upstream remove --repo django
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

**Analyze multiple repositories:**
```bash
gitco analyze --repos "django,fastapi"
```

**Get detailed analysis:**
```bash
gitco analyze --repo django --detailed
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

**Sort by metrics:**
```bash
gitco status --sort health
gitco status --sort activity
gitco status --sort stars
```

**Export health data:**
```bash
gitco status --export health.json
```

### Activity Monitoring

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
```

**Export activity data:**
```bash
gitco activity --export activity.json
```

---

## Contribution Tracking

### Sync Contribution History

**Sync your contribution history:**
```bash
gitco contributions sync-history --username yourusername
```

**View contribution stats:**
```bash
gitco contributions stats
```

**Get recommendations:**
```bash
gitco contributions recommendations
```

**Trending analysis:**
```bash
gitco contributions trending --days 30 --export skill-trends.json
```

---

## Backup and Recovery

### Create Backups

**Create full backup:**
```bash
gitco backup create --type full --description "Weekly backup"
```

**Create incremental backup:**
```bash
gitco backup create --type incremental --description "Daily backup"
```

**List backups:**
```bash
gitco backup list
```

**Restore from backup:**
```bash
gitco backup restore --backup-id backup-id
```

---

## Cost Management

### View Cost Summary

**View cost summary:**
```bash
gitco cost summary
```

**Configure cost limits:**
```bash
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0
```

**Cost breakdown by provider:**
```bash
gitco cost breakdown --provider openai
```

---

## Automation

### Quiet Mode

**Quiet sync for automation:**
```bash
gitco --quiet sync --batch
```

**Export for monitoring:**
```bash
gitco status --export status.json --output-format json
```

### GitHub Actions

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

---

## Advanced Workflows

### Multi-Repository Analysis

**Analyze multiple repositories:**
```bash
gitco analyze --repos "django,fastapi,flask" --detailed --export analysis.json
```

**Batch discovery across repositories:**
```bash
gitco discover --repos "django,fastapi" --skill python --export opportunities.json
```

### Performance Monitoring

**Check performance metrics:**
```bash
gitco performance --detailed
```

**Export performance data:**
```bash
gitco performance --export performance.json
```

### GitHub Integration

**Check rate limits:**
```bash
gitco github rate-limit-status
```

**Get repository info:**
```bash
gitco github get-repo --repo django/django
```

**Get issues from multiple repos:**
```bash
gitco github get-issues-multi --repos "django/django,fastapi/fastapi"
```

---

## Troubleshooting

### Common Issues

**Validate configuration:**
```bash
gitco config validate
```

**Check GitHub connection:**
```bash
gitco github connection-status
```

**Check rate limits:**
```bash
gitco github rate-limit-status
```

**Debug mode:**
```bash
gitco --debug sync
```

### Get Help

**Comprehensive help:**
```bash
gitco help
```

**Command-specific help:**
```bash
gitco sync --help
gitco analyze --help
gitco discover --help
```
