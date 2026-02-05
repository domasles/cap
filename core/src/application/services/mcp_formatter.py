"""MCP formatter - transforms domain models to MCP-friendly JSON format."""

from typing import Optional

from src.domain.models import DependenciesYAML, ArchitectureYAML, ApiYAML


class MCPFormatter:
    """Service that transforms domain models into MCP-compatible JSON."""

    @staticmethod
    def format_dependencies(model: DependenciesYAML) -> dict:
        """
        Transform DependenciesYAML to MCP JSON format.

        Args:
            model: Validated domain model

        Returns:
            MCP-compatible JSON dict
        """
        result = {
            "dependencies": {
                lang: {
                    "runtime": {pkg: info.model_dump() for pkg, info in deps.runtime.items()},
                    "dev": {pkg: info.model_dump() for pkg, info in deps.dev.items()},
                }
                for lang, deps in model.dependencies.items()
            }
        }

        if model.rules:
            result["rules"] = {"forbid": [rule.model_dump() for rule in model.rules.forbid]}

        if model.notes:
            result["notes"] = model.notes

        return result

    @staticmethod
    def format_architecture(model: ArchitectureYAML) -> dict:
        """
        Transform ArchitectureYAML to MCP JSON format.

        Args:
            model: Validated domain model

        Returns:
            MCP-compatible JSON dict
        """
        result = {"architecture": model.architecture.model_dump()}

        if model.layers:
            result["layers"] = {
                name: layer.model_dump() for name, layer in model.layers.items()
            }

        if model.modules:
            result["modules"] = {
                name: module.model_dump(exclude_none=True)
                for name, module in model.modules.items()
            }

        if model.rules:
            result["rules"] = {"forbid": [rule.model_dump() for rule in model.rules.forbid]}

        if model.notes:
            result["notes"] = model.notes

        return result

    @staticmethod
    def format_api(model: ApiYAML) -> dict:
        """
        Transform ApiYAML to MCP JSON format.

        Args:
            model: Validated domain model

        Returns:
            MCP-compatible JSON dict
        """
        result = {"api": {}}

        if model.api.public:
            result["api"]["public"] = {
                name: export.model_dump(exclude_none=True)
                for name, export in model.api.public.items()
            }

        if model.api.internal:
            result["api"]["internal"] = {
                name: export.model_dump(exclude_none=True)
                for name, export in model.api.internal.items()
            }

        if model.rules:
            result["rules"] = {"forbid": []}
            for rule in model.rules.forbid:
                rule_dict = rule.model_dump(exclude={"except_"})
                if rule.except_:
                    rule_dict["except"] = rule.except_
                result["rules"]["forbid"].append(rule_dict)

        if model.notes:
            result["notes"] = model.notes

        return result
