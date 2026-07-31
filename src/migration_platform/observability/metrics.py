from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


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

    def __init__(self, root: Union[str, Path]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "metrics.jsonl"

    def emit(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        tags = tags or {}
        ts = datetime.utcnow().isoformat() + "Z"
        record = Metric(name=name, value=float(value), tags=tags, ts=ts)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(record)) + "\n")

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
