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
- **Comprehensive retry mechanisms** for network operations with exponential backoff
- **Configurable retry strategies** (exponential, linear) with jitter support
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
- **JSON export functionality** for comprehensive sync reports
- **Detailed sync metadata** including success rates, timing, and error tracking
- **Export support for single repository and batch operations**
- **Structured JSON output** with repository-specific sync details

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
- **Personalized recommendations based on contribution history and patterns**
- **Repository familiarity bonus for repositories with successful contributions**
- **Skill development pattern analysis for improved matching**
- **Issue type preference analysis (PRs vs Issues)**
- **Difficulty preference analysis based on past successful contributions**
- **Repository activity pattern analysis for engagement scoring**
- Supports exact, partial, related, and language-based skill matching
- Difficulty level detection (beginner, intermediate, advanced)
- Time estimation for issues (quick, medium, long)
- Skill filtering and label filtering for targeted discovery
- **Enhanced CLI output with confidence indicators and categorized recommendations**
- **Grouped recommendation display (High Confidence, Good Matches, Exploration)**
- **Personalized insights and tips based on contribution history**
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
- **CSV export functionality for detailed contribution data**
- **Automatic format detection based on file extension (.csv or .json)**
- **Separate statistics CSV file generation with summary metrics**
- **Direct contribution data export with filtering by time period**
- Integration with discovery engine for history-aware recommendations
- **Enhanced impact metrics with trend analysis over 30d and 7d periods**

### 📊 **Enhanced Logging & Performance Tracking**
- **Detailed logging with file output and log rotation**
- **Structured logging with context and performance tracking**
- **Log rotation with configurable file size and backup count**
- **Detailed log format with function names and line numbers**
- **Performance metrics tracking for all operations**
- **API interaction logging with timing and status codes**
- **Repository operation logging with detailed status tracking**
- **Validation result logging with comprehensive details**
- **Configuration change logging with structured data**
- **Error logging with full stack traces and context**
- **Performance summary display with rich formatting**
- **Log export functionality in JSON and CSV formats**
- **New `logs` command for viewing and exporting log data**
- **Enhanced logging configuration options in CLI commands**
- **High-impact and critical contribution identification and tracking**
- **Skill-based and repository-based impact scoring**
- **Contribution velocity tracking (contributions per day over 30 days)**
- **Skill growth rate analysis with trending and declining skill identification**
- **Repository engagement trend analysis with engagement scoring**
- **Advanced metrics including collaboration, recognition, influence, and sustainability scores**
- **Comprehensive trending analysis with detailed CLI output**

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
- **Repository overview dashboard with comprehensive metrics display**
- **Filtering capabilities for repositories by health status (healthy, needs_attention, critical)**
- **Sorting capabilities for repositories by metrics (health, activity, stars, forks, engagement)**
- **Visual health status indicators with emoji-based status display**
- **Sync status tracking with color-coded status indicators**
- **Activity bars showing recent commit activity with visual indicators**
- **Summary statistics panels showing key metrics at a glance**
- **Alert system for repositories needing attention (health issues, sync problems)**
- **Rich table display with comprehensive repository metrics**
- **Summary panels showing health status, sync status, popularity, and community engagement**

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
# Interactive guided setup (recommended)
gitco init --interactive

# Non-interactive setup with defaults
gitco init

# Force overwrite existing configuration
gitco init --force

# Use custom template
gitco init --template custom.yml
```

This creates a `~/.gitco/config.yml` file in your home directory with guided setup options.

**Interactive Setup Features:**
- Guided repository configuration with validation
- LLM provider selection (OpenAI, Anthropic)
- GitHub integration setup with authentication options
- General settings configuration with default paths
- Skill-based repository configuration
- Configuration summary and confirmation

### 2. Configure Your Repositories
Edit `~/.gitco/config.yml` to add your repositories:

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
  llm_provider: openai  # or anthropic, custom
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
  # Optional: Custom LLM endpoints
  # llm_openai_api_url: https://api.openai.com/v1
  # llm_anthropic_api_url: https://api.anthropic.com
  # llm_custom_endpoints:
  #   my_custom_llm: https://api.mycompany.com/v1/chat/completions
```

### 3. Set Up LLM API Key
```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"

# For custom endpoints
export MY_CUSTOM_LLM_API_KEY="your-custom-api-key-here"
```

### Custom LLM Endpoints

GitCo supports custom LLM endpoints for enterprise deployments and self-hosted models:

