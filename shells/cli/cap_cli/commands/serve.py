"""Serve command - Launch MCP server."""

import click

from ..utils import get_workspace, validate_workspace, console, print_error


@click.command()
@click.argument("workspace", type=click.Path(exists=True), default=".", required=False)
@click.pass_context
def serve(ctx, workspace):
    """
    Launch MCP server in stdio mode for a workspace.

    WORKSPACE is the path to the workspace root. Defaults to current directory.

    This command is typically used by IDE extensions to spawn an MCP server
    process that communicates over stdin/stdout using the MCP protocol.

    Example:
        cap serve                    # Serve current directory
        cap serve /path/to/project   # Serve specific project
    """
    workspace_path = get_workspace(workspace)

    # Validate workspace has .cap/ directory
    is_valid, error_msg = validate_workspace(workspace_path)
    if not is_valid:
        print_error(error_msg)
        console.print(f"\nRun 'cap init' in {workspace_path} to create .cap/ directory.", style="yellow")
        ctx.exit(1)

    try:
        from cap_mcp import create_server
    except ImportError:
        print_error("cap_mcp package not found. Install with: pip install cap_mcp")
        ctx.exit(1)

    # Log to stderr (stdout is for MCP protocol)
    click.echo(f"Starting MCP server for workspace: {workspace_path}", err=True)
    click.echo("Listening on stdin/stdout...", err=True)

    # Create and run FastMCP server in stdio mode
    try:
        server = create_server(str(workspace_path))
        server.run(transport="stdio")
    except KeyboardInterrupt:
        click.echo("\nServer stopped by user", err=True)
        ctx.exit(0)
    except Exception as e:
        print_error(f"Server error: {e}")
        ctx.exit(1)
