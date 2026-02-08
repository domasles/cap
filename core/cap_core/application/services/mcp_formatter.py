"""MCP formatter - transforms domain models to MCP-friendly JSON format."""

from pydantic import BaseModel

from ...domain.models import DependenciesYAML, ArchitectureYAML, ApiYAML


class MCPFormatter:
    """Service that transforms domain models into MCP-compatible JSON."""

    @staticmethod
    def format_model(model: BaseModel) -> dict:
        """
        Transform any CAP domain model to MCP JSON format.

        Serializes the model with None values excluded, and removes
        empty rules dicts (when both forbid and permit are None).

        Args:
            model: Validated Pydantic domain model

        Returns:
            MCP-compatible JSON dict
        """
        result = model.model_dump(exclude_none=True)

        if "rules" in result and not result["rules"]:
            del result["rules"]

        return result

    @staticmethod
    def format_dependencies(model: DependenciesYAML) -> dict:
        """Transform DependenciesYAML to MCP JSON format."""
        return MCPFormatter.format_model(model)

    @staticmethod
    def format_architecture(model: ArchitectureYAML) -> dict:
        """Transform ArchitectureYAML to MCP JSON format."""
        return MCPFormatter.format_model(model)

    @staticmethod
    def format_api(model: ApiYAML) -> dict:
        """Transform ApiYAML to MCP JSON format."""
        return MCPFormatter.format_model(model)
