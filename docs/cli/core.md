# Core Commands

This document covers GitCo's core CLI commands: init, sync, analyze, discover, status, activity, logs, performance, version, help, completion, and validate-repo.

## `gitco init`

Initialize GitCo configuration.

```bash
gitco init [OPTIONS]

Options:
  --interactive, -i        Interactive setup mode
  --non-interactive, -n    Non-interactive setup with defaults
  --force, -f              Force reinitialization
  --template, -t <path>    Use custom template for configuration
  --config-path <path>     Custom configuration path
```

**Examples:**
```bash
# Interactive setup
gitco init --interactive

# Non-interactive setup
gitco init --non-interactive

# Force reinitialization
gitco init --force
```

## `gitco sync`

Synchronize repositories with upstream.

```bash
gitco sync [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Sync specific repository
  --batch, -b              Batch sync all repositories
  --analyze, -a            Run analysis after sync
  --stash                  Stash local changes before sync
  --force, -f              Force sync even if conflicts
  --max-repos <count>      Maximum repositories per batch
  --export <file>          Export sync report
  --quiet, -q              Suppress output
  --log, -l <file>         Log to file
  --detailed-log           Use detailed log format with function names and line numbers
  --max-log-size <MB>      Maximum log file size in MB before rotation (default: 10)
  --log-backups <count>    Number of backup log files to keep (default: 5)
  --max-workers, -w <num>  Maximum concurrent workers for batch processing (default: 4)
```

**Examples:**
```bash
# Sync all repositories
gitco sync

# Sync specific repository
gitco sync --repo django

# Sync with analysis
gitco sync --analyze

# Batch sync with export
gitco sync --batch --export sync-report.json
```

## `gitco analyze`

Analyze repository changes using AI.

```bash
gitco analyze [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Analyze specific repository
  --repos <names>          Analyze multiple repositories (comma-separated)
  --detailed, -d           Detailed analysis
  --prompt, -p <text>      Custom analysis prompt
  --model <model>          LLM model to use
  --provider <provider>    LLM provider to use (openai only)
  --no-llm                 Skip LLM analysis
  --max-commits <count>    Maximum commits to analyze
  --export, -e <file>      Export analysis results
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# Analyze repository
gitco analyze --repo django

# Detailed analysis with custom prompt
gitco analyze --repo django --detailed --prompt "Focus on security implications"

# Analyze without LLM
gitco analyze --repo django --no-llm
```

## `gitco discover`

Discover contribution opportunities.

```bash
gitco discover [OPTIONS]

Options:
  --skill, -s <skill>      Filter by skill
  --label, -l <label>      Filter by GitHub label
  --repos <repos>          Filter by repositories
  --min-confidence, -c <float> Minimum confidence threshold (0.0-1.0)
  --limit, -n <count>      Maximum results to return
  --personalized, -p       Use personalized recommendations
  --show-history, -h       Show contribution history analysis
  --export, -e <file>      Export discovery results
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# Discover all opportunities
gitco discover

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Personalized recommendations
gitco discover --personalized --limit 10
```

## `gitco status`

Check repository health and status.

```bash
gitco status [OPTIONS]

Options:
  --repo, -r <name>        Show specific repository status
  --detailed, -d           Detailed status report
  --overview, -o           Overview status
  --activity, -a           Show repository activity dashboard
  --filter <status>        Filter by status (healthy, needs_attention, critical)
  --sort <field>           Sort by field (health, activity, stars, forks)
  --export <file>          Export status report
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# Check all repositories
gitco status

# Check specific repository
gitco status --repo django

# Detailed status
gitco status --detailed

# Filter by health
gitco status --filter healthy

# Sort by forks count
gitco status --sort forks

# Export status
gitco status --export status.json

# Quiet mode for automation
gitco status --quiet --export status.json
```

## `gitco activity`

View repository activity dashboard.

```bash
gitco activity [OPTIONS]

Options:
  --repo, -r <name>        Activity for specific repository
  --detailed, -d           Detailed activity report
  --filter <level>         Filter by activity level (high, moderate, low)
  --sort <field>           Sort by field (activity, engagement, commits, contributors)
  --export <file>          Export activity report
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# View activity dashboard
gitco activity

# Detailed activity
gitco activity --detailed

# Activity for specific repository
gitco activity --repo django

# Sort by contributors count
gitco activity --sort contributors

# Export activity
gitco activity --export activity.json

# Quiet mode for automation
gitco activity --quiet --export activity.json
```

## `gitco logs`

View and manage logs.

```bash
gitco logs [OPTIONS]

Options:
  --export <file>          Export logs
  --lines <count>          Number of lines to show
  --follow, -f             Follow log file
```

**Examples:**
```bash
# Export logs
gitco logs --export logs.json

# Show last 100 lines
gitco logs --lines 100
```

## `gitco performance`

View performance metrics.

```bash
gitco performance [OPTIONS]

Options:
  --detailed, -d           Detailed performance metrics
  --export <file>          Export performance data
```

**Examples:**
```bash
# View performance metrics
gitco performance

# Detailed metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json
```

## `gitco version`

Show GitCo version.

```bash
gitco version

# Output example:
# GitCo version 0.1.0
```

## `gitco help`

Get help for commands.

```bash
gitco help [COMMAND]

Examples:
  gitco help               Show general help
  gitco help sync          Show help for sync command
  gitco help analyze       Show help for analyze command
```

## `gitco completion`

Generate or install shell completion scripts.

```bash
gitco completion [OPTIONS]

Options:
  --shell, -s <shell>      Shell type (bash, zsh)
  --output, -o <file>      Output file path (default: auto-detect)
  --install, -i            Install completion script
```

**Examples:**
```bash
# Generate bash completion script
gitco completion --shell bash

# Generate and save to file
gitco completion --shell zsh --output ~/.zshrc

# Install completion script
gitco completion --shell bash --install
```

## `gitco validate-repo`

Validate repository structure and configuration.

```bash
gitco validate-repo [OPTIONS] [REPOSITORIES]

Options:
  --repo, -r <name>        Validate specific repository
  --all, -a                Validate all repositories
  --detailed, -d           Detailed validation report
  --path <path>            Validate repository at path
  --recursive              Recursive validation
  --export <file>          Export validation report
```

**Examples:**
```bash
# Validate specific repository
gitco validate-repo --repo django

# Validate all repositories
gitco validate-repo --all

# Validate at specific path
gitco validate-repo --path ~/code/django
```
