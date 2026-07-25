from __future__ import annotations

import hashlib
from typing import List, Tuple

import pandas as pd


def table_row_count(df: pd.DataFrame) -> int:
    return int(len(df))


def table_checksum_on_keys(df: pd.DataFrame, keys: List[str]) -> str:
    # Compute a deterministic checksum by hashing concatenated key values per row
    if not keys:
        raise ValueError("No keys provided for checksum")
    parts: List[str] = []
    for _, row in df[keys].iterrows():
        vals = ["" if pd.isna(v) else str(v) for v in row.tolist()]
        parts.append("|".join(vals))
    joined = "\n".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def reconcile_counts(source: pd.DataFrame, target: pd.DataFrame) -> Tuple[int, int, int]:
    s = table_row_count(source)
    t = table_row_count(target)
    diff = s - t
    return s, t, diff


def reconcile_keys_checksum(
    source: pd.DataFrame, target: pd.DataFrame, keys: List[str]
) -> Tuple[str, str, bool]:
    s_hash = table_checksum_on_keys(source, keys)
    t_hash = table_checksum_on_keys(target, keys)
    return s_hash, t_hash, s_hash == t_hash
