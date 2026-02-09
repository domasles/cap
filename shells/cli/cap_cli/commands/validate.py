"""Validate command - Check .cap/ configuration files."""

import json
import click

from ..utils import get_workspace, validate_workspace, console, print_success, print_error, print_info


@click.command()
@click.argument("workspace", type=click.Path(exists=True), default=".", required=False)
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON for programmatic use")
@click.option(
    "--file",
    "-f",
    "file_filter",
    multiple=True,
    type=click.Choice(["dependencies", "architecture", "api"], case_sensitive=False),
    help="Validate only specific file(s). Can be used multiple times.",
)
@click.pass_context
def validate(ctx, workspace, json_output, file_filter):
    """
    Validate .cap/ configuration files in a workspace.

    WORKSPACE is the path to the workspace root. Defaults to current directory.

    Checks each YAML file for correct structure and valid values.

    Example:
        cap validate                         # Validate current directory
        cap validate /path/to/project        # Validate specific project
        cap validate --json                  # Output as JSON
        cap validate -f dependencies         # Validate only dependencies.yaml
        cap validate -f dependencies -f api  # Validate two files
    """
    workspace_path = get_workspace(workspace)

    is_valid, error_msg = validate_workspace(workspace_path)
    if not is_valid:
        if json_output:
            click.echo(json.dumps({"error": error_msg, "results": []}))
            ctx.exit(1)
        print_error(error_msg)
        console.print(f"\nRun 'cap init' in {workspace_path} to create .cap/ directory.", style="yellow")
        ctx.exit(1)

    try:
        from cap_core import ConfigService, ValidationService
    except ImportError:
        if json_output:
            click.echo(json.dumps({"error": "cap_core package not found", "results": []}))
            ctx.exit(1)
        print_error("cap_core package not found. Install with: pip install cap_core")
        ctx.exit(1)

    config_service = ConfigService(str(workspace_path))
    validation_service = ValidationService(config_service)
    result = validation_service.validate_all(files=list(file_filter) if file_filter else None)

    if json_output:
        output = [
            {
                "file": r.file,
                "valid": r.valid,
                "errors": [{"message": e.message, "line": e.line, "column": e.column} for e in r.errors],
            }
            for r in result.results
        ]
        click.echo(json.dumps(output))
        ctx.exit(0 if result.all_valid else 1)

    if not result.results:
        print_info("No configuration files found in .cap/ directory.")
        console.print("Run 'cap init' to create template files.", style="dim")
        ctx.exit(0)

    has_errors = False

    for file_result in result.results:
        if file_result.valid:
            print_success(f"{file_result.file}")
        else:
            has_errors = True
            print_error(f"{file_result.file}")
            for err in file_result.errors:
                if err.line is not None:
                    line_info = f"Line {err.line + 1}"
                    if err.column is not None:
                        line_info += f", column {err.column + 1}"
                else:
                    line_info = ""
                prefix = f"  {line_info}: " if line_info else "  "
                console.print(f"{prefix}{err.message}", style="dim")

    valid_count = sum(1 for r in result.results if r.valid)
    total_count = len(result.results)

    console.print()
    if has_errors:
        console.print(f"{valid_count}/{total_count} files valid", style="bold yellow")
        ctx.exit(1)
    else:
        console.print(f"All {total_count} files valid", style="bold green")
