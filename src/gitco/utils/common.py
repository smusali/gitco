"""Utility functions for GitCo."""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Any, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

# Import exception classes
from .exception import (
    ValidationError,
)

# Import enhanced logging utilities
from .logging import (
    create_gitco_logger,
    get_gitco_logger,
    set_gitco_logger,
)

# Global console instance for consistent styling
console = Console()

# Global quiet mode state
_quiet_mode = False

# Global logging configuration
_logging_config = {
    "log_file": None,
    "log_level": logging.INFO,
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "detailed_format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
}


def set_quiet_mode(enabled: bool) -> None:
    """Set the global quiet mode state.

    Args:
        enabled: Whether to enable quiet mode.
    """
    global _quiet_mode
    _quiet_mode = enabled


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled.

    Returns:
        True if quiet mode is enabled, False otherwise.
    """
    return _quiet_mode


def set_logging_config(
    log_file: Optional[str] = None,
    log_level: int = logging.INFO,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    detailed_format: bool = False,
) -> None:
    """Set global logging configuration.

    Args:
        log_file: Path to log file
        log_level: Logging level
        max_file_size: Maximum file size in bytes before rotation
        backup_count: Number of backup files to keep
        detailed_format: Use detailed log format with function names and line numbers
    """
    global _logging_config
    _logging_config.update(
        {
            "log_file": log_file,
            "log_level": log_level,
            "max_file_size": max_file_size,
            "backup_count": backup_count,
            "detailed_format": detailed_format,
        }
    )


def get_logging_config() -> dict[str, Any]:
    """Get current logging configuration.

    Returns:
        Current logging configuration dictionary.
    """
    return _logging_config.copy()


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False,
    detailed: bool = False,
    max_file_size: Optional[int] = None,
    backup_count: Optional[int] = None,
) -> logging.Logger:
    """Set up logging for GitCo with enhanced file output capabilities.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        verbose: Enable verbose logging
        quiet: Suppress output
        detailed: Use detailed log format with function names and line numbers
        max_file_size: Maximum file size in bytes before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance.
    """
    # Determine log level
    if verbose:
        log_level = "DEBUG"
    elif quiet:
        log_level = "ERROR"
    else:
        log_level = level.upper()

    # Create enhanced GitCo logger
    gitco_logger = create_gitco_logger(
        log_file=log_file,
        level=log_level,
        detailed=detailed,
        max_file_size=_safe_int(
            max_file_size, int(str(_logging_config["max_file_size"]))
        ),
        backup_count=_safe_int(backup_count, int(str(_logging_config["backup_count"]))),
    )

    # Set as global logger
    set_gitco_logger(gitco_logger)

    # Update global configuration
    config_updates = {
        "log_level": getattr(logging, log_level, logging.INFO),
        "detailed_format": detailed,
    }

    if log_file:
        config_updates["log_file"] = log_file
    if max_file_size is not None:
        config_updates["max_file_size"] = max_file_size
    if backup_count is not None:
        config_updates["backup_count"] = backup_count

    set_logging_config(
        log_file=_safe_str(config_updates.get("log_file")),
        log_level=_safe_int(config_updates.get("log_level"), int(str(logging.INFO))),
        max_file_size=_safe_int(
            config_updates.get("max_file_size"),
            int(str(_logging_config["max_file_size"])),
        ),
        backup_count=_safe_int(
            config_updates.get("backup_count"),
            int(str(_logging_config["backup_count"])),
        ),
        detailed_format=bool(config_updates.get("detailed_format", False)),
    )

    return gitco_logger.logger


def get_logger() -> logging.Logger:
    """Get the GitCo logger instance.

    Returns:
        Logger instance.
    """
    return logging.getLogger("gitco")


def log_to_file(
    message: str, level: str = "INFO", context: Optional[dict[str, Any]] = None
) -> None:
    """Log a message to file with optional context.

    Args:
        message: Message to log
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        context: Optional context dictionary to include in log
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_structured(level, message, context)


def log_operation_with_context(
    operation: str,
    status: str = "started",
    context: Optional[dict[str, Any]] = None,
    level: str = "INFO",
) -> None:
    """Log an operation with context information.

    Args:
        operation: Name of the operation
        status: Status of the operation (started, completed, failed)
        context: Optional context dictionary
        level: Log level
    """
    gitco_logger = get_gitco_logger()

    if status == "started":
        gitco_logger.start_operation(operation, context)
    elif status == "completed":
        gitco_logger.end_operation(operation, success=True, context=context)
    elif status == "failed":
        gitco_logger.end_operation(operation, success=False, context=context)
    else:
        gitco_logger.log_structured(
            level, f"Operation: {operation} | Status: {status}", context, operation
        )


