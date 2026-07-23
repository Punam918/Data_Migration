from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyScore:
    row_index: int
    score: float
    is_anomaly: bool


class TableAnomalyDetector:
    """Simple baseline anomaly detector over numeric columns."""

    def __init__(self, contamination: float = 0.05, random_state: int = 42) -> None:
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self._fitted = False

    def fit(self, frame: pd.DataFrame) -> None:
        features = _numeric_matrix(frame)
        self.model.fit(features)
        self._fitted = True

    def score(self, frame: pd.DataFrame) -> list[AnomalyScore]:
        if not self._fitted:
            raise RuntimeError("Model not fitted")
        features = _numeric_matrix(frame)
        raw_scores = self.model.score_samples(features)
        flags = self.model.predict(features)

        results: list[AnomalyScore] = []
        for i, (score, flag) in enumerate(zip(raw_scores, flags)):
            results.append(AnomalyScore(row_index=i, score=float(score), is_anomaly=(flag == -1)))
        return results


def _numeric_matrix(frame: pd.DataFrame) -> np.ndarray:
    numeric = frame.select_dtypes(include=["number"]).fillna(0)
    if numeric.empty:
        raise ValueError("No numeric columns available for anomaly detection")
    return numeric.to_numpy()
