from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from .patcher import PatchManager

router = APIRouter()


def _template_path() -> Path:
    return Path(__file__).with_name("ui_template.html")


def _render_ui() -> str:
    return _template_path().read_text(encoding="utf-8")


@router.get("/governance/ui", response_class=HTMLResponse)
def governance_ui() -> HTMLResponse:
    return HTMLResponse(_render_ui())


@router.get("/governance/patches")
def list_patches(limit: int = 100, q: Optional[str] = None, status: Optional[str] = None):
    root = Path("./var/governance")
    mgr = PatchManager(root)
    patches = mgr.list_patches()
    if q:
        query = q.lower()
        patches = [
            patch
            for patch in patches
            if query in str(patch.get("id", "")).lower()
            or query in str(patch.get("title", "")).lower()
            or query in str(patch.get("description", "")).lower()
            or query in str(patch.get("status", "")).lower()
            or query in str(patch.get("metadata", "")).lower()
        ]
    if status and status != "all":
        patches = [patch for patch in patches if patch.get("status") == status]
    return patches[:limit]


@router.post("/governance/patches/{patch_id}/apply")
def apply_patch(patch_id: str):
    root = Path("./var/governance")
    mgr = PatchManager(root)
    rec = mgr.apply_patch(patch_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="patch not found")
    return rec
