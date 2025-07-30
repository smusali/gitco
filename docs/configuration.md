# Configuration Guide

This guide explains how to configure GitCo for your specific needs.

## Configuration File

GitCo uses a YAML configuration file (`gitco-config.yml`) to manage your repositories and settings.

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

### Settings Configuration

```yaml
settings:
  llm_provider: openai  # or anthropic
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

### Settings Fields

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `llm_provider` | string | `openai` | LLM provider (openai, anthropic) |
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
    sync_frequency: daily    # Custom sync frequency
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

#### GitHub Authentication Methods

**1. Personal Access Token (Recommended):**
```bash
export GITHUB_TOKEN="your-personal-access-token"
```

**2. Username/Password (Less Secure):**
```bash
export GITHUB_USERNAME="your-username"
export GITHUB_PASSWORD="your-password"
```

**3. Environment Variables:**
GitCo automatically detects GitHub credentials from environment variables:
- `GITHUB_TOKEN` - Personal access token
- `GITHUB_USERNAME` - GitHub username
- `GITHUB_PASSWORD` - GitHub password

#### GitHub API Features

- **Rate Limiting**: Automatic handling of GitHub API rate limits
- **Retry Logic**: Exponential backoff for failed requests
- **Error Handling**: Comprehensive error handling for API failures
- **Connection Testing**: Validate GitHub API connectivity
- **Repository Info**: Fetch detailed repository metadata
- **Issue Management**: Get issues with filtering and search

### Environment Variables

GitCo supports environment variables for sensitive configuration:

```bash
# LLM API Keys (choose one based on your provider)
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"



# GitHub API credentials (optional)
export GITHUB_TOKEN="your-github-token"
export GITHUB_USERNAME="your-github-username"
export GITHUB_PASSWORD="your-github-password"
```



## Configuration Examples

### Minimal Configuration

```yaml
repositories:
  - name: my-project
    fork: username/my-project
    upstream: original-owner/my-project
    local_path: ~/code/my-project

settings:
  llm_provider: openai
```

### Full Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm, database]

  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async, web]

  - name: requests
    fork: username/requests
    upstream: psf/requests
    local_path: ~/code/requests
    skills: [python, http, networking]

settings:
  llm_provider: anthropic
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 5
  sync_timeout: 300
  log_level: INFO
```



## Configuration Validation

GitCo validates your configuration file for:

- Required fields presence
- Valid repository paths
- Correct YAML syntax
- Valid settings values

### Validation Commands

```bash
# Validate configuration
gitco config validate

# Check configuration status
gitco config status
```

## Troubleshooting Configuration

### Common Issues

1. **Invalid YAML syntax:**
   - Use a YAML validator
   - Check indentation and quotes

2. **Repository not found:**
   - Verify local paths exist
   - Check repository permissions

3. **API key issues:**
   - Verify environment variable is set
   - Check API key permissions

### Configuration Tips

1. **Use absolute paths** for local_path to avoid issues
2. **Group related repositories** with similar skills
3. **Start with minimal configuration** and expand as needed
4. **Backup your configuration** before major changes

## Next Steps

After configuring GitCo, see the [Usage Guide](usage.md) to start using the tool.
