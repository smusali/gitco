# GitCo ✨

**A simple CLI tool for intelligent OSS fork management and contribution discovery.**

GitCo transforms the tedious process of managing multiple OSS forks into an intelligent, context-aware workflow. It combines automated synchronization with AI-powered insights to help developers stay current with upstream changes and discover meaningful contribution opportunities.

## 🚀 Key Features

- **🔄 Intelligent Fork Synchronization** - Automated sync with safe stashing and error recovery
- **🧠 AI-Powered Change Analysis** - OpenAI integration for intelligent change analysis
- **🎯 Contribution Discovery** - Skill-based matching for finding contribution opportunities
- **📊 Repository Health Monitoring** - Comprehensive health metrics and activity tracking
- **💾 Backup & Recovery** - Robust backup system with multiple backup types
- **🤖 Automation Support** - Quiet mode and export functionality for CI/CD integration

## 📦 Installation

```bash
pip install gitco
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

### 4. Start Using GitCo
```bash
# Sync repositories
gitco sync

# Analyze changes
gitco analyze --repo django

# Discover opportunities
gitco discover --skill python

# Check repository health
gitco status
```

## 📖 Documentation

- [Quick Start Guide](docs/quick-start.md) - Get up and running in 5 minutes
- [Configuration Guide](docs/configuration.md) - Detailed configuration options
- [Usage Guide](docs/usage.md) - Complete command reference and examples
- [CLI Reference](docs/cli.md) - Comprehensive CLI command reference
- [Features Guide](docs/features.md) - Detailed feature overview
- [Tutorials](docs/tutorials.md) - Step-by-step tutorials and examples
- [Workflows](docs/workflows.md) - User persona-based workflows
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [FAQ](docs/faq.md) - Frequently asked questions
- [Releases](docs/releases.md) - Release process and management

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**GitCo makes OSS contribution management simple, intelligent, and rewarding. Start contributing more effectively today! 🚀**
