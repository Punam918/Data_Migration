
from migration_platform.governance.patcher import PatchManager
from scripts.patch_review import main


def test_cli_list_and_apply(tmp_path, capsys):
    root = tmp_path / "var" / "governance"
    mgr = PatchManager(root)
    rec = mgr.suggest_patch("t1", "desc", metadata={"type": "test"})

    # list
    rc = main(["--root", str(root), "--list"])
    assert rc == 0

    # apply without auto-confirm should prompt; use --yes
    rc2 = main(["--root", str(root), "--apply", rec.id, "--yes"])
    assert rc2 == 0

    # verify applied
    patches = mgr.list_patches()
    assert any(p.get("status") == "applied" for p in patches)
