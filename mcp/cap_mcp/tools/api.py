"""API tool for MCP."""

import logging

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService
from cap_core.application import MCPFormatter

logger = logging.getLogger(__name__)


def register(server: FastMCP, config_service: ConfigService, formatter: MCPFormatter) -> None:
    """Register the get_api tool on the server."""

    @server.tool(
        name="get_api",
        description="ALWAYS call BEFORE reading source files. Returns all public and internal exports with file locations, stability markers, and access rules. Provides the full codebase surface faster than scanning files.",
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
            logger.exception("Failed to load API config")
            return {"error": f"Failed to load API: {str(e)}"}
