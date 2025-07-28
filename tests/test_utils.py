"""Test GitCo utility functions."""

import logging
import os
import tempfile
from collections.abc import Generator

import pytest

from gitco.utils import (
    APIError,
    ConfigurationError,
    GitCoError,
    GitOperationError,
    ValidationError,
    create_progress_context,
    ensure_directory_exists,
    format_error_message,
    get_logger,
    handle_validation_errors,
    log_api_call,
    log_configuration_loaded,
    log_error_and_exit,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    log_repository_operation,
    log_validation_result,
    safe_execute,
    setup_logging,
    update_progress,
    validate_directory_exists,
    validate_file_exists,
)


@pytest.fixture
def temp_log_file() -> Generator[str, None, None]:
    """Create a temporary log file path."""
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
        temp_path = f.name
        f.close()
        os.unlink(temp_path)  # Remove the file immediately
        yield temp_path


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
