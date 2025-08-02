# Automated Releases

GitCo uses automated GitHub releases to streamline the release process and ensure consistency across all releases.

## Overview

When a new version tag is pushed to the repository, the automated release workflow:

1. **Validates** the release tag format and checks for breaking changes
2. **Tests** the codebase across multiple Python versions
3. **Performs security checks** to identify vulnerabilities
4. **Builds** the Python package with proper validation
5. **Creates** a GitHub release with auto-generated changelog
6. **Publishes** to PyPI and Test PyPI with retry mechanisms
7. **Verifies** the package is available and installable
8. **Notifies** the community of the successful release

## Creating a Release

### Prerequisites

1. **PyPI API Token**: Add `PYPI_API_TOKEN` to repository secrets
2. **Test PyPI API Token**: Add `TEST_PYPI_API_TOKEN` to repository secrets (optional)
3. **Conventional Commits**: Ensure all commits follow conventional commit format

### Release Process

1. **Update Version**: Update version in `pyproject.toml` and `src/gitco/__init__.py`
2. **Create Tag**: Create and push a version tag:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```
3. **Monitor Workflow**: Watch the GitHub Actions workflow run
4. **Verify Release**: Check that the release appears on GitHub and PyPI

### Version Format

Releases must follow semantic versioning:
- **Format**: `vX.Y.Z[-prerelease][+build]`
- **Examples**: `v1.2.3`, `v2.0.0-alpha.1`, `v1.5.0+20231201`

## Workflow Stages

### 1. Validation Stage

- **Tag Format Check**: Validates semantic versioning format
- **Breaking Changes Detection**: Identifies major version bumps
- **Pre-release Detection**: Automatically marks pre-releases

### 2. Testing Stage

- **Multi-version Testing**: Tests on Python 3.9, 3.10, 3.11, 3.12
- **Coverage Reporting**: Generates and uploads coverage reports
- **Test Artifacts**: Preserves test results for analysis

### 3. Security Stage

- **Vulnerability Scanning**: Uses `pip-audit` to check dependencies
- **Code Security**: Uses `bandit` to scan for security issues
- **Secret Detection**: Uses `detect-secrets` to find exposed secrets
- **Report Generation**: Creates security reports for review

### 4. Build Stage

- **Changelog Generation**: Creates changelog from conventional commits
- **Package Validation**: Validates `pyproject.toml` and manifest
- **Package Building**: Creates wheel and source distributions
- **Installation Testing**: Tests package installation in clean environment

### 5. Release Stage

- **GitHub Release**: Creates release with auto-generated notes
- **PyPI Publishing**: Publishes to PyPI with retry mechanism
- **Test PyPI Publishing**: Publishes to Test PyPI (optional)
- **Availability Verification**: Confirms package is installable from PyPI

### 6. Post-Release Stage

- **Success Handling**: Logs successful release completion
- **Failure Handling**: Provides guidance for failed releases
- **Community Notification**: Announces release completion

## Configuration

### Required Secrets

Add these secrets to your GitHub repository:

```bash
# PyPI API Token (required for publishing)
PYPI_API_TOKEN=your-pypi-token-here

# Test PyPI API Token (optional)
TEST_PYPI_API_TOKEN=your-test-pypi-token-here
```

### Optional Configuration

- **Environment Protection**: Configure branch protection rules
- **Required Reviews**: Set up required PR reviews for releases
- **Status Checks**: Configure required status checks

## Troubleshooting

### Common Issues

#### Release Fails During Validation
- **Cause**: Invalid version format
- **Solution**: Ensure tag follows `vX.Y.Z` format

#### PyPI Upload Fails
- **Cause**: Missing or invalid API token
- **Solution**: Check `PYPI_API_TOKEN` secret configuration

#### Package Not Available After Release
- **Cause**: PyPI processing delay
- **Solution**: Wait 5-10 minutes for PyPI to process upload

#### Security Checks Fail
- **Cause**: Vulnerable dependencies or security issues
- **Solution**: Review security reports and update dependencies

### Manual Recovery

If automated release fails:

1. **Check Workflow Logs**: Review detailed error messages
2. **Fix Issues**: Address the root cause
3. **Delete Tag**: Remove the failed tag
4. **Recreate Tag**: Push a new tag with fixes
5. **Monitor**: Watch the new workflow run

### Emergency Rollback

To rollback a release:

1. **Delete GitHub Release**: Remove from GitHub releases
2. **Delete PyPI Package**: Use PyPI web interface to delete
3. **Update Documentation**: Remove references to the release
4. **Communicate**: Notify community of the rollback

## Best Practices

### Before Release

- [ ] Update version numbers in all files
- [ ] Review and merge all pending PRs
- [ ] Run local tests to ensure everything works
- [ ] Update documentation if needed
- [ ] Check for security vulnerabilities

### During Release

- [ ] Monitor the GitHub Actions workflow
- [ ] Watch for any error messages
- [ ] Verify the release appears on GitHub
- [ ] Check PyPI for the new package version
- [ ] Test installation: `pip install gitco==X.Y.Z`

### After Release

- [ ] Update installation documentation
- [ ] Announce the release to the community
- [ ] Monitor for any issues or feedback
- [ ] Plan the next release cycle

## Monitoring and Metrics

### Release Metrics

Track these metrics for each release:

- **Build Time**: How long the release process takes
- **Success Rate**: Percentage of successful releases
- **Download Statistics**: PyPI download counts
- **Community Feedback**: Issues and discussions

### Quality Gates

The release process includes several quality gates:

- ✅ **Version Validation**: Ensures proper semantic versioning
- ✅ **Test Coverage**: Maintains minimum coverage requirements
- ✅ **Security Scanning**: Identifies vulnerabilities
- ✅ **Package Validation**: Ensures installable packages
- ✅ **Availability Verification**: Confirms PyPI availability

## Support

For issues with the release process:

1. **Check Documentation**: Review this guide and related docs
2. **Review Logs**: Examine GitHub Actions workflow logs
3. **Create Issue**: Open an issue with detailed information
4. **Contact Maintainers**: Reach out to the maintainer team

## Related Documentation

- [Installation Guide](installation.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)
- [Security Policy](../SECURITY.md)
