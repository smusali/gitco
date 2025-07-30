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

### Method 3: Development Setup

For contributors and developers:

```bash
# Clone the repository
git clone https://github.com/41technologies/gitco.git
cd gitco

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks for code quality
pre-commit install
```

**Pre-commit Hooks:**
The project uses pre-commit hooks to ensure code quality:
- **Ruff**: Fast Python linting and formatting (includes end-of-file fixing)
- **Black**: Code formatting
- **Conventional Commits**: Commit message validation
- **YAML Validation**: Syntax checking for configuration files
- **End-of-file Fixer**: Ensures files end with newline

To run quality checks manually:
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
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

**Note:** The CLI framework, configuration management, logging system, and CI pipeline are implemented. Full functionality will be added in subsequent commits.

## Configuration

### 1. Initialize Configuration

```bash
gitco init
```

This creates a `gitco-config.yml` file in your current directory.

## LLM Provider Setup

GitCo supports multiple LLM providers for AI-powered analysis. Choose one of the following:

### OpenAI (Recommended)
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Anthropic
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```



**Note:** GitCo uses provider-specific environment variables. Set the appropriate API key for your chosen provider.

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
