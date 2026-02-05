"""Dependencies tool for MCP."""

from cap_core import ConfigService
from cap_core.application import MCPFormatter


class DependenciesTool:
    """Tool for retrieving project dependencies."""

    @staticmethod
    def get_definition() -> dict:
        """
        Get MCP tool definition.

        Returns:
            Tool definition dict
        """
        return {
            "name": "get_dependencies",
            "description": "Get project dependencies, versions, and dependency rules. Returns runtime and dev dependencies organized by language, with rules for forbidden dependency patterns.",
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
            Dependencies data or error
        """
        try:
            config_service = ConfigService(workspace_path)
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
