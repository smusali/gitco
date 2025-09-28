"""Shell completion script templates."""

import logging
from dataclasses import dataclass
from typing import Optional, Union

BASH_COMPLETION_TEMPLATE = """# GitCo bash completion script

_gitco_completion() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    cmds="init sync analyze discover status activity logs performance help config upstream validate-repo github contributions backup"

    # Subcommands
    config_cmds="validate config-status validate-detailed"
    upstream_cmds="add remove update validate-upstream fetch merge"
    github_cmds="rate-limit-status test-connection get-repo get-issues get-issues-multi"
    contributions_cmds="sync-history stats recommendations export trending"
    backup_cmds="create list-backups restore validate-backup delete cleanup"

    # Options
    global_opts="-v --verbose -q --quiet --log-file --detailed-log --max-log-size --log-backups -c --config --help --version"

    case "${prev}" in
        gitco)
            COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
            return 0
            ;;
        config)
            COMPREPLY=( $(compgen -W "${config_cmds}" -- "${cur}") )
            return 0
            ;;
        upstream)
            COMPREPLY=( $(compgen -W "${upstream_cmds}" -- "${cur}") )
            return 0
            ;;
        github)
            COMPREPLY=( $(compgen -W "${github_cmds}" -- "${cur}") )
            return 0
            ;;
        contributions)
            COMPREPLY=( $(compgen -W "${contributions_cmds}" -- "${cur}") )
            return 0
            ;;
        backup)
            COMPREPLY=( $(compgen -W "${backup_cmds}" -- "${cur}") )
            return 0
            ;;
        -r|--repo)
            # Repository completion
            repos="$(gitco _completion repos 2>/dev/null || echo '')"
            COMPREPLY=( $(compgen -W "${repos}" -- "${cur}") )
            return 0
            ;;
        -s|--skill)
            # Skill completion
            skills="$(gitco _completion skills 2>/dev/null || echo '')"
            COMPREPLY=( $(compgen -W "${skills}" -- "${cur}") )
            return 0
            ;;
        -l|--label)
            # Label completion
            labels="good\\ first\\ issue help\\ wanted bug enhancement documentation question invalid wontfix duplicate feature improvement refactor test ci build deploy security performance accessibility internationalization"
            COMPREPLY=( $(compgen -W "${labels}" -- "${cur}") )
            return 0
            ;;
        --provider)
            # Provider completion
            providers="openai anthropic"
            COMPREPLY=( $(compgen -W "${providers}" -- "${cur}") )
            return 0
            ;;
        -f|--format)
            # Format completion
            formats="json csv"
            COMPREPLY=( $(compgen -W "${formats}" -- "${cur}") )
            return 0
            ;;
        --type)
            # Backup type completion
            types="full incremental config-only"
            COMPREPLY=( $(compgen -W "${types}" -- "${cur}") )
            return 0
            ;;
        --strategy)
            # Strategy completion
            strategies="ours theirs manual"
            COMPREPLY=( $(compgen -W "${strategies}" -- "${cur}") )
            return 0
            ;;
        --state)
            # State completion
            states="open closed all"
            COMPREPLY=( $(compgen -W "${states}" -- "${cur}") )
            return 0
            ;;
        --filter)
            # Filter completion
            filters="healthy needs_attention critical"
            COMPREPLY=( $(compgen -W "${filters}" -- "${cur}") )
            return 0
            ;;
        --sort)
            # Sort completion
            sorts="health activity stars forks engagement commits contributors"
            COMPREPLY=( $(compgen -W "${sorts}" -- "${cur}") )
            return 0
            ;;
        *)
            # Check if we're completing an option
            if [[ ${cur} == -* ]] ; then
                COMPREPLY=( $(compgen -W "${global_opts}" -- "${cur}") )
                return 0
            fi
            ;;
    esac

    # Default completion
    COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
    return 0
}

complete -F _gitco_completion gitco
"""