```yaml
settings:
  # Custom API endpoints
  llm_openai_api_url: https://api.openai.com/v1  # Custom OpenAI endpoint
  llm_anthropic_api_url: https://api.anthropic.com  # Custom Anthropic endpoint

  # Custom LLM providers
  llm_custom_endpoints:
    my_custom_llm: https://api.mycompany.com/v1/chat/completions
    local_llm: http://localhost:11434/v1/chat/completions
```

**Usage:**
```bash
# Use custom provider
gitco analyze --repo django --provider my_custom_llm

# Use custom OpenAI endpoint
gitco analyze --repo django --provider openai
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

# Personalized recommendations based on contribution history
gitco discover --personalized

# Show contribution history analysis
gitco discover --show-history

# Personalized discovery with history analysis
gitco discover --personalized --show-history --skill python

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

# Export statistics to CSV
gitco contributions stats --export stats.csv

# Get personalized recommendations
gitco contributions recommendations

# Filter recommendations by skill
gitco contributions recommendations --skill python

# Filter by repository
gitco contributions recommendations --repository django

# Limit recommendations
gitco contributions recommendations --limit 5

# Show detailed trending analysis
gitco contributions trending

# Analyze trends for last 60 days
gitco contributions trending --days 60

# Export trending analysis
gitco contributions trending --export trends.json

# Export trending analysis to CSV
gitco contributions trending --export trends.csv

### 7. Enhanced Logging & Performance Tracking
```bash
# View performance summary
gitco logs

# Export performance summary to JSON
gitco logs --export performance.json

# Export performance summary to CSV
gitco logs --export performance.csv

# Sync with detailed logging
gitco sync --log sync.log --detailed-log

# Sync with log rotation (10MB max file size, 5 backups)
gitco sync --log sync.log --max-log-size 10 --log-backups 5

# Analyze with performance tracking
gitco analyze --repo django --log analysis.log

# Discover with detailed logging
gitco discover --log discovery.log --detailed-log

# Status with performance tracking
gitco status --log status.log
```

# Export contribution data to CSV
gitco contributions export --output contributions.csv

# Export recent contributions (last 30 days)
gitco contributions export --days 30 --output recent.csv

# Export with summary statistics
gitco contributions export --output data.csv --include-stats

# Export to JSON format
gitco contributions export --output data.json
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

# Personalized discovery with contribution history
gitco discover --personalized --show-history

# Track contribution history
gitco contributions sync-history --username your-username

# View contribution statistics
gitco contributions stats

# Get personalized recommendations
gitco contributions recommendations

# Show repository status
gitco status

# Show repository overview dashboard
gitco status --overview

# Filter repositories by health status
gitco status --overview --filter healthy
gitco status --overview --filter needs_attention
gitco status --overview --filter critical

# Sort repositories by metrics
gitco status --overview --sort health
gitco status --overview --sort activity
gitco status --overview --sort stars
gitco status --overview --sort forks
gitco status --overview --sort engagement

# Show detailed status information
gitco status --detailed

# Export status data
gitco status --export status.json

# Show repository activity dashboard
gitco activity

# Show activity for specific repository
gitco activity --repo django

# Show detailed activity information
gitco activity --detailed

# Filter repositories by activity level
gitco activity --filter high
gitco activity --filter moderate
gitco activity --filter low

# Sort repositories by activity metrics
gitco activity --sort activity
gitco activity --sort engagement
gitco activity --sort commits
gitco activity --sort contributors

# Show activity dashboard via status command
gitco status --activity
gitco status --activity --detailed

# Monitor system performance
gitco performance

# Show detailed performance metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json
gitco performance --export performance.csv --format csv

# Get comprehensive help with contextual examples
gitco help

# View and export logging information
gitco logs
gitco logs --export performance.json
gitco logs --export performance.csv --format csv

# Validate Git repositories
gitco validate-repo --path ~/code/django
gitco validate-repo --recursive --detailed

# Manage upstream remotes
gitco upstream add --repo ~/code/django --url git@github.com:django/django.git
gitco upstream validate-upstream --repo ~/code/django
gitco upstream fetch --repo ~/code/django
```

### Performance Optimizations

GitCo includes advanced batch processing optimizations for handling large numbers of repositories efficiently:

