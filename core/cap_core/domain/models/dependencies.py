"""Domain models matching exact YAML structure for dependencies.yaml"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class PackageInfo(BaseModel):
    """Package version and reason."""

    model_config = ConfigDict(extra="forbid")

    version: str
    reason: str


class LanguageDependencies(BaseModel):
    """Runtime and dev dependencies for a language."""

    model_config = ConfigDict(extra="forbid")

    runtime: Dict[str, PackageInfo]
    dev: Dict[str, PackageInfo]


class DependencyRule(BaseModel):
    """Dependency restriction rule."""

    model_config = ConfigDict(extra="forbid")

    layer: str
    dependency: str
    reason: str


class DependencyRules(BaseModel):
    """Rules section wrapper."""

    model_config = ConfigDict(extra="forbid")

    forbid: Optional[List[DependencyRule]] = None
    permit: Optional[List[DependencyRule]] = None


class DependenciesYAML(BaseModel):
    """Root model for dependencies.yaml - matches YAML structure exactly."""

    model_config = ConfigDict(extra="forbid")

    dependencies: Dict[str, LanguageDependencies]
    rules: Optional[DependencyRules] = None
    notes: Optional[List[str]] = None
