from fastapi.testclient import TestClient

from migration_platform.api.main import app
from migration_platform.governance.patcher import PatchManager


def test_governance_ui_and_patch_flow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    mgr = PatchManager(tmp_path / "var" / "governance")
    first = mgr.suggest_patch(
        "unique-constraint-users-id",
        "Add a uniqueness guard for users.id",
        metadata={"type": "unique_constraint", "columns": ["id"]},
    )
    second = mgr.suggest_patch(
        "not-null-orders-email",
        "Enforce not null on orders.email",
        metadata={"type": "not_null", "column": "email"},
    )

    client = TestClient(app)

    ui_response = client.get("/governance/ui")
    assert ui_response.status_code == 200
    assert "Patch Review Desk" in ui_response.text
    assert "/governance/patches" in ui_response.text
    assert "search title, description, metadata, or patch id" in ui_response.text.lower()
    assert "Suggested" in ui_response.text
    assert "Applied" in ui_response.text
    assert "Patch preview" in ui_response.text
    assert "Confirm patch application" in ui_response.text
    assert "View details" in ui_response.text

    list_response = client.get("/governance/patches")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert any(item["id"] == first.id for item in payload)
    assert any(item["id"] == second.id for item in payload)

    filtered_response = client.get("/governance/patches", params={"q": "orders", "status": "suggested"})
    assert filtered_response.status_code == 200
    filtered_payload = filtered_response.json()
    assert len(filtered_payload) == 1
    assert filtered_payload[0]["id"] == second.id

    apply_response = client.post(f"/governance/patches/{first.id}/apply")
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert applied["status"] == "applied"
