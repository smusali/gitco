"""Utility functions for GitCo."""

import logging
import sys
from pathlib import Path
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

# Global console instance for consistent styling
console = Console()


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
    quiet: bool = False,
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
        logger.error(f"{message}: {error}")
        console.print(f"[red]❌ {message}: {error}[/red]")
    else:
        logger.error(message)
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
        func: Function to execute.
        *args: Arguments to pass to the function.
        error_message: Error message to display if the function fails.
        exit_on_error: Whether to exit on error.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Result of the function execution.

    Raises:
        Exception: If the function fails and exit_on_error is False.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if exit_on_error:
            log_error_and_exit(error_message, e)
        else:
            raise e


def validate_file_exists(file_path: str, description: str = "File") -> None:
    """Validate that a file exists.

    Args:
        file_path: Path to the file.
        description: Description of the file for error messages.

    Raises:
        ValidationError: If the file doesn't exist.
    """
    if not Path(file_path).exists():
        raise ValidationError(f"{description} not found: {file_path}")


def validate_directory_exists(dir_path: str, description: str = "Directory") -> None:
    """Validate that a directory exists.

    Args:
        dir_path: Path to the directory.
        description: Description of the directory for error messages.

    Raises:
        ValidationError: If the directory doesn't exist.
    """
    if not Path(dir_path).exists():
        raise ValidationError(f"{description} not found: {dir_path}")


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
    """Handle validation errors by logging them and exiting.

    Args:
        errors: List of validation errors.
        context: Context for the validation errors.
    """
    if errors:
        console.print(f"[red]❌ {context} validation failed:[/red]")
        for error in errors:
            console.print(f"  [red]• {error}[/red]")
        sys.exit(1)


def log_operation_start(operation: str, **kwargs: Any) -> None:
    """Log the start of an operation.

    Args:
        operation: Name of the operation.
        **kwargs: Additional context for the operation.
    """
    logger = get_logger()
    context_str = " ".join(f"{k}={v}" for k, v in kwargs.items())
    message = f"Starting {operation}"
    if context_str:
        message += f" ({context_str})"

    logger.info(message)
    console.print(f"[blue]🔄 {message}[/blue]")


def log_operation_success(operation: str, **kwargs: Any) -> None:
    """Log the successful completion of an operation.

    Args:
        operation: Name of the operation.
        **kwargs: Additional context for the operation.
    """
    logger = get_logger()
    context_str = " ".join(f"{k}={v}" for k, v in kwargs.items())
    message = f"Completed {operation}"
    if context_str:
        message += f" ({context_str})"

    logger.info(message)
    console.print(f"[green]✅ {message}[/green]")


def log_operation_failure(operation: str, error: Exception, **kwargs: Any) -> None:
    """Log the failure of an operation.

    Args:
        operation: Name of the operation.
        error: The exception that caused the failure.
        **kwargs: Additional context for the operation.
    """
    logger = get_logger()
    context_str = " ".join(f"{k}={v}" for k, v in kwargs.items())
    message = f"Failed {operation}"
    if context_str:
        message += f" ({context_str})"

    logger.error(f"{message}: {error}")
    console.print(f"[red]❌ {message}: {error}[/red]")


def create_progress_context(operation: str, total: int = 0) -> dict[str, Any]:
    """Create a context for progress tracking.

    Args:
        operation: Name of the operation.
        total: Total number of items to process.

    Returns:
        Progress context dictionary.
    """
    return {"operation": operation, "total": total, "current": 0, "start_time": None}


def update_progress(context: dict[str, Any], current: int, message: str = "") -> None:
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
        progress_msg = (
            f"{context['operation']}: {current}/{context['total']} ({percentage:.1f}%)"
        )
    else:
        progress_msg = f"{context['operation']}: {current}"

    if message:
        progress_msg += f" - {message}"

    logger.info(progress_msg)


