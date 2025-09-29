# GitCo Quality Assurance Testing Guide

## Overview

This document provides comprehensive QA testing procedures for GitCo, covering all functionality, commands, and features before release. Each test section includes specific commands, expected outcomes, and validation criteria.

**Note:** GitCo now uses Git-based authentication for GitHub integration. No GitHub API keys are required - the system automatically detects and uses SSH keys, stored credentials, and Git configuration.

## Prerequisites

### Environment Setup
```bash
# Install GitCo in development mode
pip install -e .

# Verify installation
gitco --version

# Check configuration
gitco config validate
```

### Test Data Preparation
```bash
# Create test repositories
mkdir -p ~/test-gitco-repos
cd ~/test-gitco-repos

# Clone actual test repositories (real forks)
git clone https://github.com/smusali/fastapi.git test-repo-1
git clone https://github.com/smusali/django.git test-repo-2

# Alternative: Clone using SSH if you have SSH keys set up
# git clone git@github.com:smusali/fastapi.git test-repo-1
# git clone git@github.com:smusali/django.git test-repo-2
```

## Core Functionality Testing

### 1. Configuration Management

#### 1.1 Configuration Initialization
```bash
# Test configuration initialization
gitco init

# Verify configuration file creation
ls -la ~/.config/gitco/config.yaml

# Test configuration validation
gitco config validate

# Test detailed configuration validation
gitco config validate-detailed

# Test configuration status
gitco config config-status
```

**Expected Outcomes:**
- Configuration file created successfully
- All validation checks pass
- Status shows valid configuration

#### 1.2 Repository Configuration
```bash
# Add FastAPI repository to configuration
gitco config add-repo --name fastapi --fork smusali/fastapi --upstream fastapi/fastapi --path ~/test-gitco-repos/test-repo-1 --skills python,web,api

# Add Django repository to configuration
gitco config add-repo --name django --fork smusali/django --upstream django/django --path ~/test-gitco-repos/test-repo-2 --skills python,web,orm

# Verify repository addition
gitco config validate

# Test repository validation
gitco validate-repo --repo fastapi
gitco validate-repo --repo django
```

**Expected Outcomes:**
- Repositories added successfully
- Configuration validation passes
- Repository validation passes
- Skills properly configured for each repository

### 2. Repository Operations

#### 2.1 Repository Synchronization
```bash
# Test FastAPI repository sync
gitco sync --repo fastapi

# Test Django repository sync
gitco sync --repo django

# Test batch sync (both repositories)
gitco sync --all

# Test sync with verbose output
gitco sync --repo fastapi --verbose

# Test sync with quiet mode
gitco sync --repo django --quiet
```

**Expected Outcomes:**
- Sync completes successfully for both repositories
- No merge conflicts
- Repositories are up to date with upstream (fastapi/fastapi and django/django)
- Git-based authentication works automatically

#### 2.2 Repository Status
```bash
# Test FastAPI repository status
gitco status --repo fastapi

# Test Django repository status
gitco status --repo django

# Test status for all repositories
gitco status --all

# Test detailed status
gitco status --repo fastapi --detailed
gitco status --repo django --detailed
```

**Expected Outcomes:**
- Status shows current branch for each repository
- Shows sync status with upstream (fastapi/fastapi and django/django)
- Displays any pending changes
- Git authentication status displayed

#### 2.3 Repository Activity
```bash
# Test FastAPI activity dashboard
gitco activity --repo fastapi

# Test Django activity dashboard
gitco activity --repo django

# Test activity for all repositories
gitco activity --all

# Test activity with export
gitco activity --repo fastapi --export fastapi-activity-report.json
gitco activity --repo django --export django-activity-report.json
```

**Expected Outcomes:**
- Activity data displayed correctly for both repositories
- Export files created successfully
- Activity metrics calculated properly
- Git-based authentication used for activity data retrieval

### 3. AI-Powered Analysis

#### 3.1 Change Analysis
```bash
# Test FastAPI change analysis
gitco analyze --repo fastapi

# Test Django change analysis
gitco analyze --repo django

# Test analysis with custom prompt
gitco analyze --repo fastapi --prompt "Focus on API changes and security updates"
gitco analyze --repo django --prompt "Focus on ORM changes and security updates"

# Test analysis with export
gitco analyze --repo fastapi --export fastapi-analysis-report.json
gitco analyze --repo django --export django-analysis-report.json

# Test batch analysis
gitco analyze --all
```

**Expected Outcomes:**
- Analysis completes successfully for both repositories
- Breaking changes detected if present in FastAPI/Django updates
- Security updates identified
- Deprecations flagged
- Export files generated
- AI analysis works with Git-based authentication

