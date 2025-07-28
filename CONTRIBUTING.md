# Contributing to GitCo

Thank you for your interest in contributing to GitCo! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- pip

### Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/gitco.git
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
- **MyPy** for type checking
- **Pre-commit** for automated checks

### Running Quality Checks

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gitco

# Run specific test file
pytest tests/test_imports.py

# Run tests in parallel
pytest -n auto
```

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the existing code style
- Add tests for new functionality
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
git commit -m "test(sync): add unit tests for git operations"
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
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Scopes

- `cli`: Command-line interface
- `config`: Configuration management
- `sync`: Git synchronization
- `analyzer`: AI analysis features
- `discovery`: Issue discovery
- `reporter`: Status and reporting
- `utils`: Utility functions

### Examples

```bash
feat(cli): add init command for configuration setup
fix(sync): resolve merge conflict handling
docs(readme): update installation instructions
test(analyzer): add unit tests for LLM integration
chore(ci): update GitHub Actions workflow
```

## Pull Request Guidelines

### Before Submitting

1. **Ensure all tests pass:**
   ```bash
   pytest
   ```

2. **Run code quality checks:**
   ```bash
   pre-commit run --all-files
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Test addition
- [ ] Code refactoring

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

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

## Testing Guidelines

### Unit Tests

- Test all public functions
- Use descriptive test names
- Mock external dependencies
- Aim for 70%+ coverage

### Integration Tests

- Test CLI commands end-to-end
- Test configuration file handling
- Test API integrations

### Test Structure

```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = "test"

    # Act
    result = function(input_data)

    # Assert
    assert result == "expected"
```

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

### Feature Requests

Include:
- Clear description of the feature
- Use cases and benefits
- Implementation suggestions (if any)
- Priority level

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
