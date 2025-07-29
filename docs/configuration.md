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
  llm_provider: openai  # or anthropic, local
  api_key_env: AETHERIUM_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

### Settings Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `llm_provider` | string | `openai` | LLM provider (openai, anthropic, local) |
| `api_key_env` | string | `AETHERIUM_API_KEY` | Environment variable for API key |
| `default_path` | string | `~/code` | Default path for repositories |
| `analysis_enabled` | boolean | `true` | Enable AI analysis features |
| `max_repos_per_batch` | integer | `10` | Maximum repositories to process in batch |

## Advanced Configuration

### Custom LLM Endpoints

For custom LLM deployments:

```yaml
settings:
  llm_provider: custom
  custom_endpoint: "https://your-llm-endpoint.com/v1"
  api_key_env: CUSTOM_API_KEY
```

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

### Environment Variables

GitCo supports environment variables for sensitive configuration:

```bash
# Required for AI features - Unified configuration
export AETHERIUM_API_KEY="your-api-key"

# Optional: Override provider
export AETHERIUM_LLM_PROVIDER="anthropic"

# Optional: Provider-specific API keys (takes precedence)
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optional: Custom endpoint
export AETHERIUM_CUSTOM_ENDPOINT="https://your-endpoint.com"
```

**API Key Priority:**
1. Provider-specific keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
2. Unified key (`AETHERIUM_API_KEY`)
3. Configuration file `api_key_env` setting

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
  api_key_env: AETHERIUM_API_KEY
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
  api_key_env: AETHERIUM_API_KEY
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
