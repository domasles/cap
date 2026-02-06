"""Architecture tool for MCP."""

from cap_core import ConfigService
from cap_core.application import MCPFormatter


class ArchitectureTool:
    """Tool for retrieving codebase architecture."""

    @staticmethod
    def get_definition() -> dict:
        """
        Get MCP tool definition.

        Returns:
            Tool definition dict
        """
        return {
            "name": "get_architecture",
            "description": "Get codebase architecture including style, layers, modules, and architectural rules. Shows ownership patterns, import restrictions, and bounded contexts.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        }

    @staticmethod
    def execute(workspace_path: str, arguments: dict) -> dict:
        """
        Execute the tool.

        Args:
            workspace_path: Path to workspace root
            arguments: Tool arguments (empty for this tool)

        Returns:
            Architecture data or error
        """
        try:
            config_service = ConfigService(workspace_path)
            arch = config_service.load_architecture()

            if arch is None:
                return {
                    "error": "No architecture.yaml found in workspace",
                    "hint": "Create a .cap/architecture.yaml file in your workspace",
                }

            formatter = MCPFormatter()
            return formatter.format_architecture(arch)

        except Exception as e:
            return {"error": f"Failed to load architecture: {str(e)}"}
