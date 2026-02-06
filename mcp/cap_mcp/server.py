"""MCP server for CAP - handles protocol communication only."""

import json
import sys

from .tools import DependenciesTool, ArchitectureTool, ApiTool


class MCPServer:
    """MCP server - handles JSON-RPC protocol and tool routing."""

    def __init__(self, workspace_path: str):
        """
        Initialize MCP server.

        Args:
            workspace_path: Path to workspace root
        """
        self.workspace_path = workspace_path
        self.tools = {
            "get_dependencies": DependenciesTool,
            "get_architecture": ArchitectureTool,
            "get_api": ApiTool,
        }

    def get_tool_definitions(self) -> list[dict]:
        """
        Get list of all tool definitions.

        Returns:
            List of tool definition dicts
        """
        return [tool_class.get_definition() for tool_class in self.tools.values()]

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Route tool call to appropriate tool class.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        tool_class = self.tools.get(tool_name)
        if tool_class is None:
            return {"error": f"Unknown tool: {tool_name}"}

        return tool_class.execute(self.workspace_path, arguments)

    def run_stdio(self):
        """
        Run MCP server in stdio mode.
        Reads JSON-RPC messages from stdin, writes responses to stdout.
        """
        print("MCP Server started", file=sys.stderr)
        print(f"Workspace: {self.workspace_path}", file=sys.stderr)

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                response = self._handle_jsonrpc(request)

                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                    "id": None,
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {e}"},
                    "id": None,
                }
                print(json.dumps(error_response), flush=True)

    def _handle_jsonrpc(self, request: dict) -> dict:
        """
        Handle JSON-RPC 2.0 request.

        Args:
            request: JSON-RPC request object

        Returns:
            JSON-RPC response object
        """
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "mcp-server", "version": "0.1.0"},
                },
                "id": req_id,
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {"tools": self.get_tool_definitions()},
                "id": req_id,
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = self.call_tool(tool_name, arguments)

            return {
                "jsonrpc": "2.0",
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
                "id": req_id,
            }

        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": req_id,
            }
