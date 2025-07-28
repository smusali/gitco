"""Test GitCo utility functions."""

import logging
import os
import tempfile

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
def temp_log_file():
    """Create a temporary log file path."""
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
        temp_path = f.name
        f.close()
        os.unlink(temp_path)  # Remove the file immediately
        yield temp_path


def test_gitco_error():
    """Test GitCoError base exception."""
    error = GitCoError("Test error")
    assert str(error) == "Test error"


def test_configuration_error():
    """Test ConfigurationError exception."""
    error = ConfigurationError("Configuration error")
    assert str(error) == "Configuration error"
    assert isinstance(error, GitCoError)


def test_git_operation_error():
    """Test GitOperationError exception."""
    error = GitOperationError("Git operation failed")
    assert str(error) == "Git operation failed"
    assert isinstance(error, GitCoError)


def test_validation_error():
    """Test ValidationError exception."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"
    assert isinstance(error, GitCoError)


def test_api_error():
    """Test APIError exception."""
    error = APIError("API call failed")
    assert str(error) == "API call failed"
    assert isinstance(error, GitCoError)


def test_setup_logging_default():
    """Test setup_logging with default parameters."""
    logger = setup_logging()
    assert logger.name == "gitco"
    assert logger.level == logging.INFO


def test_setup_logging_verbose():
    """Test setup_logging with verbose mode."""
    logger = setup_logging(verbose=True)
    assert logger.level == logging.DEBUG


def test_setup_logging_quiet():
    """Test setup_logging with quiet mode."""
    logger = setup_logging(quiet=True)
    assert logger.level == logging.ERROR


def test_setup_logging_with_file(temp_log_file):
    """Test setup_logging with log file."""
    logger = setup_logging(log_file=temp_log_file)
    assert logger.name == "gitco"

    # Test that logging works
    test_message = "Test log message"
    logger.info(test_message)

    # Check that file was created and contains the message
    assert os.path.exists(temp_log_file)
    with open(temp_log_file) as f:
        content = f.read()
        assert test_message in content


def test_get_logger():
    """Test get_logger function."""
    logger = get_logger()
    assert logger.name == "gitco"
    assert isinstance(logger, logging.Logger)


def test_log_error_and_exit(caplog):
    """Test log_error_and_exit function."""
    with pytest.raises(SystemExit) as exc_info:
        log_error_and_exit("Test error")

    assert exc_info.value.code == 1
    assert "Test error" in caplog.text


def test_log_error_and_exit_with_error(caplog):
    """Test log_error_and_exit function with exception."""
    error = ValueError("Test exception")
    with pytest.raises(SystemExit) as exc_info:
        log_error_and_exit("Test error", error)

    assert exc_info.value.code == 1
    assert "Test error" in caplog.text
    assert "Test exception" in caplog.text


def test_log_error_and_exit_custom_code(caplog):
    """Test log_error_and_exit function with custom exit code."""
    with pytest.raises(SystemExit) as exc_info:
        log_error_and_exit("Test error", exit_code=42)

    assert exc_info.value.code == 42


def test_safe_execute_success():
    """Test safe_execute with successful function."""

    def test_func(x, y):
        return x + y

    result = safe_execute(test_func, 2, 3, error_message="Test error")
    assert result == 5


def test_safe_execute_failure_exit(caplog):
    """Test safe_execute with failing function that exits."""

    def test_func():
        raise ValueError("Test error")

    with pytest.raises(SystemExit) as exc_info:
        safe_execute(test_func, error_message="Operation failed")

    assert exc_info.value.code == 1
    assert "Operation failed" in caplog.text


def test_safe_execute_failure_no_exit(caplog):
    """Test safe_execute with failing function that doesn't exit."""

    def test_func():
        raise ValueError("Test error")

    result = safe_execute(
        test_func, error_message="Operation failed", exit_on_error=False
    )
    assert result is None
    assert "Operation failed" in caplog.text


def test_validate_file_exists_success(temp_log_file):
    """Test validate_file_exists with existing file."""
    # Create a temporary file
    with open(temp_log_file, "w") as f:
        f.write("test")

    # Should not raise an exception
    validate_file_exists(temp_log_file)


def test_validate_file_exists_failure():
    """Test validate_file_exists with non-existing file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        validate_file_exists("nonexistent.txt")

    assert "File not found: nonexistent.txt" in str(exc_info.value)


def test_validate_directory_exists_success(temp_log_file):
    """Test validate_directory_exists with existing directory."""
    # Create a temporary directory
    temp_dir = os.path.dirname(temp_log_file)
    validate_directory_exists(temp_dir)


def test_validate_directory_exists_failure():
    """Test validate_directory_exists with non-existing directory."""
    with pytest.raises(FileNotFoundError) as exc_info:
        validate_directory_exists("nonexistent_dir")

    assert "Directory not found: nonexistent_dir" in str(exc_info.value)


def test_ensure_directory_exists_new():
    """Test ensure_directory_exists with new directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        new_dir = os.path.join(temp_dir, "new_subdir")
        ensure_directory_exists(new_dir)
        assert os.path.isdir(new_dir)


