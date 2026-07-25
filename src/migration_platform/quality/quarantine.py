from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


class QuarantineWriter:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, dataset: str, frame: pd.DataFrame, reason: str, run_id: Optional[str] = None) -> Path:
        ds_dir = self.root / dataset
        ds_dir.mkdir(parents=True, exist_ok=True)
        rid = run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out = ds_dir / f"quarantine_{rid}.csv"
        meta = ds_dir / f"quarantine_{rid}.meta.txt"
        frame.to_csv(out, index=False)
        meta.write_text(f"reason={reason}\nrows={len(frame)}\n", encoding="utf-8")
        return out
