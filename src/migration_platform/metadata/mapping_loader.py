from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field


class EndpointSpec(BaseModel):
    system: Optional[str] = None
    table: str
    layer: Optional[str] = None


class MappingSpec(BaseModel):
    mapping_name: str
    source: EndpointSpec
    target: EndpointSpec
    column_mappings: Dict[str, str] = Field(default_factory=dict)
    required_columns: List[str] = Field(default_factory=list)
    primary_key: List[str] = Field(default_factory=list)


def load_mapping(path: Union[str, Path]) -> MappingSpec:
    mapping_path = Path(path)
    with mapping_path.open("r", encoding="utf-8") as fh:
        payload: Dict[str, Any] = yaml.safe_load(fh) or {}
    spec = MappingSpec.model_validate(payload)
    _validate_mapping(spec)
    return spec


def _validate_mapping(spec: MappingSpec) -> None:
    missing_required = [c for c in spec.required_columns if c not in spec.column_mappings]
    if missing_required:
        joined = ", ".join(sorted(missing_required))
        raise ValueError(f"Required columns missing from column_mappings: {joined}")

    if spec.primary_key:
        missing_pk = [c for c in spec.primary_key if c not in spec.column_mappings]
        if missing_pk:
            joined = ", ".join(sorted(missing_pk))
            raise ValueError(f"Primary key columns missing from column_mappings: {joined}")
