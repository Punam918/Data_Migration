from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd


def cast_columns(frame: pd.DataFrame, casts: Dict[str, str], strict: bool = True) -> pd.DataFrame:
    df = frame.copy()
    for col, dtype in casts.items():
        if col not in df.columns:
            if strict:
                raise KeyError(f"Missing column for cast: {col}")
            else:
                df[col] = None
                continue
        try:
            df[col] = df[col].astype(dtype)
        except Exception as exc:
            if strict:
                raise
            else:
                df[col] = df[col].astype(object)
    return df


def apply_defaults(frame: pd.DataFrame, defaults: Dict[str, Any]) -> pd.DataFrame:
    df = frame.copy()
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val
        else:
            df[col] = df[col].fillna(val)
    return df


def normalize_strings(frame: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    df = frame.copy()
    cols = columns or df.select_dtypes(include=[object]).columns.tolist()
    for c in cols:
        df[c] = df[c].astype(str).str.strip()
    return df


def derive_columns(frame: pd.DataFrame, derives: Dict[str, Any]) -> pd.DataFrame:
    df = frame.copy()
    for col, expr in derives.items():
        # expr is a callable that accepts df and returns a Series
        if callable(expr):
            df[col] = expr(df)
        else:
            df[col] = expr
    return df