ZSH_COMPLETION_TEMPLATE = """# GitCo zsh completion script

_gitco() {
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -C \\
        ': :->command' \\
        '*:: :->args'

    case $state in
        command)
            local -a commands
            commands=(
                'init:Initialize GitCo configuration'
                'sync:Synchronize repositories with upstream'
                'analyze:Analyze changes with AI'
                'discover:Discover contribution opportunities'
                'status:Show repository status'
                'activity:Show repository activity'
                'logs:Show performance logs'
                'performance:Show performance metrics'
                'help:Show help information'
                'config:Configuration management'
                'upstream:Upstream repository management'
                'validate-repo:Validate repository'
                'github:GitHub API operations'
                'contributions:Contribution management'
                'backup:Backup management'
            )
            _describe -t commands 'gitco commands' commands
            ;;
        args)
            case $line[1] in
                config)
                    local -a subcommands
                    subcommands=(
                        'validate:Validate configuration'
                        'config-status:Show configuration status'
                        'validate-detailed:Show detailed validation'
                    )
                    _describe -t subcommands 'config subcommands' subcommands
                    ;;
                upstream)
                    local -a subcommands
                    subcommands=(
                        'add:Add upstream remote'
                        'remove:Remove upstream remote'
                        'update:Update upstream URL'
                        'validate-upstream:Validate upstream'
                        'fetch:Fetch from upstream'
                        'merge:Merge upstream changes'
                    )
                    _describe -t subcommands 'upstream subcommands' subcommands
                    ;;
                github)
                    local -a subcommands
                    subcommands=(
                        'rate-limit-status:Show rate limit status'
                        'test-connection:Test GitHub connection'
                        'get-repo:Get repository information'
                        'get-issues:Get repository issues'
                        'get-issues-multi:Get issues from multiple repositories'
                    )
                    _describe -t subcommands 'github subcommands' subcommands
                    ;;
                contributions)
                    local -a subcommands
                    subcommands=(
                        'sync-history:Sync contribution history'
                        'stats:Show contribution statistics'
                        'recommendations:Show recommendations'
                        'export:Export contributions'
                        'trending:Show trending analysis'
                    )
                    _describe -t subcommands 'contributions subcommands' subcommands
                    ;;
                backup)
                    local -a subcommands
                    subcommands=(
                        'create:Create backup'
                        'list-backups:List backups'
                        'restore:Restore backup'
                        'validate-backup:Validate backup'
                        'delete:Delete backup'
                        'cleanup:Cleanup old backups'
                    )
                    _describe -t subcommands 'backup subcommands' subcommands
                    ;;
                sync|analyze|status|activity)
                    _arguments \\
                        '-r[Repository name]:repository:_gitco_repositories' \\
                        '--repo[Repository name]:repository:_gitco_repositories' \\
                        '-q[Suppress output]' \\
                        '--quiet[Suppress output]' \\
                        '-v[Verbose output]' \\
                        '--verbose[Verbose output]' \\
                        '--export[Export to file]:file:_files' \\
                        '-e[Export to file]:file:_files'
                    ;;
                discover)
                    _arguments \\
                        '-s[Filter by skill]:skill:_gitco_skills' \\
                        '--skill[Filter by skill]:skill:_gitco_skills' \\
                        '-l[Filter by label]:label:_gitco_labels' \\
                        '--label[Filter by label]:label:_gitco_labels' \\
                        '-n[Limit results]:number:' \\
                        '--limit[Limit results]:number:' \\
                        '-c[Minimum confidence]:number:' \\
                        '--min-confidence[Minimum confidence]:number:' \\
                        '-p[Personalized recommendations]' \\
                        '--personalized[Personalized recommendations]' \\
                        '-h[Show history]' \\
                        '--show-history[Show history]' \\
                        '-q[Suppress output]' \\
                        '--quiet[Suppress output]' \\
                        '--export[Export to file]:file:_files' \\
                        '-e[Export to file]:file:_files'
                    ;;
                logs|performance)
                    _arguments \\
                        '--export[Export to file]:file:_files' \\
                        '-e[Export to file]:file:_files' \\
                        '-f[Export format]:format:_gitco_formats' \\
                        '--format[Export format]:format:_gitco_formats' \\
                        '-d[Detailed output]' \\
                        '--detailed[Detailed output]'
                    ;;
                backup)
                    _arguments \\
                        '-r[Repository paths]:repos:' \\
                        '--repos[Repository paths]:repos:' \\
                        '-c[Config file]:file:_files' \\
                        '--config[Config file]:file:_files' \\
                        '-t[Backup type]:type:_gitco_backup_types' \\
                        '--type[Backup type]:type:_gitco_backup_types' \\
                        '-d[Description]:description:' \\
                        '--description[Description]:description:' \\
                        '--no-git-history[Exclude git history]' \\
                        '--compression[Compression level]:level:(0 1 2 3 4 5 6 7 8 9)' \\
                        '-q[Suppress output]' \\
                        '--quiet[Suppress output]'
                    ;;
            esac
            ;;
    esac
}

_gitco_repositories() {
    local repos
    repos=$(gitco _completion repos 2>/dev/null || echo '')
    _describe -t repositories 'repositories' repos
}

_gitco_skills() {
    local skills
    skills=$(gitco _completion skills 2>/dev/null || echo '')
    _describe -t skills 'skills' skills
}

_gitco_labels() {
    local labels
    labels=(
        'good first issue'
        'help wanted'
        'bug'
        'enhancement'
        'documentation'
        'question'
        'invalid'
        'wontfix'
        'duplicate'
        'feature'
        'improvement'
        'refactor'
        'test'
        'ci'
        'build'
        'deploy'
        'security'
        'performance'
        'accessibility'
        'internationalization'
    )
    _describe -t labels 'labels' labels
}

_gitco_providers() {
    local providers
    providers=(openai anthropic)
    _describe -t providers 'providers' providers
}

_gitco_formats() {
    local formats
    formats=(json csv)
    _describe -t formats 'formats' formats
}

_gitco_backup_types() {
    local types
    types=(full incremental config-only)
    _describe -t types 'backup types' types
}

compdef _gitco gitco
"""


