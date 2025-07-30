"""Test cases for logging_utils.py."""

import json
import logging
from pathlib import Path
from typing import Any

from gitco.utils.logging import (
    GitCoLogger,
    create_gitco_logger,
    get_gitco_logger,
    set_gitco_logger,
)

# Import fixtures


class TestGitCoLoggerInitialization:
    """Test GitCoLogger initialization and setup."""

    def test_gitco_logger_default_initialization(self) -> None:
        """Test GitCoLogger initialization with default parameters."""
        logger = GitCoLogger()

        assert logger.name == "gitco"
        assert logger.log_file is None
        assert logger.detailed is False
        assert logger.max_file_size == 10 * 1024 * 1024  # 10MB
        assert logger.backup_count == 5
        assert isinstance(logger.logger, logging.Logger)
        assert logger.logger.name == "gitco"
        assert logger.logger.level == logging.INFO

    def test_gitco_logger_custom_initialization(self) -> None:
        """Test GitCoLogger initialization with custom parameters."""
        logger = GitCoLogger(
            name="test_logger",
            level="DEBUG",
            detailed=True,
            max_file_size=1024,
            backup_count=3,
        )

        assert logger.name == "test_logger"
        assert logger.detailed is True
        assert logger.max_file_size == 1024
        assert logger.backup_count == 3
        assert logger.logger.level == logging.DEBUG

    def test_gitco_logger_with_log_file(self, temp_log_file: str) -> None:
        """Test GitCoLogger initialization with log file."""
        logger = GitCoLogger(log_file=temp_log_file)

        assert logger.log_file == temp_log_file
        assert Path(temp_log_file).parent.exists()

        # Test that logging works
        logger.logger.info("Test message")
        assert Path(temp_log_file).exists()

    def test_gitco_logger_handlers_setup(self) -> None:
        """Test that handlers are properly set up."""
        logger = GitCoLogger()

        # Should have at least one handler (console)
        assert len(logger.logger.handlers) >= 1

        # Check that console handler exists
        console_handlers = [
            h for h in logger.logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) >= 1

    def test_gitco_logger_detailed_format(self) -> None:
        """Test that detailed format is used when detailed=True."""
        logger = GitCoLogger(detailed=True)

        # Check that detailed format is used
        for handler in logger.logger.handlers:
            if hasattr(handler, "formatter") and handler.formatter:
                format_string = handler.formatter._fmt
                if format_string is not None:
                    assert "funcName" in format_string
                    assert "lineno" in format_string


class TestGitCoLoggerMethods:
    """Test GitCoLogger methods and functionality."""

    def test_log_structured(self) -> None:
        """Test structured logging functionality."""
        logger = GitCoLogger()

        # Test basic structured logging
        logger.log_structured("INFO", "Test message")

        # Test with context
        context: dict[str, str] = {"user": "test_user", "operation": "test_op"}
        logger.log_structured("INFO", "Test message", context=context)

        # Test with operation
        logger.log_structured("INFO", "Test message", operation="test_operation")

        # Test with performance data
        performance: dict[str, str] = {"duration": "1.5", "memory_usage": "10MB"}
        logger.log_structured("INFO", "Test message", performance=performance)

    def test_start_operation(self) -> None:
        """Test operation start tracking."""
        logger = GitCoLogger()

        # Start an operation
        logger.start_operation("test_operation")

        # Check that operation timer was set
        assert "test_operation" in logger.operation_timers
        assert logger.operation_timers["test_operation"] > 0

    def test_end_operation(self) -> None:
        """Test operation end tracking."""
        logger = GitCoLogger()

        # Start and end an operation
        logger.start_operation("test_operation")
        logger.end_operation("test_operation", success=True)

        # Check that performance metrics were recorded
        assert "test_operation" in logger.performance_metrics
        metrics = logger.performance_metrics["test_operation"]
        assert "duration_seconds" in metrics
        assert "success" in metrics
        assert metrics["success"] is True

    def test_end_operation_with_additional_metrics(self) -> None:
        """Test operation end with additional metrics."""
        logger = GitCoLogger()

        # Start and end an operation with additional metrics
        logger.start_operation("test_operation")
        additional_metrics: dict[str, str] = {"memory_usage": "10MB", "cpu_usage": "5%"}
        logger.end_operation(
            "test_operation", success=True, additional_metrics=additional_metrics
        )

        # Check that additional metrics were recorded
        metrics = logger.performance_metrics["test_operation"]
        assert metrics["memory_usage"] == "10MB"
        assert metrics["cpu_usage"] == "5%"

    def test_log_error(self) -> None:
        """Test error logging functionality."""
        logger = GitCoLogger()

        # Test logging an exception
        test_error = ValueError("Test error message")
        logger.log_error(test_error, operation="test_operation")

        # Test with context
        context: dict[str, str] = {"file": "test.py", "line": "10"}
        logger.log_error(test_error, operation="test_operation", context=context)

    def test_log_api_call(self) -> None:
        """Test API call logging."""
        logger = GitCoLogger()

        # Test basic API call logging
        logger.log_api_call("github", "/repos/user/repo", "GET")

        # Test with all parameters
        logger.log_api_call(
            provider="github",
            endpoint="/repos/user/repo",
            method="POST",
            status_code=200,
            duration=1.5,
            success=True,
            context={"user": "test_user"},
        )

    def test_log_repository_operation(self) -> None:
        """Test repository operation logging."""
        logger = GitCoLogger()

        # Test basic repository operation logging
        logger.log_repository_operation("test-repo", "sync")

        # Test with details
        details: dict[str, Any] = {"branch": "main", "commits": 5}
        logger.log_repository_operation("test-repo", "sync", "completed", details)

    def test_log_validation(self) -> None:
        """Test validation logging."""
        logger = GitCoLogger()

        # Test successful validation
        logger.log_validation("config", True, "Configuration is valid")

        # Test failed validation
        logger.log_validation(
            "config", False, "Invalid configuration", {"file": "config.yml"}
        )

    def test_log_configuration_change(self) -> None:
        """Test configuration change logging."""
        logger = GitCoLogger()

        # Test basic configuration change
        logger.log_configuration_change("repository", "added")

        # Test with details
        details: dict[str, str] = {"name": "new-repo", "path": "/path/to/repo"}
        logger.log_configuration_change("repository", "removed", details)


