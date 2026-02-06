"""MCP Server package - Codebase-Awareness Protocol."""

from .server import create_server
from .meta import __version__

__all__ = ["create_server", "__version__"]
