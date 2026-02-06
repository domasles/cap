"""Core package - Codebase-Awareness Protocol."""

from .application import ConfigService, ValidationService, ValidationResult, WorkspaceValidation, MCPFormatter
from .meta import __version__

__all__ = ["ConfigService", "ValidationService", "ValidationResult", "WorkspaceValidation", "MCPFormatter", "__version__"]
