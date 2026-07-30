from fastapi.testclient import TestClient

from migration_platform.api.main import app
from migration_platform.governance.patcher import PatchManager


def test_governance_ui_and_patch_flow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    mgr = PatchManager(tmp_path / "var" / "governance")
    rec = mgr.suggest_patch(
        "unique-constraint-users-id",
        "Add a uniqueness guard for users.id",
        metadata={"type": "unique_constraint", "columns": ["id"]},
    )

    client = TestClient(app)

    ui_response = client.get("/governance/ui")
    assert ui_response.status_code == 200
    assert "Patch Review Desk" in ui_response.text
    assert "/governance/patches" in ui_response.text

    list_response = client.get("/governance/patches")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert any(item["id"] == rec.id for item in payload)

    apply_response = client.post(f"/governance/patches/{rec.id}/apply")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["status"] == "applied"
