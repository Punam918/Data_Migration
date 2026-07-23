from __future__ import annotations

from pathlib import Path
from typing import Union

import yaml
from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    bronze_path: str = "artifacts/bronze"
    silver_path: str = "artifacts/silver"
    gold_path: str = "artifacts/gold"


class QualityConfig(BaseModel):
    max_null_rate_default: float = 0.05
    min_row_count_default: int = 1


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class AppConfig(BaseModel):
    environment: str = Field(default="dev")
    storage: StorageConfig = Field(default_factory=StorageConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)


def load_config(path: Union[str, Path]) -> AppConfig:
    file_path = Path(path)
    data: dict = {}
    if file_path.exists():
        with file_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    return AppConfig.model_validate(data)
