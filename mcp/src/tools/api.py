"""API tool for MCP."""

from cap_core import ConfigService
from cap_core.application import MCPFormatter


class ApiTool:
    """Tool for retrieving API exports."""

    @staticmethod
    def get_definition() -> dict:
        """
        Get MCP tool definition.

        Returns:
            Tool definition dict
        """
        return {
            "name": "get_api",
            "description": "Get public and internal API exports with usage rules. Shows exported functions/classes, their locations, stability markers, and access restrictions.",
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
            API data or error
        """
        try:
            config_service = ConfigService(workspace_path)
            api = config_service.load_api()

            if api is None:
                return {
                    "error": "No api.yaml found in workspace",
                    "hint": "Create a .cap/api.yaml file in your workspace",
                }

            formatter = MCPFormatter()
            return formatter.format_api(api)

        except Exception as e:
            return {"error": f"Failed to load API: {str(e)}"}
