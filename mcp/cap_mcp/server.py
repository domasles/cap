"""MCP server for CAP - powered by FastMCP."""

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService

from .tools import dependencies, architecture, api


def create_server(workspace_path: str) -> FastMCP:
    """
    Create and configure a FastMCP server for the given workspace.

    Args:
        workspace_path: Path to workspace root

    Returns:
        Configured FastMCP server instance
    """
    server = FastMCP("cap-mcp")
    config_service = ConfigService(workspace_path)

    dependencies.register(server, config_service)
    architecture.register(server, config_service)
    api.register(server, config_service)

    return server
