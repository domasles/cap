"""Architecture tool for MCP."""

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService
from cap_core.application import MCPFormatter


def register(server: FastMCP, config_service: ConfigService, formatter: MCPFormatter) -> None:
    """Register the get_architecture tool on the server."""

    @server.tool(
        name="get_architecture",
        description="ALWAYS call this before planning any code changes. Returns the codebase's layer boundaries, module ownership, import restrictions, and architectural rules. Use this to understand WHERE code should be placed and what constraints apply. Essential context for any task involving adding, moving, or restructuring code.",
    )
    def get_architecture() -> dict:
        """Get codebase architecture including style, layers, modules, and rules."""
        try:
            arch = config_service.load_architecture()

            if arch is None:
                return {
                    "error": "No architecture.yaml found in workspace",
                    "hint": "Create a .cap/architecture.yaml file in your workspace",
                }

            return formatter.format_architecture(arch)

        except Exception as e:
            return {"error": f"Failed to load architecture: {str(e)}"}
