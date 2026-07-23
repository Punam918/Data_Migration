from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Callable, Optional, Union
from uuid import uuid4

import pandas as pd

from migration_platform.pipelines.checkpointing import JsonCheckpointStore
from migration_platform.pipelines.connectors import SourceConnector


@dataclass
class IngestionResult:
    dataset_name: str
    status: str
    row_count: int
    run_id: Optional[str]
    snapshot_path: Optional[str]
    manifest_path: Optional[str]
    cursor_start: Optional[str]
    cursor_end: Optional[str]


class IngestionPipeline:
    """Extracts from source and writes immutable raw snapshots to bronze."""

    def __init__(self, bronze_root: Union[str, Path]) -> None:
        self.bronze_root = Path(bronze_root)
        self.bronze_root.mkdir(parents=True, exist_ok=True)

    def ingest(self, dataset_name: str, extractor: Callable[[], pd.DataFrame]) -> Path:
        frame = extractor()
        if frame.empty:
            raise ValueError("Extractor returned empty dataset")

        output_dir = self.bronze_root / dataset_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "snapshot.csv"
        frame.to_csv(output_path, index=False)
        return output_path

    def ingest_incremental(
        self,
        dataset_name: str,
        connector: SourceConnector,
        checkpoint_store: JsonCheckpointStore,
        batch_size: int = 10000,
        run_id: Optional[str] = None,
        deduplicate_on: Optional[list[str]] = None,
    ) -> IngestionResult:
        dataset_dir = self.bronze_root / dataset_name
        dataset_dir.mkdir(parents=True, exist_ok=True)

        actual_run_id = run_id or self._new_run_id()
        snapshot_path = dataset_dir / "snapshot_{0}.csv".format(actual_run_id)
        manifest_path = dataset_dir / "manifest_{0}.json".format(actual_run_id)

        # Idempotent retry: if manifest exists for run_id, return it as-is.
        if manifest_path.exists():
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            return IngestionResult(
                dataset_name=dataset_name,
                status="idempotent_reuse",
                row_count=int(payload.get("row_count", 0)),
                run_id=actual_run_id,
                snapshot_path=str(snapshot_path),
                manifest_path=str(manifest_path),
                cursor_start=payload.get("cursor_start"),
                cursor_end=payload.get("cursor_end"),
            )

        checkpoint = checkpoint_store.load(dataset_name)
        cursor_start = checkpoint.last_cursor if checkpoint else None

        frame = connector.fetch_batch(cursor=cursor_start, limit=batch_size)
        if frame.empty:
            return IngestionResult(
                dataset_name=dataset_name,
                status="no_data",
                row_count=0,
                run_id=None,
                snapshot_path=None,
                manifest_path=None,
                cursor_start=cursor_start,
                cursor_end=cursor_start,
            )

        if deduplicate_on:
            frame = frame.drop_duplicates(subset=deduplicate_on, keep="last")

        frame.to_csv(snapshot_path, index=False)
        if connector.cursor_column not in frame.columns:
            raise ValueError(
                "Cursor column '{0}' is not present in fetched batch".format(
                    connector.cursor_column
                )
            )
        cursor_end = str(frame.iloc[-1][connector.cursor_column])

        checksum = self._file_sha256(snapshot_path)
        manifest = {
            "dataset_name": dataset_name,
            "run_id": actual_run_id,
            "created_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "row_count": int(len(frame)),
            "columns": list(frame.columns),
            "cursor_start": cursor_start,
            "cursor_end": cursor_end,
            "snapshot_path": str(snapshot_path),
            "sha256": checksum,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        checkpoint_store.update(
            dataset_name=dataset_name,
            last_cursor=cursor_end,
            last_snapshot_path=str(snapshot_path),
            row_count=int(len(frame)),
        )

        return IngestionResult(
            dataset_name=dataset_name,
            status="ingested",
            row_count=int(len(frame)),
            run_id=actual_run_id,
            snapshot_path=str(snapshot_path),
            manifest_path=str(manifest_path),
            cursor_start=cursor_start,
            cursor_end=cursor_end,
        )

    def _new_run_id(self) -> str:
        now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        return "{0}_{1}".format(now, uuid4().hex[:8])

    def _file_sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()
