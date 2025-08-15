"""Configuration management CLI commands for GitCo.

This module contains configuration-related commands:
validate, show, edit, export, import.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from ..libs.config import ConfigManager, get_config_manager
from ..utils.common import (
    get_logger,
    log_operation_failure,
    log_operation_start,
    log_operation_success,
    print_error_panel,
    print_info_panel,
    print_success_panel,
    print_warning_panel,
)
from ..utils.exception import ValidationError


def register_config_commands(main_group):
    """Register all config commands with the main CLI group."""
    # Create the config group
    config_group = click.Group(name="config", help="Configuration management commands.")
    config_group.add_command(validate)
    config_group.add_command(show)
    config_group.add_command(edit)
    config_group.add_command(export)
    config_group.add_command(import_cmd)

    # Add the config group to main
    main_group.add_command(config_group)


@click.command()
@click.option("--detailed", "-d", is_flag=True, help="Show detailed validation report")
@click.option("--strict", is_flag=True, help="Use strict validation mode")
@click.option("--export", "-e", help="Export validation report to file")
@click.pass_context
def validate(
    ctx: click.Context, detailed: bool, strict: bool, export: Optional[str]
) -> None:
    """Validate configuration file.

    Checks the configuration file for errors and displays validation results.
    """
    get_logger()
    log_operation_start("configuration validation", detailed=detailed, strict=strict)

    try:
        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()

        # Get validation report with strict mode if specified
        validation_report = config_manager.get_validation_report(config, strict=strict)
        errors = validation_report["errors"]
        warnings = validation_report["warnings"]

        repo_count = len(config.repositories) if config.repositories is not None else 0

        # Export report if requested
        if export:
            from datetime import datetime

            export_data = {
                "timestamp": datetime.now().isoformat(),
                "config_path": str(config_manager.config_path),
                "repo_count": repo_count,
                "errors": errors,
                "warnings": warnings,
                "validation_mode": "strict" if strict else "normal",
            }

            try:
                with open(export, "w") as f:
                    json.dump(export_data, f, indent=2)
                print_success_panel(f"Validation report exported to {export}")
            except Exception as export_error:
                print_error_panel(
                    "Failed to export validation report", str(export_error)
                )

        if not errors and not warnings:
            log_operation_success("configuration validation", repo_count=repo_count)
            if detailed:
                print_success_panel(
                    "Configuration is valid!",
                    f"Found {repo_count} repositories\n"
                    f"LLM provider: {config.settings.llm_provider}\n"
                    f"Validation mode: {'strict' if strict else 'normal'}",
                )
            else:
                print_success_panel(
                    "Configuration is valid!", f"Found {repo_count} repositories"
                )
        elif not errors and warnings:
            log_operation_success("configuration validation", repo_count=repo_count)
            warning_details = (
                "\n".join(f"• {warning}" for warning in warnings)
                if detailed
                else f"{len(warnings)} warnings found"
            )
            print_warning_panel(
                "Configuration is valid with warnings",
                f"Found {repo_count} repositories\n"
                f"LLM provider: {config.settings.llm_provider}\n\n"
                f"Warnings ({len(warnings)}):\n{warning_details}",
            )
        else:
            log_operation_failure(
                "configuration validation", ValidationError("Configuration has errors")
            )

            if detailed:
                error_details = "\n".join(f"• {error}" for error in errors)
                warning_details = (
                    "\n".join(f"• {warning}" for warning in warnings)
                    if warnings
                    else ""
                )
                print_error_panel(
                    f"Configuration has {len(errors)} error(s)",
                    f"Errors:\n{error_details}"
                    + (
                        f"\n\nWarnings ({len(warnings)}):\n{warning_details}"
                        if warnings
                        else ""
                    ),
                )
            else:
                print_error_panel(
                    f"Configuration has {len(errors)} error(s) and {len(warnings)} warning(s)",
                    "Use --detailed flag to see full details",
                )
            sys.exit(1)

    except FileNotFoundError as e:
        log_operation_failure("configuration validation", e)
        print_error_panel(
            "Configuration file not found",
            "Run 'gitco init' to create a configuration file.",
        )
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration validation", e)
        print_error_panel("Error validating configuration", str(e))
        sys.exit(1)


@click.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Show configuration status.

    Displays information about the current configuration.
    """
    get_logger()
    log_operation_start("configuration status")

    try:
        config_manager = ConfigManager(ctx.obj.get("config"))
        config = config_manager.load_config()

        repo_count = len(config.repositories) if config.repositories is not None else 0
        log_operation_success("configuration status", repo_count=repo_count)
        print_success_panel("Configuration Status", f"Found {repo_count} repositories")

        print_info_panel(
            "Configuration File", f"Configuration file: {config_manager.config_path}"
        )
        print_info_panel("Repositories", f"Repositories: {repo_count}")
        print_info_panel(
            "LLM Provider", f"LLM provider: {config.settings.llm_provider}"
        )
        print_info_panel(
            "Analysis Enabled", f"Analysis enabled: {config.settings.analysis_enabled}"
        )
        print_info_panel(
            "Max Repos per Batch",
            f"Max repos per batch: {config.settings.max_repos_per_batch}",
        )

        if config.repositories is not None and config.repositories:
            print_info_panel("Repository Details", "Repository Details:")
            for repo_name, repo_info in config.repositories.items():
                if hasattr(repo_info, "fork") and hasattr(repo_info, "upstream"):
                    print_info_panel(
                        "Repository",
                        f"  - {repo_name}: {repo_info.fork} -> {repo_info.upstream}",
                    )
                else:
                    print_info_panel("Repository", f"  - {repo_name}")

    except FileNotFoundError as e:
        log_operation_failure("configuration status", e)
        print_error_panel(
            "Configuration file not found",
            "Run 'gitco init' to create a configuration file.",
        )
        sys.exit(1)
    except Exception as e:
        log_operation_failure("configuration status", e)
        print_error_panel("Error reading configuration", str(e))
        sys.exit(1)


