# Configuration Guide

This guide explains how to configure GitCo for your specific needs.

## Configuration File

GitCo uses a YAML configuration file (`gitco-config.yml`) to manage your repositories and settings.

## Configuration Validation

GitCo includes comprehensive configuration validation to help you identify and fix configuration issues early.

### Validation Features

- **Field Validation**: Ensures all required fields are present and properly formatted
- **URL Validation**: Validates repository URLs and GitHub API endpoints
- **Path Validation**: Checks local repository paths and file system access
- **Cross-Reference Validation**: Validates relationships between different configuration sections
- **Warning System**: Provides suggestions for improving configuration quality

### Running Validation

Use the validation command to check your configuration:

```bash
# Basic validation
gitco config validate

# Detailed validation with warnings
gitco config validate_detailed --detailed

# Export validation report
gitco config validate_detailed --export validation-report.json
```

### Validation Error Types

| Error Type | Description | Example |
|------------|-------------|---------|
| **Errors** | Critical issues that prevent GitCo from working | Missing required fields, invalid URLs |
| **Warnings** | Issues that may cause problems but don't prevent operation | High timeout values, relative paths |

### Common Validation Issues

#### Repository Configuration Issues

```yaml
# ❌ Invalid: Missing required fields
repositories:
  - name: ""  # Empty name
  - fork: ""  # Missing fork URL
  - upstream: "invalid-url"  # Invalid URL format

# ✅ Valid: Complete configuration
repositories:
  - name: "django"
    fork: "https://github.com/user/django"
    upstream: "https://github.com/django/django"
    local_path: "~/code/django"
```

#### Settings Validation Issues

```yaml
# ❌ Invalid: Invalid LLM provider
settings:
  llm_provider: "invalid_provider"  # Must be openai, anthropic, or ollama

# ❌ Invalid: Invalid numeric values
settings:
  max_repos_per_batch: 0  # Must be at least 1
  git_timeout: 10  # Must be at least 30 seconds

# ✅ Valid: Proper settings
settings:
  llm_provider: "openai"
  max_repos_per_batch: 10
  git_timeout: 300
```

#### URL Validation

GitCo validates repository URLs to ensure they follow proper formats:

```yaml
# ❌ Invalid URLs
repositories:
  - fork: "invalid-url"
  - upstream: "github.com/user/repo"  # Missing protocol

# ✅ Valid URLs
repositories:
  - fork: "https://github.com/user/repo"
  - upstream: "https://github.com/owner/repo"
```

#### Path Validation

GitCo checks local repository paths:

```yaml
# ⚠️ Warning: Relative path
repositories:
  - local_path: "./repos/django"  # May cause issues

# ✅ Recommended: Absolute or home-relative path
repositories:
  - local_path: "~/code/django"
  - local_path: "/absolute/path/to/repo"
```

### Validation Report Format

When exporting validation reports, GitCo provides detailed information:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "config_path": "/path/to/gitco-config.yml",
  "repository_count": 5,
  "validation_results": {
    "errors": [
      {
        "field": "repositories[0].name",
        "message": "Repository name is required",
        "suggestion": "Provide a unique name for this repository"
      }
    ],
    "warnings": [
      {
        "field": "repositories[1].local_path",
        "message": "Relative path may cause issues",
        "suggestion": "Use absolute path or path starting with ~"
      }
    ]
  },
  "summary": {
    "total_errors": 1,
    "total_warnings": 1,
    "is_valid": false
  }
}
```

## Basic Configuration

### Repository Configuration

Each repository in your configuration should include:

```yaml
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
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for the repository |
| `fork` | string | Yes | Your fork repository (username/repo) |
| `upstream` | string | Yes | Original repository (owner/repo) |
| `local_path` | string | Yes | Local path where repository is cloned |
| `skills` | list | No | Your skills relevant to this project |
| `analysis_enabled` | boolean | No | Enable AI analysis for this repo (default: true) |
| `sync_frequency` | string | No | Cron-like sync frequency |
| `language` | string | No | Primary programming language |

### Settings Configuration

