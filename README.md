# GitCo ✨

**A simple CLI tool for intelligent OSS fork management and contribution discovery.**

GitCo transforms the tedious process of managing multiple OSS forks into an intelligent, context-aware workflow. It combines automated synchronization with AI-powered insights to help developers stay current with upstream changes and discover meaningful contribution opportunities.

## 🚀 Features

### 🔄 **Intelligent Fork Synchronization**
- Automated sync of multiple repositories from YAML configuration
- Safe stashing of local changes before updates
- Automatic detection of default branches (main/master)
- Batch processing with colored, informative output
- Built-in error handling and recovery mechanisms
- **Automatic retry for network operations** with configurable max retries
- **Recoverable error detection** for timeouts, rate limits, and connection issues
- **Enhanced error reporting** with retry attempt information and recovery status
- **Improved stash restoration** with failure handling and warning messages
- **Better progress tracking** with retry status displayed in CLI output
- Comprehensive stash management with automatic restoration
- Detection of uncommitted changes before operations
- Atomic stash-and-restore operations for data safety
- **Rich progress indicators** with real-time updates and colored status messages
- **Enhanced CLI output** with success, error, warning, and info panels
- **Progress bars** for repository operations with spinners and time tracking
- **Color-coded status** for different operation types (started, completed, failed, skipped)

### 🧠 **AI-Powered Change Analysis**
- **OpenAI API integration** for intelligent change analysis
- Generates human-readable summaries of upstream changes
- Identifies breaking changes, new features, and critical fixes
- Analyzes commit messages and diff content for context
- Highlights security updates and deprecations
- Provides confidence scoring for analysis results
- Rich console output with color-coded analysis sections
- Export analysis results to JSON format
- Custom prompt support for specialized analysis
- Integration with sync command for automatic analysis

### 🎯 **Contribution Discovery**
- Scans repositories for "good first issue" and "help wanted" labels
- Matches issues to your past contributions and skills
- Provides personalized contribution recommendations
- Tracks your contribution history across projects

### 📊 **Repository Health Insights**
- Shows activity levels and contributor engagement
- Identifies trending repositories in your fork list
- Highlights repositories that need attention
- Provides contribution impact metrics

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Git installed and configured

### Install from Source
```bash
# Clone the repository
git clone https://github.com/41technologies/gitco.git
cd gitco

# Install in development mode
pip install -e .
```

### Install Dependencies
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

## 🛠️ Quick Start

### 1. Initialize Configuration
```bash
gitco init
```

This creates a `gitco-config.yml` file in your current directory.

**Note:** The CLI framework, configuration management, logging system, and CI pipeline are now implemented. Full functionality will be added in subsequent commits.

### 2. Configure Your Repositories
Edit `gitco-config.yml` to add your repositories:

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

settings:
  llm_provider: openai  # or anthropic, local
  api_key_env: AETHERIUM_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

### 3. Set Up LLM API Key
```bash
export AETHERIUM_API_KEY="your-api-key-here"
export AETHERIUM_LLM_PROVIDER="openai"  # or anthropic
```

### 4. Sync Your Repositories
```bash
# Sync all repositories
gitco sync

# Sync specific repository
gitco sync --repo django

# Sync with detailed analysis
gitco sync --analyze
```

### 5. Discover Contribution Opportunities
```bash
# Find all opportunities
gitco discover

# Find issues by skill/language
gitco discover --skill python --label "good first issue"
```

## 📖 Usage

### Basic Commands

```bash
# Initialize configuration
gitco init

# Sync all repositories
gitco sync

# Sync specific repository
gitco sync --repo django

# Get AI summary of changes
gitco analyze --repo fastapi

# Analyze with custom prompt
gitco analyze --repo fastapi --prompt "Focus on security implications"

# Export analysis results
gitco analyze --repo fastapi --export analysis.json

# Find contribution opportunities
gitco discover

# Show repository status
gitco status

# Get help
gitco help

# Validate Git repositories
gitco validate-repo --path ~/code/django
gitco validate-repo --recursive --detailed

# Manage upstream remotes
gitco upstream add --repo ~/code/django --url git@github.com:django/django.git
gitco upstream validate-upstream --repo ~/code/django
gitco upstream fetch --repo ~/code/django
```

### AI Analysis

GitCo provides intelligent analysis of repository changes using OpenAI's API:

```bash
# Analyze specific repository
gitco analyze --repo fastapi

# Analyze with custom prompt
gitco analyze --repo fastapi --prompt "Focus on breaking changes"

# Export analysis to JSON
gitco analyze --repo fastapi --export analysis.json

# Sync with automatic analysis
gitco sync --analyze
```

The analysis provides:
- **Summary**: Human-readable overview of changes
- **Breaking Changes**: API changes that may affect existing code
- **New Features**: New functionality added
- **Bug Fixes**: Issues resolved
- **Security Updates**: Security-related changes
- **Deprecations**: Deprecated functionality
- **Recommendations**: Suggestions for contributors

### Upstream Remote Management

GitCo provides comprehensive upstream remote management functionality:

```bash
# Add or update upstream remote
gitco upstream add --repo ~/code/django --url git@github.com:django/django.git

# Remove upstream remote
gitco upstream remove --repo ~/code/django

# Update upstream remote URL
gitco upstream update --repo ~/code/django --url git@github.com:new/django.git

# Validate upstream remote configuration
gitco upstream validate-upstream --repo ~/code/django

# Fetch latest changes from upstream
gitco upstream fetch --repo ~/code/django

# Merge upstream changes into current branch
gitco upstream merge --repo ~/code/django

# Merge specific branch from upstream
gitco upstream merge --repo ~/code/django --branch develop

# Resolve merge conflicts automatically
gitco upstream merge --repo ~/code/django --resolve --strategy ours
gitco upstream merge --repo ~/code/django --resolve --strategy theirs

# Abort current merge operation
gitco upstream merge --repo ~/code/django --abort
```

