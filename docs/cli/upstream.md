# Upstream Management Commands

This document covers GitCo's upstream management commands: add, remove, update, validate, fetch, and merge.

## `gitco upstream`

Manage upstream repository connections.

```bash
gitco upstream [COMMAND] [OPTIONS]

Commands:
  add                      Add upstream remote
  remove                   Remove upstream remote
  update                   Update upstream URL
  validate                 Validate upstream configuration
  fetch                    Fetch from upstream
  merge                    Merge upstream changes
```

## `gitco upstream add`

Add upstream remote to repository.

```bash
gitco upstream add [OPTIONS]

Options:
  --repo, -r <name>        Repository name (required)
  --url <url>              Upstream repository URL (required)
  --name <name>            Remote name (default: upstream)
```

**Examples:**
```bash
# Add upstream remote
gitco upstream add --repo django --url https://github.com/django/django.git
```

## `gitco upstream remove`

Remove upstream remote from repository.

```bash
gitco upstream remove [OPTIONS]

Options:
  --repo, -r <name>        Repository name (required)
```

**Examples:**
```bash
# Remove upstream remote
gitco upstream remove --repo django
```

## `gitco upstream update`

Update upstream remote URL for repository.

```bash
gitco upstream update [OPTIONS]

Options:
  --repo, -r <name>        Repository name (required)
  --url <url>              New upstream repository URL (required)
```

**Examples:**
```bash
# Update upstream URL
gitco upstream update --repo django --url https://github.com/django/django.git
```

## `gitco upstream validate`

Validate upstream configuration.

```bash
gitco upstream validate [OPTIONS]

Options:
  --repo, -r <name>        Validate specific repository
  --detailed, -d           Detailed validation
```

**Examples:**
```bash
# Validate upstream
gitco upstream validate --repo django

# Detailed validation
gitco upstream validate --repo django --detailed
```

## `gitco upstream fetch`

Fetch latest changes from upstream.

```bash
gitco upstream fetch [OPTIONS]

Options:
  --repo, -r <name>        Repository name (required)
```

**Examples:**
```bash
# Fetch from upstream
gitco upstream fetch --repo django
```

## `gitco upstream merge`

Merge upstream changes into current branch.

```bash
gitco upstream merge [OPTIONS]

Options:
  --repo, -r <name>        Repository name (required)
  --branch, -b <branch>    Branch to merge (default: default branch)
  --strategy, -s <strategy> Conflict resolution strategy (ours, theirs, manual) (default: ours)
  --abort, -a              Abort current merge
  --resolve                Resolve conflicts automatically
```

**Examples:**
```bash
# Merge upstream changes
gitco upstream merge --repo django

# Merge with conflict resolution strategy
gitco upstream merge --repo django --strategy ours

# Abort current merge
gitco upstream merge --repo django --abort
```