def create_progress_bar(description: str, total: int) -> Progress:
    """Create a rich progress bar for operations.

    Args:
        description: Description of the operation.
        total: Total number of items to process.

    Returns:
        Rich Progress instance.
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True,
    )


def print_status_table(
    title: str, data: list[dict[str, Any]], columns: list[str]
) -> None:
    """Print a status table using rich.

    Args:
        title: Title for the table.
        data: List of dictionaries containing the data.
        columns: List of column names.
    """
    table = Table(title=title, box=box.ROUNDED)

    # Add columns
    for column in columns:
        table.add_column(column, style="cyan")

    # Add rows
    for row in data:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    console.print(table)


def print_success_panel(message: str, details: Optional[str] = None) -> None:
    """Print a success message in a panel.

    Args:
        message: Success message.
        details: Optional details to include.
    """
    content = message
    if details:
        content += f"\n\n{details}"

    panel = Panel(
        content,
        title="[green]Success[/green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)


def print_error_panel(message: str, details: Optional[str] = None) -> None:
    """Print an error message in a panel.

    Args:
        message: Error message.
        details: Optional details to include.
    """
    content = message
    if details:
        content += f"\n\n{details}"

    panel = Panel(
        content,
        title="[red]Error[/red]",
        border_style="red",
        padding=(1, 2),
    )
    console.print(panel)


def print_info_panel(message: str, details: Optional[str] = None) -> None:
    """Print an info message in a panel.

    Args:
        message: Info message.
        details: Optional details to include.
    """
    content = message
    if details:
        content += f"\n\n{details}"

    panel = Panel(
        content,
        title="[blue]Info[/blue]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


def print_warning_panel(message: str, details: Optional[str] = None) -> None:
    """Print a warning message in a panel.

    Args:
        message: Warning message.
        details: Optional details to include.
    """
    content = message
    if details:
        content += f"\n\n{details}"

    panel = Panel(
        content,
        title="[yellow]Warning[/yellow]",
        border_style="yellow",
        padding=(1, 2),
    )
    console.print(panel)


def log_configuration_loaded(config_path: str, repo_count: int) -> None:
    """Log that configuration has been loaded.

    Args:
        config_path: Path to the configuration file.
        repo_count: Number of repositories in the configuration.
    """
    logger = get_logger()
    logger.info(f"Configuration loaded from {config_path}")
    logger.info(f"Found {repo_count} repositories")

    console.print(f"[green]📋 Configuration loaded from {config_path}[/green]")
    console.print(f"[green]📦 Found {repo_count} repositories[/green]")


def log_repository_operation(
    repo_name: str, operation: str, status: str = "started"
) -> None:
    """Log a repository operation.

    Args:
        repo_name: Name of the repository.
        operation: Name of the operation.
        status: Status of the operation.
    """
    logger = get_logger()
    logger.info(f"Repository '{repo_name}': {operation} {status}")

    # Color coding for different statuses
    if status == "started":
        console.print(f"[blue]🔄 {repo_name}: {operation} started[/blue]")
    elif status == "completed":
        console.print(f"[green]✅ {repo_name}: {operation} completed[/green]")
    elif status == "failed":
        console.print(f"[red]❌ {repo_name}: {operation} failed[/red]")
    elif status == "skipped":
        console.print(f"[yellow]⏭️  {repo_name}: {operation} skipped[/yellow]")
    else:
        console.print(f"[white]ℹ️  {repo_name}: {operation} {status}[/white]")


def log_api_call(provider: str, endpoint: str, status: str = "started") -> None:
    """Log an API call.

    Args:
        provider: API provider name.
        endpoint: API endpoint.
        status: Status of the API call.
    """
    logger = get_logger()
    logger.debug(f"API call to {provider} {endpoint}: {status}")

    if status == "started":
        console.print(f"[blue]🌐 API call to {provider} {endpoint}[/blue]")
    elif status == "completed":
        console.print(f"[green]✅ API call to {provider} {endpoint} completed[/green]")
    elif status == "failed":
        console.print(f"[red]❌ API call to {provider} {endpoint} failed[/red]")


def log_validation_result(
    validation_type: str, passed: bool, details: str = ""
) -> None:
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
        console.print(f"[green]✅ {validation_type} validation passed[/green]")
    else:
        logger.warning(message)
        console.print(f"[red]❌ {validation_type} validation failed: {details}[/red]")
