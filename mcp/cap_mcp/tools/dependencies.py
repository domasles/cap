"""Dependencies tool for MCP."""

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService
from cap_core.application import MCPFormatter


def register(server: FastMCP, config_service: ConfigService) -> None:
    """Register the get_dependencies tool on the server."""

    @server.tool(
        name="get_dependencies",
        description="Get project dependencies, versions, and dependency rules. Returns runtime and dev dependencies organized by language, with rules for forbidden dependency patterns.",
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

            formatter = MCPFormatter()
            return formatter.format_dependencies(deps)

        except Exception as e:
            return {"error": f"Failed to load dependencies: {str(e)}"}
