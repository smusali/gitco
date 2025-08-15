# GitHub Integration Commands

This document covers GitCo's GitHub API integration commands: connection-status, rate-limit-status, get-repo, get-issues, and get-issues-multi.

## `gitco github`

GitHub integration commands.

```bash
gitco github [COMMAND] [OPTIONS]

Commands:
  connection-status        Check GitHub connection status
  rate-limit-status        Check rate limit status
  get-repo                 Get repository information
  get-issues               Get repository issues
  get-issues-multi         Get issues from multiple repositories
```

## `gitco github connection-status`

Check GitHub API connection status.

```bash
gitco github connection-status [OPTIONS]

Options:
  --detailed, -d           Detailed connection check
```

**Examples:**
```bash
# Check connection
gitco github connection-status

# Detailed check
gitco github connection-status --detailed
```

## `gitco github rate-limit-status`

Check GitHub API rate limits.

```bash
gitco github rate-limit-status [OPTIONS]

Options:
  --detailed, -d           Detailed rate limit information
  --wait                   Wait for rate limit reset
```

**Examples:**
```bash
# Check rate limits
gitco github rate-limit-status

# Detailed information
gitco github rate-limit-status --detailed
```

## `gitco github get-repo`

Get repository information from GitHub.

```bash
gitco github get-repo [OPTIONS]

Options:
  --repo, -r <name>        Repository name (owner/repo) (required)
```

**Examples:**
```bash
# Get repository information
gitco github get-repo --repo django/django
```

## `gitco github get-issues`

Get repository issues from GitHub.

```bash
gitco github get-issues [OPTIONS]

Options:
  --repo, -r <name>        Repository name (owner/repo) (required)
  --state, -s <state>      Issue state (open, closed, all) (default: open)
  --labels, -l <labels>    Filter by labels (comma-separated)
  --exclude-labels, -e <labels> Exclude labels (comma-separated)
  --assignee, -a <user>    Filter by assignee
  --limit <count>          Maximum results to return
  --export <file>          Export results to file
```

**Examples:**
```bash
# Get open issues
gitco github get-issues --repo django/django

# Get issues with specific labels
gitco github get-issues --repo django/django --labels "bug,enhancement"

# Export issues to file
gitco github get-issues --repo django/django --export issues.json
```

## `gitco github get-issues-multi`

Get issues from multiple repositories.

```bash
gitco github get-issues-multi [OPTIONS]

Options:
  --repos, -r <names>      Repository names (comma-separated, owner/repo format) (required)
  --state, -s <state>      Issue state (open, closed, all) (default: open)
  --labels, -l <labels>    Filter by labels (comma-separated)
  --exclude-labels, -e <labels> Exclude labels (comma-separated)
  --assignee, -a <user>    Filter by assignee
  --limit <count>          Maximum results to return per repository
  --export <file>          Export results to file
```

**Examples:**
```bash
# Get issues from multiple repositories
gitco github get-issues-multi --repos "django/django,fastapi/fastapi"

# Filter by labels across repositories
gitco github get-issues-multi --repos "django/django,fastapi/fastapi" --labels "good first issue"

# Export combined results
gitco github get-issues-multi --repos "django/django,fastapi/fastapi" --export multi-issues.json
```
