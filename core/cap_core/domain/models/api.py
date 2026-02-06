"""Domain models matching exact YAML structure for api.yaml"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ApiExport(BaseModel):
    """API export definition."""

    model_config = ConfigDict(extra="forbid")

    location: str
    exports: List[str]
    stability: str
    warning: Optional[str] = None


class ApiRule(BaseModel):
    """API restriction rule."""

    model_config = ConfigDict(extra="forbid")

    path: str
    api: str
    reason: str
    exceptions: Optional[Dict[str, str]] = None


class ApiRules(BaseModel):
    """Rules section wrapper."""

    model_config = ConfigDict(extra="forbid")

    forbid: Optional[List[ApiRule]] = None
    permit: Optional[List[ApiRule]] = None


class ApiSection(BaseModel):
    """API section (public or internal)."""

    model_config = ConfigDict(extra="forbid")

    public: Dict[str, ApiExport]
    internal: Optional[Dict[str, ApiExport]] = None


class ApiYAML(BaseModel):
    """Root model for api.yaml - matches YAML structure exactly."""

    model_config = ConfigDict(extra="forbid")

    api: ApiSection
    rules: Optional[ApiRules] = None
    notes: Optional[List[str]] = None
