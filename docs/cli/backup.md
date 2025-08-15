# Backup and Recovery Commands

This document covers GitCo's backup management commands: create, list, restore, validate, delete, and cleanup.

## `gitco backup`

Manage backups and recovery.

```bash
gitco backup [COMMAND] [OPTIONS]

Commands:
  create                   Create backup
  list                     List backups
  restore                  Restore from backup
  validate                 Validate backup
  delete                   Delete backup
  cleanup                  Clean up old backups
```

## `gitco backup create`

Create a new backup.

```bash
gitco backup create [OPTIONS]

Options:
  --type, -t <type>        Backup type (full, incremental, config-only) (default: full)
  --description, -d <text> Backup description
  --repos, -r <names>      Backup specific repositories
  --config, -c <path>      Path to configuration file
  --no-git-history         Skip git history
  --compression <level>    Compression level (0-9) (default: 6)
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# Create full backup
gitco backup create --type full --description "Weekly backup"

# Create incremental backup
gitco backup create --type incremental --description "Daily backup"

# Backup specific repositories
gitco backup create --repos "django,fastapi" --description "Python repos"
```

## `gitco backup list`

List available backups.

```bash
gitco backup list [OPTIONS]

Options:
  --detailed, -d           Detailed backup information
  --sort, -s <field>       Sort by field (date, size, type) (default: date)
```

**Examples:**
```bash
# List backups
gitco backup list

# Detailed list
gitco backup list --detailed
```

## `gitco backup restore`

Restore from backup.

```bash
gitco backup restore [OPTIONS]

Options:
  --backup-id <id>         Backup ID to restore
  --target-dir <path>      Target directory for restoration
  --overwrite              Overwrite existing files
  --no-config              Skip configuration restoration
  --quiet, -q              Suppress output
```

**Examples:**
```bash
# Restore from backup
gitco backup restore --backup-id backup-2024-01-15

# Restore to specific directory
gitco backup restore --backup-id backup-2024-01-15 --target-dir ~/restored
```

## `gitco backup validate`

Validate a backup archive.

```bash
gitco backup validate [OPTIONS]

Options:
  --backup-id <id>         Backup ID to validate
```

**Examples:**
```bash
# Validate backup
gitco backup validate --backup-id backup-2024-01-15
```

## `gitco backup delete`

Delete a backup.

```bash
gitco backup delete [OPTIONS]

Options:
  --backup-id <id>         Backup ID to delete
  --force, -f              Force deletion without confirmation
```

**Examples:**
```bash
# Delete backup
gitco backup delete --backup-id backup-2024-01-15

# Force delete
gitco backup delete --backup-id backup-2024-01-15 --force
```

## `gitco backup cleanup`

Clean up old backups, keeping only the most recent ones.

```bash
gitco backup cleanup [OPTIONS]

Options:
  --keep, -k <count>       Number of backups to keep (default: 5)
```

**Examples:**
```bash
# Cleanup keeping 5 most recent
gitco backup cleanup

# Keep only 3 most recent
gitco backup cleanup --keep 3
```
