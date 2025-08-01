"""Tests for prompt utilities."""


from gitco.utils.prompts import (
    PromptConfig,
    PromptManager,
    PromptTemplate,
    get_prompt_manager,
    reset_prompt_manager,
)


class TestPromptConfig:
    """Test PromptConfig dataclass."""

    def test_prompt_config_creation(self) -> None:
        """Test creating PromptConfig with default values."""
        config = PromptConfig()

        assert config.max_tokens == 1000
        assert config.temperature == 0.7
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0

    def test_prompt_config_with_custom_values(self) -> None:
        """Test creating PromptConfig with custom values."""
        config = PromptConfig(
            max_tokens=2000,
            temperature=0.5,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
        )

        assert config.max_tokens == 2000
        assert config.temperature == 0.5
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.1
        assert config.presence_penalty == 0.1

    def test_prompt_config_with_none_values(self) -> None:
        """Test PromptConfig creation with None values."""
        config = PromptConfig(
            max_tokens=None,
            temperature=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
        )

        assert config.max_tokens is None
        assert config.temperature is None
        assert config.top_p is None
        assert config.frequency_penalty is None
        assert config.presence_penalty is None


class TestPromptTemplate:
    """Test PromptTemplate dataclass."""

    def test_prompt_template_creation(self) -> None:
        """Test creating PromptTemplate with values."""
        template = PromptTemplate(
            name="test_template",
            content="Hello {name}, how are you?",
            variables=["name"],
        )

        assert template.name == "test_template"
        assert template.content == "Hello {name}, how are you?"
        assert template.variables == ["name"]

    def test_prompt_template_with_empty_variables(self) -> None:
        """Test PromptTemplate with empty variables."""
        template = PromptTemplate(
            name="simple_template",
            content="Simple prompt without variables",
            variables=[],
        )

        assert template.name == "simple_template"
        assert template.content == "Simple prompt without variables"
        assert template.variables == []

    def test_prompt_template_with_none_values(self) -> None:
        """Test PromptTemplate creation with None values."""
        template = PromptTemplate(name=None, content=None, variables=None)

        assert template.name is None
        assert template.content is None
        assert template.variables is None


class TestPromptManager:
    """Test PromptManager class."""

    def test_prompt_manager_initialization(self) -> None:
        """Test PromptManager initialization."""
        config = PromptConfig()
        manager = PromptManager(config)

        assert manager.config == config
        assert manager.logger is not None

    def test_prompt_manager_with_none_config(self) -> None:
        """Test PromptManager with None config."""
        manager = PromptManager(None)

        # Should handle None config gracefully
        assert manager.config is None
        assert manager.logger is not None

    def test_get_prompt_template_not_found(self) -> None:
        """Test get_prompt_template when template not found."""
        config = PromptConfig()
        manager = PromptManager(config)

        template = manager.get_prompt_template("nonexistent")

        assert template is None

    def test_format_prompt_with_none_template(self) -> None:
        """Test format_prompt with None template."""
        config = PromptConfig()
        manager = PromptManager(config)

        result = manager.format_prompt(None, {})

        assert result == ""

    def test_format_prompt_with_none_variables(self) -> None:
        """Test format_prompt with None variables."""
        config = PromptConfig()
        manager = PromptManager(config)

        template = PromptTemplate("test", "Hello {name}", ["name"])
        manager.templates["test"] = template

        result = manager.format_prompt("test", None)

        assert result == "Hello {name}"


class TestGlobalFunctions:
    """Test global functions."""

    def test_get_prompt_manager(self) -> None:
        """Test getting global prompt manager."""
        # Reset first
        reset_prompt_manager()

        manager1 = get_prompt_manager()
        manager2 = get_prompt_manager()

        # Should return the same instance
        assert manager1 is manager2

    def test_reset_prompt_manager(self) -> None:
        """Test resetting global prompt manager."""
        manager1 = get_prompt_manager()
        reset_prompt_manager()
        manager2 = get_prompt_manager()

        # Should be different instances
        assert manager1 is not manager2