class TestGitCoLoggerPerformance:
    """Test GitCoLogger performance tracking functionality."""

    def test_get_performance_summary(self) -> None:
        """Test performance summary generation."""
        logger = GitCoLogger()

        # Add some test operations
        logger.start_operation("op1")
        logger.end_operation("op1", success=True)

        logger.start_operation("op2")
        logger.end_operation("op2", success=False)

        # Get performance summary
        summary = logger.get_performance_summary()

        assert "total_operations" in summary
        assert "successful_operations" in summary
        assert "failed_operations" in summary
        assert "average_duration" in summary
        assert summary["total_operations"] == 2
        assert summary["successful_operations"] == 1
        assert summary["failed_operations"] == 1

    def test_print_performance_summary(self) -> None:
        """Test performance summary printing."""
        logger = GitCoLogger()

        # Add test operations
        logger.start_operation("test_op")
        logger.end_operation("test_op", success=True)

        # Test that print_performance_summary doesn't raise an exception
        logger.print_performance_summary()

    def test_export_logs_json(self, temp_log_file: str) -> None:
        """Test log export in JSON format."""
        logger = GitCoLogger(log_file=temp_log_file)

        # Add some test operations
        logger.start_operation("test_op")
        logger.end_operation("test_op", success=True)

        # Export logs
        export_file = temp_log_file + ".json"
        logger.export_logs(export_file, "json")

        # Check that export file was created
        assert Path(export_file).exists()

        # Check JSON content
        with open(export_file) as f:
            data = json.load(f)

        assert "performance_summary" in data
        assert "log_file" in data
        assert "export_timestamp" in data

    def test_export_logs_csv(self, temp_log_file: str) -> None:
        """Test log export in CSV format."""
        logger = GitCoLogger(log_file=temp_log_file)

        # Add some test operations
        logger.start_operation("test_op")
        logger.end_operation("test_op", success=True)

        # Export logs
        export_file = temp_log_file + ".csv"
        logger.export_logs(export_file, "csv")

        # Check that export file was created
        assert Path(export_file).exists()

        # Check CSV content
        with open(export_file) as f:
            lines = f.readlines()

        assert len(lines) >= 2  # Header + at least one data row
        assert "Operation,Duration,Success,Additional Metrics" in lines[0]


class TestUtilityFunctions:
    """Test utility functions in logging_utils."""

    def test_create_gitco_logger(self) -> None:
        """Test create_gitco_logger function."""
        logger = create_gitco_logger(
            log_file="test.log",
            level="DEBUG",
            detailed=True,
            max_file_size=1024,
            backup_count=3,
        )

        assert isinstance(logger, GitCoLogger)
        assert logger.log_file == "test.log"
        assert logger.detailed is True
        assert logger.max_file_size == 1024
        assert logger.backup_count == 3

    def test_get_gitco_logger_default(self) -> None:
        """Test get_gitco_logger returns default logger."""
        # Reset global logger
        set_gitco_logger(None)

        logger = get_gitco_logger()
        assert isinstance(logger, GitCoLogger)
        assert logger.name == "gitco"

    def test_set_gitco_logger(self) -> None:
        """Test set_gitco_logger function."""
        custom_logger = GitCoLogger(name="custom_logger")
        set_gitco_logger(custom_logger)

        retrieved_logger = get_gitco_logger()
        assert retrieved_logger is custom_logger
        assert retrieved_logger.name == "custom_logger"

    def test_get_gitco_logger_singleton(self) -> None:
        """Test that get_gitco_logger returns the same instance."""
        # Reset global logger
        set_gitco_logger(None)

        logger1 = get_gitco_logger()
        logger2 = get_gitco_logger()

        assert logger1 is logger2
