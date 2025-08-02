# GitCo Configuration Guide

This guide covers all configuration options available in GitCo, from basic setup to advanced customization.

## Table of Contents

1. [Configuration File Structure](#configuration-file-structure)
2. [Repository Configuration](#repository-configuration)
3. [Settings Configuration](#settings-configuration)
4. [LLM Provider Configuration](#llm-provider-configuration)
5. [GitHub Integration](#github-integration)
6. [Cost Optimization](#cost-optimization)
7. [Rate Limiting](#rate-limiting)
8. [Environment Variables](#environment-variables)
9. [Validation](#validation)
10. [Examples](#examples)

---

## Configuration File Structure

GitCo uses a YAML configuration file to manage all settings, repositories, and integration options. The configuration file is typically located at `~/.gitco/config.yml`.

### Basic Configuration Structure

```yaml
# GitCo Configuration File
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

settings:
  llm_provider: openai
  default_path: ~/code
  analysis_enabled: true
```

### Top-Level Sections

```yaml
repositories:     # Repository definitions
settings:         # Global settings
```

---

## Repository Configuration

### Required Fields

Each repository in the `repositories` section defines a fork to manage:

```yaml
repositories:
  - name: django                    # Unique identifier
    fork: username/django           # Your fork (username/repo)
    upstream: django/django         # Original repository (owner/repo)
    local_path: ~/code/django      # Local clone path
    skills: [python, web, orm]     # Your relevant skills
```

### Optional Fields

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]
    analysis_enabled: true          # Enable AI analysis for this repo
    sync_frequency: daily           # Sync schedule (daily, weekly, monthly, manual)
    language: python                # Primary programming language
    description: "Django web framework fork"
    tags: [web-framework, orm]     # Additional tags for organization
```

### Repository Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for the repository |
| `fork` | string | Yes | Your fork (username/repo) |
| `upstream` | string | Yes | Original repository (owner/repo) |
| `local_path` | string | Yes | Local clone path |
| `skills` | array | No | List of relevant skills |
| `analysis_enabled` | boolean | No | Enable AI analysis (default: true) |
| `sync_frequency` | string | No | Sync schedule (default: manual) |
| `language` | string | No | Primary programming language |
| `description` | string | No | Repository description |
| `tags` | array | No | Additional tags for organization |

---

## Settings Configuration

### Global Settings

Global settings that apply to all operations:

```yaml
settings:
  llm_provider: openai              # LLM provider (openai, anthropic, custom)
  default_path: ~/code              # Default repository path
  analysis_enabled: true            # Global AI analysis setting
  max_repos_per_batch: 10          # Batch processing limit
  git_timeout: 300                 # Git operation timeout (seconds)
  rate_limit_delay: 1.0            # API call delay (seconds)
  log_level: INFO                  # Logging level
```

### Settings Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `llm_provider` | string | openai | LLM provider (openai, anthropic, custom) |
| `default_path` | string | ~/code | Default repository path |
| `analysis_enabled` | boolean | true | Global AI analysis setting |
| `max_repos_per_batch` | integer | 10 | Maximum repositories per batch |
| `git_timeout` | integer | 300 | Git operation timeout (seconds) |
| `rate_limit_delay` | float | 1.0 | API call delay (seconds) |
| `log_level` | string | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `merge_strategy` | string | ours | Merge conflict strategy (ours, theirs, manual) |
| `backup_enabled` | boolean | true | Enable backup functionality |
| `backup_retention_days` | integer | 30 | Backup retention period (days) |

---

## LLM Provider Configuration

### OpenAI Configuration

```yaml
settings:
  llm_provider: openai
  openai:
    api_key_env: OPENAI_API_KEY    # Environment variable name
    default_model: gpt-3.5-turbo   # Default model
    max_tokens: 4000               # Maximum tokens per request
    temperature: 0.7               # Response creativity (0.0-1.0)
    timeout: 60                    # API timeout (seconds)
```

### Anthropic Configuration

```yaml
settings:
  llm_provider: anthropic
  anthropic:
    api_key_env: ANTHROPIC_API_KEY # Environment variable name
    default_model: claude-3-sonnet # Default model
    max_tokens: 4000               # Maximum tokens per request
    temperature: 0.7               # Response creativity (0.0-1.0)
    timeout: 60                    # API timeout (seconds)
```

### Custom Endpoint Configuration

```yaml
settings:
  llm_provider: custom
  custom:
    api_key_env: CUSTOM_API_KEY    # Environment variable name
    endpoint_url: https://api.example.com/v1/chat/completions
    default_model: custom-model    # Model name
    max_tokens: 4000               # Maximum tokens per request
    timeout: 60                    # API timeout (seconds)
```

---

## GitHub Integration

### GitHub API Configuration

```yaml
settings:
  github:
    token_env: GITHUB_TOKEN         # Environment variable name
    api_url: https://api.github.com # GitHub API URL
    timeout: 30                    # API timeout (seconds)
    user_agent: GitCo/0.1.0       # User agent string
```

### Rate Limiting Configuration

```yaml
settings:
  rate_limiting:
    github_requests_per_minute: 30  # GitHub API requests per minute
    github_requests_per_hour: 5000  # GitHub API requests per hour
    llm_requests_per_minute: 60     # LLM API requests per minute
    llm_requests_per_hour: 1000     # LLM API requests per hour
    retry_attempts: 3               # Number of retry attempts
    retry_delay: 1.0               # Delay between retries (seconds)
```

---

## Cost Optimization

### Cost Management Configuration

```yaml
settings:
  cost_management:
    enabled: true                   # Enable cost tracking
    daily_limit_usd: 5.0           # Daily cost limit
    monthly_limit_usd: 50.0        # Monthly cost limit
    per_request_limit_usd: 0.10    # Per-request cost limit
    token_optimization: true        # Enable token optimization
    cost_alert_threshold: 0.8      # Alert when 80% of limit reached
```

### Token Optimization

```yaml
settings:
  token_optimization:
    enabled: true                   # Enable token optimization
    max_tokens_per_request: 4000   # Maximum tokens per request
    prompt_truncation: true         # Enable prompt truncation
    compression_enabled: true       # Enable response compression
    cache_enabled: true            # Enable response caching
```

---

## Rate Limiting

### API Rate Limiting

```yaml
settings:
  rate_limiting:
    # GitHub API limits
    github_requests_per_minute: 30
    github_requests_per_hour: 5000

    # LLM API limits
    llm_requests_per_minute: 60
    llm_requests_per_hour: 1000

    # General settings
    retry_attempts: 3
    retry_delay: 1.0
    exponential_backoff: true
    jitter: true
```

### Adaptive Rate Limiting

```yaml
settings:
  adaptive_rate_limiting:
    enabled: true                   # Enable adaptive rate limiting
    learning_rate: 0.1             # Learning rate for adaptation
    min_delay: 0.5                 # Minimum delay between requests
    max_delay: 5.0                 # Maximum delay between requests
    success_threshold: 0.9         # Success rate threshold
```

---

## Environment Variables

### Required Environment Variables

```bash
# GitHub integration
export GITHUB_TOKEN="your-github-token"

# LLM provider (choose one)
export OPENAI_API_KEY="your-openai-api-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Optional Environment Variables

```bash
# Custom configuration path
export GITCO_CONFIG_PATH="/path/to/config.yml"

# Custom log level
export GITCO_LOG_LEVEL="DEBUG"

# Custom log file
export GITCO_LOG_FILE="/path/to/gitco.log"

# Disable color output
export GITCO_NO_COLOR="true"
```

### Environment Variable Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub API token | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required for OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required for Anthropic |
| `GITCO_CONFIG_PATH` | Custom config path | ~/.gitco/config.yml |
| `GITCO_LOG_LEVEL` | Log level | INFO |
| `GITCO_LOG_FILE` | Log file path | ~/.gitco/gitco.log |
| `GITCO_NO_COLOR` | Disable colors | false |

---

## Validation

### Configuration Validation

GitCo provides comprehensive configuration validation:

```bash
# Basic validation
gitco config validate

# Detailed validation
gitco config validate --detailed

# Strict validation
gitco config validate --strict

# Export validation report
gitco config validate --export validation-report.json
```

### Validation Checks

GitCo validates the following aspects:

- **YAML Syntax**: Valid YAML structure
- **Required Fields**: All required fields are present
- **Field Types**: Correct data types for all fields
- **URL Format**: Valid repository URLs
- **Path Existence**: Local paths exist and are accessible
- **Environment Variables**: Required environment variables are set
- **API Connectivity**: API endpoints are accessible
- **Repository Structure**: Repository structure is valid

---

## Examples

### Minimal Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django

settings:
  llm_provider: openai
  default_path: ~/code
```

### Advanced Configuration

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]
    analysis_enabled: true
    sync_frequency: daily
    language: python

  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async]
    analysis_enabled: true
    sync_frequency: weekly
    language: python

settings:
  llm_provider: anthropic
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 5
  git_timeout: 300
  rate_limit_delay: 1.0
  log_level: INFO

  # GitHub settings
  github:
    token_env: GITHUB_TOKEN
    api_url: https://api.github.com

  # Rate limiting
  rate_limiting:
    github_requests_per_minute: 30
    github_requests_per_hour: 5000
    llm_requests_per_minute: 60
    llm_requests_per_hour: 1000

  # Cost optimization
  cost_management:
    enabled: true
    daily_limit_usd: 5.0
    monthly_limit_usd: 50.0
    per_request_limit_usd: 0.10
    token_optimization: true

  # LLM provider settings
  anthropic:
    api_key_env: ANTHROPIC_API_KEY
    default_model: claude-3-sonnet
    max_tokens: 4000
    temperature: 0.7
    timeout: 60
```

### Development Configuration

```yaml
repositories:
  - name: test-repo
    fork: username/test-repo
    upstream: owner/test-repo
    local_path: ~/code/test-repo
    skills: [python, testing]
    analysis_enabled: false

settings:
  llm_provider: openai
  default_path: ~/code
  analysis_enabled: false
  log_level: DEBUG
  git_timeout: 60
  rate_limit_delay: 2.0

  # Development-specific settings
  development:
    debug_mode: true
    verbose_logging: true
    mock_apis: false
```

### Production Configuration

```yaml
repositories:
  - name: production-repo
    fork: username/production-repo
    upstream: owner/production-repo
    local_path: ~/code/production-repo
    skills: [python, production, monitoring]
    analysis_enabled: true
    sync_frequency: daily

settings:
  llm_provider: openai
  default_path: ~/code
  analysis_enabled: true
  log_level: INFO
  git_timeout: 600
  rate_limit_delay: 1.0

  # Production-specific settings
  backup:
    enabled: true
    retention_days: 90
    compression_level: 6

  monitoring:
    enabled: true
    metrics_export: true
    alerting: true
```

This comprehensive configuration guide covers all available options for customizing GitCo to your specific needs. For more information about specific features, see the [Usage Guide](usage.md) and [CLI Reference](cli.md).
