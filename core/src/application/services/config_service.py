"""Config service - orchestrates file reading and parsing."""

from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from src.domain.models import DependenciesYAML, ArchitectureYAML, ApiYAML
from src.infrastructure import FileReader, FileReaderError
from .mcp_formatter import MCPFormatter


class ConfigService:
    """Service that orchestrates CAP configuration loading and parsing."""

    def __init__(self, workspace_path: str):
        """
        Initialize config service for a workspace.

        Args:
            workspace_path: Path to workspace root
        """
        self.workspace_path = workspace_path
        self.file_reader = FileReader()

    def load_dependencies(self) -> Optional[DependenciesYAML]:
        """
        Load and parse dependencies.yaml if it exists.

        Returns:
            DependenciesYAML if file exists and is valid, None otherwise

        Raises:
            ValidationError: If file structure is invalid (from Pydantic)
            FileReaderError: If file cannot be read
        """
        cap_dir = self.file_reader.find_cap_directory(self.workspace_path)
        if cap_dir is None:
            return None

        dependencies_file = cap_dir / "dependencies.yaml"
        if not dependencies_file.exists():
            return None

        data = self.file_reader.read_yaml(str(dependencies_file))
        return DependenciesYAML.model_validate(data)

    def load_architecture(self) -> Optional[ArchitectureYAML]:
        """
        Load and parse architecture.yaml if it exists.

        Returns:
            ArchitectureYAML if file exists and is valid, None otherwise

        Raises:
            ValidationError: If file structure is invalid (from Pydantic)
            FileReaderError: If file cannot be read
        """
        cap_dir = self.file_reader.find_cap_directory(self.workspace_path)
        if cap_dir is None:
            return None

        architecture_file = cap_dir / "architecture.yaml"
        if not architecture_file.exists():
            return None

        data = self.file_reader.read_yaml(str(architecture_file))
        return ArchitectureYAML.model_validate(data)

    def load_api(self) -> Optional[ApiYAML]:
        """
        Load and parse api.yaml if it exists.

        Returns:
            ApiYAML if file exists and is valid, None otherwise

        Raises:
            ValidationError: If file structure is invalid (from Pydantic)
            FileReaderError: If file cannot be read
        """
        cap_dir = self.file_reader.find_cap_directory(self.workspace_path)
        if cap_dir is None:
            return None

        api_file = cap_dir / "api.yaml"
        if not api_file.exists():
            return None

        data = self.file_reader.read_yaml(str(api_file))
        return ApiYAML.model_validate(data)

    def load_all(self) -> dict:
        """
        Load all CAP configuration files as MCP-ready JSON.

        Returns:
            Dict with keys 'dependencies', 'architecture', 'api'
            (values are MCP-ready JSON dicts or None if file doesn't exist)
        """
        deps = self.load_dependencies()
        arch = self.load_architecture()
        api = self.load_api()

        formatter = MCPFormatter()

        return {
            "dependencies": formatter.format_dependencies(deps) if deps else None,
            "architecture": formatter.format_architecture(arch) if arch else None,
            "api": formatter.format_api(api) if api else None,
        }
