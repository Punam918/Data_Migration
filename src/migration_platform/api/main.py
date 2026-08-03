from __future__ import annotations

from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from migration_platform.governance.api import router as governance_router
from migration_platform.observability.api import router as observability_router

ROOT = Path(__file__).resolve().parents[2]
UI_PATH = ROOT / "src" / "migration_platform" / "governance" / "ui_template.html"


app = FastAPI(title="Migration Intelligence API", version="0.1.0")

# Allow local UI or tests to call the API from browsers during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(observability_router)
app.include_router(governance_router)


@app.on_event("startup")
def ensure_dirs() -> None:
    # Ensure runtime directories exist for observability and governance
    (Path("./var/observability")).mkdir(parents=True, exist_ok=True)
    (Path("./var/governance")).mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "Self-Healing Migration Intelligence Platform"}


@app.get("/governance/ui", include_in_schema=False)
def governance_ui() -> FileResponse:
    """Serve the governance patch-review UI template for quick access during development."""
    if UI_PATH.exists():
        return FileResponse(UI_PATH)
    return FileResponse(str(UI_PATH))
