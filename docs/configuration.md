# GitCo Configuration Guide

This guide covers all configuration options available in GitCo, from basic setup to advanced customization.

## Table of Contents

1. [Overview](#overview)
2. [Configuration File Structure](#configuration-file-structure)
3. [Repository Configuration](#repository-configuration)
4. [Settings Configuration](#settings-configuration)
5. [LLM Provider Configuration](#llm-provider-configuration)
6. [GitHub Integration](#github-integration)
7. [Cost Optimization](#cost-optimization)
8. [Rate Limiting](#rate-limiting)
9. [Interactive Setup](#interactive-setup)
10. [Environment Variables](#environment-variables)
11. [Validation](#validation)
12. [Examples](#examples)

---

## Overview

GitCo uses a YAML configuration file to manage all settings, repositories, and integration options. The configuration file is typically located at `~/.gitco/config.yml` and can be customized for different environments.

### Configuration File Location

```bash
# Default location
~/.gitco/config.yml

# Custom location (specified with --config)
/path/to/custom/config.yml
```

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

---

## Configuration File Structure

### Top-Level Sections

```yaml
repositories:     # Repository definitions
settings:         # Global settings
```

### Repository Configuration

Each repository in the `repositories` section defines a fork to manage:

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
```

### Settings Configuration

Global settings that apply to all operations:

```yaml
settings:
  llm_provider: openai
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
  git_timeout: 300
  rate_limit_delay: 1.0
  log_level: INFO
```

---

## Repository Configuration

### Required Fields

**`name`** (string, required)
- Unique identifier for the repository
- Used in commands like `gitco sync --repo <name>`

**`fork`** (string, required)
- Your fork of the repository
- Format: `username/repository` or full URL

**`upstream`** (string, required)
- Original repository to sync from
- Format: `owner/repository` or full URL

**`local_path`** (string, required)
- Local path where the repository is cloned
- Supports `~` for home directory expansion

### Optional Fields

**`skills`** (list of strings, optional)
- Skills associated with this repository
- Used for contribution discovery and matching
- Examples: `[python, web, api, testing]`

**`analysis_enabled`** (boolean, default: true)
- Whether to enable AI analysis for this repository
- Can be disabled to save costs

**`sync_frequency`** (string, optional)
- Recommended sync frequency
- Values: `daily`, `weekly`, `monthly`, `manual`

**`language`** (string, optional)
- Primary programming language
- Used for skill matching and filtering

### Repository Examples

```yaml
repositories:
  # Simple repository
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

  # Repository with custom settings
  - name: fastapi
    fork: username/fastapi
    upstream: tiangolo/fastapi
    local_path: ~/code/fastapi
    skills: [python, api, async]
    analysis_enabled: false
    sync_frequency: weekly
    language: python

  # Repository with full URLs
  - name: requests
    fork: https://github.com/username/requests.git
    upstream: https://github.com/psf/requests.git
    local_path: ~/code/requests
    skills: [python, http, networking]
```

---

## Settings Configuration

### LLM Provider Settings

**`llm_provider`** (string, default: "openai")
- Primary LLM provider for analysis
- Values: `openai`, `anthropic`, `custom`

**`llm_openai_api_url`** (string, optional)
- Custom OpenAI API URL
- Default: Uses OpenAI's standard API

**`llm_anthropic_api_url`** (string, optional)
- Custom Anthropic API URL
- Default: Uses Anthropic's standard API

**`llm_custom_endpoints`** (dict, optional)
- Custom LLM endpoint configurations
- Format: `{"provider_name": "endpoint_url"}`

### GitHub Integration Settings

**`github_token_env`** (string, default: "GITHUB_TOKEN")
- Environment variable name for GitHub token

**`github_username_env`** (string, default: "GITHUB_USERNAME")
- Environment variable name for GitHub username

**`github_password_env`** (string, default: "GITHUB_PASSWORD")
- Environment variable name for GitHub password

**`github_api_url`** (string, default: "https://api.github.com")
- GitHub API base URL

**`github_timeout`** (integer, default: 30)
- GitHub API timeout in seconds

**`github_max_retries`** (integer, default: 3)
- Maximum retries for GitHub API calls

### General Settings

**`default_path`** (string, default: "~/code")
- Default path for repository cloning

**`analysis_enabled`** (boolean, default: true)
- Global setting for AI analysis

**`max_repos_per_batch`** (integer, default: 10)
- Maximum repositories to process in batch

**`git_timeout`** (integer, default: 300)
- Git operation timeout in seconds

**`rate_limit_delay`** (float, default: 1.0)
- Delay between API calls in seconds

**`log_level`** (string, default: "INFO")
- Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Rate Limiting Settings

**`github_rate_limit_per_minute`** (integer, default: 30)
- GitHub API rate limit per minute

**`github_rate_limit_per_hour`** (integer, default: 5000)
- GitHub API rate limit per hour

**`github_burst_limit`** (integer, default: 5)
- GitHub API burst limit

**`llm_rate_limit_per_minute`** (integer, default: 60)
- LLM API rate limit per minute

**`llm_rate_limit_per_hour`** (integer, default: 1000)
- LLM API rate limit per hour

**`llm_burst_limit`** (integer, default: 10)
- LLM API burst limit

**`min_request_interval`** (float, default: 0.1)
- Minimum interval between requests

---

## LLM Provider Configuration

### OpenAI Configuration

```yaml
settings:
  llm_provider: openai
  llm_openai_api_url: https://api.openai.com/v1  # Optional custom URL
```

**Environment Variables:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Anthropic Configuration

```yaml
settings:
  llm_provider: anthropic
  llm_anthropic_api_url: https://api.anthropic.com  # Optional custom URL
```

**Environment Variables:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Custom Endpoints

```yaml
settings:
  llm_provider: custom
  llm_custom_endpoints:
    local_llm: "http://localhost:8000/v1"
    enterprise_llm: "https://api.company.com/v1"
```

**Environment Variables:**
```bash
export LOCAL_LLM_API_KEY="your-local-api-key"
export ENTERPRISE_LLM_API_KEY="your-enterprise-api-key"
```

---

## GitHub Integration

### Authentication Methods

**Personal Access Token (Recommended):**
```bash
export GITHUB_TOKEN="your-github-token"
```

**Username/Password (Less Secure):**
```bash
export GITHUB_USERNAME="your-username"
export GITHUB_PASSWORD="your-password"
```

### GitHub Enterprise

```yaml
settings:
  github_api_url: "https://github.company.com/api/v3"
```

**Environment Variables:**
```bash
export GITHUB_TOKEN="your-enterprise-token"
```

---

## Cost Optimization

### Cost Tracking Settings

**`enable_cost_tracking`** (boolean, default: true)
- Enable cost tracking for LLM API usage

**`enable_token_optimization`** (boolean, default: true)
- Enable token optimization to reduce costs

**`max_tokens_per_request`** (integer, default: 4000)
- Maximum tokens per LLM request

**`max_cost_per_request_usd`** (float, default: 0.10)
- Maximum cost per request in USD

**`max_daily_cost_usd`** (float, default: 5.0)
- Maximum daily cost in USD

**`max_monthly_cost_usd`** (float, default: 50.0)
- Maximum monthly cost in USD

**`cost_log_file`** (string, default: "~/.gitco/cost_log.json")
- Path to cost tracking log file

### Cost Configuration Example

```yaml
settings:
  enable_cost_tracking: true
  enable_token_optimization: true
  max_tokens_per_request: 4000
  max_cost_per_request_usd: 0.10
  max_daily_cost_usd: 5.0
  max_monthly_cost_usd: 50.0
  cost_log_file: ~/.gitco/cost_log.json
```

---

## Rate Limiting

### Rate Limit Configuration

GitCo includes intelligent rate limiting to respect API limits and avoid rate limit errors.

**GitHub Rate Limiting:**
```yaml
settings:
  github_rate_limit_per_minute: 30
  github_rate_limit_per_hour: 5000
  github_burst_limit: 5
```

**LLM Rate Limiting:**
```yaml
settings:
  llm_rate_limit_per_minute: 60
  llm_rate_limit_per_hour: 1000
  llm_burst_limit: 10
  min_request_interval: 0.1
```

### Rate Limit Monitoring

Check rate limit status:
```bash
gitco github rate-limit-status
gitco github rate-limit-status --detailed
```

---

## Interactive Setup

### Guided Configuration

Use interactive setup for easy configuration:

```bash
gitco init --interactive
```

**Interactive Setup Features:**
- Repository configuration with validation
- LLM provider selection and setup
- GitHub integration configuration
- Cost optimization settings
- Configuration summary and confirmation

### Non-Interactive Setup

Use default settings for quick setup:

```bash
gitco init --non-interactive
```

### Custom Template

Use a custom configuration template:

```bash
gitco init --template /path/to/template.yml
```

---

## Environment Variables

### Core Environment Variables

```bash
# GitHub Integration
export GITHUB_TOKEN="your-github-token"
export GITHUB_USERNAME="your-username"
export GITHUB_PASSWORD="your-password"

# LLM Providers
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Custom LLM Endpoints
export LOCAL_LLM_API_KEY="your-local-api-key"
export ENTERPRISE_LLM_API_KEY="your-enterprise-api-key"
```

### Configuration Override

```bash
# Custom configuration file
export GITCO_CONFIG="/path/to/config.yml"

# Custom log file
export GITCO_LOG_FILE="/path/to/gitco.log"
```

---

## Validation

### Configuration Validation

Validate your configuration:

```bash
# Basic validation
gitco config validate

# Detailed validation
gitco config validate-detailed --detailed

# Export validation report
gitco config validate-detailed --export validation-report.json
```

### Validation Features

**Field Validation:**
- Required fields presence
- Data type validation
- Format validation (URLs, paths)

**Cross-Reference Validation:**
- Repository URL consistency
- Path accessibility
- Provider configuration

**Warning System:**
- Suggest improvements
- Identify potential issues
- Provide optimization recommendations

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

  - name: react
    fork: username/react
    upstream: facebook/react
    local_path: ~/code/react
    skills: [javascript, react, frontend]
    analysis_enabled: false
    sync_frequency: monthly
    language: javascript

settings:
  llm_provider: anthropic
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 5
  git_timeout: 300
  rate_limit_delay: 1.0
  log_level: INFO

  # GitHub settings
  github_token_env: GITHUB_TOKEN
  github_api_url: https://api.github.com
  github_timeout: 30
  github_max_retries: 3

  # Rate limiting
  github_rate_limit_per_minute: 30
  github_rate_limit_per_hour: 5000
  github_burst_limit: 5
  llm_rate_limit_per_minute: 60
  llm_rate_limit_per_hour: 1000
  llm_burst_limit: 10
  min_request_interval: 0.1

  # LLM settings
  llm_anthropic_api_url: https://api.anthropic.com

  # Cost optimization
  enable_cost_tracking: true
  enable_token_optimization: true
  max_tokens_per_request: 4000
  max_cost_per_request_usd: 0.10
  max_daily_cost_usd: 5.0
  max_monthly_cost_usd: 50.0
  cost_log_file: ~/.gitco/cost_log.json
```

### Enterprise Configuration

```yaml
repositories:
  - name: internal-tool
    fork: company/internal-tool
    upstream: company/internal-tool
    local_path: ~/code/internal-tool
    skills: [python, internal, api]
    analysis_enabled: true
    sync_frequency: daily
    language: python

settings:
  llm_provider: custom
  default_path: ~/code

  # GitHub Enterprise
  github_api_url: https://github.company.com/api/v3
  github_token_env: GITHUB_TOKEN

  # Custom LLM endpoint
  llm_custom_endpoints:
    enterprise_llm: "https://api.company.com/v1"

  # Conservative rate limiting
  github_rate_limit_per_minute: 20
  github_rate_limit_per_hour: 3000
  llm_rate_limit_per_minute: 30
  llm_rate_limit_per_hour: 500

  # Cost optimization
  enable_cost_tracking: true
  enable_token_optimization: true
  max_tokens_per_request: 2000
  max_cost_per_request_usd: 0.05
  max_daily_cost_usd: 2.0
  max_monthly_cost_usd: 20.0
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
    sync_frequency: manual
    language: python

settings:
  llm_provider: openai
  default_path: ~/code
  analysis_enabled: false
  max_repos_per_batch: 1
  git_timeout: 60
  rate_limit_delay: 2.0
  log_level: DEBUG

  # Minimal rate limiting for development
  github_rate_limit_per_minute: 10
  github_rate_limit_per_hour: 1000
  llm_rate_limit_per_minute: 20
  llm_rate_limit_per_hour: 500

  # Disable cost tracking for development
  enable_cost_tracking: false
  enable_token_optimization: false
```

This comprehensive configuration guide covers all aspects of GitCo configuration, from basic setup to advanced customization for enterprise environments. The configuration system is designed to be flexible and powerful while remaining easy to use for common scenarios.
