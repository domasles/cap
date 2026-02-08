"""Validation service - validates CAP configuration files."""

from typing import Optional

from pydantic import ValidationError

from ...domain.models.validation import ValidationIssue, ValidationResult, WorkspaceValidation
from ...infrastructure import FileReaderError
from .config_service import ConfigService


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

            errors: list[ValidationIssue] = []
            root = self.config_service.file_reader.compose_yaml(str(file_path))

            if root is not None:
                errors.extend(self.config_service.file_reader.find_duplicate_keys(root))

            try:
                loader()
            except ValidationError as e:
                for err in e.errors():
                    loc = ".".join(str(part) for part in err["loc"])
                    line, col = (0, 0)
                    if root is not None:
                        line, col = self.config_service.file_reader.resolve_yaml_line(root, err["loc"])
                    errors.append(
                        ValidationIssue(
                            message=f"{loc}: {err['msg']}",
                            line=line,
                            column=col,
                        )
                    )
            except FileReaderError as e:
                errors.append(ValidationIssue(message=e.message))

            validation.results.append(
                ValidationResult(
                    file=filename,
                    valid=len(errors) == 0,
                    errors=errors,
                )
            )

        return validation
