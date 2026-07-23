from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ColumnDefinition(BaseModel):
    name: str
    dtype: str
    nullable: bool = True


class TableSchema(BaseModel):
    system: str
    table: str
    version: int = 1
    columns: List[ColumnDefinition] = Field(default_factory=list)


class SchemaRegistry:
    """Stores versioned table schemas as JSON files."""

    def __init__(self, registry_root: Union[str, Path]) -> None:
        self.registry_root = Path(registry_root)
        self.registry_root.mkdir(parents=True, exist_ok=True)

    def _schema_path(self, system: str, table: str, version: int) -> Path:
        safe_table = table.replace(".", "_").replace("/", "_")
        return self.registry_root / f"{system}__{safe_table}__v{version}.json"

    def register(self, schema: TableSchema) -> Path:
        path = self._schema_path(schema.system, schema.table, schema.version)
        path.write_text(schema.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, system: str, table: str, version: int) -> TableSchema:
        path = self._schema_path(system, table, version)
        payload = path.read_text(encoding="utf-8")
        return TableSchema.model_validate_json(payload)

    def latest_version(self, system: str, table: str) -> Optional[int]:
        prefix = f"{system}__{table.replace('.', '_')}__v"
        versions: list[int] = []
        for item in self.registry_root.glob(f"{prefix}*.json"):
            tail = item.stem.split("__v")[-1]
            if tail.isdigit():
                versions.append(int(tail))
        return max(versions) if versions else None


def schema_diff(old: TableSchema, new: TableSchema) -> Dict[str, Any]:
    old_cols = {c.name: c for c in old.columns}
    new_cols = {c.name: c for c in new.columns}

    added = [name for name in new_cols if name not in old_cols]
    removed = [name for name in old_cols if name not in new_cols]

    type_changes: List[Dict[str, str]] = []
    for name in new_cols.keys() & old_cols.keys():
        old_t = old_cols[name].dtype
        new_t = new_cols[name].dtype
        if old_t != new_t:
            type_changes.append({"column": name, "from": old_t, "to": new_t})

    return {"added": sorted(added), "removed": sorted(removed), "type_changes": type_changes}
