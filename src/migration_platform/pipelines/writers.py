from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

import pandas as pd


def write_silver(
    frame: pd.DataFrame,
    root: Union[str, Path],
    dataset: str,
    partition_by: Optional[List[str]] = None,
) -> Path:
    root_path = Path(root)
    ds_dir = root_path / dataset / "silver"
    ds_dir.mkdir(parents=True, exist_ok=True)
    out_path = ds_dir / "data.csv"
    frame.to_csv(out_path, index=False)
    return out_path


def write_gold(
    frame: pd.DataFrame,
    root: Union[str, Path],
    dataset: str,
    partition_by: Optional[List[str]] = None,
) -> Path:
    root_path = Path(root)
    ds_dir = root_path / dataset / "gold"
    ds_dir.mkdir(parents=True, exist_ok=True)
    out_path = ds_dir / "data.csv"
    frame.to_csv(out_path, index=False)
    return out_path