#### 3.2 Contribution Discovery
```bash
# Test contribution discovery for FastAPI
gitco discover --repo fastapi

# Test contribution discovery for Django
gitco discover --repo django

# Test discovery with skill filter (Python skills for both repos)
gitco discover --skill python --skill web --skill api

# Test discovery with label filter
gitco discover --label "good first issue" --label "help wanted"

# Test discovery with limit
gitco discover --limit 10

# Test discovery with confidence threshold
gitco discover --min-confidence 0.8

# Test personalized discovery
gitco discover --personalized

# Test discovery with history
gitco discover --show-history

# Test discovery across both repositories
gitco discover --all
```

**Expected Outcomes:**
- Opportunities discovered successfully
- Filters applied correctly
- Confidence scores calculated
- Personalized recommendations generated

### 4. Upstream Management

#### 4.1 Upstream Operations
```bash
# Test upstream addition for FastAPI
gitco upstream add --repo fastapi --url https://github.com/fastapi/fastapi.git

# Test upstream addition for Django
gitco upstream add --repo django --url https://github.com/django/django.git

# Test upstream removal
gitco upstream remove --repo fastapi

# Test upstream update
gitco upstream update --repo fastapi --url https://github.com/fastapi/fastapi.git

# Test upstream validation
gitco upstream validate-upstream --repo fastapi
gitco upstream validate-upstream --repo django

# Test upstream fetch
gitco upstream fetch --repo fastapi
gitco upstream fetch --repo django

# Test upstream merge
gitco upstream merge --repo fastapi
gitco upstream merge --repo django
```

**Expected Outcomes:**
- Upstream operations complete successfully for both repositories
- Validation passes for fastapi/fastapi and django/django
- Fetch and merge operations work correctly
- Git-based authentication used for upstream operations

### 5. GitHub Integration

#### 5.1 Git-Based Authentication
```bash
# Test Git authentication detection
gitco config validate

# Test GitHub connection (uses Git credentials automatically)
gitco github connection-status

# Test with different authentication methods
# SSH: git@github.com:user/repo.git
# HTTPS: https://github.com/user/repo.git
```

**Expected Outcomes:**
- Git authentication automatically detected
- SSH keys or stored credentials used
- No GitHub API key required
- Connection successful using existing Git setup

#### 5.2 GitHub API Operations
```bash
# Test GitHub connection
gitco github connection-status

# Test rate limit status
gitco github rate-limit-status

# Test repository information for FastAPI
gitco github get-repo --repo smusali/fastapi

# Test repository information for Django
gitco github get-repo --repo smusali/django

# Test issue retrieval for FastAPI
gitco github get-issues --repo smusali/fastapi

# Test issue retrieval for Django
gitco github get-issues --repo smusali/django

# Test multi-repository issues
gitco github get-issues-multi --repos smusali/fastapi,smusali/django
```

**Expected Outcomes:**
- GitHub connection successful using Git authentication
- Rate limits displayed correctly
- Repository information retrieved
- Issues fetched successfully
- Fallback authentication works if Git auth fails

### 6. Contribution Management

#### 6.1 Contribution Tracking
```bash
# Test contribution history sync for both repositories
gitco contributions sync-history

# Test contribution statistics
gitco contributions stats

# Test contribution recommendations (Python/web skills)
gitco contributions recommendations --skills python,web,api,orm

# Test contribution export
gitco contributions export --format json

# Test trending analysis
gitco contributions trending

# Test repository-specific contributions
gitco contributions stats --repo fastapi
gitco contributions stats --repo django
```

**Expected Outcomes:**
- History synced successfully for both FastAPI and Django repositories
- Statistics calculated correctly
- Recommendations generated based on Python/web skills
- Export completed
- Trending analysis performed
- Repository-specific stats work correctly

### 7. Backup and Recovery

#### 7.1 Backup Operations
```bash
# Test backup creation for both repositories
gitco backup create --repos fastapi,django --type full

# Test incremental backup for FastAPI
gitco backup create --repos fastapi --type incremental

# Test incremental backup for Django
gitco backup create --repos django --type incremental

# Test config-only backup
gitco backup create --type config-only

# Test backup listing
gitco backup list-backups

# Test backup validation
gitco backup validate-backup --backup-id <backup-id>

# Test backup restoration
gitco backup restore --backup-id <backup-id>

# Test backup deletion
gitco backup delete --backup-id <backup-id>

# Test backup cleanup
gitco backup cleanup
```

**Expected Outcomes:**
- Backups created successfully
- Backup listing shows created backups
- Validation passes
- Restoration works correctly
- Deletion and cleanup complete

### 8. Performance and Logging

