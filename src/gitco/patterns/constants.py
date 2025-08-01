"""Regex pattern constants for GitCo detection."""

# Discovery skill synonyms and related terms
SKILL_SYNONYMS: dict[str, list[str]] = {
    "python": ["python", "py", "django", "flask", "fastapi", "pandas", "numpy"],
    "javascript": ["javascript", "js", "node", "react", "vue", "angular", "typescript"],
    "java": ["java", "spring", "android", "kotlin"],
    "cpp": ["cpp", "c++", "cplusplus", "qt", "boost"],
    "csharp": ["c#", "csharp", "dotnet", "asp.net"],
    "go": ["go", "golang"],
    "rust": ["rust"],
    "php": ["php", "laravel", "symfony", "wordpress"],
    "ruby": ["ruby", "rails", "sinatra"],
    "swift": ["swift", "ios", "macos"],
    "kotlin": ["kotlin", "android"],
    "scala": ["scala", "akka", "play"],
    "r": ["r", "rlang"],
    "matlab": ["matlab"],
    "perl": ["perl"],
    "shell": ["bash", "shell", "zsh", "powershell"],
    "sql": ["sql", "mysql", "postgresql", "sqlite"],
    "html": ["html", "css", "frontend"],
    "docker": ["docker", "container", "kubernetes"],
    "aws": ["aws", "amazon", "cloud"],
    "azure": ["azure", "microsoft"],
    "gcp": ["gcp", "google", "cloud"],
    "linux": ["linux", "unix", "ubuntu", "debian"],
    "windows": ["windows", "win"],
    "macos": ["macos", "mac", "apple"],
    "api": ["api", "rest", "graphql", "openapi"],
    "database": ["database", "db", "orm", "migration"],
    "testing": ["test", "testing", "unit", "integration", "e2e"],
    "ci": ["ci", "cd", "pipeline", "github actions", "jenkins"],
    "security": ["security", "auth", "oauth", "jwt"],
    "performance": ["performance", "optimization", "caching"],
    "ui": ["ui", "ux", "frontend", "design"],
    "mobile": ["mobile", "ios", "android", "react native"],
    "ml": ["ml", "ai", "machine learning", "tensorflow", "pytorch"],
    "data": ["data", "analytics", "visualization"],
    "devops": ["devops", "deployment", "infrastructure"],
    "documentation": ["docs", "documentation", "readme"],
    "internationalization": ["i18n", "l10n", "translation"],
    "accessibility": ["a11y", "accessibility", "wcag"],
}

# Discovery difficulty indicators
DIFFICULTY_INDICATORS: dict[str, list[str]] = {
    "beginner": [
        "good first issue",
        "first-timers-only",
        "beginner-friendly",
        "easy",
        "starter",
        "newcomer",
        "junior",
        "help wanted",
        "documentation",
        "docs",
        "readme",
        "tutorial",
    ],
    "intermediate": [
        "intermediate",
        "medium",
        "moderate",
        "enhancement",
        "feature",
        "improvement",
        "refactor",
    ],
    "advanced": [
        "advanced",
        "expert",
        "hard",
        "complex",
        "architecture",
        "performance",
        "optimization",
        "security",
        "critical",
    ],
}

# Discovery time estimation patterns
TIME_PATTERNS: dict[str, list[str]] = {
    "quick": [
        "typo",
        "documentation",
        "readme",
        "comment",
        "formatting",
        "lint",
        "style",
        "quick fix",
        "small",
        "minor",
    ],
    "medium": [
        "feature",
        "enhancement",
        "improvement",
        "refactor",
        "test",
        "bug fix",
        "moderate",
    ],
    "long": [
        "architecture",
        "major",
        "rewrite",
        "redesign",
        "performance",
        "optimization",
        "complex",
    ],
}

# API patterns
API_PATTERNS: list[str] = [
    r"@api",
    r"@endpoint",
    r"@route",
    r"@path",
    r"@method",
    r"@get",
    r"@post",
    r"@put",
    r"@delete",
    r"@patch",
    r"api/",
    r"rest/",
    r"graphql",
    r"openapi",
    r"swagger",
    r"endpoint",
    r"route",
    r"controller",
    r"resource",
]

