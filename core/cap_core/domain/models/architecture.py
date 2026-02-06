"""Domain models matching exact YAML structure for architecture.yaml"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ArchitectureStyle(BaseModel):
    """Architecture style definition."""

    model_config = ConfigDict(extra="forbid")

    style: str


class Layer(BaseModel):
    """Layer definition."""

    model_config = ConfigDict(extra="forbid")

    owns: str
    may_import: List[str]


class Module(BaseModel):
    """Module definition."""

    model_config = ConfigDict(extra="forbid")

    owns: str
    purpose: str
    owner: Optional[str] = None
    forbidden_imports: Optional[List[str]] = None


class ArchitectureRule(BaseModel):
    """Architecture restriction rule."""

    model_config = ConfigDict(extra="forbid")

    path: str
    calls: str
    reason: str


class ArchitectureRules(BaseModel):
    """Rules section wrapper."""

    model_config = ConfigDict(extra="forbid")

    forbid: Optional[List[ArchitectureRule]] = None
    permit: Optional[List[ArchitectureRule]] = None


class ArchitectureYAML(BaseModel):
    """Root model for architecture.yaml - matches YAML structure exactly."""

    model_config = ConfigDict(extra="forbid")

    architecture: ArchitectureStyle
    layers: Dict[str, Layer]
    modules: Dict[str, Module]
    rules: Optional[ArchitectureRules] = None
    notes: Optional[List[str]] = None
