from pathlib import Path

from migration_platform.governance.patcher import PatchManager


def test_patch_manager(tmp_path):
    root = tmp_path / "var"
    mgr = PatchManager(root)

    rec = mgr.suggest_patch("add-not-null", "Add NOT NULL on column id", metadata={"table": "users", "column": "id"})
    assert rec.id is not None
    listed = mgr.list_patches()
    assert any(p["id"] == rec.id for p in listed)

    applied = mgr.apply_patch(rec.id)
    assert applied is not None
    assert applied.status == "applied"
    assert applied.applied_at is not None
