# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Ollama local LLM integration for intelligent change analysis
- OllamaAnalyzer class for local LLM integration with Ollama
- Support for Ollama server configuration (host, model, timeout)
- Default Ollama configuration (localhost:11434, llama2 model)
- Ollama-specific settings in configuration (ollama_host, ollama_model)
- Integration of Ollama provider into ChangeAnalyzer
- Comprehensive testing for Ollama integration
- Support for custom Ollama models and server endpoints
- Local LLM analysis without external API dependencies
- Anthropic Claude API integration for intelligent change analysis
- AnthropicAnalyzer class for Claude API integration
- Support for provider-specific API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
- Enhanced API key priority system with fallback support
- Improved response parsing for Anthropic Claude API responses
- Comprehensive testing for Anthropic Claude integration
- OpenAI API integration for intelligent change analysis
- ChangeAnalyzer class for coordinating analysis operations
- OpenAIAnalyzer class for OpenAI API integration
- ChangeAnalysis dataclass for structured analysis results
- AnalysisRequest dataclass for analysis request handling
- Intelligent prompt building for code change analysis
- JSON and text-based response parsing for OpenAI responses
- Breaking change detection and categorization
- New feature identification and reporting
- Bug fix detection and categorization
- Security update identification and highlighting
- Deprecation detection and reporting
- Contribution recommendation generation
- Confidence scoring for analysis results
- Rich console output for analysis results with color coding
- Integration of analysis into sync command with --analyze flag
- Analysis export functionality with JSON format
- Custom prompt support for analysis requests
- Analysis result display with categorized sections
- Support for multiple repositories in batch analysis
- Error handling and fallback for analysis failures
- Comprehensive testing for all analysis functionality
- Type-safe implementation with full mypy compliance
- Initial project structure and configuration
- Python package setup with pyproject.toml
- Development environment configuration
- Basic documentation structure
- CLI framework with Click and basic command structure
- Command-line interface with init, sync, analyze, discover, status, and help commands
- Comprehensive CLI testing with pytest
- Global options for verbose and quiet output
- Configuration management with YAML support
- ConfigManager class for handling configuration files
- Repository and Settings dataclasses for type-safe configuration
- Configuration validation with detailed error reporting
- Configuration status and validation commands
- Sample configuration generation with example repositories
- Comprehensive logging system with configurable levels
- Custom exception hierarchy for GitCo errors
- Error handling utilities with safe execution patterns
- Progress tracking and operation logging
- File and directory validation utilities
- Validation error handling with detailed reporting
- API call logging and monitoring
- Configuration operation logging with detailed context
- GitHub Actions CI pipeline with Python testing
- Multi-Python version testing (3.9, 3.10, 3.11, 3.12)
- Automated linting with ruff and black
- Type checking with mypy
- Security scanning with pip-audit and bandit
- Package building and validation
- Code coverage reporting with Codecov integration
- PR validation with conventional commit checks
- Issue templates for bug reports, feature requests, and questions
- Pull request template with comprehensive checklist
- Dependabot configuration for automated dependency updates
- Security policy with vulnerability reporting guidelines
- Pre-commit hooks configuration with ruff and black linting
- End-of-file fixing with ruff W292 rule
- Conventional commit message validation
- YAML syntax validation and formatting
- Merge conflict detection and prevention
- CONTRIBUTING.md with GitCo-specific guidelines
- CODE_OF_CONDUCT.md with community values
- Git repository detection and validation functionality
- GitRepository class for repository status and validation
- GitRepositoryManager for batch repository operations
- Repository sync status checking with upstream comparison
- Recursive repository discovery in directory trees
- Comprehensive repository validation with detailed error reporting
- Git command execution with timeout and error handling
- Remote URL detection and default branch identification
- Repository status reporting with uncommitted changes detection
- New validate-repo CLI command for repository validation
- Integration of git validation into configuration validation
- Upstream remote management functionality
- Add, remove, update, and validate upstream remotes
- Fetch latest changes from upstream repositories
- Upstream remote accessibility testing and validation
- CLI commands for upstream remote management (upstream add, remove, update, validate-upstream, fetch)
- Comprehensive testing for upstream remote operations
- Integration of upstream status into repository status reporting
- Safe stashing and unstashing of local changes
- Automatic detection of uncommitted changes before operations
- Stash creation with custom messages and reference tracking
- Stash application and restoration with error handling
- Stash management (list, drop) with comprehensive validation
- Safe stash-and-restore pattern for atomic operations
- Integration of stashing into repository sync operations
- Comprehensive testing for all stashing functionality
- Git fetch and merge operations with conflict detection
- Merge upstream branch functionality with automatic conflict detection
- Conflict resolution strategies (ours, theirs, manual)
- Merge abort functionality for failed merge operations
- Merge status detection and reporting
- Comprehensive merge result reporting with commit information
- Integration of fetch and merge into unified sync operations
- CLI merge command with conflict resolution options
- Merge conflict detection and detailed conflict reporting
- Automatic merge commit tracking and reporting
- Comprehensive testing for all merge functionality
- Batch processing for multiple repositories with concurrent execution
- BatchProcessor class for efficient multi-repository operations
- ThreadPoolExecutor-based concurrent processing with configurable workers
- Batch sync, fetch, and validate operations with progress tracking
- Colored output and progress indicators for batch operations
- Batch result tracking with detailed success/failure reporting
- Rate limiting and error handling for batch operations
- Batch summary reporting with timing and statistics
- Integration of batch processing into sync command with --batch flag
- Configurable max workers for batch processing performance tuning
- Sequential fallback for batch processing when concurrent processing fails
- Rich console output with colored status messages and progress indicators
- **Enhanced sync command with basic error recovery**
- **Retry mechanism for network operations with configurable max retries**
- **Recoverable error detection for network timeouts and rate limits**
- **Automatic retry with exponential backoff for transient failures**
- **Enhanced error reporting with retry attempt information**
- **Improved stash restoration with failure handling**
- **Better progress tracking with retry status in CLI output**
- **Comprehensive logging of recovery attempts and retry counts**

### Fixed
- Updated deprecated GitHub Actions to latest versions (actions/upload-artifact@v4, actions/download-artifact@v4, actions/cache@v4, codecov/codecov-action@v4)
- Fixed import sorting issues in test files (test_cli.py, test_config.py, test_utils.py)
- Fixed YAML linting issues in .codecov.yml (truthy values)
- Fixed trailing whitespace and end-of-file issues in .yamllint
- Updated pre-commit ruff version to v0.12.5 to match local ruff version and ensure consistency

## [0.1.0] - 2025-01-XX

### Added
- Initial project foundation
- Python package configuration with comprehensive metadata
- Development dependencies and tooling setup
- Package distribution configuration
- Type checking and linting configuration
- Testing framework setup
- Documentation structure

[Unreleased]: https://github.com/41technologies/gitco/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/41technologies/gitco/releases/tag/v0.1.0
