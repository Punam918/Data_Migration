from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


class ContractViolation(Exception):
    pass


class ContractSpec:
    def __init__(
        self,
        required: Optional[List[str]] = None,
        unique_keys: Optional[List[str]] = None,
        dtypes: Optional[Dict[str, str]] = None,
    ) -> None:
        self.required = required or []
        self.unique_keys = unique_keys or []
        self.dtypes = dtypes or {}

    def validate(self, frame: pd.DataFrame) -> None:
        missing = [c for c in self.required if c not in frame.columns]
        if missing:
            raise ContractViolation(f"Missing required columns: {missing}")

        if self.unique_keys:
            if any(k not in frame.columns for k in self.unique_keys):
                raise ContractViolation(f"Primary key columns missing: {self.unique_keys}")
            duplicates = frame.duplicated(subset=self.unique_keys).sum()
            if duplicates > 0:
                raise ContractViolation(f"Duplicate primary keys detected: {duplicates} duplicates")

        # Basic dtype checking via astype attempt
        for col, dtype in self.dtypes.items():
            if col not in frame.columns:
                raise ContractViolation(f"Dtype column missing: {col}")
            try:
                frame[col].astype(dtype)
            except Exception as err:
                raise ContractViolation(
                    f"Column {col} cannot be cast to {dtype}"
                ) from err
