from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import json
import uuid


@dataclass
class PatchRecord:
    id: str
    title: str
    description: str
    status: str  # suggested | applied
    metadata: Dict[str, Any]
    created_at: str
    applied_at: Optional[str]


class PatchManager:
    """Simple file-backed patch manager for governance/autopatch artifacts.

    Stores one JSON file per patch under `root/patches`.
    """

    def __init__(self, root: Union[str, Path]) -> None:
        self.root = Path(root)
        self.dir = self.root / "patches"
        self.dir.mkdir(parents=True, exist_ok=True)

    def suggest_patch(self, title: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> PatchRecord:
        metadata = metadata or {}
        pid = uuid.uuid4().hex
        rec = PatchRecord(
            id=pid,
            title=title,
            description=description,
            status="suggested",
            metadata=metadata,
            created_at=datetime.utcnow().isoformat() + "Z",
            applied_at=None,
        )
        path = self.dir / f"{pid}.json"
        with path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(rec), ensure_ascii=False))
        return rec

    def list_patches(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for p in sorted(self.dir.glob("*.json")):
            try:
                with p.open("r", encoding="utf-8") as fh:
                    out.append(json.loads(fh.read()))
            except Exception:
                continue
        return out

    def apply_patch(self, patch_id: str) -> Optional[PatchRecord]:
        path = self.dir / f"{patch_id}.json"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            data = json.loads(fh.read())
        data["status"] = "applied"
        data["applied_at"] = datetime.utcnow().isoformat() + "Z"
        with path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, ensure_ascii=False))
        return PatchRecord(**data)
