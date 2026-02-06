"""Utility functions for workspace detection and path handling."""

from pathlib import Path
from typing import Optional

from cap_core.infrastructure import FileReader


def get_workspace(path: Optional[str] = None) -> Path:
    """
    Get workspace path, defaulting to current working directory.

    Args:
        path: Optional path to workspace. If None, uses CWD.

    Returns:
        Absolute path to workspace
    """
    if path is None:
        return Path.cwd()
    return Path(path).resolve()


def validate_workspace(workspace: Path) -> tuple[bool, str]:
    """
    Validate that workspace has a .cap/ directory.

    Args:
        workspace: Workspace path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not workspace.exists():
        return False, f"Workspace does not exist: {workspace}"

    if not workspace.is_dir():
        return False, f"Workspace is not a directory: {workspace}"

    cap_dir = FileReader.find_cap_directory(str(workspace))

    if cap_dir is None:
        return False, f"No .cap/ directory found in {workspace}"

    return True, ""
