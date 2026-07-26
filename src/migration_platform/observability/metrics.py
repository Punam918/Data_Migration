from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import json


@dataclass
class Metric:
    name: str
    value: float
    tags: Dict[str, str]
    ts: str


class MetricEmitter:
    """Simple file-backed metric emitter for local development/testing.

    Emits newline-delimited JSON metric records to `root/metrics.jsonl`.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "metrics.jsonl"

    def emit(self, name: str, value: float, tags: Dict[str, str] | None = None) -> None:
        tags = tags or {}
        record = Metric(name=name, value=float(value), tags=tags, ts=datetime.utcnow().isoformat() + "Z")
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(record)) + "\n")

    def tail(self, n: int = 100) -> list[Dict[str, Any]]:
        if not self.path.exists():
            return []
        out: list[Dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()[-n:]
            for L in lines:
                try:
                    out.append(json.loads(L))
                except Exception:
                    continue
        return out
