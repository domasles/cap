"""Domain models matching exact YAML structure for dependencies.yaml"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PackageInfo(BaseModel):
    """Package version and reason."""

    version: str
    reason: str


class LanguageDependencies(BaseModel):
    """Runtime and dev dependencies for a language."""

    runtime: Dict[str, PackageInfo]
    dev: Dict[str, PackageInfo]


class DependencyRule(BaseModel):
    """Dependency restriction rule."""

    layer: str
    dependency: str
    reason: str


class DependencyRules(BaseModel):
    """Rules section wrapper."""

    forbid: List[DependencyRule]


class DependenciesYAML(BaseModel):
    """Root model for dependencies.yaml - matches YAML structure exactly."""

    dependencies: Dict[str, LanguageDependencies]
    rules: Optional[DependencyRules] = None
    notes: Optional[List[str]] = None
