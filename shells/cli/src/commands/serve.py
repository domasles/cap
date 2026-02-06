"""Serve command - Launch MCP server."""

import sys
import click
from pathlib import Path

from ..utils import get_workspace, validate_workspace, console, print_error


@click.command()
@click.argument("workspace", type=click.Path(exists=True), default=".", required=False)
def stdio(workspace):
    """
    Launch MCP server in stdio mode for a workspace.

    WORKSPACE is the path to the workspace root. Defaults to current directory.

    This command is typically used by IDE extensions to spawn an MCP server
    process that communicates over stdin/stdout using JSON-RPC 2.0.

    Example:
        cap serve stdio                    # Serve current directory
        cap serve stdio /path/to/project   # Serve specific project
    """
    workspace_path = get_workspace(workspace)

    # Validate workspace has .cap/ directory
    is_valid, error_msg = validate_workspace(workspace_path)
    if not is_valid:
        print_error(error_msg)
        console.print(f"\nRun 'cap init' in {workspace_path} to create .cap/ directory.", style="yellow")
        sys.exit(1)

    # Import here to avoid loading MCP when not needed
    try:
        from cap_mcp import MCPServer
    except ImportError:
        print_error("cap-mcp package not found. Install with: pip install cap-mcp")
        sys.exit(1)

    # Log to stderr (stdout is for JSON-RPC)
    console.print(f"Starting MCP server for workspace: {workspace_path}", file=sys.stderr, style="cyan")
    console.print("Listening on stdin/stdout...", file=sys.stderr, style="dim")

    # Start server (blocks until stdin closes)
    try:
        server = MCPServer(str(workspace_path))
        server.run_stdio()
    except KeyboardInterrupt:
        console.print("\nServer stopped by user", file=sys.stderr, style="yellow")
        sys.exit(0)
    except Exception as e:
        print_error(f"Server error: {e}")
        sys.exit(1)


@click.group()
def serve():
    """Launch MCP server in various modes."""
    pass


serve.add_command(stdio)