def log_performance_metric(
    operation: str,
    duration: float,
    success: bool = True,
    additional_metrics: Optional[dict[str, Any]] = None,
) -> None:
    """Log performance metrics for operations.

    Args:
        operation: Name of the operation
        duration: Duration in seconds
        success: Whether the operation was successful
        additional_metrics: Additional metrics to log
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.end_operation(
        operation, success, additional_metrics=additional_metrics
    )


def log_error_with_stack(
    error: Exception,
    operation: str,
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Log an error with full stack trace.

    Args:
        error: The exception that occurred
        operation: Name of the operation that failed
        context: Optional context dictionary
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_error(error, operation, context)


def log_configuration_change(
    config_type: str,
    action: str,
    details: Optional[dict[str, Any]] = None,
) -> None:
    """Log configuration changes.

    Args:
        config_type: Type of configuration (repositories, settings, etc.)
        action: Action performed (added, removed, updated)
        details: Optional details about the change
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_configuration_change(config_type, action, details)


def log_api_interaction(
    provider: str,
    endpoint: str,
    method: str = "GET",
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    success: bool = True,
) -> None:
    """Log API interactions with detailed information.

    Args:
        provider: API provider (GitHub, OpenAI, etc.)
        endpoint: API endpoint
        method: HTTP method
        status_code: HTTP status code
        duration: Request duration in seconds
        success: Whether the request was successful
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_api_call(
        provider, endpoint, method, status_code, duration, success
    )


def log_repository_operation_detailed(
    repo_name: str,
    operation: str,
    status: str = "started",
    details: Optional[dict[str, Any]] = None,
) -> None:
    """Log detailed repository operations.

    Args:
        repo_name: Name of the repository
        operation: Operation being performed
        status: Status of the operation
        details: Optional additional details
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_repository_operation(repo_name, operation, status, details)