# Configuration patterns
CONFIGURATION_PATTERNS: list[str] = [
    r"config\.",
    r"settings\.",
    r"\.env",
    r"\.ini",
    r"\.toml",
    r"\.yaml",
    r"\.yml",
    r"\.json",
    r"\.xml",
    r"configuration",
    r"settings",
    r"options",
    r"parameters",
]

# Database patterns
DATABASE_PATTERNS: list[str] = [
    r"database",
    r"db\.",
    r"table",
    r"column",
    r"index",
    r"query",
    r"sql",
    r"migration",
    r"schema",
    r"orm",
    r"model",
    r"entity",
    r"repository",
]

# Dependency patterns
DEPENDENCY_PATTERNS: list[str] = [
    r"requirements\.txt",
    r"pyproject\.toml",
    r"setup\.py",
    r"package\.json",
    r"Gemfile",
    r"go\.mod",
    r"Cargo\.toml",
    r"pom\.xml",
    r"build\.gradle",
    r"dependencies",
    r"import",
    r"require",
    r"include",
]

# Security update patterns
SECURITY_PATTERNS: dict[str, list[str]] = {
    "vulnerability": [
        r"CVE-\d{4}-\d+",
        r"vulnerability\b",
        r"security\s+fix",
        r"security\s+patch",
        r"security\s+update",
        r"buffer\s+overflow",
        r"sql\s+injection",
        r"xss\b",
        r"cross-site\s+scripting",
        r"authentication\s+bypass",
        r"privilege\s+escalation",
        r"remote\s+code\s+execution",
        r"rce\b",
        r"denial\s+of\s+service",
        r"dos\b",
        r"ddos\b",
    ],
    "authentication": [
        r"auth\b",
        r"authentication\b",
        r"login\b",
        r"password\b",
        r"token\b",
        r"jwt\b",
        r"oauth\b",
        r"session\b",
    ],
    "authorization": [
        r"csrf\b",
        r"csrf\s+token",
        r"authorization\b",
        r"permission\b",
        r"role\b",
        r"access\s+control",
        r"rbac\b",
        r"acl\b",
        r"privilege\b",
        r"admin\b",
        r"user\s+role",
    ],
    "encryption": [
        r"encrypt\b",
        r"decrypt\b",
        r"hash\b",
        r"sha\d*\b",
        r"md5\b",
        r"bcrypt\b",
        r"pbkdf2\b",
        r"aes\b",
        r"rsa\b",
        r"ssl\b",
        r"tls\b",
        r"certificate\b",
        r"private\s+key",
        r"public\s+key",
    ],
    "dependency": [
        r"dependency\s+update",
        r"package\s+update",
        r"npm\s+audit",
        r"pip\s+audit",
        r"cargo\s+audit",
        r"go\s+mod\s+tidy",
        r"security\s+dependency",
    ],
}

# Deprecation patterns
DEPRECATION_PATTERNS: dict[str, list[str]] = {
    "api_deprecation": [
        r"@deprecated\b",
        r"DeprecationWarning\b",
        r"deprecated\b",
        r"deprecation\b",
        r"old\s+api",
    ],
    "feature_deprecation": [
        r"obsolete\b",
        r"legacy\b",
        r"feature\s+deprecated",
        r"functionality\s+deprecated",
    ],
    "config_deprecation": [
        r"option\s+deprecated",
        r"setting\s+deprecated",
        r"parameter\s+deprecated",
        r"config\s+deprecated",
    ],
    "dependency_deprecation": [
        r"dependency\s+deprecated",
        r"package\s+deprecated",
        r"library\s+deprecated",
        r"version\s+deprecated",
    ],
    "removal": [
        r"removed\b",
        r"will\s+be\s+removed",
        r"sunset\b",
    ],
}

# Breaking change patterns
BREAKING_CHANGE_PATTERNS: dict[str, list[str]] = {
    "api_signature": [
        r"def\s+\w+\s*\([^)]*\)\s*->\s*[^:]+:",  # Function signature changes
        r"class\s+\w+\s*\([^)]*\):",  # Class definition changes
        r"@\w+\([^)]*\)",  # Decorator changes
    ],
    "configuration": [
        r"config\.",
        r"settings\.",
        r"\.env",
        r"\.ini",
        r"\.toml",
        r"\.yaml",
        r"\.yml",
    ],
    "database": [
        r"migration\b",
        r"schema\b",
        r"ALTER\s+TABLE",
        r"DROP\s+TABLE",
        r"CREATE\s+TABLE",
        r"INDEX\b",
    ],
    "dependencies": [
        r"requirements\.txt",
        r"pyproject\.toml",
        r"setup\.py",
        r"package\.json",
        r"Gemfile\b",
        r"go\.mod",
    ],
    "deprecation": [
        r"@deprecated\b",
        r"DeprecationWarning\b",
        r"deprecated\b",
        r"removed\b",
        r"obsolete\b",
    ],
    "security": [
        r"security\b",
        r"vulnerability\b",
        r"CVE-\d+",
        r"authentication\b",
        r"authorization\b",
    ],
}