**Key Optimizations:**
- **System Resource Monitoring**: Automatic detection of available memory and CPU cores
- **Optimal Batch Sizing**: Dynamic batch size calculation based on system resources
- **Thread Pool Reuse**: Efficient connection pooling and thread management
- **Memory Management**: Automatic cache clearing and garbage collection
- **Performance Metrics**: Real-time throughput and resource usage tracking
- **Progress Optimization**: Efficient progress tracking with minimal overhead

**Performance Features:**
- **Resource-Based Scaling**: Automatically scales based on available system resources
- **Memory-Efficient Processing**: Processes repositories in optimal batch sizes
- **Performance Monitoring**: Real-time metrics for throughput and resource usage
- **System Resource Dashboard**: Comprehensive view of CPU, memory, and disk usage
- **Export Capabilities**: Export performance data for analysis and monitoring

```bash
# Monitor system performance
gitco performance

# Show detailed performance metrics
gitco performance --detailed

# Export performance data
gitco performance --export performance.json
gitco performance --export performance.csv --format csv

# Batch processing with optimized workers
gitco sync --batch --max-workers 8
```

### AI Analysis

GitCo provides intelligent analysis of repository changes using multiple LLM providers:

**Supported Providers:**
- **OpenAI**: GPT-3.5/GPT-4 models (requires API key)
- **Anthropic**: Claude models (requires API key)

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
- **Personalized Scoring**: Recommendations based on contribution history and patterns
- **Repository Familiarity**: Bonus scoring for repositories with successful contributions
- **Skill Development Patterns**: Analysis of past skill usage for improved matching
- **Issue Type Preferences**: Analysis of PR vs Issue preferences
- **Difficulty Preferences**: Analysis based on past successful contributions
- **Repository Activity Patterns**: Engagement scoring for similar repositories
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

# Personalized recommendations based on contribution history
gitco discover --personalized

# Show contribution history analysis
gitco discover --show-history

# Personalized discovery with history analysis
gitco discover --personalized --show-history --skill python
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

# Export sync report to JSON
gitco sync --export report.json

# Export sync report with analysis
gitco sync --analyze --export report.json

# Export batch sync results
gitco sync --batch --export batch-report.json

# Schedule sync (cron-friendly)
gitco sync --quiet --log sync.log

# Sync with detailed logging and log rotation
gitco sync --log sync.log --detailed-log --max-log-size 10 --log-backups 5

# View performance summary
gitco logs

# Export performance data
gitco logs --export performance.json

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
For automated usage or cron jobs, use the `--quiet` flag to suppress progress indicators and user-facing output:

```bash
# Basic quiet mode
gitco sync --quiet

# Quiet mode with logging to file
gitco sync --quiet --log sync.log

# Quiet mode for other commands
gitco analyze --repo django --quiet
gitco discover --skill python --quiet
gitco status --quiet
gitco contributions stats --quiet

# Cron job example
0 */6 * * * gitco sync --quiet --log /var/log/gitco-sync.log
```

**Quiet Mode Features:**

### Shell Completion

GitCo provides comprehensive shell completion support for both bash and zsh, making command-line usage more efficient and user-friendly.

**Installation:**

```bash
# Generate bash completion script
gitco completion --shell bash --output ~/.bash_completion.d/gitco

# Generate zsh completion script
gitco completion --shell zsh --output ~/.zsh/completions/_gitco

# Install completion scripts automatically
gitco completion --shell bash --install
gitco completion --shell zsh --install
```

**Bash Setup:**
Add this line to your `~/.bashrc`:
```bash
source ~/.bash_completion.d/gitco
```

**Zsh Setup:**
Add these lines to your `~/.zshrc`:
```bash
autoload -U compinit
compinit
```

**Completion Features:**
- **Command completion** for all GitCo commands and subcommands
- **Option completion** for all command-line flags and options
- **Repository name completion** for `--repo` options (dynamically loaded from configuration)
- **Skill name completion** for `--skill` options (dynamically loaded from configuration)
- **Label name completion** for `--label` options (common GitHub labels)
- **Provider name completion** for `--provider` options (openai, anthropic)
- **Format name completion** for `--format` options (json, csv)
- **Backup type completion** for `--type` options (full, incremental, config-only)
- **Strategy name completion** for `--strategy` options (ours, theirs, manual)
- **State name completion** for `--state` options (open, closed, all)
- **Filter name completion** for `--filter` options (healthy, needs_attention, critical)
- **Sort name completion** for `--sort` options (health, activity, stars, forks, engagement, commits, contributors)
- **Activity level completion** for activity filtering (high, moderate, low)

