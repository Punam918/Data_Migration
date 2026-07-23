from __future__ import annotations

import pandas as pd

from migration_platform.metadata.mapping_loader import MappingSpec


class TransformationPipeline:
    """Applies declarative mapping from source columns to target columns."""

    def transform(self, frame: pd.DataFrame, mapping: MappingSpec) -> pd.DataFrame:
        reverse = {src: tgt for src, tgt in mapping.column_mappings.items()}
        missing = [src for src in reverse if src not in frame.columns]
        if missing:
            joined = ", ".join(sorted(missing))
            raise ValueError(f"Source data missing mapped columns: {joined}")

        selected = frame[list(reverse.keys())].rename(columns=reverse)
        return selected
