"""Utility functions for GitCo."""

import logging
import sys
from typing import Optional, Any, Dict
from pathlib import Path


class GitCoError(Exception):
    """Base exception for GitCo errors."""
    pass


class ConfigurationError(GitCoError):
    """Raised when there's a configuration error."""
    pass


class GitOperationError(GitCoError):
    """Raised when a Git operation fails."""
    pass


class ValidationError(GitCoError):
    """Raised when validation fails."""
    pass


class APIError(GitCoError):
    """Raised when an API call fails."""
    pass


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False
) -> logging.Logger:
    """Set up logging for GitCo.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        verbose: Enable verbose logging
        quiet: Suppress output
        
    Returns:
        Configured logger instance.
    """
    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    elif quiet:
        log_level = logging.ERROR
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("gitco")
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """Get the GitCo logger instance.
    
    Returns:
        Logger instance.
    """
    return logging.getLogger("gitco")


def log_error_and_exit(
    message: str,
    error: Optional[Exception] = None,
    exit_code: int = 1
) -> None:
    """Log an error and exit with the specified code.
    
    Args:
        message: Error message to log.
        error: Optional exception that caused the error.
        exit_code: Exit code to use.
    """
    logger = get_logger()
    if error:
        logger.error(f"{message}: {error}")
    else:
        logger.error(message)
    sys.exit(exit_code)


def safe_execute(
    func,
    *args,
    error_message: str = "Operation failed",
    exit_on_error: bool = True,
    **kwargs
) -> Any:
    """Safely execute a function with error handling.
    
    Args:
        func: Function to execute.
        *args: Arguments to pass to the function.
        error_message: Message to log on error.
        exit_on_error: Whether to exit on error.
        **kwargs: Keyword arguments to pass to the function.
        
    Returns:
        Function result or None if error occurred.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger = get_logger()
        logger.error(f"{error_message}: {e}")
        if exit_on_error:
            sys.exit(1)
        return None


def validate_file_exists(file_path: str, description: str = "File") -> None:
    """Validate that a file exists.
    
    Args:
        file_path: Path to the file.
        description: Description of the file for error messages.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"{description} not found: {file_path}")


def validate_directory_exists(dir_path: str, description: str = "Directory") -> None:
    """Validate that a directory exists.
    
    Args:
        dir_path: Path to the directory.
        description: Description of the directory for error messages.
        
    Raises:
        FileNotFoundError: If the directory doesn't exist.
    """
    if not Path(dir_path).is_dir():
        raise FileNotFoundError(f"{description} not found: {dir_path}")


def ensure_directory_exists(dir_path: str) -> None:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory.
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def format_error_message(error: Exception, context: str = "") -> str:
    """Format an error message with context.
    
    Args:
        error: The exception that occurred.
        context: Additional context for the error.
        
    Returns:
        Formatted error message.
    """
    if context:
        return f"{context}: {error}"
    return str(error)


def handle_validation_errors(errors: list, context: str = "Configuration") -> None:
    """Handle validation errors by logging them and optionally exiting.
    
    Args:
        errors: List of validation error messages.
        context: Context for the validation errors.
    """
    if errors:
        logger = get_logger()
        logger.error(f"{context} validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise ValidationError(f"{context} validation failed")


def log_operation_start(operation: str, **kwargs) -> None:
    """Log the start of an operation.
    
    Args:
        operation: Name of the operation.
        **kwargs: Additional context for the operation.
    """
    logger = get_logger()
    context = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    if context:
        logger.info(f"Starting {operation}: {context}")
    else:
        logger.info(f"Starting {operation}")


def log_operation_success(operation: str, **kwargs) -> None:
    """Log the successful completion of an operation.
    
    Args:
        operation: Name of the operation.
        **kwargs: Additional context for the operation.
    """
    logger = get_logger()
    context = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    if context:
        logger.info(f"Completed {operation}: {context}")
    else:
        logger.info(f"Completed {operation}")


def log_operation_failure(operation: str, error: Exception, **kwargs) -> None:
    """Log the failure of an operation.
    
    Args:
        operation: Name of the operation.
        error: The exception that caused the failure.
        **kwargs: Additional context for the operation.
    """
    logger = get_logger()
    context = " ".join([f"{k}={v}" for k, v in kwargs.items()])
    if context:
        logger.error(f"Failed {operation}: {context} - {error}")
    else:
        logger.error(f"Failed {operation}: {error}")


def create_progress_context(operation: str, total: int = 0) -> Dict[str, Any]:
    """Create a context for progress tracking.
    
    Args:
        operation: Name of the operation.
        total: Total number of items to process.
        
    Returns:
        Progress context dictionary.
    """
    return {
        "operation": operation,
        "total": total,
        "current": 0,
        "start_time": None
    }


def update_progress(context: Dict[str, Any], current: int, message: str = "") -> None:
    """Update progress in a context.
    
    Args:
        context: Progress context dictionary.
        current: Current progress value.
        message: Optional message to log.
    """
    context["current"] = current
    logger = get_logger()
    
    if context["total"] > 0:
        percentage = (current / context["total"]) * 100
        progress_msg = f"{context['operation']}: {current}/{context['total']} ({percentage:.1f}%)"
    else:
        progress_msg = f"{context['operation']}: {current}"
    
    if message:
        progress_msg += f" - {message}"
    
    logger.info(progress_msg)


def log_configuration_loaded(config_path: str, repo_count: int) -> None:
    """Log that configuration has been loaded.
    
    Args:
        config_path: Path to the configuration file.
        repo_count: Number of repositories in the configuration.
    """
    logger = get_logger()
    logger.info(f"Configuration loaded from {config_path}")
    logger.info(f"Found {repo_count} repositories")


def log_repository_operation(repo_name: str, operation: str, status: str = "started") -> None:
    """Log a repository operation.
    
    Args:
        repo_name: Name of the repository.
        operation: Name of the operation.
        status: Status of the operation.
    """
    logger = get_logger()
    logger.info(f"Repository '{repo_name}': {operation} {status}")


def log_api_call(provider: str, endpoint: str, status: str = "started") -> None:
    """Log an API call.
    
    Args:
        provider: API provider name.
        endpoint: API endpoint.
        status: Status of the API call.
    """
    logger = get_logger()
    logger.debug(f"API call to {provider} {endpoint}: {status}")


def log_validation_result(validation_type: str, passed: bool, details: str = "") -> None:
    """Log a validation result.
    
    Args:
        validation_type: Type of validation performed.
        passed: Whether validation passed.
        details: Additional details about the validation.
    """
    logger = get_logger()
    status = "passed" if passed else "failed"
    message = f"Validation {validation_type}: {status}"
    if details:
        message += f" - {details}"
    
    if passed:
        logger.debug(message)
    else:
        logger.warning(message) 
