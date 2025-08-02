# GitCo ✨

**A simple CLI tool for intelligent OSS fork management and contribution discovery.**

[![codecov](https://codecov.io/gh/41technologies/gitco/graph/badge.svg?token=R6BEP2IPGN)](https://codecov.io/gh/41technologies/gitco)

GitCo transforms the tedious process of managing multiple OSS forks into an intelligent, context-aware workflow. It combines automated synchronization with AI-powered insights to help developers stay current with upstream changes and discover meaningful contribution opportunities.

## 🚀 Features

- **🔄 Intelligent Fork Synchronization** - Automated sync with safe stashing and error recovery
- **🧠 AI-Powered Change Analysis** - OpenAI/Anthropic integration for intelligent change analysis
- **🎯 Contribution Discovery** - Skill-based matching for finding contribution opportunities
- **📊 Repository Health Monitoring** - Comprehensive health metrics and activity tracking
- **💾 Backup & Recovery** - Robust backup system with multiple backup types
- **🤖 Automation Support** - Quiet mode and export functionality for CI/CD integration
- **💰 Cost Optimization** - Token usage tracking and cost management for LLM APIs
- **📈 Contribution Tracking** - Personal contribution history and impact analysis
- **🔍 Advanced Discovery** - Personalized recommendations based on contribution history
- **📋 Health Dashboards** - Repository activity and health monitoring

## 📦 Installation

```bash
# Install from PyPI
pip install gitco

# Or install from source
git clone https://github.com/41technologies/gitco.git
cd gitco
pip install -e .
```

## 🛠️ Quick Start

### 1. Initialize Configuration
```bash
gitco init --interactive
```

### 2. Set Up API Keys
```bash
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"
```

### 3. Configure Repositories
Edit `~/.gitco/config.yml`:
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
```

### 4. Sync and Analyze
```bash
# Sync repositories
gitco sync

# Analyze changes
gitco analyze --repo django

# Discover opportunities
gitco discover --skill python

# Check repository health
gitco status

# View activity dashboard
gitco activity
```

## 📖 Documentation

- [Quick Start Guide](docs/quick-start.md) - Get up and running in 5 minutes
- [Configuration Guide](docs/configuration.md) - Detailed configuration options
- [Usage Guide](docs/usage.md) - Complete command reference and examples
- [CLI Reference](docs/cli.md) - Comprehensive CLI command reference
- [Features Guide](docs/features.md) - Detailed feature overview
- [Tutorials Guide](docs/tutorials.md) - Step-by-step tutorials and examples
- [Workflows Guide](docs/workflows.md) - User persona-based workflows
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions
- [FAQ](docs/faq.md) - Frequently asked questions
- [Releases Guide](docs/releases.md) - Automated release process and management

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md).

### Development

For developers, we provide automated changelog generation:

```bash
# Generate changelog preview
./scripts/generate-changelog.sh preview

# Update main changelog
./scripts/generate-changelog.sh update
```

See [CONTRIBUTING.md](CONTRIBUTING.md#changelog-generation) for detailed information.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**GitCo makes OSS contribution management simple, intelligent, and rewarding. Start contributing more effectively today! 🚀**
