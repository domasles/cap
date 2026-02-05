"""Domain models matching exact YAML structure for architecture.yaml"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class ArchitectureStyle(BaseModel):
    """Architecture style definition."""

    style: str


class Layer(BaseModel):
    """Layer definition."""

    owns: str
    may_import: List[str]


class Module(BaseModel):
    """Module definition."""

    owns: str
    purpose: str
    owner: Optional[str] = None
    forbidden_imports: Optional[List[str]] = None


class ArchitectureRule(BaseModel):
    """Architecture restriction rule."""

    path: str
    calls: str
    reason: str


class ArchitectureRules(BaseModel):
    """Rules section wrapper."""

    forbid: List[ArchitectureRule]


class ArchitectureYAML(BaseModel):
    """Root model for architecture.yaml - matches YAML structure exactly."""

    architecture: ArchitectureStyle
    layers: Optional[Dict[str, Layer]] = None
    modules: Optional[Dict[str, Module]] = None
    rules: Optional[ArchitectureRules] = None
    notes: Optional[List[str]] = None