@click.command()
@click.pass_context
def edit(ctx: click.Context) -> None:
    """Edit configuration file.

    Opens the configuration file in the default editor for editing.
    """
    try:
        config_manager = get_config_manager(ctx.obj.get("config"))
        config_path = config_manager.config_path

        # Get the default editor
        editor = os.environ.get("EDITOR", "nano")

        # Open the config file in the editor
        subprocess.run([editor, str(config_path)])

        print_success_panel(
            "Configuration Editor", "Configuration file opened for editing"
        )

    except Exception as e:
        log_operation_failure("configuration editing", e)
        print_error_panel("Error opening configuration editor", str(e))
        sys.exit(1)


@click.command()
@click.option("--output", "-o", required=True, help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Export format",
)
@click.pass_context
def export(ctx: click.Context, output: str, format: str) -> None:
    """Export configuration.

    Exports the current configuration to a file in the specified format.
    """
    try:
        config_manager = get_config_manager(ctx.obj.get("config"))
        config_data = config_manager.get_config_dict()

        output_path = Path(output)

        if format == "json":
            with open(output_path, "w") as f:
                json.dump(config_data, f, indent=2)
        else:  # yaml
            with open(output_path, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False)

        print_success_panel(
            "Configuration Export", f"Configuration exported to: {output_path}"
        )

    except Exception as e:
        log_operation_failure("configuration export", e)
        print_error_panel("Error exporting configuration", str(e))
        sys.exit(1)


@click.command(name="import")
@click.option("--input", "-i", required=True, help="Input file path")
@click.option("--merge", "-m", is_flag=True, help="Merge with existing configuration")
@click.pass_context
def import_cmd(ctx: click.Context, input: str, merge: bool) -> None:
    """Import configuration.

    Imports configuration from a file, optionally merging with existing configuration.
    """
    try:
        config_manager = get_config_manager(ctx.obj.get("config"))
        input_path = Path(input)

        if not input_path.exists():
            print_error_panel(
                "Import Error", f"Configuration file not found: {input_path}"
            )
            sys.exit(1)

        # Load the input configuration
        with open(input_path) as f:
            if input_path.suffix.lower() == ".json":
                import_data = json.load(f)
            else:
                import_data = yaml.safe_load(f)

        if merge:
            # Merge with existing configuration
            current_config = config_manager.get_config_dict()
            current_config.update(import_data)
            import_data = current_config

        # Save the imported configuration
        config_manager.save_config_dict(import_data)

        action = "merged with existing" if merge else "imported"
        print_success_panel(
            "Configuration Import", f"Configuration {action} from: {input_path}"
        )

    except Exception as e:
        log_operation_failure("configuration import", e)
        print_error_panel("Error importing configuration", str(e))
        sys.exit(1)


# Export function for CLI registration
config_commands = register_config_commands
