"""Enhanced logging utilities for GitCo."""

import json
import logging
import logging.handlers
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


class GitCoLogger:
    """Enhanced logger for GitCo with structured logging and performance tracking."""

    def __init__(
        self,
        name: str = "gitco",
        log_file: Optional[str] = None,
        level: str = "INFO",
        detailed: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """Initialize the GitCo logger.

        Args:
            name: Logger name
            log_file: Path to log file
            level: Logging level
            detailed: Use detailed log format with function names and line numbers
            max_file_size: Maximum file size in bytes before rotation
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_file = log_file
        self.detailed = detailed
        self.max_file_size = max_file_size
        self.backup_count = backup_count

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers
        self._setup_handlers()

        # Performance tracking
        self.operation_timers: dict[str, float] = {}
        self.performance_metrics: dict[str, dict[str, Any]] = {}

    def _setup_handlers(self) -> None:
        """Setup logging handlers."""
        # Choose format based on detailed flag
        if self.detailed:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        else:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        formatter = logging.Formatter(format_string)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.logger.level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler with rotation (if specified)
        if self.log_file:
            # Ensure log directory exists
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Use RotatingFileHandler for automatic log rotation
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            # Log the start of file logging
            self.logger.info(f"Logging to file: {self.log_file}")

    def log_structured(
        self,
        level: str,
        message: str,
        context: Optional[dict[str, Any]] = None,
        operation: Optional[str] = None,
        performance: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a structured message with context.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Main log message
            context: Optional context dictionary
            operation: Optional operation name
            performance: Optional performance metrics
        """
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
        }

        if context:
            log_entry["context"] = context
        if operation:
            log_entry["operation"] = operation
        if performance:
            log_entry["performance"] = performance

        # Format for logging
        if context or operation or performance:
            context_str = " | ".join(
                f"{k}={v}" for k, v in log_entry.items() if k != "message"
            )
            full_message = f"{message} | {context_str}"
        else:
            full_message = message

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(full_message)

    def start_operation(
        self, operation: str, context: Optional[dict[str, Any]] = None
    ) -> None:
        """Start timing an operation.

        Args:
            operation: Name of the operation
            context: Optional context dictionary
        """
        self.operation_timers[operation] = time.time()

        self.log_structured(
            "INFO",
            f"Operation started: {operation}",
            context=context,
            operation=operation,
        )

    def end_operation(
        self,
        operation: str,
        success: bool = True,
        context: Optional[dict[str, Any]] = None,
        additional_metrics: Optional[dict[str, Any]] = None,
    ) -> None:
        """End timing an operation and log results.

        Args:
            operation: Name of the operation
            success: Whether the operation was successful
            context: Optional context dictionary
            additional_metrics: Additional metrics to log
        """
        if operation not in self.operation_timers:
            self.logger.warning(f"Operation '{operation}' was not started")
            return

        duration = time.time() - self.operation_timers[operation]
        del self.operation_timers[operation]

        # Build performance metrics
        performance = {
            "duration_seconds": round(duration, 3),
            "success": success,
        }

        if additional_metrics:
            performance.update(additional_metrics)

        # Store performance data
        self.performance_metrics[operation] = performance

        status = "completed" if success else "failed"

        self.log_structured(
            "INFO",
            f"Operation {status}: {operation}",
            context=context,
            operation=operation,
            performance=performance,
        )

    def log_error(
        self,
        error: Exception,
        operation: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an error with full stack trace.

        Args:
            error: The exception that occurred
            operation: Optional operation name
            context: Optional context dictionary
        """
        import traceback

        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
        }

        if context:
            error_context.update(context)

        self.log_structured(
            "ERROR",
            f"Error occurred: {type(error).__name__}: {error}",
            context=error_context,
            operation=operation,
        )

    def log_api_call(
        self,
        provider: str,
        endpoint: str,
        method: str = "GET",
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        success: bool = True,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log API interactions with detailed information.

        Args:
            provider: API provider (GitHub, OpenAI, etc.)
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            duration: Request duration in seconds
            success: Whether the request was successful
            context: Optional context dictionary
        """
        api_context = {
            "provider": provider,
            "endpoint": endpoint,
            "method": method,
            "success": success,
        }

        if status_code:
            api_context["status_code"] = status_code
        if duration:
            api_context["duration_seconds"] = round(duration, 3)
        if context:
            api_context.update(context)

        status = "completed" if success else "failed"

        self.log_structured(
            "INFO",
            f"API {method} {endpoint} {status}",
            context=api_context,
            operation=f"api_{provider}_{method}",
        )

    def log_repository_operation(
        self,
        repo_name: str,
        operation: str,
        status: str = "started",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log repository operations with detailed information.

        Args:
            repo_name: Name of the repository
            operation: Operation being performed
            status: Status of the operation
            details: Optional additional details
        """
        repo_context = {
            "repository": repo_name,
            "operation": operation,
            "status": status,
        }

        if details:
            repo_context.update(details)

        self.log_structured(
            "INFO",
            f"Repository {operation} {status}: {repo_name}",
            context=repo_context,
            operation=f"repo_{operation}",
        )

    def log_validation(
        self,
        validation_type: str,
        passed: bool,
        details: str = "",
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log validation results with detailed information.

        Args:
            validation_type: Type of validation
            passed: Whether validation passed
            details: Additional details about the validation
            context: Optional context dictionary
        """
        validation_context = {
            "validation_type": validation_type,
            "passed": passed,
            "details": details,
        }

        if context:
            validation_context.update(context)

        status = "passed" if passed else "failed"

        self.log_structured(
            "INFO",
            f"Validation {validation_type} {status}",
            context=validation_context,
            operation=f"validation_{validation_type}",
        )

    def log_configuration_change(
        self,
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
        config_context = {
            "config_type": config_type,
            "action": action,
        }

        if details:
            config_context.update(details)

        self.log_structured(
            "INFO",
            f"Configuration {action}: {config_type}",
            context=config_context,
            operation=f"config_{action}",
        )

    def get_performance_summary(self) -> dict[str, Any]:
        """Get a summary of performance metrics.

        Returns:
            Dictionary containing performance summary
        """
        if not self.performance_metrics:
            return {}

        total_operations = len(self.performance_metrics)
        successful_operations = sum(
            1 for m in self.performance_metrics.values() if m.get("success", False)
        )
        total_duration = sum(
            m.get("duration_seconds", 0) for m in self.performance_metrics.values()
        )

        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": total_operations - successful_operations,
            "success_rate": (
                successful_operations / total_operations if total_operations > 0 else 0
            ),
            "total_duration": round(total_duration, 3),
            "average_duration": (
                round(total_duration / total_operations, 3)
                if total_operations > 0
                else 0
            ),
            "operations": self.performance_metrics,
        }

    def print_performance_summary(self) -> None:
        """Print a formatted performance summary."""
        summary = self.get_performance_summary()

        if not summary:
            console.print("No performance data available.")
            return

        table = Table(title="Performance Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Operations", str(summary["total_operations"]))
        table.add_row("Successful", str(summary["successful_operations"]))
        table.add_row("Failed", str(summary["failed_operations"]))
        table.add_row("Success Rate", f"{summary['success_rate']:.1%}")
        table.add_row("Total Duration", f"{summary['total_duration']}s")
        table.add_row("Average Duration", f"{summary['average_duration']}s")

        console.print(table)

    def export_logs(self, output_file: str, format: str = "json") -> None:
        """Export logs to a file.

        Args:
            output_file: Path to output file
            format: Export format (json, csv)
        """
        if format.lower() == "json":
            export_data = {
                "performance_summary": self.get_performance_summary(),
                "log_file": self.log_file,
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)

        elif format.lower() == "csv":
            import csv

            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Operation", "Duration", "Success", "Additional Metrics"]
                )

                for operation, metrics in self.performance_metrics.items():
                    additional_metrics = {
                        k: v
                        for k, v in metrics.items()
                        if k not in ["duration_seconds", "success"]
                    }
                    writer.writerow(
                        [
                            operation,
                            metrics.get("duration_seconds", 0),
                            metrics.get("success", False),
                            (
                                json.dumps(additional_metrics)
                                if additional_metrics
                                else ""
                            ),
                        ]
                    )

        self.logger.info(f"Logs exported to {output_file} in {format} format")


def create_gitco_logger(
    log_file: Optional[str] = None,
    level: str = "INFO",
    detailed: bool = False,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> GitCoLogger:
    """Create a GitCo logger instance.

    Args:
        log_file: Path to log file
        level: Logging level
        detailed: Use detailed log format
        max_file_size: Maximum file size in bytes before rotation
        backup_count: Number of backup files to keep

    Returns:
        GitCoLogger instance
    """
    return GitCoLogger(
        log_file=log_file,
        level=level,
        detailed=detailed,
        max_file_size=max_file_size,
        backup_count=backup_count,
    )


# Global logger instance
_gitco_logger: Optional[GitCoLogger] = None


def get_gitco_logger() -> GitCoLogger:
    """Get the global GitCo logger instance.

    Returns:
        GitCoLogger instance
    """
    global _gitco_logger
    if _gitco_logger is None:
        _gitco_logger = create_gitco_logger()
    return _gitco_logger


def set_gitco_logger(logger: Optional[GitCoLogger]) -> None:
    """Set the global GitCo logger instance.

    Args:
        logger: GitCoLogger instance to set as global, or None to reset
    """
    global _gitco_logger
    _gitco_logger = logger


__all__ = [
    "GitCoLogger",
    "create_gitco_logger",
    "get_gitco_logger",
    "set_gitco_logger",
]