```yaml
settings:
  llm_provider: openai  # or anthropic, ollama
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

### Settings Fields

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `llm_provider` | string | `openai` | LLM provider (openai, anthropic, ollama) |
| `default_path` | string | `~/code` | Default path for repository clones |
| `analysis_enabled` | boolean | `true` | Enable AI-powered change analysis |
| `max_repos_per_batch` | integer | `10` | Maximum repositories to process in batch |
| `git_timeout` | integer | `300` | Git operation timeout in seconds |
| `rate_limit_delay` | float | `1.0` | Delay between API calls in seconds |
| `log_level` | string | `INFO` | Logging level |

| `github_token_env` | string | `GITHUB_TOKEN` | Environment variable for GitHub token |
| `github_username_env` | string | `GITHUB_USERNAME` | Environment variable for GitHub username |
| `github_password_env` | string | `GITHUB_PASSWORD` | Environment variable for GitHub password |
| `github_api_url` | string | `https://api.github.com` | GitHub API base URL |
| `github_timeout` | integer | `30` | GitHub API request timeout in seconds |
| `github_max_retries` | integer | `3` | Maximum retries for GitHub API requests |

## Advanced Configuration

### Repository-Specific Settings

You can override settings per repository:

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]
    analysis_enabled: false  # Disable analysis for this repo
    sync_frequency: "0 2 * * *"  # Sync daily at 2 AM
    language: python
```

### GitHub Configuration

GitCo supports comprehensive GitHub API integration with multiple authentication methods:

```yaml
settings:
  # GitHub API settings
  github_token_env: GITHUB_TOKEN
  github_username_env: GITHUB_USERNAME
  github_password_env: GITHUB_PASSWORD
  github_api_url: https://api.github.com
  github_timeout: 30
  github_max_retries: 3
```

### Skills and Language Configuration

Configure your skills and programming languages for better issue matching:

```yaml
repositories:
  - name: backend-api
    fork: username/backend-api
    upstream: owner/backend-api
    local_path: ~/code/backend-api
    skills: [python, fastapi, postgresql, docker]
    language: python

  - name: frontend-app
    fork: username/frontend-app
    upstream: owner/frontend-app
    local_path: ~/code/frontend-app
    skills: [javascript, react, typescript, css]
    language: javascript
```

### Sync Frequency Configuration

Configure automatic sync schedules using cron-like syntax:

```yaml
repositories:
  - name: active-project
    fork: username/active-project
    upstream: owner/active-project
    local_path: ~/code/active-project
    sync_frequency: "0 */6 * * *"  # Every 6 hours

  - name: stable-project
    fork: username/stable-project
    upstream: owner/stable-project
    local_path: ~/code/stable-project
    sync_frequency: "0 2 * * 0"  # Weekly on Sunday at 2 AM
```

## Configuration Best Practices

### Repository Naming

- Use descriptive, unique names
- Avoid special characters except hyphens and underscores
- Keep names concise but meaningful

```yaml
# ✅ Good names
repositories:
  - name: django-framework
  - name: fastapi-backend
  - name: react-frontend

# ❌ Avoid
repositories:
  - name: "my project"  # Spaces not allowed
  - name: "repo1"  # Not descriptive
```

### Path Configuration

- Use absolute paths or home-relative paths (`~/`)
- Avoid relative paths that may cause issues
- Ensure paths are accessible and writable

```yaml
# ✅ Good paths
repositories:
  - local_path: "~/code/django"
  - local_path: "/Users/username/projects/fastapi"

# ⚠️ May cause issues
repositories:
  - local_path: "./repos/django"  # Relative path
```

### Skills Configuration

- List relevant technical skills for each repository
- Use consistent skill names across repositories
- Include both specific technologies and general areas

```yaml
# ✅ Comprehensive skills
repositories:
  - name: web-app
    skills: [python, django, postgresql, docker, aws]

  - name: mobile-app
    skills: [javascript, react-native, firebase, ios, android]
```

### Validation Integration

GitCo automatically validates your configuration during operations, but you can also run validation manually:

```bash
# Validate before making changes
gitco config validate

# Get detailed validation report
gitco config validate_detailed --detailed

# Export validation results for review
gitco config validate_detailed --export config-validation.json
```

This validation helps ensure your configuration is correct and will work reliably with GitCo's features.
