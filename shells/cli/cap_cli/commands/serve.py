"""Serve command - Launch MCP server."""

import sys
import click

from ..utils import get_workspace, validate_workspace, console, print_error


@click.command()
@click.argument("workspace", type=click.Path(exists=True), default=".", required=False)
def serve(workspace):
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
        sys.exit(1)

    try:
        from cap_mcp import create_server
    except ImportError:
        print_error("cap_mcp package not found. Install with: pip install cap_mcp")
        sys.exit(1)

    # Log to stderr (stdout is for MCP protocol)
    print(f"Starting MCP server for workspace: {workspace_path}", file=sys.stderr)
    print("Listening on stdin/stdout...", file=sys.stderr)

    # Create and run FastMCP server in stdio mode
    try:
        server = create_server(str(workspace_path))
        server.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print_error(f"Server error: {e}")
        sys.exit(1)