#### 8.1 Performance Monitoring
```bash
# Test performance logs
gitco logs

# Test performance metrics
gitco performance

# Test detailed performance
gitco performance --detailed

# Test performance export
gitco performance --export performance-report.json --format json
```

**Expected Outcomes:**
- Performance data displayed
- Metrics calculated correctly
- Export files generated

#### 8.2 Logging Operations
```bash
# Test verbose logging
gitco sync --repo fastapi --verbose
gitco sync --repo django --verbose

# Test quiet mode
gitco sync --repo fastapi --quiet
gitco sync --repo django --quiet

# Test log file output
gitco sync --repo fastapi --log-file ~/gitco-fastapi-test.log
gitco sync --repo django --log-file ~/gitco-django-test.log

# Test detailed logging
gitco sync --repo fastapi --detailed-log
gitco sync --repo django --detailed-log
```

**Expected Outcomes:**
- Logging levels work correctly for both repositories
- Log files created and populated
- Detailed logging provides comprehensive information
- Git authentication events logged properly

### 9. Error Handling and Edge Cases

#### 9.1 Network Error Handling
```bash
# Test with invalid repository URL
gitco upstream add --repo fastapi --url https://invalid-url.com/repo.git

# Test with non-existent repository
gitco sync --repo non-existent-repo

# Test with invalid configuration
gitco config validate --config-file invalid-config.yaml
```

**Expected Outcomes:**
- Appropriate error messages displayed
- Graceful error handling
- No crashes or unexpected behavior

#### 9.2 Authentication Error Handling
```bash
# Test with invalid Git authentication (no SSH keys, no stored credentials)
# Remove SSH keys temporarily or use invalid repository
gitco github connection-status

# Test with invalid OpenAI API key
OPENAI_API_KEY=invalid gitco analyze --repo fastapi
OPENAI_API_KEY=invalid gitco analyze --repo django

# Test fallback authentication with invalid token
GITHUB_TOKEN=invalid gitco github connection-status
```

**Expected Outcomes:**
- Git authentication errors handled gracefully
- Fallback authentication attempts work
- Clear error messages provided
- No sensitive information exposed
- Anonymous access attempted as last resort

### 10. Shell Completion Testing

#### 10.1 Bash Completion
```bash
# Test bash completion installation
gitco _completion install --shell bash

# Test completion functionality
# Type: gitco <TAB>
# Should show: init sync analyze discover status activity logs performance help config upstream validate-repo github contributions backup

# Test subcommand completion
# Type: gitco config <TAB>
# Should show: validate config-status validate-detailed
```

**Expected Outcomes:**
- Completion scripts install correctly
- Tab completion works for all commands
- Subcommand completion functions properly

#### 10.2 ZSH Completion
```bash
# Test zsh completion installation
gitco _completion install --shell zsh

# Test completion functionality
# Type: gitco <TAB>
# Should show available commands

# Test option completion
# Type: gitco sync --<TAB>
# Should show available options
```

**Expected Outcomes:**
- ZSH completion installs correctly
- Completion works for commands and options
- Dynamic completion data functions properly

### 11. Configuration Validation

#### 11.1 Comprehensive Configuration Testing
```bash
# Test with minimal configuration
gitco config validate --config-file minimal-config.yaml

# Test with complex configuration
gitco config validate --config-file complex-config.yaml

# Test with invalid repository paths
gitco config validate --config-file invalid-paths-config.yaml

# Test with missing required fields
gitco config validate --config-file missing-fields-config.yaml
```

**Expected Outcomes:**
- Valid configurations pass validation
- Invalid configurations fail with clear messages
- All validation rules enforced

### 12. Integration Testing

#### 12.1 End-to-End Workflows
```bash
# Test complete workflow: init -> add repos -> sync -> analyze -> discover
gitco init
gitco config add-repo --name fastapi --fork smusali/fastapi --upstream fastapi/fastapi --path ~/test-gitco-repos/test-repo-1 --skills python,web,api
gitco config add-repo --name django --fork smusali/django --upstream django/django --path ~/test-gitco-repos/test-repo-2 --skills python,web,orm
gitco sync --repo fastapi
gitco sync --repo django
gitco analyze --repo fastapi
gitco analyze --repo django
gitco discover --repo fastapi
gitco discover --repo django

# Test backup and restore workflow
gitco backup create --repos fastapi,django --type full
gitco backup list-backups
gitco backup restore --backup-id <backup-id>
```

**Expected Outcomes:**
- Complete workflows execute successfully for both repositories
- All steps complete without errors
- Data integrity maintained throughout
- Git-based authentication works seamlessly

### 13. Performance Testing

#### 13.1 Large Repository Testing
```bash
# Test with large repository
gitco sync --repo large-repo
gitco analyze --repo large-repo
gitco discover --repo large-repo
```

