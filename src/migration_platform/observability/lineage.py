from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import json


@dataclass
class LineageEntry:
    dataset: str
    operation: str
    inputs: List[str]
    outputs: List[str]
    metadata: Dict[str, Any]
    ts: str


class LineageStore:
    """Simple file-backed lineage store.

    Stores JSON lines in `root/lineage.jsonl`.
    """

    def __init__(self, root: Union[str, Path]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "lineage.jsonl"

    def add(self, dataset: str, operation: str, inputs: List[str], outputs: List[str], metadata: Optional[Dict[str, Any]] = None) -> None:
        meta = metadata or {}
        ts = datetime.utcnow().isoformat() + "Z"
        entry = LineageEntry(
            dataset=dataset,
            operation=operation,
            inputs=inputs,
            outputs=outputs,
            metadata=meta,
            ts=ts,
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(entry)) + "\n")

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
