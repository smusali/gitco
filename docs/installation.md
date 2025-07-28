# Installation Guide

This guide will help you install GitCo on your system.

## Prerequisites

Before installing GitCo, ensure you have:

- **Python 3.9 or higher** - GitCo requires Python 3.9+
- **Git** - For repository operations
- **pip** - Python package installer

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/41technologies/gitco.git
   cd gitco
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Install Development Dependencies (Optional)

For development and testing:

```bash
pip install -r requirements-dev.txt
```

## Verification

After installation, verify GitCo is working:

```bash
# Check if gitco command is available
gitco --help

# Check version
gitco --version

# Test basic commands
gitco init
```

**Note:** The CLI framework, configuration management, and logging system are implemented. Full functionality will be added in subsequent commits.

## Configuration

### 1. Initialize Configuration

```bash
gitco init
```

This creates a `gitco-config.yml` file in your current directory.

### 2. Set Up LLM API Key

For AI-powered features, you'll need to set up an API key:

```bash
# For OpenAI
export AETHERIUM_API_KEY="your-openai-api-key"
export AETHERIUM_LLM_PROVIDER="openai"

# For Anthropic
export AETHERIUM_API_KEY="your-anthropic-api-key"
export AETHERIUM_LLM_PROVIDER="anthropic"
```

### 3. Configure Repositories

Edit the generated `gitco-config.yml` file to add your repositories:

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]

settings:
  llm_provider: openai
  api_key_env: AETHERIUM_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

## Troubleshooting

### Common Issues

1. **Command not found:**
   - Ensure you're in the correct virtual environment
   - Check that the installation completed successfully

2. **Import errors:**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version`

3. **Permission errors:**
   - Use `pip install --user` for user-level installation
   - Or use a virtual environment

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/41technologies/gitco/issues)
3. Create a new issue with detailed information

## Next Steps

After installation, see the [Usage Guide](usage.md) to get started with GitCo. 
