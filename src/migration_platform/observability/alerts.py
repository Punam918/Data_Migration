from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import json


@dataclass
class Alert:
    name: str
    severity: str
    message: str
    metadata: Dict[str, Any]
    ts: str


class AlertManager:
    """Simple alert manager that writes alerts to `root/alerts.jsonl`."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "alerts.jsonl"

    def create_alert(self, name: str, severity: str, message: str, metadata: Dict[str, Any] | None = None) -> None:
        meta = metadata or {}
        alert = Alert(name=name, severity=severity, message=message, metadata=meta, ts=datetime.utcnow().isoformat() + "Z")
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(alert)) + "\n")

    def tail(self, n: int = 100) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        out: List[Dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()[-n:]
            for L in lines:
                try:
                    out.append(json.loads(L))
                except Exception:
                    continue
        return out
