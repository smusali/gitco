---
name: Bug report
about: Create a report to help us improve GitCo
title: '[BUG] '
labels: ['bug']
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
A clear and concise description of what actually happened.

**Environment:**
 - OS: [e.g. macOS, Ubuntu, Windows]
 - Python version: [e.g. 3.9, 3.10, 3.11, 3.12]
 - GitCo version: [e.g. 0.1.0]
 - Git version: [e.g. 2.35.1]

**Configuration:**
```yaml
# Your gitco-config.yml (remove sensitive information)
repositories:
  - name: example
    fork: username/repo
    upstream: owner/repo
    local_path: ~/code/repo
```

**Logs:**
```
# Add relevant log output here
```

**Additional context**
Add any other context about the problem here.

**Checklist:**
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have provided all the information requested above
- [ ] I can reproduce this issue consistently
- [ ] This is a bug in GitCo (not a configuration issue)
