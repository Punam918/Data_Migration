from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Any

from .patcher import PatchManager

router = APIRouter()

@router.get("/governance/patches")
def list_patches(limit: int = 100):
    root = Path("./var/governance")
    mgr = PatchManager(root)
    return mgr.list_patches()[:limit]


@router.post("/governance/patches/{patch_id}/apply")
def apply_patch(patch_id: str):
    root = Path("./var/governance")
    mgr = PatchManager(root)
    rec = mgr.apply_patch(patch_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="patch not found")
    return rec
