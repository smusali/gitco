"""Test GitCo utility functions."""

import logging
import os
import tempfile

import pytest

from gitco.utils.common import (
    create_progress_context,
    ensure_directory_exists,
    format_error_message,
    get_logger,
    handle_validation_errors,
    is_quiet_mode,
    log_api_call,
    log_configuration_loaded,
    log_error_and_exit,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    log_repository_operation,
    log_validation_result,
    print_success_panel,
    safe_execute,
    set_quiet_mode,
    setup_logging,
    update_progress,
    validate_directory_exists,
    validate_file_exists,
)
from gitco.utils.exception import (
    APIError,
    ConfigurationError,
    GitCoError,
    GitOperationError,
    ValidationError,
)


def test_gitco_error() -> None:
    """Test GitCoError base exception."""
    error = GitCoError("Test error")
    assert str(error) == "Test error"


def test_configuration_error() -> None:
    """Test ConfigurationError exception."""
    error = ConfigurationError("Configuration error")
    assert str(error) == "Configuration error"
    assert isinstance(error, GitCoError)


def test_git_operation_error() -> None:
    """Test GitOperationError exception."""
    error = GitOperationError("Git operation failed")
    assert str(error) == "Git operation failed"
    assert isinstance(error, GitCoError)


def test_validation_error() -> None:
    """Test ValidationError exception."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"
    assert isinstance(error, GitCoError)


def test_api_error() -> None:
    """Test APIError exception."""
    error = APIError("API call failed")
    assert str(error) == "API call failed"
    assert isinstance(error, GitCoError)


def test_setup_logging_default() -> None:
    """Test setup_logging with default parameters."""
    logger = setup_logging()
    assert logger.name == "gitco"
    assert logger.level == logging.INFO


def test_setup_logging_verbose() -> None:
    """Test setup_logging with verbose mode."""
    logger = setup_logging(verbose=True)
    assert logger.level == logging.DEBUG


def test_setup_logging_quiet() -> None:
    """Test setup_logging with quiet mode."""
    logger = setup_logging(quiet=True)
    assert logger.level == logging.ERROR


def test_setup_logging_with_file(temp_log_file: str) -> None:
    """Test setup_logging with log file."""
    logger = setup_logging(log_file=temp_log_file)
    assert logger.name == "gitco"
    assert logger.level == logging.INFO


def test_get_logger() -> None:
    """Test get_logger function."""
    logger = get_logger()
    assert logger.name == "gitco"


def test_log_error_and_exit(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_error_and_exit function."""
    with pytest.raises(SystemExit):
        log_error_and_exit("Test error")


