"""Regex pattern constants for GitCo detection."""

# Security update patterns
SECURITY_PATTERNS: dict[str, list[str]] = {
    "vulnerability_fix": [
        r"CVE-\d{4}-\d+",
        r"vulnerability",
        r"security\s+fix",
        r"security\s+patch",
        r"security\s+update",
        r"buffer\s+overflow",
        r"sql\s+injection",
        r"xss",
        r"cross-site\s+scripting",
        r"authentication\s+bypass",
        r"privilege\s+escalation",
        r"remote\s+code\s+execution",
        r"rce",
        r"denial\s+of\s+service",
        r"dos",
        r"ddos",
    ],
    "authentication": [
        r"auth",
        r"authentication",
        r"login",
        r"password",
        r"token",
        r"jwt",
        r"oauth",
        r"session",
        r"csrf",
        r"csrf\s+token",
    ],
    "authorization": [
        r"authorization",
        r"permission",
        r"role",
        r"access\s+control",
        r"rbac",
        r"acl",
        r"privilege",
        r"admin",
        r"user\s+role",
    ],
    "encryption": [
        r"encrypt",
        r"decrypt",
        r"hash",
        r"sha",
        r"md5",
        r"bcrypt",
        r"pbkdf2",
        r"aes",
        r"rsa",
        r"ssl",
        r"tls",
        r"certificate",
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
        r"@deprecated",
        r"DeprecationWarning",
        r"deprecated",
        r"deprecation",
        r"obsolete",
        r"legacy",
        r"old\s+api",
        r"removed",
        r"will\s+be\s+removed",
        r"sunset",
    ],
    "feature_deprecation": [
        r"feature\s+deprecated",
        r"functionality\s+deprecated",
        r"option\s+deprecated",
        r"setting\s+deprecated",
        r"parameter\s+deprecated",
    ],
    "dependency_deprecation": [
        r"dependency\s+deprecated",
        r"package\s+deprecated",
        r"library\s+deprecated",
        r"version\s+deprecated",
    ],
    "config_deprecation": [
        r"config\s+deprecated",
        r"setting\s+deprecated",
        r"option\s+deprecated",
        r"parameter\s+deprecated",
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
        r"migration",
        r"schema",
        r"ALTER\s+TABLE",
        r"DROP\s+TABLE",
        r"CREATE\s+TABLE",
        r"INDEX",
    ],
    "dependencies": [
        r"requirements\.txt",
        r"pyproject\.toml",
        r"setup\.py",
        r"package\.json",
        r"Gemfile",
        r"go\.mod",
    ],
    "deprecation": [
        r"@deprecated",
        r"DeprecationWarning",
        r"deprecated",
        r"removed",
        r"obsolete",
    ],
    "security": [
        r"security",
        r"vulnerability",
        r"CVE-",
        r"authentication",
        r"authorization",
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
