"""Init command - Create .cap/ directory with template files."""

import click
import shutil

from pathlib import Path

from ..utils import get_workspace, console, print_success, print_error, print_info, print_warning


@click.command()
@click.argument("workspace", type=click.Path(exists=True), default=".", required=False)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing .cap/ directory")
@click.option("--minimal", "-m", is_flag=True, help="Create only directory structure without template files")
@click.pass_context
def init(ctx, workspace, force, minimal):
    """
    Initialize .cap/ directory with template configuration files.

    WORKSPACE is the path to the workspace root. Defaults to current directory.

    Creates a .cap/ directory with example YAML files that you can customize.

    Example:
        cap init                   # Initialize in current directory
        cap init /path/to/project  # Initialize in specific project
        cap init --force           # Overwrite existing .cap/
        cap init --minimal         # Create empty .cap/ directory only
    """
    workspace_path = get_workspace(workspace)

    if not workspace_path.exists():
        print_error(f"Workspace does not exist: {workspace_path}")
        ctx.exit(1)

    cap_dir = workspace_path / ".cap"

    # Check if .cap/ already exists
    if cap_dir.exists():
        if not force:
            print_warning(f".cap/ directory already exists in {workspace_path}")
            console.print("Use --force to overwrite existing files.\n", style="dim")
            ctx.exit(1)
        else:
            print_info(f"Overwriting existing .cap/ directory...")

    # Create .cap/ directory
    cap_dir.mkdir(exist_ok=True)
    print_success(f"Created .cap/ directory in {workspace_path}")

    if minimal:
        console.print("\n[OK] Minimal initialization complete\n", style="bold green")
        console.print(f"Next steps:", style="bold")
        console.print(f"  1. Add your configuration files to {cap_dir}/", style="dim")
        console.print("  2. Run 'cap validate' to check your configuration\n", style="dim")
        ctx.exit(0)

    # Copy template files
    try:
        # Get template files from package
        templates_dir = Path(__file__).parent.parent / "templates"

        if not templates_dir.exists():
            print_error("Template files not found in package")
            ctx.exit(1)

        templates = ["dependencies.yaml", "architecture.yaml", "api.yaml"]
        copied = 0

        for template in templates:
            src = templates_dir / template
            dst = cap_dir / template

            if src.exists():
                shutil.copy2(src, dst)
                print_success(f"Created {template}")
                copied += 1
            else:
                print_warning(f"Template not found: {template}")

        if copied > 0:
            console.print("\n[OK] Initialization complete\n", style="bold green")
            console.print(f"Next steps:", style="bold")
            console.print(f"  1. Edit the template files in {cap_dir}/", style="dim")
            console.print(f"  2. Remove any files you don't need", style="dim")
            console.print(f"  3. Run 'cap validate' to check your configuration", style="dim")
            console.print(f"  4. Run 'cap serve' to start the MCP server manually\n", style="dim")
        else:
            print_error("No template files were copied")
            ctx.exit(1)

    except OSError as e:
        print_error(f"Failed to copy template files: {e}")
        ctx.exit(1)
