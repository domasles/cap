"""Dependencies tool for MCP."""

import logging

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService
from cap_core.application import MCPFormatter

logger = logging.getLogger(__name__)


def register(server: FastMCP, config_service: ConfigService, formatter: MCPFormatter) -> None:
    """Register the get_dependencies tool on the server."""

    @server.tool(
        name="get_dependencies",
        description="ALWAYS call BEFORE adding imports or suggesting packages. Returns all runtime and dev dependencies with version constraints and forbidden-dependency rules per layer. More accurate than reading package manifests directly.",
    )
    def get_dependencies() -> dict:
        """Get project dependencies, versions, and dependency rules."""
        try:
            deps = config_service.load_dependencies()

            if deps is None:
                return {
                    "error": "No dependencies.yaml found in workspace",
                    "hint": "Create a .cap/dependencies.yaml file in your workspace",
                }

            return formatter.format_dependencies(deps)

        except Exception as e:
            logger.exception("Failed to load dependencies config")
            return {"error": f"Failed to load dependencies: {str(e)}"}
