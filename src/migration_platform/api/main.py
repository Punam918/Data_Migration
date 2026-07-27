from __future__ import annotations

from fastapi import FastAPI
from migration_platform.observability.api import router as observability_router
from migration_platform.governance.api import router as governance_router

app = FastAPI(title="Migration Intelligence API", version="0.1.0")
app.include_router(observability_router)
app.include_router(governance_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Self-Healing Migration Intelligence Platform"}
