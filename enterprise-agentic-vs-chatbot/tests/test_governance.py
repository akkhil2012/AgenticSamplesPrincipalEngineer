import asyncio
import time
import pytest
from conftest import create
from src.governance.identity import DEMO_USERS, Identity
from src.governance.pdp import PDP, Decision
from src.governance.pep import PolicyDenied
from src.state.models import Workflow


@pytest.mark.parametrize("token", [None, "not-valid"])
def test_authentication(client, token):
    headers = {} if token is None else {"Authorization": f"Bearer {token}"}
    assert (
        client.post(
            "/agentic/requests",
            headers=headers,
            json={"message": "prepare campaign", "idempotency_key": "auth-test"},
        ).status_code
        == 401
    )


def test_unauthorized_immediate_activation(client, manager):
    w = create(client, manager, "Activate the campaign immediately.")
    assert w["status"] == "FAILED" and w["outcome"] is None
    assert client.post(f"/agentic/workflows/{w['workflow_id']}/execute", headers=manager).status_code == 403


def test_independent_approval_and_hash(client, manager, approver):
    w = create(client, manager)
    path = f"/agentic/workflows/{w['workflow_id']}/approval"
    assert client.post(path, headers=manager, json={"payload_hash": w["payload_hash"]}).status_code == 403
    assert client.post(path, headers=approver, json={"payload_hash": "0" * 64}).status_code == 409
    assert client.post(f"/agentic/workflows/{w['workflow_id']}/execute", headers=approver).status_code == 403


@pytest.mark.parametrize("mutation", ["expired", "payload", "requester", "role", "tenant"])
def test_approval_revalidated(client, app, manager, approver, mutation):
    w = create(client, manager)
    with app.state.repo.transaction() as session:
        row = session.get(Workflow, w["workflow_id"])
        row.status = "APPROVED"
        approval = {
            "approver": "approver-a",
            "tenant": "bank-a",
            "role": "campaign_approver",
            "payload_hash": row.payload_hash,
            "expires_at": time.time() + 900,
        }
        if mutation == "expired":
            approval["expires_at"] = time.time() - 1
        if mutation == "payload":
            row.payload = {**row.payload, "customer_ids": ["bank-a-c3"]}
        if mutation == "requester":
            row.requester = "approver-a"
        if mutation == "role":
            approval["role"] = "campaign_manager"
        if mutation == "tenant":
            approval["tenant"] = "bank-b"
        row.approval = approval
    assert client.post(f"/agentic/workflows/{w['workflow_id']}/execute", headers=approver).status_code == 409


def test_agent_least_privilege_and_self_approval(client, app, manager):
    w = create(client, manager)
    actor = DEMO_USERS["demo-manager-a"]
    with app.state.repo.transaction() as session:
        row = session.get(Workflow, w["workflow_id"])
        with pytest.raises(PolicyDenied):
            asyncio.run(
                app.state.gateway.invoke(
                    session, row, actor, "offers", "create_campaign_draft", payload=row.payload
                )
            )
        assert (
            PDP().evaluate(actor, "campaign", "activate_campaign_simulated", row.tenant, row) == Decision.DENY
        )
        row.approval = {
            "approver": row.requester,
            "role": "campaign_approver",
            "tenant": row.tenant,
            "payload_hash": row.payload_hash,
            "expires_at": time.time() + 900,
        }
        row.status = "APPROVED"
        elevated = Identity(row.requester, row.tenant, "campaign_approver")
        assert (
            PDP().evaluate(elevated, "campaign", "activate_campaign_simulated", row.tenant, row)
            == Decision.APPROVAL_REQUIRED
        )
