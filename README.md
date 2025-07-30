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
- **Enhanced security update and deprecation highlighting** with advanced pattern detection
- **SecurityDeprecationDetector** for sophisticated security and deprecation analysis
- **CVE reference detection** and highlighting in security updates
- **Security severity classification** (critical, high, medium, low) with color-coded display
- **Deprecation severity classification** (high, medium, low) with color-coded display
- **Security pattern detection** for vulnerability fixes, authentication, authorization, encryption
- **Deprecation pattern detection** for API, feature, dependency, and configuration deprecations
- **Detailed security update reporting** with CVE IDs and remediation guidance
- **Detailed deprecation reporting** with replacement suggestions and migration paths
- **Enhanced breaking change detection** with pattern-based analysis
- **API signature change detection** for function and class definitions
- **Configuration file change detection** with filename and content patterns
- **Database schema change detection** for migration and schema files
- **Dependency change detection** for package management files
- **Commit message analysis** for explicit breaking change indicators
- **Severity-based categorization** (high, medium, low) for breaking changes
- **Migration guidance generation** for detected breaking changes
- **Enhanced commit diff analysis** with detailed content analysis
- **Intelligent diff pattern recognition** for test, documentation, and configuration changes
- **File type and line count statistics** for comprehensive change overview
- **Multi-commit analysis** with detailed diff content for recent commits
- **Specific commit analysis** with targeted diff examination
- **Commit categorization** by type (feature, fix, docs, refactor, test, chore)
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
- Matches issues to your skills using intelligent skill-based matching algorithm
- Provides personalized contribution recommendations with confidence scores
- Supports exact, partial, related, and language-based skill matching
- Difficulty level detection (beginner, intermediate, advanced)
- Time estimation for issues (quick, medium, long)
- Skill filtering and label filtering for targeted discovery
- Export functionality for discovery results in JSON format
- Rich CLI output with detailed recommendation information

### 📈 **Contribution History Tracking**
- Persistent storage of contribution history across repositories
- Automatic skill extraction from GitHub issues and pull requests
- Impact score calculation based on engagement and contribution type
- Skill development tracking and timeline analysis
- Personalized contribution recommendations based on historical patterns
- Repository familiarity scoring for improved recommendations
- Recent activity tracking with detailed contribution information
- Export functionality for contribution statistics in JSON format
- Integration with discovery engine for history-aware recommendations

### 📊 **Repository Health Insights**
- Comprehensive health metrics calculation for all repositories
- Activity metrics including commit counts and contributor statistics
- GitHub metrics integration (stars, forks, issues, language, topics)
- Sync health tracking with status and last sync information
- Engagement metrics with contributor engagement scoring
- Trending metrics for repository growth analysis
- Overall health scoring with weighted factors (activity, sync, engagement, GitHub, stability)
- Health status classification (excellent, good, fair, poor, critical)
- Trending repository identification based on growth metrics
- Declining repository identification based on activity metrics
- Health summary display with repository statistics
- Detailed repository health information with rich formatting
- Export functionality for health data in JSON format

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
  llm_provider: openai  # or anthropic, ollama, local
  api_key_env: AETHERIUM_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
  ollama_host: http://localhost:11434  # for ollama provider
  ollama_model: llama2  # for ollama provider
```

### 3. Set Up LLM API Key
```bash
export AETHERIUM_API_KEY="your-api-key-here"
export AETHERIUM_LLM_PROVIDER="openai"  # or anthropic, ollama
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

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Set minimum confidence score
gitco discover --min-confidence 0.5

# Limit results
gitco discover --limit 10

# Export results
gitco discover --export results.json

# Combine filters
gitco discover --skill python --label "good first issue" --limit 5

### 6. Track Contribution History
```bash
# Sync contribution history from GitHub
gitco contributions sync-history --username your-username

# View contribution statistics
gitco contributions stats

# View stats for last 30 days
gitco contributions stats --days 30

# Export statistics
gitco contributions stats --export stats.json

# Get personalized recommendations
gitco contributions recommendations

# Filter recommendations by skill
gitco contributions recommendations --skill python

# Filter by repository
gitco contributions recommendations --repository django

# Limit recommendations
gitco contributions recommendations --limit 5
```
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

# Analyze with specific LLM provider
gitco analyze --repo fastapi --provider anthropic

# Export analysis results
gitco analyze --repo fastapi --export analysis.json

# Find contribution opportunities
gitco discover

# Filter by skill
gitco discover --skill python

