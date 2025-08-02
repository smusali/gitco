"""Tests for shell completion utilities."""

from gitco.templates.shell_completion import (
    CompletionConfig,
    CompletionTemplate,
    ShellCompletionGenerator,
    generate_completion_script,
    get_completion_generator,
    reset_completion_generator,
)


class TestCompletionConfig:
    """Test CompletionConfig dataclass."""

    def test_completion_config_creation(self) -> None:
        """Test creating CompletionConfig with default values."""
        config = CompletionConfig()

        assert config.shell_type == "bash"
        assert config.command_name == "gitco"
        assert config.enable_descriptions is True
        assert config.enable_subcommands is True

    def test_completion_config_with_custom_values(self) -> None:
        """Test creating CompletionConfig with custom values."""
        config = CompletionConfig(
            shell_type="zsh",
            command_name="custom_command",
            enable_descriptions=False,
            enable_subcommands=False,
        )

        assert config.shell_type == "zsh"
        assert config.command_name == "custom_command"
        assert config.enable_descriptions is False
        assert config.enable_subcommands is False

    def test_completion_config_with_none_values(self) -> None:
        """Test CompletionConfig creation with None values."""
        config = CompletionConfig(
            shell_type=None,
            command_name=None,
            enable_descriptions=None,
            enable_subcommands=None,
        )

        assert config.shell_type is None
        assert config.command_name is None
        assert config.enable_descriptions is None
        assert config.enable_subcommands is None


class TestCompletionTemplate:
    """Test CompletionTemplate dataclass."""

    def test_completion_template_creation(self) -> None:
        """Test creating CompletionTemplate with values."""
        template = CompletionTemplate(
            name="test_template", content="# Test completion script", shell_type="bash"
        )

        assert template.name == "test_template"
        assert template.content == "# Test completion script"
        assert template.shell_type == "bash"

    def test_completion_template_with_empty_content(self) -> None:
        """Test CompletionTemplate with empty content."""
        template = CompletionTemplate(
            name="empty_template", content="", shell_type="zsh"
        )

        assert template.name == "empty_template"
        assert template.content == ""
        assert template.shell_type == "zsh"

    def test_completion_template_with_none_values(self) -> None:
        """Test CompletionTemplate creation with None values."""
        template = CompletionTemplate(name=None, content=None, shell_type=None)

        assert template.name is None
        assert template.content is None
        assert template.shell_type is None


class TestShellCompletionGenerator:
    """Test ShellCompletionGenerator class."""

    def test_completion_generator_initialization(self) -> None:
        """Test ShellCompletionGenerator initialization."""
        config = CompletionConfig()
        generator = ShellCompletionGenerator(config)

        assert generator.config == config
        assert generator.logger is not None

    def test_completion_generator_with_none_config(self) -> None:
        """Test ShellCompletionGenerator with None config."""
        generator = ShellCompletionGenerator(None)

        # Should handle None config gracefully
        assert generator.config is None
        assert generator.logger is not None

    def test_generate_completion_script_bash(self) -> None:
        """Test generate_completion_script for bash."""
        config = CompletionConfig(shell_type="bash")
        generator = ShellCompletionGenerator(config)

        script = generator.generate_completion_script()

        assert isinstance(script, str)
        assert len(script) > 0
        assert "bash" in script.lower() or "complete" in script.lower()

    def test_generate_completion_script_zsh(self) -> None:
        """Test generate_completion_script for zsh."""
        config = CompletionConfig(shell_type="zsh")
        generator = ShellCompletionGenerator(config)

        script = generator.generate_completion_script()

        assert isinstance(script, str)
        assert len(script) > 0
        assert "zsh" in script.lower() or "compdef" in script.lower()

    def test_generate_completion_script_unsupported_shell(self) -> None:
        """Test generate_completion_script with unsupported shell."""
        config = CompletionConfig(shell_type="unsupported")
        generator = ShellCompletionGenerator(config)

        script = generator.generate_completion_script()

        assert isinstance(script, str)
        assert script == ""  # Should return empty string for unsupported shells

    def test_get_completion_template_not_found(self) -> None:
        """Test get_completion_template when template not found."""
        config = CompletionConfig()
        generator = ShellCompletionGenerator(config)

        template = generator.get_completion_template("nonexistent")

        assert template is None

    def test_format_completion_script_with_none_template(self) -> None:
        """Test format_completion_script with None template."""
        config = CompletionConfig()
        generator = ShellCompletionGenerator(config)

        result = generator.format_completion_script(None, {})

        assert result == ""

    def test_format_completion_script_with_none_variables(self) -> None:
        """Test format_completion_script with None variables."""
        config = CompletionConfig()
        generator = ShellCompletionGenerator(config)

        template = CompletionTemplate("test", "echo {command}", "bash")
        generator.templates["test"] = template

        result = generator.format_completion_script("test", None)

        assert result == "echo {command}"


class TestGlobalFunctions:
    """Test global functions."""

    def test_generate_completion_script(self) -> None:
        """Test generate_completion_script function."""
        script = generate_completion_script("bash")

        assert isinstance(script, str)
        assert len(script) > 0

    def test_get_completion_generator(self) -> None:
        """Test getting global completion generator."""
        # Reset first
        reset_completion_generator()

        generator1 = get_completion_generator()
        generator2 = get_completion_generator()

        # Should return the same instance
        assert generator1 is generator2

    def test_reset_completion_generator(self) -> None:
        """Test resetting global completion generator."""
        generator1 = get_completion_generator()
        reset_completion_generator()
        generator2 = get_completion_generator()

        # Should be different instances
        assert generator1 is not generator2
