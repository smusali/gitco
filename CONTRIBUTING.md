# Contributing to GitCo

Thank you for your interest in contributing to GitCo! This document provides guidelines and information for contributors to our intelligent OSS fork management tool.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip
- GitHub account (for API access)
- LLM API key (OpenAI or Anthropic)

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/41technologies/gitco.git
   cd gitco
   ```

2. **Install in development mode:**
   ```bash
   pip install -e .
   ```

3. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Ruff** for linting
- **Pre-commit** for automated checks

### Running Quality Checks

```bash
# Format code
black src/

# Lint code
ruff check src/

# Run all checks
pre-commit run --all-files
```

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the existing code style
- Update documentation as needed
- Use type hints for all functions

### 3. Commit Your Changes

We use conventional commits:

```bash
# Format: type(scope): description
git commit -m "feat(cli): add new sync command"

# Examples:
git commit -m "fix(config): resolve YAML parsing error"
git commit -m "docs(readme): update installation instructions"
```

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: Continuous integration changes
- `build`: Build system changes
- `deps`: Dependency updates

### Scopes

- `cli`: Command-line interface
- `config`: Configuration management
- `sync`: Git synchronization
- `analyzer`: AI analysis features
- `discovery`: Issue discovery
- `reporter`: Status and reporting
- `utils`: Utility functions
- `github`: GitHub API integration
- `llm`: LLM provider integrations

### Examples

```bash
feat(cli): add init command for configuration setup
fix(sync): resolve merge conflict handling
docs(readme): update installation instructions

chore(ci): update GitHub Actions workflow
feat(github): add issue discovery functionality
feat(llm): integrate OpenAI API for change analysis
perf(sync): optimize batch processing performance
ci(deps): bump actions/setup-python from 4 to 5
```

## Changelog Generation

We use automated changelog generation based on conventional commits. The changelog is automatically updated during releases.

### Local Changelog Generation

For development, you can generate changelogs locally:

```bash
# Generate a preview changelog
./scripts/generate-changelog.sh preview

# Update the main CHANGELOG.md file
./scripts/generate-changelog.sh update

# Prepare release changelog for a specific version
./scripts/generate-changelog.sh release 1.0.0
```

### Prerequisites for Local Generation

- Node.js (for conventional-changelog-cli)
- Git repository with conventional commits

The script will automatically install `conventional-changelog-cli` if not present.

### Automated Release Process

During releases, the GitHub Actions workflow automatically:

1. Parses conventional commits since the last release
2. Generates changelog entries grouped by type
3. Updates `CHANGELOG.md` with new version
4. Creates release notes for GitHub releases
5. Publishes to PyPI with updated changelog

### Commit Message Requirements

For proper changelog generation, ensure your commits follow the conventional format:

```bash
# ✅ Good - will appear in changelog
git commit -m "feat(cli): add new sync command"
git commit -m "fix(config): resolve YAML parsing error"

# ❌ Bad - won't appear in changelog
git commit -m "add new feature"
git commit -m "fix bug"
```

## Pull Request Guidelines

### Before Submitting

1. **Run code quality checks:**
   ```bash
   pre-commit run --all-files
   ```

2. **Update documentation** if needed

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Documentation
- [ ] README updated (if needed)
- [ ] Docstrings added/updated
- [ ] Configuration examples updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Corresponding changes to documentation
- [ ] No breaking changes (or documented)
```

## Code Review Process

1. **Automated checks** must pass
2. **At least one maintainer** must approve
3. **All conversations resolved** before merge
4. **Squash and merge** for clean history

## Documentation Guidelines

### Code Documentation

- Use docstrings for all public functions
- Follow Google docstring format
- Include type hints
- Provide usage examples

### User Documentation

- Keep documentation up-to-date
- Include practical examples
- Use clear, concise language
- Add troubleshooting sections

## Issue Guidelines

### Bug Reports

Include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment information
- Error messages/logs
- GitCo configuration (if relevant)
- Repository setup details (if relevant)

### Feature Requests

Include:
- Clear description of the feature
- Use cases and benefits
- Implementation suggestions (if any)
- Priority level
- Impact on existing workflows
- Compatibility with current LLM providers

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Help others learn and grow
- Give constructive feedback
- Follow the project's code of conduct

### Communication

- Use GitHub issues for discussions
- Be clear and concise
- Provide context when needed
- Respond to feedback promptly

## Getting Help

### Questions and Discussions

- Use GitHub Discussions for questions
- Search existing issues first
- Provide context and details
- Be patient with responses

### Mentorship

- New contributors are welcome
- Ask questions freely
- We're here to help you succeed
- Don't hesitate to reach out

## Recognition

### Contributors

- All contributors are listed in CONTRIBUTORS.md
- Significant contributions are acknowledged
- We appreciate every contribution

### Hall of Fame

- Top contributors are featured
- Special recognition for major features
- Community highlights

## Next Steps

1. **Start small** - pick a good first issue
2. **Ask questions** - we're here to help
3. **Be patient** - quality takes time
4. **Have fun** - enjoy the process!

Thank you for contributing to GitCo! 🚀

## GitCo-Specific Guidelines

### Repository Management
- Work with real OSS repositories when possible
- Consider the impact on users managing multiple forks
- Ensure backward compatibility with existing configurations

### LLM Integration
- Support multiple LLM providers (OpenAI, Anthropic)
- Consider API rate limits and costs
- Validate prompt engineering for different use cases

### Git Operations
- Always use safe repository operations
- Consider edge cases in merge conflicts
- Validate upstream remote management

### GitHub Integration
- Respect GitHub API rate limits
- Support various repository permissions
- Consider private vs public repository handling
