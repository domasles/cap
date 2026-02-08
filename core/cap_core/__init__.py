"""Core package - Codebase-Awareness Protocol."""

from .application import (
    ConfigService,
    ValidationService,
    ValidationIssue,
    ValidationResult,
    WorkspaceValidation,
    MCPFormatter,
)
from .meta import __version__

__all__ = [
    "ConfigService",
    "ValidationService",
    "ValidationIssue",
    "ValidationResult",
    "WorkspaceValidation",
    "MCPFormatter",
    "__version__",
]
