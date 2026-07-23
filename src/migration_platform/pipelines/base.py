from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class PipelineStep(ABC):
    name: str

    @abstractmethod
    def run(self, frame: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