**Example Usage:**
```bash
# Tab completion for commands
gitco <TAB>
# Shows: init sync analyze discover status activity logs performance help config upstream validate-repo github contributions backup cost completion

# Tab completion for subcommands
gitco config <TAB>
# Shows: validate config-status validate-detailed

# Tab completion for repository names
gitco sync --repo <TAB>
# Shows repository names from your configuration

# Tab completion for skills
gitco discover --skill <TAB>
# Shows skill names from your configuration

# Tab completion for labels
gitco discover --label <TAB>
# Shows common GitHub labels

# Tab completion for providers
gitco analyze --provider <TAB>
# Shows: openai anthropic
```

**Dynamic Completion:**
GitCo's completion system dynamically loads data from your configuration:
- **Repository names** are loaded from your configured repositories
- **Skill names** are extracted from repository skills in your configuration
- **Labels** include common GitHub labels and can be customized
- **Providers** include all supported LLM providers

**Cross-Platform Support:**
- **Bash completion** works on Linux, macOS, and Windows (with bash)
- **Zsh completion** works on macOS and Linux with zsh
- **Automatic installation** to standard shell directories
- **Error handling** for completion script generation and installation
- **Suppresses all user-facing output** (progress bars, panels, console messages)
- **Maintains logging functionality** for debugging and monitoring
- **Preserves error reporting** for critical issues
- **Ideal for automated workflows** and cron jobs
- **Available on all major commands** (sync, analyze, discover, status, contributions)

## 🔧 Configuration

### Repository Configuration (`~/.gitco/config.yml`)

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
  llm_provider: openai  # or anthropic
  default_path: ~/code
  analysis_enabled: true
  max_repos_per_batch: 10
```

### LLM Configuration

Users provide their own API keys through provider-specific environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"


```

Supports multiple providers:
- OpenAI (GPT-3.5/GPT-4)
- Anthropic (Claude)

### Cost Optimization Configuration

GitCo includes comprehensive cost optimization features to help manage LLM API usage costs:

```yaml
settings:
  # Cost optimization settings
  enable_cost_tracking: true
  enable_token_optimization: true
  max_tokens_per_request: 4000
  max_cost_per_request_usd: 0.10
  max_daily_cost_usd: 5.0
  max_monthly_cost_usd: 50.0
  cost_log_file: "~/.gitco/cost_log.json"
```

**Cost Management Features:**
- **Real-time cost estimation** before API calls
- **Token optimization** with intelligent prompt truncation
- **Cost limits** (per-request, daily, monthly)
- **Cost tracking** with detailed usage history
- **Cost reporting** by provider and model
- **Cost export** in JSON and CSV formats

**Cost Management Commands:**
```bash
# View cost summary
gitco cost summary

# View detailed cost breakdown
gitco cost summary --detailed

# Configure cost limits
gitco cost configure --daily-limit 10.0 --monthly-limit 100.0

# View cost breakdown by model
gitco cost breakdown --model gpt-3.5-turbo

# View cost breakdown by provider
gitco cost breakdown --provider openai

# Reset cost history
gitco cost reset

# Export cost data
gitco cost summary --export costs.json
```

## 🔧 CLI Options

### Global Options
```bash
# Enable verbose output
gitco --verbose <command>

# Suppress output (quiet mode)
gitco --quiet <command>

# Log to file
gitco --log-file sync.log <command>

# Use detailed log format with function names and line numbers
gitco --detailed-log <command>

# Set maximum log file size in MB before rotation (default: 10)
gitco --max-log-size 20 <command>

# Set number of backup log files to keep (default: 5)
gitco --log-backups 10 <command>
```

### Command-Specific Logging Options
```bash
# Sync with detailed logging
gitco sync --log sync.log --detailed-log

# Sync with log rotation
gitco sync --log sync.log --max-log-size 10 --log-backups 5

# Analyze with performance tracking
gitco analyze --repo django --log analysis.log

# Discover with detailed logging
gitco discover --log discovery.log --detailed-log

# Status with performance tracking
gitco status --log status.log
```

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


```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Usage Guide](docs/usage.md)
- [Tutorials Guide](docs/tutorials.md) - Step-by-step tutorials and examples
- [Examples Guide](docs/examples.md) - Real-world scenarios and code snippets
- [Workflows Guide](docs/workflows.md) - User persona-based workflows
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