@dataclass
class CompletionConfig:
    """Configuration for shell completion generation."""

    shell_type: Optional[str] = "bash"
    command_name: Optional[str] = "gitco"
    enable_descriptions: Optional[bool] = True
    enable_subcommands: Optional[bool] = True


@dataclass
class CompletionTemplate:
    """Template for shell completion scripts."""

    name: Optional[str] = None
    content: Optional[str] = None
    shell_type: Optional[str] = None


class ShellCompletionGenerator:
    """Generator for shell completion scripts."""

    def __init__(self, config: Optional[CompletionConfig] = None):
        """Initialize the completion generator.

        Args:
            config: Configuration for completion generation
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.templates: dict[str, CompletionTemplate] = {}

        # Initialize default templates
        self.templates["bash"] = CompletionTemplate(
            "bash", BASH_COMPLETION_TEMPLATE, "bash"
        )
        self.templates["zsh"] = CompletionTemplate(
            "zsh", ZSH_COMPLETION_TEMPLATE, "zsh"
        )

    def generate_completion_script(self) -> str:
        """Generate completion script based on configuration.

        Returns:
            Generated completion script
        """
        if not self.config:
            return ""

        shell_type = self.config.shell_type or "bash"

        if shell_type == "bash":
            return BASH_COMPLETION_TEMPLATE
        elif shell_type == "zsh":
            return ZSH_COMPLETION_TEMPLATE
        else:
            return ""

    def get_completion_template(
        self, template_name: str
    ) -> Optional[CompletionTemplate]:
        """Get a completion template by name.

        Args:
            template_name: Name of the template

        Returns:
            Completion template or None if not found
        """
        return self.templates.get(template_name)

    def format_completion_script(
        self,
        template: Optional[Union[CompletionTemplate, str]],
        variables: Optional[dict[str, str]],
    ) -> str:
        """Format a completion script with variables.

        Args:
            template: Completion template or template name
            variables: Variables to substitute

        Returns:
            Formatted completion script
        """
        # Handle template name lookup
        if isinstance(template, str):
            template = self.get_completion_template(template)

        if not template or not template.content:
            return ""

        if not variables:
            return template.content

        # Simple variable substitution
        result = template.content
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))

        return result


# Global completion generator instance
_completion_generator: Optional[ShellCompletionGenerator] = None


def get_completion_generator() -> ShellCompletionGenerator:
    """Get the global completion generator instance.

    Returns:
        Global completion generator
    """
    global _completion_generator
    if _completion_generator is None:
        _completion_generator = ShellCompletionGenerator()
    return _completion_generator


def reset_completion_generator() -> None:
    """Reset the global completion generator instance."""
    global _completion_generator
    _completion_generator = None


def generate_completion_script(shell_type: str = "bash") -> str:
    """Generate completion script for the specified shell.

    Args:
        shell_type: Type of shell (bash or zsh)

    Returns:
        Generated completion script
    """
    config = CompletionConfig(shell_type=shell_type)
    generator = ShellCompletionGenerator(config)
    return generator.generate_completion_script()