def test_ensure_directory_exists_existing():
    """Test ensure_directory_exists with existing directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        ensure_directory_exists(temp_dir)
        assert os.path.isdir(temp_dir)


def test_format_error_message():
    """Test format_error_message function."""
    error = ValueError("Test error")

    # Without context
    message = format_error_message(error)
    assert message == "Test error"

    # With context
    message = format_error_message(error, "Test context")
    assert message == "Test context: Test error"


def test_handle_validation_errors():
    """Test handle_validation_errors function."""
    errors = ["Error 1", "Error 2"]

    with pytest.raises(ValidationError) as exc_info:
        handle_validation_errors(errors, "Test validation")

    assert "Test validation validation failed" in str(exc_info.value)


def test_handle_validation_errors_empty():
    """Test handle_validation_errors function with empty errors."""
    errors = []
    # Should not raise an exception
    handle_validation_errors(errors, "Test validation")


def test_log_operation_start(caplog):
    """Test log_operation_start function."""
    log_operation_start("test operation")
    assert "Starting test operation" in caplog.text


def test_log_operation_start_with_context(caplog):
    """Test log_operation_start function with context."""
    log_operation_start("test operation", param1="value1", param2="value2")
    assert "Starting test operation: param1=value1 param2=value2" in caplog.text


def test_log_operation_success(caplog):
    """Test log_operation_success function."""
    log_operation_success("test operation")
    assert "Completed test operation" in caplog.text


def test_log_operation_success_with_context(caplog):
    """Test log_operation_success function with context."""
    log_operation_success("test operation", result="success", count=5)
    assert "Completed test operation: result=success count=5" in caplog.text


def test_log_operation_failure(caplog):
    """Test log_operation_failure function."""
    error = ValueError("Test error")
    log_operation_failure("test operation", error)
    assert "Failed test operation: Test error" in caplog.text


def test_log_operation_failure_with_context(caplog):
    """Test log_operation_failure function with context."""
    error = ValueError("Test error")
    log_operation_failure("test operation", error, param1="value1")
    assert "Failed test operation: param1=value1 - Test error" in caplog.text


def test_create_progress_context():
    """Test create_progress_context function."""
    context = create_progress_context("test operation", 10)

    assert context["operation"] == "test operation"
    assert context["total"] == 10
    assert context["current"] == 0
    assert context["start_time"] is None


def test_update_progress(caplog):
    """Test update_progress function."""
    context = create_progress_context("test operation", 10)

    update_progress(context, 5, "Processing item")
    assert context["current"] == 5
    assert "test operation: 5/10 (50.0%) - Processing item" in caplog.text


def test_update_progress_no_total(caplog):
    """Test update_progress function without total."""
    context = create_progress_context("test operation")

    update_progress(context, 5, "Processing item")
    assert context["current"] == 5
    assert "test operation: 5 - Processing item" in caplog.text


def test_log_configuration_loaded(caplog):
    """Test log_configuration_loaded function."""
    log_configuration_loaded("/path/to/config.yml", 5)

    assert "Configuration loaded from /path/to/config.yml" in caplog.text
    assert "Found 5 repositories" in caplog.text


def test_log_repository_operation(caplog):
    """Test log_repository_operation function."""
    log_repository_operation("test-repo", "sync", "started")
    assert "Repository 'test-repo': sync started" in caplog.text


def test_log_api_call(caplog):
    """Test log_api_call function."""
    # Set up logging for test
    setup_logging(level="DEBUG")
    log_api_call("openai", "/v1/chat/completions", "started")
    assert "API call to openai /v1/chat/completions: started" in caplog.text


def test_log_validation_result_passed(caplog):
    """Test log_validation_result function with passed validation."""
    # Set up logging for test
    setup_logging(level="DEBUG")
    log_validation_result("test validation", True, "All good")
    assert "Validation test validation: passed - All good" in caplog.text


def test_log_validation_result_failed(caplog):
    """Test log_validation_result function with failed validation."""
    # Set up logging for test
    setup_logging(level="WARNING")
    log_validation_result("test validation", False, "Something wrong")
    assert "Validation test validation: failed - Something wrong" in caplog.text


def test_log_validation_result_no_details(caplog):
    """Test log_validation_result function without details."""
    # Set up logging for test
    setup_logging(level="DEBUG")
    log_validation_result("test validation", True)
    assert "Validation test validation: passed" in caplog.text