# Severity patterns for breaking changes
HIGH_SEVERITY_PATTERNS: list[str] = [
    r"BREAKING CHANGE",
    r"breaking change",
    r"major version",
    r"incompatible",
    r"removed",
    r"deleted",
]

MEDIUM_SEVERITY_PATTERNS: list[str] = [
    r"deprecated",
    r"deprecation",
    r"changed",
    r"modified",
    r"updated",
]

# Security severity patterns
CRITICAL_SECURITY_PATTERNS: list[str] = [
    r"critical\s+vulnerability",
    r"remote\s+code\s+execution",
    r"rce",
    r"privilege\s+escalation",
    r"authentication\s+bypass",
]

HIGH_SECURITY_PATTERNS: list[str] = [
    r"cve-",
    r"vulnerability",
    r"security\s+fix",
    r"security\s+patch",
    r"buffer\s+overflow",
    r"sql\s+injection",
    r"xss",
    r"cross-site\s+scripting",
]

MEDIUM_SECURITY_PATTERNS: list[str] = [
    r"security",
    r"auth",
    r"authentication",
    r"authorization",
    r"encryption",
]

# Deprecation severity patterns
HIGH_DEPRECATION_PATTERNS: list[str] = [
    r"removed",
    r"deleted",
    r"obsolete",
    r"will\s+be\s+removed",
    r"breaking\s+change",
]

MEDIUM_DEPRECATION_PATTERNS: list[str] = [
    r"deprecated",
    r"deprecation",
    r"legacy",
    r"old\s+api",
    r"sunset",
]


def get_patterns_for_type(pattern_type: str) -> list[str]:
    """Get patterns for a specific type.

    Args:
        pattern_type: Type of patterns to retrieve

    Returns:
        List of patterns for the specified type
    """
    if pattern_type == "breaking_change":
        # Return all patterns from the breaking change dictionary
        all_patterns = []
        for patterns in BREAKING_CHANGE_PATTERNS.values():
            all_patterns.extend(patterns)
        return all_patterns
    elif pattern_type == "deprecation":
        # Return all patterns from the deprecation dictionary
        all_patterns = []
        for patterns in DEPRECATION_PATTERNS.values():
            all_patterns.extend(patterns)
        return all_patterns
    elif pattern_type == "security":
        # Return all patterns from the security dictionary
        all_patterns = []
        for patterns in SECURITY_PATTERNS.values():
            all_patterns.extend(patterns)
        return all_patterns
    elif pattern_type == "api":
        return API_PATTERNS
    elif pattern_type == "configuration":
        return CONFIGURATION_PATTERNS
    elif pattern_type == "database":
        return DATABASE_PATTERNS
    elif pattern_type == "dependency":
        return DEPENDENCY_PATTERNS
    else:
        return []


def get_all_patterns() -> dict[str, list[str]]:
    """Get all available patterns.

    Returns:
        Dictionary mapping pattern types to their patterns
    """
    # For breaking_change, flatten the nested dictionary
    breaking_patterns = []
    for patterns in BREAKING_CHANGE_PATTERNS.values():
        breaking_patterns.extend(patterns)

    # For security, flatten the nested dictionary
    security_patterns = []
    for patterns in SECURITY_PATTERNS.values():
        security_patterns.extend(patterns)

    # For deprecation, flatten the nested dictionary
    deprecation_patterns = []
    for patterns in DEPRECATION_PATTERNS.values():
        deprecation_patterns.extend(patterns)

    return {
        "breaking_change": breaking_patterns,
        "deprecation": deprecation_patterns,
        "security": security_patterns,
        "api": API_PATTERNS,
        "configuration": CONFIGURATION_PATTERNS,
        "database": DATABASE_PATTERNS,
        "dependency": DEPENDENCY_PATTERNS,
    }
