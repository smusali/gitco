# Cost Management Commands

This document covers GitCo's cost tracking and optimization commands: summary, breakdown, configure, and reset.

## `gitco cost`

Manage cost tracking and optimization.

```bash
gitco cost [COMMAND] [OPTIONS]

Commands:
  summary                  View cost summary
  breakdown                View cost breakdown
  configure                Configure cost settings
  reset                    Reset cost tracking
```

## `gitco cost summary`

View cost summary.

```bash
gitco cost summary [OPTIONS]

Options:
  --detailed, -d           Detailed cost breakdown
  --days <count>           Cost for last N days
  --months <count>         Cost for last N months
  --export <file>          Export cost data
```

**Examples:**
```bash
# View cost summary
gitco cost summary

# Detailed summary
gitco cost summary --detailed

# Export cost data
gitco cost summary --export costs.json
```

## `gitco cost breakdown`

View detailed cost breakdown.

```bash
gitco cost breakdown [OPTIONS]

Options:
  --detailed, -d           Detailed cost breakdown
  --provider, -p <provider> Show breakdown for specific provider
  --days <count>           Show breakdown for last N days (default: 30)
  --export <file>          Export breakdown to file (.json or .csv)
```

**Examples:**
```bash
# View cost breakdown
gitco cost breakdown

# Breakdown for specific provider
gitco cost breakdown --provider openai

# Export breakdown
gitco cost breakdown --export cost-breakdown.json
```

## `gitco cost configure`

Configure cost settings.

```bash
gitco cost configure [OPTIONS]

Options:
  --daily-limit <amount>        Daily cost limit
  --monthly-limit <amount>      Monthly cost limit
  --per-request-limit <amount>  Per-request cost limit
  --max-tokens <count>          Set maximum tokens per request
  --enable-tracking             Enable cost tracking
  --disable-tracking            Disable cost tracking
  --enable-optimization         Enable cost optimization
  --disable-optimization        Disable cost optimization
  --show                        Show current configuration
```

**Examples:**
```bash
# Set cost limits
gitco cost configure --daily-limit 5.0 --monthly-limit 50.0

# Enable optimization
gitco cost configure --enable-optimization

# Show configuration
gitco cost configure --show
```

## `gitco cost reset`

Reset cost history and statistics.

```bash
gitco cost reset [OPTIONS]

Options:
  --force, -f              Force reset without confirmation
```

**Examples:**
```bash
# Reset cost tracking
gitco cost reset

# Force reset
gitco cost reset --force
```
