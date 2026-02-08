"""Validation domain models - pure data structures for validation results."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationIssue:
    """A single validation issue with location information."""

    message: str
    line: Optional[int] = None
    column: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of validating a single CAP configuration file."""

    file: str
    valid: bool
    errors: List[ValidationIssue] = field(default_factory=list)


@dataclass
class WorkspaceValidation:
    """Result of validating an entire workspace's CAP configuration."""

    workspace_path: str
    cap_directory_found: bool
    results: List[ValidationResult] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if .cap/ exists and at least one file is valid."""
        return self.cap_directory_found and any(r.valid for r in self.results)

    @property
    def all_valid(self) -> bool:
        """True if all found files are valid."""
        return self.cap_directory_found and all(r.valid for r in self.results)
