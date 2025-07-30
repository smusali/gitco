# Troubleshooting Guide

This guide helps you resolve common issues with GitCo.

## Common Issues

### Installation Problems

#### Command Not Found
**Problem:** `gitco` command is not recognized

**Solutions:**
1. Verify installation:
   ```bash
   pip list | grep gitco
   ```

2. Check PATH:
   ```bash
   which gitco
   ```

3. Reinstall in development mode:
   ```bash
   pip install -e .
   ```

#### Import Errors
**Problem:** Module import errors when running GitCo

**Solutions:**
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Check Python version:
   ```bash
   python --version
   ```
   GitCo requires Python 3.9+

3. Use virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

### Configuration Issues

#### Invalid YAML Syntax
**Problem:** Configuration file has syntax errors

**Solutions:**
1. Validate YAML syntax:
   ```bash
   python -c "import yaml; yaml.safe_load(open('gitco-config.yml'))"
   ```

2. Check indentation (use spaces, not tabs)

3. Verify quotes around strings with special characters

#### Repository Not Found
**Problem:** GitCo can't find specified repositories

**Solutions:**
1. Check local paths exist:
   ```bash
   ls -la ~/code/django
   ```

2. Verify repository permissions:
   ```bash
   ls -la ~/code/django/.git
   ```

3. Use absolute paths in configuration

#### Missing API Key
**Problem:** AI features fail due to missing API key

**Solutions:**
1. Set environment variable for your chosen provider:
   ```bash
   # For OpenAI
   export OPENAI_API_KEY="your-openai-api-key"

   # For Anthropic
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

2. Verify key is set:
   ```bash
   # For OpenAI
   echo $OPENAI_API_KEY

   # For Anthropic
   echo $ANTHROPIC_API_KEY
   ```

3. Check API key permissions and validity

### Git Operations Issues

#### Permission Denied
**Problem:** Git operations fail with permission errors

**Solutions:**
1. Check repository ownership:
   ```bash
   ls -la ~/code/django
   ```

2. Fix permissions:
   ```bash
   chmod -R 755 ~/code/django
   ```

3. Use SSH keys for GitHub access

#### Merge Conflicts
**Problem:** Sync fails due to merge conflicts

**Solutions:**
1. Stash local changes:
   ```bash
   cd ~/code/django
   git stash
   ```

2. Reset to upstream:
   ```bash
   git reset --hard upstream/main
   ```

3. Reapply local changes:
   ```bash
   git stash pop
   ```

#### Network Issues
**Problem:** Git operations timeout or fail

**Solutions:**
1. Check internet connectivity:
   ```bash
   ping github.com
   ```

2. Increase timeout in configuration:
   ```yaml
   settings:
     git_timeout: 300
   ```

3. Use SSH instead of HTTPS for better reliability

### AI Analysis Issues

#### API Rate Limits
**Problem:** Analysis fails due to rate limits

**Solutions:**
1. Implement rate limiting in configuration:
   ```yaml
   settings:
     rate_limit_delay: 1.0
   ```

2. Use batch processing with delays

3. Upgrade API plan if needed

#### Invalid API Key
**Problem:** API key is rejected

**Solutions:**
1. Verify key format and permissions
2. Check API provider settings
3. Generate new API key if necessary

#### Analysis Timeout
**Problem:** Analysis takes too long or times out

**Solutions:**
1. Increase timeout in configuration:
   ```yaml
   settings:
     analysis_timeout: 300
   ```

2. Use smaller batch sizes
3. Check network connectivity

### Discovery Issues

#### No Issues Found
**Problem:** Discovery returns no results

**Solutions:**
1. Check repository accessibility
2. Verify labels exist in repositories
3. Expand search criteria

#### GitHub API Limits
**Problem:** GitHub API rate limit exceeded

**Solutions:**
1. Use GitHub token for higher limits:
   ```bash
   export GITHUB_TOKEN="your-github-token"
   ```

2. Implement rate limiting
3. Use authenticated requests

## Debugging

### Enable Verbose Logging

```bash
# Set log level
export GITCO_LOG_LEVEL=DEBUG

# Run with verbose output
gitco sync --verbose
```

### Check Configuration

```bash
# Validate configuration
gitco config validate

# Show configuration status
gitco config status
```

### Test Individual Components

```bash
# Test Git operations
gitco sync --repo django --dry-run

# Test API connectivity
gitco analyze --repo django --test-api

# Test discovery
gitco discover --test
```

## Performance Issues

### Slow Sync Operations

**Solutions:**
1. Reduce batch size:
   ```yaml
   settings:
     max_repos_per_batch: 5
   ```

2. Use parallel processing:
   ```yaml
   settings:
     parallel_sync: true
   ```

3. Optimize network settings

### Memory Issues

**Solutions:**
1. Reduce concurrent operations
2. Use streaming for large repositories
3. Implement memory limits

## Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Search existing issues** on GitHub
3. **Gather information:**
   - GitCo version: `gitco --version`
   - Python version: `python --version`
   - Operating system: `uname -a`
   - Error messages and logs

### Creating an Issue

When creating a GitHub issue, include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Environment information**
5. **Relevant logs and error messages**
6. **Configuration file** (with sensitive data removed)

### Example Issue Template

```markdown
## Problem Description
Brief description of the issue

## Steps to Reproduce
1. Run `gitco init`
2. Configure repository
3. Run `gitco sync`
4. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- GitCo version: 0.1.0
- Python version: 3.9.0
- OS: macOS 12.0
- Configuration: [attached]

## Error Messages
[Paste error messages here]

## Additional Information
Any other relevant details
```

## Prevention

### Best Practices

1. **Backup configuration** before major changes
2. **Test in isolated environment** first
3. **Use version control** for configuration
4. **Monitor logs** regularly
5. **Keep dependencies updated**

### Regular Maintenance

1. **Update GitCo** regularly
2. **Clean up old repositories** periodically
3. **Review and update skills** in configuration
4. **Monitor API usage** and limits
5. **Backup important data** regularly

## Next Steps

- Check [Configuration Guide](configuration.md) for advanced settings
- Review [Usage Guide](usage.md) for best practices
- Contribute fixes via [Contributing Guide](../CONTRIBUTING.md)