# Filter by label
gitco discover --label "good first issue"

# Set minimum confidence score
gitco discover --min-confidence 0.5

# Export discovery results
gitco discover --export results.json

# Track contribution history
gitco contributions sync-history --username your-username

# View contribution statistics
gitco contributions stats

# Get personalized recommendations
gitco contributions recommendations

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

GitCo provides intelligent analysis of repository changes using multiple LLM providers:

**Supported Providers:**
- **OpenAI**: GPT-3.5/GPT-4 models (requires API key)
- **Anthropic**: Claude models (requires API key)
- **Ollama**: Local LLM models (requires Ollama server)

```bash
# Analyze specific repository
gitco analyze --repo fastapi

# Analyze with custom prompt
gitco analyze --repo fastapi --prompt "Focus on breaking changes"

# Analyze with specific LLM provider
gitco analyze --repo fastapi --provider openai

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

### Contribution Discovery

GitCo provides intelligent contribution opportunity discovery using skill-based matching:

**Skill Matching:**
- **Exact Matches**: Direct skill matches in issue content
- **Partial Matches**: Skill-related terms and synonyms
- **Related Matches**: Related technologies and frameworks
- **Language Matches**: Repository language alignment

**Features:**
- **Difficulty Detection**: Beginner, intermediate, or advanced issues
- **Time Estimation**: Quick, medium, or long-term contributions
- **Confidence Scoring**: 0.0-1.0 confidence for each recommendation
- **Skill Filtering**: Filter by specific skills or technologies
- **Label Filtering**: Filter by GitHub labels (e.g., "good first issue")
- **Export Support**: Export results to JSON for further analysis

```bash
# Discover opportunities with skill filtering
gitco discover --skill python --min-confidence 0.7

# Find beginner-friendly issues
gitco discover --label "good first issue" --skill javascript

# Export results for analysis
gitco discover --export opportunities.json
```

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

### GitHub API Integration

GitCo provides comprehensive GitHub API integration for repository and issue management:

**Supported Authentication Methods:**
- **Personal Access Token**: Most secure and recommended method
- **Username/Password**: Basic authentication (less secure)
- **Environment Variables**: Automatic detection of credentials

```bash
# Test GitHub API connection
gitco github test-connection

# Get repository information
gitco github get-repo --repo owner/repository

# Get issues from repository
gitco github get-issues --repo owner/repository

# Get issues with filters
gitco github get-issues --repo owner/repository --state open --labels "bug,help wanted" --limit 10

# Get issues with advanced filtering
gitco github get-issues --repo owner/repository --state open --labels "bug,help wanted" --exclude-labels "wontfix" --created-after "2024-01-01" --detailed

# Get issues from multiple repositories
gitco github get-issues-multi --repos "owner/repo1,owner/repo2" --labels "good first issue" --export results.json
```

**Environment Variables:**
```bash
# Set GitHub token (recommended)
export GITHUB_TOKEN="your-personal-access-token"

# Or set username/password (less secure)
export GITHUB_USERNAME="your-username"
export GITHUB_PASSWORD="your-password"
```

**Configuration Settings:**
```yaml
settings:
  github_token_env: GITHUB_TOKEN
  github_username_env: GITHUB_USERNAME
  github_password_env: GITHUB_PASSWORD
  github_api_url: https://api.github.com
  github_timeout: 30
  github_max_retries: 3
```

**Key Features:**
- **Rate Limiting**: Automatic rate limit handling with retry logic
- **Error Handling**: Comprehensive error handling for API failures
- **Authentication**: Multiple authentication methods with fallback support
- **Repository Info**: Detailed repository metadata and statistics
- **Issue Management**: Advanced issue fetching with comprehensive filtering
- **Multi-Repository Support**: Fetch issues from multiple repositories in batch
- **Advanced Filtering**: Filter by labels, exclude labels, date ranges, assignees, milestones
- **Export Functionality**: Export issue results to JSON format
- **Detailed Information**: Show comprehensive issue details with --detailed flag
- **Connection Testing**: Validate GitHub API connectivity and credentials
- **Rich Output**: Color-coded and formatted API response display

**Rate Limiting:**
- Automatically handles GitHub API rate limits
- Implements exponential backoff for retries
- Displays current rate limit status
- Waits for rate limit reset when needed

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
  llm_provider: openai  # or anthropic, ollama, local
  api_key_env: AETHERIUM_API_KEY
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
  ollama_host: http://localhost:11434  # for ollama provider
  ollama_model: llama2  # for ollama provider
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
