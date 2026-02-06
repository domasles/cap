"""Validate command - Check .cap/ configuration files."""

import sys
import click

from ..utils import get_workspace, validate_workspace, console, print_success, print_error, print_info


@click.command()
@click.argument("workspace", type=click.Path(exists=True), default=".", required=False)
def validate(workspace):
    """
    Validate .cap/ configuration files in a workspace.

    WORKSPACE is the path to the workspace root. Defaults to current directory.

    Checks each YAML file for correct structure and valid values.

    Example:
        cap validate                    # Validate current directory
        cap validate /path/to/project   # Validate specific project
    """
    workspace_path = get_workspace(workspace)

    # Quick check that .cap/ exists
    is_valid, error_msg = validate_workspace(workspace_path)
    if not is_valid:
        print_error(error_msg)
        console.print(f"\nRun 'cap init' in {workspace_path} to create .cap/ directory.", style="yellow")
        sys.exit(1)

    try:
        from cap_core import ConfigService, ValidationService
    except ImportError:
        print_error("cap_core package not found. Install with: pip install cap_core")
        sys.exit(1)

    config_service = ConfigService(str(workspace_path))
    validation_service = ValidationService(config_service)
    result = validation_service.validate_all()

    if not result.results:
        print_info("No configuration files found in .cap/ directory.")
        console.print("Run 'cap init' to create template files.", style="dim")
        sys.exit(0)

    # Print results
    has_errors = False

    for file_result in result.results:
        if file_result.valid:
            print_success(f"{file_result.file}")
        else:
            has_errors = True
            print_error(f"{file_result.file}")
            console.print(f"  {file_result.error}", style="dim")

    # Summary
    valid_count = sum(1 for r in result.results if r.valid)
    total_count = len(result.results)

    console.print()
    if has_errors:
        console.print(f"{valid_count}/{total_count} files valid", style="bold yellow")
        sys.exit(1)
    else:
        console.print(f"All {total_count} files valid", style="bold green")