### Merge Operations and Conflict Resolution

GitCo provides advanced merge functionality with automatic conflict detection and resolution:

**Key Features:**
- **Conflict Detection**: Automatically detects merge conflicts and reports conflicted files
- **Resolution Strategies**: Supports 'ours', 'theirs', and 'manual' conflict resolution
- **Safe Operations**: Checks for uncommitted changes before merging
- **Detailed Reporting**: Provides comprehensive merge result information including commit hashes
- **Error Recovery**: Allows aborting failed merges to restore repository state

**Conflict Resolution Strategies:**
- **`ours`**: Keep your local changes in conflicted files
- **`theirs`**: Keep upstream changes in conflicted files
- **`manual`**: Leave conflicts for manual resolution

**How It Works:**
1. Validates repository and upstream remote configuration
2. Checks for uncommitted changes (prevents data loss)
3. Fetches latest changes from upstream
4. Attempts to merge upstream branch into current branch
5. Detects and reports any merge conflicts
6. Provides options for automatic or manual conflict resolution
7. Reports merge success with commit information

### Safe Stashing and Change Management

GitCo provides comprehensive stashing functionality to safely handle local changes during operations:

```bash
# Check for uncommitted changes in a repository
gitco validate-repo --path ~/code/django

# The system automatically detects and stashes changes before sync operations
gitco sync --repo django  # Changes are automatically stashed and restored

# Manual stash management (if needed)
# Note: GitCo handles stashing automatically during sync operations
```

**Key Features:**
- **Automatic Detection**: Detects uncommitted changes before any operation
- **Safe Stashing**: Creates stashes with descriptive messages for easy identification
- **Automatic Restoration**: Restores stashed changes after successful operations
- **Error Recovery**: Attempts to restore stashes even if operations fail
- **Stash Management**: Provides tools to list, apply, and drop stashes when needed

**How It Works:**
1. Before any sync operation, GitCo checks for uncommitted changes
2. If changes exist, they are automatically stashed with a descriptive message
3. The sync operation proceeds with a clean working directory
4. After successful completion, stashed changes are automatically restored
5. If the operation fails, GitCo attempts to restore the stash to preserve your work

### Advanced Usage

```bash
# Sync with detailed analysis
gitco sync --analyze

# Find issues by skill/language
gitco discover --skill python --label "good first issue"

# Export sync report
gitco sync --export report.json

# Schedule sync (cron-friendly)
gitco sync --quiet --log sync.log

# Validate repositories recursively
gitco validate-repo --recursive --detailed
```

### Enhanced CLI Experience

GitCo provides a rich, user-friendly CLI experience with progress indicators and colored output:

**Progress Indicators:**
- **Real-time progress bars** for batch operations with spinners and time tracking
- **Color-coded status messages** for different operation types
- **Success panels** with detailed completion information and next steps
- **Error panels** with detailed context and resolution suggestions
- **Info panels** for operation status and informational messages
- **Warning panels** for non-critical issues and recommendations

**Visual Features:**
- **Emojis and icons** for quick visual identification of operation types
- **Color coding** for different status levels (green for success, red for errors, blue for info, yellow for warnings)
- **Rich tables** for batch operation summaries with detailed statistics
- **Progress tracking** with percentage completion and time elapsed
- **Status indicators** for repository operations (started, completed, failed, skipped)

**Example Output:**
```
🔄 Starting batch sync for 3 repositories
════════════════════════════════════════════════════════════════════

✅ django                   2.34s - Sync completed
❌ fastapi                  1.87s - Merge conflicts detected
✅ requests                 3.12s - Sync completed

════════════════════════════════════════════════════════════════════
📊 Batch sync Summary
   Total repositories: 3
   Successful: 2
   Failed: 1
   Total duration: 7.33s
   Average per repo: 2.44s

❌ Failed repositories:
  • fastapi: Merge conflicts detected
════════════════════════════════════════════════════════════════════
```

**Quiet Mode:**
For automated usage or cron jobs, use the `--quiet` flag to suppress progress indicators:
```bash
gitco sync --quiet --log sync.log
```

## 🔧 Configuration

### Repository Configuration (`gitco-config.yml`)

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

settings:
  llm_provider: openai  # or anthropic, local
  api_key_env: AETHERIUM_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

### LLM Configuration

Users provide their own API keys through environment variables:

```bash
export AETHERIUM_API_KEY="your-api-key-here"
export AETHERIUM_LLM_PROVIDER="openai"  # or anthropic
```

Supports multiple providers:
- OpenAI (GPT-3.5/GPT-4)
- Anthropic (Claude)
- Local models (Ollama)
- Configurable endpoints for custom deployments

## 🧪 Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/41technologies/gitco.git
cd gitco

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=gitco

# Run specific test file
pytest tests/test_imports.py
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Usage Guide](docs/usage.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ by [FortyOne Technologies](https://github.com/41technologies)
- Inspired by the open source community's need for better fork management tools

## 📊 Status

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/41technologies/gitco/branch/main/graph/badge.svg)](https://codecov.io/gh/41technologies/gitco)

---

**GitCo makes OSS contribution management simple, intelligent, and rewarding. Start contributing more effectively today! 🚀**
