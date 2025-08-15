# Configuration Commands

This document covers GitCo's configuration management commands: validate, show, edit, export, and import.

## `gitco config`

Manage configuration.

```bash
gitco config [COMMAND] [OPTIONS]

Commands:
  validate                 Validate configuration
  show                     Show current configuration
  edit                     Edit configuration file
  export                   Export configuration
  import                   Import configuration
```

## `gitco config validate`

Validate configuration file.

```bash
gitco config validate [OPTIONS]

Options:
  --detailed, -d           Detailed validation report
  --strict                 Strict validation mode
  --export, -e <file>      Export validation report
```

**Examples:**
```bash
# Basic validation
gitco config validate

# Detailed validation
gitco config validate --detailed

# Export validation report
gitco config validate --export validation-report.json
```

## `gitco config show`

Show configuration status.

```bash
gitco config show
```

**Examples:**
```bash
# Show configuration
gitco config show
```

## `gitco config edit`

Edit configuration file.

```bash
gitco config edit
```

**Examples:**
```bash
# Edit configuration
gitco config edit
```

## `gitco config export`

Export configuration.

```bash
gitco config export [OPTIONS]

Options:
  --output, -o <file>      Output file path (required)
  --format, -f <format>    Export format (yaml, json) - default: yaml
```

**Examples:**
```bash
# Export to YAML
gitco config export --output config-backup.yml

# Export to JSON
gitco config export --output config-backup.json --format json
```

## `gitco config import`

Import configuration.

```bash
gitco config import [OPTIONS]

Options:
  --input, -i <file>       Input file path (required)
  --merge, -m              Merge with existing configuration
```

**Examples:**
```bash
# Import configuration (replace)
gitco config import --input config-backup.yml

# Import and merge with existing
gitco config import --input config-backup.yml --merge
```
