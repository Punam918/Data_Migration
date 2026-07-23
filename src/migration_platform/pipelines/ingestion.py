from __future__ import annotations

from pathlib import Path
from typing import Callable, Union

import pandas as pd


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