def test_log_error_and_exit_with_error(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_error_and_exit function with error."""
    error = ValueError("Test exception")
    with pytest.raises(SystemExit):
        log_error_and_exit("Test error", error)


def test_log_error_and_exit_custom_code(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_error_and_exit function with custom exit code."""
    with pytest.raises(SystemExit) as exc_info:
        log_error_and_exit("Test error", exit_code=42)
    assert exc_info.value.code == 42


def test_safe_execute_success() -> None:
    """Test safe_execute with successful function."""

    def test_func(x: int, y: int) -> int:
        return x + y

    result = safe_execute(test_func, 2, 3, error_message="Test error")
    assert result == 5


def test_safe_execute_failure_exit(caplog: pytest.LogCaptureFixture) -> None:
    """Test safe_execute with function that raises exception."""

    def test_func() -> None:
        raise ValueError("Test exception")

    with pytest.raises(SystemExit):
        safe_execute(test_func, error_message="Test error", exit_on_error=True)


def test_safe_execute_failure_no_exit(caplog: pytest.LogCaptureFixture) -> None:
    """Test safe_execute with function that raises exception but doesn't exit."""

    def test_func() -> None:
        raise ValueError("Test exception")

    with pytest.raises(ValueError):
        safe_execute(test_func, error_message="Test error", exit_on_error=False)


def test_validate_file_exists_success(temp_log_file: str) -> None:
    """Test validate_file_exists with existing file."""
    # Create a temporary file
    with open(temp_log_file, "w") as f:
        f.write("test content")

    # Should not raise an exception
    validate_file_exists(temp_log_file, "Test file")


def test_validate_file_exists_failure() -> None:
    """Test validate_file_exists with non-existent file."""
    with pytest.raises(ValidationError):
        validate_file_exists("/nonexistent/file", "Test file")


def test_validate_directory_exists_success(temp_log_file: str) -> None:
    """Test validate_directory_exists with existing directory."""
    # Create a temporary directory
    temp_dir = os.path.dirname(temp_log_file)
    validate_directory_exists(temp_dir, "Test directory")


def test_validate_directory_exists_failure() -> None:
    """Test validate_directory_exists with non-existent directory."""
    with pytest.raises(ValidationError):
        validate_directory_exists("/nonexistent/directory", "Test directory")


def test_ensure_directory_exists_new() -> None:
    """Test ensure_directory_exists with new directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        new_dir = os.path.join(temp_dir, "new_dir")
        ensure_directory_exists(new_dir)
        assert os.path.exists(new_dir)


def test_ensure_directory_exists_existing() -> None:
    """Test ensure_directory_exists with existing directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        ensure_directory_exists(temp_dir)
        assert os.path.exists(temp_dir)


def test_format_error_message() -> None:
    """Test format_error_message function."""
    error = ValueError("Test error")
    message = format_error_message(error, "Test context")
    assert "Test error" in message
    assert "Test context" in message


def test_handle_validation_errors() -> None:
    """Test handle_validation_errors function."""
    errors: list[str] = ["Error 1", "Error 2"]
    with pytest.raises(SystemExit):
        handle_validation_errors(errors, "Test context")


def test_handle_validation_errors_empty() -> None:
    """Test handle_validation_errors function with empty errors."""
    errors: list[str] = []
    # Should not raise an exception
    handle_validation_errors(errors, "Test context")


def test_log_operation_start(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_operation_start function."""
    log_operation_start("test_operation")
    assert "test_operation" in caplog.text


def test_log_operation_start_with_context(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_operation_start function with context."""
    log_operation_start("test_operation", repo="test_repo")
    assert "test_operation" in caplog.text
    assert "test_repo" in caplog.text


def test_log_operation_success(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_operation_success function."""
    log_operation_success("test_operation")
    assert "test_operation" in caplog.text


def test_log_operation_success_with_context(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_operation_success function with context."""
    log_operation_success("test_operation", repo="test_repo")
    assert "test_operation" in caplog.text
    assert "test_repo" in caplog.text


def test_log_operation_failure(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_operation_failure function."""
    error = ValueError("Test error")
    log_operation_failure("test_operation", error)
    assert "test_operation" in caplog.text


def test_log_operation_failure_with_context(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_operation_failure function with context."""
    error = ValueError("Test error")
    log_operation_failure("test_operation", error, repo="test_repo")
    assert "test_operation" in caplog.text
    assert "test_repo" in caplog.text


def test_create_progress_context() -> None:
    """Test create_progress_context function."""
    context = create_progress_context("test_operation", 10)
    assert context["operation"] == "test_operation"
    assert context["total"] == 10
    assert context["current"] == 0


def test_update_progress(caplog: pytest.LogCaptureFixture) -> None:
    """Test update_progress function."""
    context = create_progress_context("test_operation", 10)
    update_progress(context, 5, "Test message")
    assert context["current"] == 5


def test_update_progress_no_total(caplog: pytest.LogCaptureFixture) -> None:
    """Test update_progress function without total."""
    context = create_progress_context("test_operation")
    update_progress(context, 5, "Test message")
    assert context["current"] == 5


def test_log_configuration_loaded(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_configuration_loaded function."""
    log_configuration_loaded("/path/to/config.yml", 5)
    assert "Configuration loaded" in caplog.text


def test_log_repository_operation(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_repository_operation function."""
    log_repository_operation("test_repo", "sync")
    assert "test_repo" in caplog.text
    assert "sync" in caplog.text


def test_log_api_call(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_api_call function."""
    # The function prints to console, not to logger, so we need to capture stdout
    import sys
    from io import StringIO

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        log_api_call("openai", "/v1/chat/completions")
        output = sys.stdout.getvalue()
        assert "openai" in output
        assert "/v1/chat/completions" in output
    finally:
        sys.stdout = old_stdout


def test_log_validation_result_passed(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_validation_result function with passed validation."""
    # The function prints to console, not to logger, so we need to capture stdout
    import sys
    from io import StringIO

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        log_validation_result("test_validation", True, "All good")
        output = sys.stdout.getvalue()
        assert "test_validation" in output
        assert "passed" in output.lower()
    finally:
        sys.stdout = old_stdout


def test_log_validation_result_failed(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_validation_result function with failed validation."""
    # The function prints to console, not to logger, so we need to capture stdout
    import sys
    from io import StringIO

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        log_validation_result("test_validation", False, "Something wrong")
        output = sys.stdout.getvalue()
        assert "test_validation" in output
        assert "failed" in output.lower()
    finally:
        sys.stdout = old_stdout


def test_log_validation_result_no_details(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_validation_result with no details."""
    # The function prints to console, not to logger, so we need to capture stdout
    import sys
    from io import StringIO

    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        log_validation_result("test_validation", True)
        output = sys.stdout.getvalue()
        assert "test_validation" in output
        assert "passed" in output.lower()
    finally:
        sys.stdout = old_stdout


def test_setup_logging_with_invalid_level() -> None:
    """Test setup_logging with invalid log level."""
    logger = setup_logging(level="INVALID_LEVEL")
    assert logger.name == "gitco"
    assert logger.level == logging.INFO  # Should default to INFO


def test_safe_execute_with_exception() -> None:
    """Test safe_execute with function that raises exception."""

    def test_func() -> None:
        raise ValueError("Test exception")

    with pytest.raises(ValueError):
        safe_execute(test_func, error_message="Test error", exit_on_error=False)


def test_validate_file_exists_with_directory() -> None:
    """Test validate_file_exists with directory path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # The function doesn't raise ValidationError for directories, it just logs
        # So we'll test that it doesn't raise an exception
        validate_file_exists(temp_dir, "Directory")
        # If we get here, the test passes


def test_ensure_directory_exists_with_file() -> None:
    """Test ensure_directory_exists with file path."""
    with tempfile.NamedTemporaryFile() as temp_file:
        with pytest.raises(OSError):
            ensure_directory_exists(temp_file.name)


# New test cases for GitCoError exception class
def test_gitco_error_creation() -> None:
    """Test GitCoError exception creation."""
    error = GitCoError("Test error message")

    assert str(error) == "Test error message"
    assert isinstance(error, Exception)


def test_gitco_error_with_details() -> None:
    """Test GitCoError with detailed message."""
    error = GitCoError("Operation failed: repository not found")

    assert "Operation failed" in str(error)
    assert "repository not found" in str(error)


def test_gitco_error_inheritance() -> None:
    """Test GitCoError inheritance from Exception."""
    error = GitCoError("Test")

    assert isinstance(error, Exception)
    assert issubclass(GitCoError, Exception)


def test_gitco_error_empty_message() -> None:
    """Test GitCoError with empty message."""
    error = GitCoError("")

    assert str(error) == ""


def test_gitco_error_special_characters() -> None:
    """Test GitCoError with special characters in message."""
    error = GitCoError("Error with special chars: !@#$%^&*()")

    assert "special chars" in str(error)
    assert "!@#$%^&*()" in str(error)


# New test cases for ConfigurationError exception class
def test_configuration_error_creation() -> None:
    """Test ConfigurationError exception creation."""
    error = ConfigurationError("Configuration file not found")

    assert str(error) == "Configuration file not found"
    assert isinstance(error, GitCoError)


def test_configuration_error_inheritance() -> None:
    """Test ConfigurationError inheritance from GitCoError."""
    error = ConfigurationError("Test")

    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)
    assert issubclass(ConfigurationError, GitCoError)


def test_configuration_error_with_file_path() -> None:
    """Test ConfigurationError with file path in message."""
    error = ConfigurationError("Invalid configuration in /path/to/config.yml")

    assert "Invalid configuration" in str(error)
    assert "/path/to/config.yml" in str(error)


def test_configuration_error_yaml_specific() -> None:
    """Test ConfigurationError with YAML-specific message."""
    error = ConfigurationError("Invalid YAML syntax at line 15")

    assert "YAML syntax" in str(error)
    assert "line 15" in str(error)


def test_configuration_error_missing_field() -> None:
    """Test ConfigurationError for missing required field."""
    error = ConfigurationError("Missing required field: 'repositories'")

    assert "Missing required field" in str(error)
    assert "repositories" in str(error)


# New test cases for GitOperationError exception class
def test_git_operation_error_creation() -> None:
    """Test GitOperationError exception creation."""
    error = GitOperationError("Git command failed: merge conflict")

    assert str(error) == "Git command failed: merge conflict"
    assert isinstance(error, GitCoError)


def test_git_operation_error_inheritance() -> None:
    """Test GitOperationError inheritance from GitCoError."""
    error = GitOperationError("Test")

    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)
    assert issubclass(GitOperationError, GitCoError)


def test_git_operation_error_merge_conflict() -> None:
    """Test GitOperationError for merge conflict."""
    error = GitOperationError("Merge conflict in api.py")

    assert "Merge conflict" in str(error)
    assert "api.py" in str(error)


def test_git_operation_error_remote_failure() -> None:
    """Test GitOperationError for remote operation failure."""
    error = GitOperationError("Failed to fetch from remote: connection timeout")

    assert "Failed to fetch" in str(error)
    assert "connection timeout" in str(error)


def test_git_operation_error_branch_operation() -> None:
    """Test GitOperationError for branch operation failure."""
    error = GitOperationError("Cannot switch to branch 'feature': uncommitted changes")

    assert "Cannot switch" in str(error)
    assert "uncommitted changes" in str(error)


# New test cases for ValidationError exception class
def test_validation_error_creation() -> None:
    """Test ValidationError exception creation."""
    error = ValidationError("Repository path is invalid")

    assert str(error) == "Repository path is invalid"
    assert isinstance(error, GitCoError)


def test_validation_error_inheritance() -> None:
    """Test ValidationError inheritance from GitCoError."""
    error = ValidationError("Test")

    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)
    assert issubclass(ValidationError, GitCoError)


def test_validation_error_path_validation() -> None:
    """Test ValidationError for path validation."""
    error = ValidationError("Path '/invalid/path' does not exist")

    assert "Path" in str(error)
    assert "/invalid/path" in str(error)
    assert "does not exist" in str(error)


def test_validation_error_url_validation() -> None:
    """Test ValidationError for URL validation."""
    error = ValidationError("Invalid repository URL: not-a-valid-url")

    assert "Invalid repository URL" in str(error)
    assert "not-a-valid-url" in str(error)


def test_validation_error_configuration_validation() -> None:
    """Test ValidationError for configuration validation."""
    error = ValidationError("Configuration validation failed: missing required fields")

    assert "Configuration validation failed" in str(error)
    assert "missing required fields" in str(error)


# New test cases for APIError exception class
def test_api_error_creation() -> None:
    """Test APIError exception creation."""
    error = APIError("API request failed: rate limit exceeded")

    assert str(error) == "API request failed: rate limit exceeded"
    assert isinstance(error, GitCoError)


def test_api_error_inheritance() -> None:
    """Test APIError inheritance from GitCoError."""
    error = APIError("Test")

    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)
    assert issubclass(APIError, GitCoError)


def test_api_error_rate_limit() -> None:
    """Test APIError for rate limit exceeded."""
    error = APIError("Rate limit exceeded: 100 requests per hour")

    assert "Rate limit exceeded" in str(error)
    assert "100 requests per hour" in str(error)


def test_api_error_authentication() -> None:
    """Test APIError for authentication failure."""
    error = APIError("Authentication failed: invalid API key")

    assert "Authentication failed" in str(error)
    assert "invalid API key" in str(error)


def test_api_error_network() -> None:
    """Test APIError for network-related issues."""
    error = APIError("Network error: connection timeout after 30 seconds")

    assert "Network error" in str(error)
    assert "connection timeout" in str(error)


# Additional test cases for GitCoError exception class
def test_gitco_error_with_cause() -> None:
    """Test GitCoError with a cause."""
    original_error = ValueError("Original error")
    error = GitCoError("Test error message")
    error.__cause__ = original_error

    assert str(error) == "Test error message"
    assert error.__cause__ == original_error


def test_gitco_error_with_context() -> None:
    """Test GitCoError with context."""
    error = GitCoError("Test error message")
    error.__context__ = Exception("Context error")

    assert str(error) == "Test error message"
    assert error.__context__ is not None


def test_gitco_error_repr() -> None:
    """Test GitCoError string representation."""
    error = GitCoError("Test error message")

    repr_str = repr(error)
    assert "GitCoError" in repr_str
    assert "Test error message" in repr_str


def test_gitco_error_attributes() -> None:
    """Test GitCoError attributes."""
    error = GitCoError("Test error message")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


def test_gitco_error_inheritance_hierarchy() -> None:
    """Test GitCoError inheritance hierarchy."""
    error = GitCoError("Test error")

    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)
    assert not isinstance(error, ValueError)  # Should not inherit from ValueError


# Additional test cases for ConfigurationError exception class
def test_configuration_error_with_cause() -> None:
    """Test ConfigurationError with a cause."""
    original_error = ValueError("Original error")
    error = ConfigurationError("Configuration error message")
    error.__cause__ = original_error

    assert str(error) == "Configuration error message"
    assert error.__cause__ == original_error


def test_configuration_error_repr() -> None:
    """Test ConfigurationError string representation."""
    error = ConfigurationError("Configuration error message")

    repr_str = repr(error)
    assert "ConfigurationError" in repr_str
    assert "Configuration error message" in repr_str


def test_configuration_error_attributes() -> None:
    """Test ConfigurationError attributes."""
    error = ConfigurationError("Configuration error message")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


def test_configuration_error_inheritance_hierarchy() -> None:
    """Test ConfigurationError inheritance hierarchy."""
    error = ConfigurationError("Test configuration error")

    assert isinstance(error, ConfigurationError)
    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)


# Additional test cases for GitOperationError exception class
def test_git_operation_error_with_cause() -> None:
    """Test GitOperationError with a cause."""
    original_error = ValueError("Original error")
    error = GitOperationError("Git operation error message")
    error.__cause__ = original_error

    assert str(error) == "Git operation error message"
    assert error.__cause__ == original_error


def test_git_operation_error_with_operation_type() -> None:
    """Test GitOperationError with specific operation type."""
    error = GitOperationError("Failed to merge branch 'feature' into 'main'")

    assert "Failed to merge" in str(error)
    assert "branch 'feature'" in str(error)
    assert "into 'main'" in str(error)


def test_git_operation_error_repr() -> None:
    """Test GitOperationError string representation."""
    error = GitOperationError("Git operation error message")

    repr_str = repr(error)
    assert "GitOperationError" in repr_str
    assert "Git operation error message" in repr_str


def test_git_operation_error_attributes() -> None:
    """Test GitOperationError attributes."""
    error = GitOperationError("Git operation error message")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


def test_git_operation_error_inheritance_hierarchy() -> None:
    """Test GitOperationError inheritance hierarchy."""
    error = GitOperationError("Test git operation error")

    assert isinstance(error, GitOperationError)
    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)


# Additional test cases for ValidationError exception class
def test_validation_error_with_cause() -> None:
    """Test ValidationError with a cause."""
    original_error = ValueError("Original error")
    error = ValidationError("Validation error message")
    error.__cause__ = original_error

    assert str(error) == "Validation error message"
    assert error.__cause__ == original_error


def test_validation_error_with_field_name() -> None:
    """Test ValidationError with specific field name."""
    error = ValidationError("Field 'repository_url' is required but missing")

    assert "Field 'repository_url'" in str(error)
    assert "is required" in str(error)
    assert "missing" in str(error)


def test_validation_error_repr() -> None:
    """Test ValidationError string representation."""
    error = ValidationError("Validation error message")

    repr_str = repr(error)
    assert "ValidationError" in repr_str
    assert "Validation error message" in repr_str


def test_validation_error_attributes() -> None:
    """Test ValidationError attributes."""
    error = ValidationError("Validation error message")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


def test_validation_error_inheritance_hierarchy() -> None:
    """Test ValidationError inheritance hierarchy."""
    error = ValidationError("Test validation error")

    assert isinstance(error, ValidationError)
    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)


# Additional test cases for APIError exception class
def test_api_error_with_cause() -> None:
    """Test APIError with a cause."""
    original_error = ValueError("Original error")
    error = APIError("API error message")
    error.__cause__ = original_error

    assert str(error) == "API error message"
    assert error.__cause__ == original_error


def test_api_error_with_status_code() -> None:
    """Test APIError with HTTP status code."""
    error = APIError("API request failed with status code 404: Not Found")

    assert "API request failed" in str(error)
    assert "status code 404" in str(error)
    assert "Not Found" in str(error)


def test_api_error_repr() -> None:
    """Test APIError string representation."""
    error = APIError("API error message")

    repr_str = repr(error)
    assert "APIError" in repr_str
    assert "API error message" in repr_str


def test_api_error_attributes() -> None:
    """Test APIError attributes."""
    error = APIError("API error message")

    assert hasattr(error, "__dict__")
    assert hasattr(error, "__cause__")
    assert hasattr(error, "__context__")


def test_api_error_inheritance_hierarchy() -> None:
    """Test APIError inheritance hierarchy."""
    error = APIError("Test API error")

    assert isinstance(error, APIError)
    assert isinstance(error, GitCoError)
    assert isinstance(error, Exception)


def test_quiet_mode_functionality() -> None:
    """Test that quiet mode properly suppresses output."""
    # Test initial state
    assert not is_quiet_mode()

    # Test setting quiet mode
    set_quiet_mode(True)
    assert is_quiet_mode()

    # Test unsetting quiet mode
    set_quiet_mode(False)
    assert not is_quiet_mode()

    # Test that print functions respect quiet mode
    set_quiet_mode(True)
    # This should not raise any exceptions and should not print anything
    print_success_panel("Test message", "Test details")

    # Reset quiet mode
    set_quiet_mode(False)
