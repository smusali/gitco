# Contribution Tracking Commands

This document covers GitCo's contribution tracking commands: sync-history, stats, recommendations, export, and trending.

## `gitco contributions`

Manage contribution tracking.

```bash
gitco contributions [COMMAND] [OPTIONS]

Commands:
  sync-history             Sync contribution history
  stats                    View contribution statistics
  recommendations          Get personalized recommendations
  trending                 View trending analysis
  export                   Export contribution data
```

## `gitco contributions sync-history`

Sync contribution history from GitHub.

```bash
gitco contributions sync-history [OPTIONS]

Options:
  --username <username>    GitHub username (required)
  --force, -f              Force sync even if recent
  --days <count>           Sync contributions from last N days
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# Sync contribution history
gitco contributions sync-history --username yourusername

# Force sync
gitco contributions sync-history --username yourusername --force
```

## `gitco contributions stats`

View contribution statistics.

```bash
gitco contributions stats [OPTIONS]

Options:
  --days <count>           Statistics for last N days
  --detailed, -d           Detailed statistics
  --export <file>          Export statistics
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# View statistics
gitco contributions stats

# Statistics for last 30 days
gitco contributions stats --days 30

# Export statistics
gitco contributions stats --export stats.json
```

## `gitco contributions recommendations`

Get personalized contribution recommendations.

```bash
gitco contributions recommendations [OPTIONS]

Options:
  --skill, -s <skill>      Filter by skill
  --repository, -r <repo>  Filter by repository
  --limit, -n <count>      Number of recommendations (default: 10)
```

**Examples:**
```bash
# Get recommendations
gitco contributions recommendations

# Filter by skill
gitco contributions recommendations --skill python

# Limit results
gitco contributions recommendations --limit 5
```

## `gitco contributions export`

Export contribution data.

```bash
gitco contributions export [OPTIONS]

Options:
  --days <count>           Export contributions from last N days
  --output, -o <file>      Output file path (.csv or .json) (required)
  --include-stats, -s      Include summary statistics
```

**Examples:**
```bash
# Export to CSV
gitco contributions export --output contributions.csv

# Export with statistics
gitco contributions export --output contributions.json --include-stats

# Export last 30 days
gitco contributions export --days 30 --output recent-contributions.csv
```

## `gitco contributions trending`

Show detailed trending analysis of contributions.

```bash
gitco contributions trending [OPTIONS]

Options:
  --days <count>           Analysis period in days (default: 30)
  --export <file>          Export trending analysis to file (.json or .csv)
```

**Examples:**
```bash
# View trending analysis
gitco contributions trending

# Custom period
gitco contributions trending --days 7

# Export trending data
gitco contributions trending --export trending.json
```
