"""Config service - orchestrates file reading and parsing."""

from pathlib import Path
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from ...domain.models import DependenciesYAML, ArchitectureYAML, ApiYAML
from ...infrastructure import FileReader, FileReaderError
from .mcp_formatter import MCPFormatter

T = TypeVar("T", bound=BaseModel)


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
        self.cap_dir = self.file_reader.find_cap_directory(self.workspace_path)

    def load_config(self, filename: str, model_class: Type[T]) -> Optional[T]:
        """
        Load and parse a CAP configuration file.

        Args:
            filename: Name of the YAML file (e.g. 'dependencies.yaml')
            model_class: Pydantic model class to validate against

        Returns:
            Validated model instance if file exists, None otherwise

        Raises:
            ValidationError: If file structure is invalid
            FileReaderError: If file cannot be read
        """
        if self.cap_dir is None:
            return None

        file_path = self.cap_dir / filename
        if not file_path.exists():
            return None

        data = self.file_reader.read_yaml(str(file_path))
        return model_class.model_validate(data)

    def load_dependencies(self) -> Optional[DependenciesYAML]:
        """Load and parse dependencies.yaml."""
        return self.load_config("dependencies.yaml", DependenciesYAML)

    def load_architecture(self) -> Optional[ArchitectureYAML]:
        """Load and parse architecture.yaml."""
        return self.load_config("architecture.yaml", ArchitectureYAML)

    def load_api(self) -> Optional[ApiYAML]:
        """Load and parse api.yaml."""
        return self.load_config("api.yaml", ApiYAML)
