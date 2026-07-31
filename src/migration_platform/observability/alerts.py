from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class Alert:
    name: str
    severity: str
    message: str
    metadata: Dict[str, Any]
    ts: str


class AlertManager:
    """Simple alert manager that writes alerts to `root/alerts.jsonl`."""

    def __init__(self, root: Union[str, Path]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "alerts.jsonl"

    def create_alert(
        self,
        name: str,
        severity: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        meta = metadata or {}
        ts = datetime.utcnow().isoformat() + "Z"
        alert = Alert(name=name, severity=severity, message=message, metadata=meta, ts=ts)
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