def log_validation_result_detailed(
    validation_type: str,
    passed: bool,
    details: str = "",
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Log detailed validation results.

    Args:
        validation_type: Type of validation
        passed: Whether validation passed
        details: Additional details about the validation
        context: Optional context dictionary
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_validation(validation_type, passed, details, context)


def log_error_and_exit(
    message: str, error: Optional[Exception] = None, exit_code: int = 1
) -> None:
    """Log an error message and exit with the specified code.

    Args:
        message: Error message to log.
        error: Optional exception that caused the error.
        exit_code: Exit code to use.
    """
    logger = get_logger()

    if error:
        log_error_with_stack(error, "CLI operation", {"message": message})
        if not is_quiet_mode():
            console.print(f"[red]❌ {message}: {error}[/red]")
    else:
        logger.error(message)
        if not is_quiet_mode():
            console.print(f"[red]❌ {message}[/red]")

    sys.exit(exit_code)


def safe_execute(
    func: Any,
    *args: Any,
    error_message: str = "Operation failed",
    exit_on_error: bool = True,
    **kwargs: Any,
) -> Any:
    """Safely execute a function and handle errors.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        error_message: Error message to display if function fails
        exit_on_error: Whether to exit on error
        **kwargs: Keyword arguments for the function

    Returns:
        Result of the function execution

    Raises:
        Exception: If the function fails and exit_on_error is False
    """
    import time

    start_time = time.time()
    operation_name = f"{func.__module__}.{func.__name__}"

    try:
        log_operation_with_context(operation_name, "started")
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        log_performance_metric(operation_name, duration, success=True)
        log_operation_with_context(operation_name, "completed")

        return result
    except Exception as e:
        duration = time.time() - start_time

        log_performance_metric(operation_name, duration, success=False)
        log_error_with_stack(e, operation_name, {"error_message": error_message})

        if exit_on_error:
            log_error_and_exit(error_message, e)
        else:
            raise


def validate_file_exists(file_path: str, description: str = "File") -> None:
    """Validate that a file exists.

    Args:
        file_path: Path to the file to validate
        description: Description of the file for error messages

    Raises:
        ValidationError: If the file doesn't exist
    """
    if not os.path.exists(file_path):
        log_validation_result_detailed(
            "file_exists",
            False,
            f"{description} not found: {file_path}",
            {"file_path": file_path},
        )
        raise ValidationError(f"{description} not found: {file_path}")

    log_validation_result_detailed(
        "file_exists",
        True,
        f"{description} found: {file_path}",
        {"file_path": file_path},
    )


def validate_directory_exists(dir_path: str, description: str = "Directory") -> None:
    """Validate that a directory exists.

    Args:
        dir_path: Path to the directory to validate
        description: Description of the directory for error messages

    Raises:
        ValidationError: If the directory doesn't exist
    """
    if not os.path.isdir(dir_path):
        log_validation_result_detailed(
            "directory_exists",
            False,
            f"{description} not found: {dir_path}",
            {"directory_path": dir_path},
        )
        raise ValidationError(f"{description} not found: {dir_path}")

    log_validation_result_detailed(
        "directory_exists",
        True,
        f"{description} found: {dir_path}",
        {"directory_path": dir_path},
    )


def ensure_directory_exists(dir_path: str) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        dir_path: Path to the directory to ensure exists
    """
    # Check if the path exists and is a file
    if os.path.exists(dir_path) and os.path.isfile(dir_path):
        raise OSError(f"Path exists but is a file: {dir_path}")

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        log_operation_with_context(
            "directory_creation", "completed", {"directory_path": dir_path}
        )


def format_error_message(error: Exception, context: str = "") -> str:
    """Format an error message with context.

    Args:
        error: The exception to format
        context: Additional context for the error

    Returns:
        Formatted error message
    """
    error_msg = f"{type(error).__name__}: {error}"
    if context:
        error_msg = f"{context} - {error_msg}"
    return error_msg


def handle_validation_errors(errors: list, context: str = "Configuration") -> None:
    """Handle validation errors by logging and displaying them.

    Args:
        errors: List of validation errors
        context: Context for the validation errors
    """
    for error in errors:
        log_validation_result_detailed(
            f"{context.lower()}_validation",
            False,
            str(error),
            {"error_type": type(error).__name__},
        )

    if not is_quiet_mode():
        print_error_panel(
            f"{context} validation failed",
            f"Found {len(errors)} error(s):\n"
            + "\n".join(f"• {error}" for error in errors),
        )

    # Exit with error code if there are validation errors
    if errors:
        sys.exit(1)


def log_operation_start(operation: str, **kwargs: Any) -> None:
    """Log the start of an operation.

    Args:
        operation: Name of the operation
        **kwargs: Additional context for the operation
    """
    # Log to standard Python logging for test capture
    import logging

    logger = logging.getLogger("gitco")
    context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    message = f"Operation started: {operation}"
    if context_str:
        message += f" | {context_str}"
    logger.info(message)

    # Also log through GitCo logger
    log_operation_with_context(operation, "started", kwargs)


def log_operation_success(operation: str, **kwargs: Any) -> None:
    """Log the successful completion of an operation.

    Args:
        operation: Name of the operation
        **kwargs: Additional context for the operation
    """
    # Log to standard Python logging for test capture
    import logging

    logger = logging.getLogger("gitco")
    context_str = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    message = f"Operation completed: {operation}"
    if context_str:
        message += f" | {context_str}"
    logger.info(message)

    # Start the operation if it hasn't been started
    gitco_logger = get_gitco_logger()
    if operation not in gitco_logger.operation_timers:
        gitco_logger.start_operation(operation, kwargs)

    log_operation_with_context(operation, "completed", kwargs)


def log_operation_failure(operation: str, error: Exception, **kwargs: Any) -> None:
    """Log the failure of an operation.

    Args:
        operation: Name of the operation
        error: The exception that caused the failure
        **kwargs: Additional context for the operation
    """
    log_error_with_stack(error, operation, kwargs)


def create_progress_context(operation: str, total: int = 0) -> dict[str, Any]:
    """Create a progress tracking context.

    Args:
        operation: Name of the operation
        total: Total number of items to process

    Returns:
        Progress context dictionary
    """
    return {
        "operation": operation,
        "total": total,
        "current": 0,
        "start_time": datetime.now(),
    }


def update_progress(context: dict[str, Any], current: int, message: str = "") -> None:
    """Update progress tracking context.

    Args:
        context: Progress context dictionary
        current: Current progress value
        message: Optional progress message
    """
    context["current"] = current
    if message:
        context["message"] = message

    # Log progress if significant
    if current > 0 and context["total"] > 0:
        percentage = (current / context["total"]) * 100
        if percentage % 10 == 0:  # Log every 10%
            log_operation_with_context(
                context["operation"],
                "in_progress",
                {
                    "progress_percentage": f"{percentage:.1f}%",
                    "current": current,
                    "total": context["total"],
                    "message": message,
                },
            )


def create_progress_bar(description: str, total: int) -> Progress:
    """Create a rich progress bar.

    Args:
        description: Description for the progress bar
        total: Total number of items

    Returns:
        Progress bar instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def print_status_table(
    title: str, data: list[dict[str, Any]], columns: list[str]
) -> None:
    """Print a status table using rich.

    Args:
        title: Table title
        data: Table data
        columns: Column names
    """
    table = Table(title=title, box=box.ROUNDED)

    for column in columns:
        table.add_column(column, style="cyan")

    for row in data:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    console.print(table)


def print_success_panel(message: str, details: Optional[str] = None) -> None:
    """Print a success panel using rich.

    Args:
        message: Success message
        details: Optional details
    """
    content = message
    if details:
        content = f"{message}\n\n{details}"

    panel = Panel(
        content,
        title="✅ Success",
        border_style="green",
        box=box.ROUNDED,
    )
    console.print(panel)


def print_error_panel(message: str, details: Optional[str] = None) -> None:
    """Print an error panel using rich.

    Args:
        message: Error message
        details: Optional details
    """
    content = message
    if details:
        content = f"{message}\n\n{details}"

    panel = Panel(
        content,
        title="❌ Error",
        border_style="red",
        box=box.ROUNDED,
    )
    console.print(panel)


def print_info_panel(message: str, details: Optional[str] = None) -> None:
    """Print an info panel using rich.

    Args:
        message: Info message
        details: Optional details
    """
    content = message
    if details:
        content = f"{message}\n\n{details}"

    panel = Panel(
        content,
        title="ℹ️  Info",
        border_style="blue",
        box=box.ROUNDED,
    )
    console.print(panel)


def print_warning_panel(message: str, details: Optional[str] = None) -> None:
    """Print a warning panel using rich.

    Args:
        message: Warning message
        details: Optional details
    """
    content = message
    if details:
        content = f"{message}\n\n{details}"

    panel = Panel(
        content,
        title="⚠️  Warning",
        border_style="yellow",
        box=box.ROUNDED,
    )
    console.print(panel)


def log_configuration_loaded(config_path: str, repo_count: int) -> None:
    """Log that configuration has been loaded.

    Args:
        config_path: Path to the configuration file
        repo_count: Number of repositories in the configuration
    """
    # Start the operation if it hasn't been started
    gitco_logger = get_gitco_logger()
    if "configuration_loading" not in gitco_logger.operation_timers:
        gitco_logger.start_operation(
            "configuration_loading",
            {
                "config_path": config_path,
                "repository_count": repo_count,
            },
        )

    log_operation_with_context(
        "configuration_loading",
        "completed",
        {
            "config_path": config_path,
            "repository_count": repo_count,
        },
    )

    # Also log the specific message expected by tests
    logger = get_logger()
    logger.info("Configuration loaded")


def log_repository_operation(
    repo_name: str, operation: str, status: str = "started"
) -> None:
    """Log a repository operation.

    Args:
        repo_name: Name of the repository
        operation: Operation being performed
        status: Status of the operation
    """
    # Log to standard Python logging for test capture
    import logging

    logger = logging.getLogger("gitco")
    logger.info(
        f"Repository operation: {repo_name} | operation={operation} | status={status}"
    )

    log_repository_operation_detailed(repo_name, operation, status)


def log_api_call(provider: str, endpoint: str, status: str = "started") -> None:
    """Log an API call.

    Args:
        provider: API provider
        endpoint: API endpoint
        status: Status of the API call
    """
    gitco_logger = get_gitco_logger()
    gitco_logger.log_api_call(
        provider, endpoint, "GET", success=(status == "completed")
    )

    # Also print to console for backward compatibility
    if not is_quiet_mode():
        console.print(f"API {provider} {endpoint} {status}")


def log_validation_result(
    validation_type: str, passed: bool, details: str = ""
) -> None:
    """Log a validation result.

    Args:
        validation_type: Type of validation
        passed: Whether validation passed
        details: Additional details
    """
    log_validation_result_detailed(validation_type, passed, details)

    # Also print to console for backward compatibility
    if not is_quiet_mode():
        status = "passed" if passed else "failed"
        console.print(f"Validation {validation_type} {status}: {details}")


def _safe_int(val: Any, default: int) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    return default


def _safe_str(val: Any) -> Optional[str]:
    """Safely convert value to string.

    Args:
        val: Value to convert

    Returns:
        String representation or None if conversion fails
    """
    try:
        return str(val) if val is not None else None
    except Exception:
        return None


__all__ = [
    "set_quiet_mode",
    "is_quiet_mode",
    "set_logging_config",
    "get_logging_config",
    "setup_logging",
    "get_logger",
    "log_to_file",
    "log_operation_with_context",
    "log_performance_metric",
    "log_error_with_stack",
    "log_configuration_change",
    "log_api_interaction",
    "log_repository_operation_detailed",
    "log_validation_result_detailed",
    "log_error_and_exit",
    "safe_execute",
    "validate_file_exists",
    "validate_directory_exists",
    "ensure_directory_exists",
    "format_error_message",
    "handle_validation_errors",
    "log_operation_start",
    "log_operation_success",
    "log_operation_failure",
    "create_progress_context",
    "update_progress",
    "create_progress_bar",
    "print_status_table",
    "print_success_panel",
    "print_error_panel",
    "print_info_panel",
    "print_warning_panel",
    "log_configuration_loaded",
    "log_repository_operation",
    "log_api_call",
    "log_validation_result",
]