**Expected Outcomes:**
- Operations complete within reasonable time
- Memory usage remains stable
- No performance degradation

#### 13.2 Batch Operations Testing
```bash
# Test batch operations with multiple repositories
gitco sync --all
gitco analyze --all
gitco discover --all
```

**Expected Outcomes:**
- Batch operations complete successfully
- Progress tracking works correctly
- All repositories processed

### 14. Security Testing

#### 14.1 Input Validation
```bash
# Test with malicious input
gitco config add-repo --name "../../etc/passwd" --fork "'; rm -rf /" --upstream "owner/repo"

# Test with SQL injection attempts
gitco discover --skill "'; DROP TABLE users; --"
```

**Expected Outcomes:**
- Malicious input rejected
- No security vulnerabilities exploited
- Safe error handling

#### 14.2 Credential Handling
```bash
# Test credential masking in logs
gitco sync --repo fastapi --verbose
gitco sync --repo django --verbose

# Test Git credential handling (SSH keys, stored credentials)
gitco github connection-status

# Test fallback environment variable handling
GITHUB_TOKEN=secret gitco github connection-status
```

**Expected Outcomes:**
- Git credentials not exposed in logs
- SSH keys and stored credentials handled securely
- Environment variables handled securely as fallback
- No credential leakage in any authentication method

### 15. Cross-Platform Testing

#### 15.1 Platform-Specific Testing
```bash
# Test on different operating systems
# Linux
gitco --version
gitco config validate

# macOS
gitco --version
gitco config validate

# Windows (if applicable)
gitco --version
gitco config validate
```

**Expected Outcomes:**
- GitCo works on all supported platforms
- Platform-specific features function correctly
- No platform-specific bugs

### 16. Documentation Testing

#### 16.1 Help System Testing
```bash
# Test help commands
gitco --help
gitco help
gitco sync --help
gitco config --help
gitco upstream --help
gitco github --help
gitco contributions --help
gitco backup --help
```

**Expected Outcomes:**
- Help text displays correctly
- All commands have help documentation
- Examples and usage information provided

### 17. Regression Testing

#### 17.1 Previous Version Compatibility
```bash
# Test configuration file compatibility
gitco config validate --config-file old-version-config.yaml

# Test backup compatibility
gitco backup restore --backup-id old-version-backup
```

**Expected Outcomes:**
- Backward compatibility maintained
- Old configurations still work
- Migration paths available

### 18. Stress Testing

#### 18.1 High-Load Testing
```bash
# Test with many repositories
gitco sync --all  # with 50+ repositories
gitco analyze --all  # with 50+ repositories
gitco discover --all  # with 50+ repositories
```

**Expected Outcomes:**
- System handles high load gracefully
- No memory leaks or crashes
- Performance remains acceptable

### 19. Error Recovery Testing

#### 19.1 Failure Recovery
```bash
# Test recovery from network failures
gitco sync --repo fastapi  # with network interruption
gitco sync --repo django  # with network interruption

# Test recovery from disk space issues
gitco backup create --repos fastapi,django --type full  # with limited disk space

# Test recovery from permission issues
gitco sync --repo fastapi  # with read-only filesystem
gitco sync --repo django  # with read-only filesystem
```

**Expected Outcomes:**
- Graceful failure handling
- Appropriate error messages
- Git authentication errors handled properly
- Recovery mechanisms work

### 20. Final Validation

#### 20.1 Release Readiness Checklist
```bash
# Run all validation commands
gitco --version
gitco config validate
gitco config validate-detailed
gitco config config-status

# Test all major commands
gitco sync --help
gitco analyze --help
gitco discover --help
gitco status --help
gitco activity --help
gitco logs --help
gitco performance --help
gitco config --help
gitco upstream --help
gitco validate-repo --help
gitco github --help
gitco contributions --help
gitco backup --help

# Test completion installation
gitco _completion install --shell bash
gitco _completion install --shell zsh
```

**Expected Outcomes:**
- All commands execute successfully
- Help text displays correctly
- Completion scripts install properly
- No critical errors or warnings

## Test Results Documentation

### Test Execution Log
```bash
# Create test execution log
gitco logs --export test-execution-log.json --format json
gitco performance --export test-performance-log.json --format json
```

### Test Coverage Report
```bash
# Generate test coverage report
coverage run -m pytest tests/
coverage report
coverage html
```

### Release Validation
```bash
# Final release validation
gitco --version
gitco config validate
gitco help
```

## Conclusion

This comprehensive QA testing guide ensures all GitCo functionality is thoroughly tested before release. Each test section includes specific commands, expected outcomes, and validation criteria to maintain high quality and reliability.

Execute all tests in the specified order, document any failures, and ensure all tests pass before proceeding with the release.