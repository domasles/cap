"""Architecture tool for MCP."""

import logging

from mcp.server.fastmcp import FastMCP

from cap_core import ConfigService
from cap_core.application import MCPFormatter

logger = logging.getLogger(__name__)


def register(server: FastMCP, config_service: ConfigService, formatter: MCPFormatter) -> None:
    """Register the get_architecture tool on the server."""

    @server.tool(
        name="get_architecture",
        description="MUST call FIRST in any conversation about this codebase. Returns layer boundaries, module ownership, import restrictions, and architectural rules. Replaces reading source files for understanding project structure. Essential before adding, moving, or modifying any code.",
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
            logger.exception("Failed to load architecture config")
            return {"error": f"Failed to load architecture: {str(e)}"}
