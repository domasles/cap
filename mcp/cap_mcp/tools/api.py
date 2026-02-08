"""API tool for MCP."""

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService
from cap_core.application import MCPFormatter


def register(server: FastMCP, config_service: ConfigService, formatter: MCPFormatter) -> None:
    """Register the get_api tool on the server."""

    @server.tool(
        name="get_api",
        description="Call this before reading source files to understand the codebase surface. Returns all public and internal exports, their file locations, stability markers, and access rules. Use this to understand WHAT exists and how components connect before diving into implementation details.",
    )
    def get_api() -> dict:
        """Get public and internal API exports with usage rules."""
        try:
            api = config_service.load_api()

            if api is None:
                return {
                    "error": "No api.yaml found in workspace",
                    "hint": "Create a .cap/api.yaml file in your workspace",
                }

            return formatter.format_api(api)

        except Exception as e:
            return {"error": f"Failed to load API: {str(e)}"}
