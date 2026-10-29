import pytest
from conftest import create
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from src.main import create_app
from src.state.models import Campaign
from src.agentic.workflow import TRANSITIONS


def test_state_survives_restart(settings, client, manager, approver):
    w = create(client, manager)
    new_app = create_app(settings)
    with TestClient(new_app) as restarted:
        loaded = restarted.get(f"/agentic/workflows/{w['workflow_id']}", headers=manager).json()
        assert loaded["payload_hash"] == w["payload_hash"]
        assert (
            restarted.post(
                f"/agentic/workflows/{w['workflow_id']}/approval",
                headers=approver,
                json={"payload_hash": w["payload_hash"]},
            ).json()["status"]
            == "COMPLETED"
        )


def test_idempotent_request_and_conflict(client, app, manager):
    first = create(client, manager)
    second = create(client, manager)
    assert first["workflow_id"] == second["workflow_id"]
    assert (
        client.post(
            "/agentic/requests",
            headers=manager,
            json={"message": "different message", "idempotency_key": "test-request-001"},
        ).status_code
        == 409
    )
    with app.state.repo.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Campaign)) == 1


def test_failure_bounded_retries_and_recovery(client, app, manager):
    app.state.gateway.failures["get_customer_profile"] = 3
    w = create(client, manager)
    assert w["status"] == "FAILED"
    path = f"/agentic/workflows/{w['workflow_id']}"
    events = client.get(path + "/events", headers=manager).json()
    assert len([e for e in events if e["outcome"] == "timeout"]) == 3
    retried = client.post(path + "/retry", headers=manager).json()
    assert retried["status"] == "PENDING_APPROVAL"
    with app.state.repo.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Campaign)) == 1


@pytest.mark.parametrize("action,expected", [("cancel", "CANCELLED"), ("reject", "REJECTED")])
def test_terminal_states(client, manager, approver, action, expected):
    w = create(client, manager)
    base = f"/agentic/workflows/{w['workflow_id']}"
    response = (
        client.post(base + "/cancel", headers=manager)
        if action == "cancel"
        else client.post(
            base + "/approval",
            headers=approver,
            json={"payload_hash": w["payload_hash"], "decision": "reject"},
        )
    )
    assert response.json()["status"] == expected
    assert client.post(base + "/retry", headers=manager).status_code == 409
    assert TRANSITIONS[expected] == set()


def test_retry_budget(client, app, manager):
    app.state.gateway.failures["get_customer_profile"] = 100
    w = create(client, manager)
    path = f"/agentic/workflows/{w['workflow_id']}/retry"
    assert client.post(path, headers=manager).json()["status"] == "FAILED"
    assert client.post(path, headers=manager).json()["status"] == "FAILED"
    assert client.post(path, headers=manager).status_code == 409


def test_concurrent_duplicate_requests(client, app, manager):
    from concurrent.futures import ThreadPoolExecutor

    def submit(_):
        return create(client, manager)

    with ThreadPoolExecutor(max_workers=4) as workers:
        results = list(workers.map(submit, range(4)))
    assert len({w["workflow_id"] for w in results}) == 1
    assert all(w["status"] in {"CREATED", "PENDING_APPROVAL"} for w in results)
    with app.state.repo.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Campaign)) == 1
