"""Domain models matching exact YAML structure for api.yaml"""

from typing import Dict, List, Optional

from pydantic import BaseModel


class ApiExport(BaseModel):
    """API export definition."""

    location: str
    exports: List[str]
    stability: Optional[str] = None
    warning: Optional[str] = None


class ApiRule(BaseModel):
    """API restriction rule."""

    path: str
    api: str
    reason: str
    exceptions: Optional[Dict[str, str]] = None


class ApiRules(BaseModel):
    """Rules section wrapper."""

    forbid: List[ApiRule]


class ApiSection(BaseModel):
    """API section (public or internal)."""

    public: Optional[Dict[str, ApiExport]] = None
    internal: Optional[Dict[str, ApiExport]] = None


class ApiYAML(BaseModel):
    """Root model for api.yaml - matches YAML structure exactly."""

    api: ApiSection
    rules: Optional[ApiRules] = None
    notes: Optional[List[str]] = None
