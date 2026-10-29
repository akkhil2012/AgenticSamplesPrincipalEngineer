from conftest import create
from sqlalchemy import select, func
from src.state.models import Campaign


def test_full_approval_workflow_and_activation_idempotency(client, app, manager, approver):
    w = create(client, manager)
    base = f"/agentic/workflows/{w['workflow_id']}"
    result = client.post(base + "/approval", headers=approver, json={"payload_hash": w["payload_hash"]})
    assert result.status_code == 200
    complete = result.json()
    assert complete["status"] == "COMPLETED", complete
    assert complete["outcome"]["simulation"] is True
    assert complete["outcome"]["customer_count"] == 2
    for _ in range(3):
        repeated = client.post(base + "/execute", headers=approver).json()
        assert repeated["outcome"] == complete["outcome"]
    with app.state.repo.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Campaign)) == 1
        assert session.scalar(select(Campaign)).status == "SIMULATED_ACTIVE"
    events = client.get(base + "/events", headers=manager).json()
    assert (
        len([e for e in events if e["tool"] == "activate_campaign_simulated" and e["outcome"] == "success"])
        == 1
    )
    for event in events:
        assert {
            "actor",
            "tenant",
            "agent",
            "tool",
            "decision",
            "timestamp",
            "workflow_id",
            "outcome",
        } <= event.keys()


def test_activation_timeout_can_resume(client, app, manager, approver):
    w = create(client, manager)
    app.state.gateway.failures["activate_campaign_simulated"] = 3
    base = f"/agentic/workflows/{w['workflow_id']}"
    failed = client.post(
        base + "/approval", headers=approver, json={"payload_hash": w["payload_hash"]}
    ).json()
    assert failed["status"] == "FAILED" and failed["approval"]
    assert client.post(base + "/execute", headers=approver).json()["status"] == "COMPLETED"


def test_concurrent_execution_is_idempotent(client, app, manager, approver):
    from concurrent.futures import ThreadPoolExecutor

    w = create(client, manager)
    base = f"/agentic/workflows/{w['workflow_id']}"
    assert (
        client.post(base + "/approval", headers=approver, json={"payload_hash": w["payload_hash"]}).json()[
            "status"
        ]
        == "COMPLETED"
    )
    with ThreadPoolExecutor(max_workers=4) as workers:
        results = list(
            workers.map(lambda _: client.post(base + "/execute", headers=approver).json(), range(4))
        )
    assert len({r["outcome"]["campaign_id"] for r in results}) == 1
    events = client.get(base + "/events", headers=manager).json()
    assert (
        len([e for e in events if e["tool"] == "activate_campaign_simulated" and e["outcome"] == "success"])
        == 1
    )


def test_consent_rechecked_after_approval(client, app, manager, approver):
    w = create(client, manager)
    app.state.gateway.failures["activate_campaign_simulated"] = 3
    base = f"/agentic/workflows/{w['workflow_id']}"
    assert (
        client.post(base + "/approval", headers=approver, json={"payload_hash": w["payload_hash"]}).json()[
            "status"
        ]
        == "FAILED"
    )
    next(c for c in app.state.gateway.customers if c["id"] == "bank-a-c1")["consent"] = False
    assert client.post(base + "/execute", headers=approver).json()["status"] == "FAILED"
    with app.state.repo.sessions() as session:
        assert session.scalar(select(Campaign)).status == "DRAFT"
