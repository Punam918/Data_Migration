from pathlib import Path
from typing import Optional

import pandas as pd

from migration_platform.pipelines.checkpointing import JsonCheckpointStore
from migration_platform.pipelines.ingestion import IngestionPipeline


class FakeConnector:
    cursor_column = "event_id"

    def __init__(self) -> None:
        self.calls = []

    def fetch_batch(self, cursor: Optional[str], limit: int) -> pd.DataFrame:
        self.calls.append((cursor, limit))
        if cursor is None:
            return pd.DataFrame(
                {
                    "event_id": [1, 2, 3],
                    "value": [10, 20, 30],
                }
            )
        if cursor == "3":
            return pd.DataFrame(
                {
                    "event_id": [4, 5],
                    "value": [40, 50],
                }
            )
        return pd.DataFrame(columns=["event_id", "value"])


def test_incremental_ingestion_advances_checkpoint(tmp_path: Path) -> None:
    bronze_root = tmp_path / "bronze"
    checkpoints = JsonCheckpointStore(tmp_path / "checkpoints")
    pipeline = IngestionPipeline(bronze_root)
    connector = FakeConnector()

    first = pipeline.ingest_incremental("orders", connector, checkpoints, batch_size=100)
    second = pipeline.ingest_incremental("orders", connector, checkpoints, batch_size=100)

    assert first.status == "ingested"
    assert first.row_count == 3
    assert first.cursor_start is None
    assert first.cursor_end == "3"

    assert second.status == "ingested"
    assert second.row_count == 2
    assert second.cursor_start == "3"
    assert second.cursor_end == "5"

    saved = checkpoints.load("orders")
    assert saved is not None
    assert saved.last_cursor == "5"
    assert saved.row_count == 2


def test_ingestion_idempotent_reuse_for_same_run_id(tmp_path: Path) -> None:
    bronze_root = tmp_path / "bronze"
    checkpoints = JsonCheckpointStore(tmp_path / "checkpoints")
    pipeline = IngestionPipeline(bronze_root)
    connector = FakeConnector()

    run_id = "fixedrun1"
    first = pipeline.ingest_incremental(
        "orders", connector, checkpoints, batch_size=100, run_id=run_id
    )
    second = pipeline.ingest_incremental(
        "orders", connector, checkpoints, batch_size=100, run_id=run_id
    )

    assert first.status == "ingested"
    assert second.status == "idempotent_reuse"
    assert len(connector.calls) == 1


def test_ingestion_no_data_keeps_checkpoint(tmp_path: Path) -> None:
    bronze_root = tmp_path / "bronze"
    checkpoints = JsonCheckpointStore(tmp_path / "checkpoints")
    pipeline = IngestionPipeline(bronze_root)
    connector = FakeConnector()

    pipeline.ingest_incremental("orders", connector, checkpoints, batch_size=100)
    pipeline.ingest_incremental("orders", connector, checkpoints, batch_size=100)
    no_data = pipeline.ingest_incremental("orders", connector, checkpoints, batch_size=100)

    assert no_data.status == "no_data"
    assert no_data.row_count == 0

    saved = checkpoints.load("orders")
    assert saved is not None
    assert saved.last_cursor == "5"
