"""Validation service - validates CAP configuration files."""

from dataclasses import dataclass, field
from typing import Optional

from pydantic import ValidationError

from ...infrastructure import FileReaderError
from .config_service import ConfigService


@dataclass
class ValidationResult:
    """Result of validating a single CAP configuration file."""

    file: str
    valid: bool
    error: Optional[str] = None


@dataclass
class WorkspaceValidation:
    """Result of validating an entire workspace's CAP configuration."""

    workspace_path: str
    cap_directory_found: bool
    results: list[ValidationResult] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if .cap/ exists and at least one file is valid."""
        return self.cap_directory_found and any(r.valid for r in self.results)

    @property
    def all_valid(self) -> bool:
        """True if all found files are valid."""
        return self.cap_directory_found and all(r.valid for r in self.results)


class ValidationService:
    """Service that validates CAP configuration files in a workspace."""

    def __init__(self, config_service: ConfigService):
        """
        Initialize validation service.

        Args:
            config_service: ConfigService instance for loading configs
        """
        self.config_service = config_service

    def validate_all(self) -> WorkspaceValidation:
        """
        Validate all CAP configuration files in the workspace.

        Returns:
            WorkspaceValidation with per-file results
        """
        validation = WorkspaceValidation(
            workspace_path=self.config_service.workspace_path,
            cap_directory_found=False,
        )

        cap_dir = self.config_service.cap_dir
        if cap_dir is None:
            return validation

        validation.cap_directory_found = True

        loaders = {
            "dependencies.yaml": self.config_service.load_dependencies,
            "architecture.yaml": self.config_service.load_architecture,
            "api.yaml": self.config_service.load_api,
        }

        for filename, loader in loaders.items():
            file_path = cap_dir / filename

            if not file_path.exists():
                continue

            try:
                loader()
                validation.results.append(ValidationResult(file=filename, valid=True))
            except ValidationError as e:
                validation.results.append(
                    ValidationResult(
                        file=filename,
                        valid=False,
                        error=str(e),
                    )
                )
            except FileReaderError as e:
                validation.results.append(
                    ValidationResult(
                        file=filename,
                        valid=False,
                        error=e.message,
                    )
                )

        return validation
