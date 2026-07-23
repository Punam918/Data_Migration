from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Optional, Union


@dataclass
class IngestionCheckpoint:
    dataset_name: str
    last_cursor: Optional[str]
    last_snapshot_path: Optional[str]
    row_count: int
    updated_at_utc: str


class JsonCheckpointStore:
    """Persists per-dataset ingestion checkpoints as JSON files."""

    def __init__(self, root: Union[str, Path]) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, dataset_name: str) -> Path:
        safe_name = dataset_name.replace("/", "_").replace("\\", "_")
        return self.root / "{0}.json".format(safe_name)

    def load(self, dataset_name: str) -> Optional[IngestionCheckpoint]:
        path = self._path_for(dataset_name)
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        return IngestionCheckpoint(**payload)

    def save(self, checkpoint: IngestionCheckpoint) -> Path:
        path = self._path_for(checkpoint.dataset_name)
        path.write_text(json.dumps(asdict(checkpoint), indent=2), encoding="utf-8")
        return path

    def update(
        self,
        dataset_name: str,
        last_cursor: Optional[str],
        last_snapshot_path: Optional[str],
        row_count: int,
    ) -> IngestionCheckpoint:
        checkpoint = IngestionCheckpoint(
            dataset_name=dataset_name,
            last_cursor=last_cursor,
            last_snapshot_path=last_snapshot_path,
            row_count=row_count,
            updated_at_utc=datetime.utcnow().isoformat(timespec="seconds") + "Z",
        )
        self.save(checkpoint)
        return checkpoint


def checkpoint_to_dict(checkpoint: Optional[IngestionCheckpoint]) -> Dict[str, Optional[str]]:
    if checkpoint is None:
        return {
            "dataset_name": None,
            "last_cursor": None,
            "last_snapshot_path": None,
            "row_count": None,
            "updated_at_utc": None,
        }

    return {
        "dataset_name": checkpoint.dataset_name,
        "last_cursor": checkpoint.last_cursor,
        "last_snapshot_path": checkpoint.last_snapshot_path,
        "row_count": str(checkpoint.row_count),
        "updated_at_utc": checkpoint.updated_at_utc,
    }
