from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Any

from .metrics import MetricEmitter
from .lineage import LineageStore
from .alerts import AlertManager

router = APIRouter()

@router.get("/observability/metrics")
def get_metrics(limit: int = 100):
    root = Path("./var/observability")
    emitter = MetricEmitter(root)
    return emitter.tail(limit)


@router.get("/observability/lineage")
def get_lineage(limit: int = 100):
    root = Path("./var/observability")
    store = LineageStore(root)
    return store.tail(limit)


@router.get("/observability/alerts")
def get_alerts(limit: int = 100):
    root = Path("./var/observability")
    manager = AlertManager(root)
    return manager.tail(limit)
