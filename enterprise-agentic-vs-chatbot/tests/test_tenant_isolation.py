import asyncio
import json
import pytest
from conftest import create
from src.governance.identity import DEMO_USERS
from src.governance.pep import PolicyDenied
from src.state.models import Workflow


@pytest.mark.parametrize("args", [{"tenant": "bank-b"}, {"customer_id": "bank-b-c1"}])
def test_gateway_isolation(client, app, manager, args):
    w = create(client, manager)
    with app.state.repo.transaction() as session:
        row = session.get(Workflow, w["workflow_id"])
        with pytest.raises(PolicyDenied):
            asyncio.run(
                app.state.gateway.invoke(
                    session,
                    row,
                    DEMO_USERS["demo-manager-a"],
                    "customer_insights",
                    "get_customer_profile",
                    **args,
                )
            )
    events = client.get(f"/agentic/workflows/{w['workflow_id']}/events", headers=manager).json()
    assert "bank-b" not in json.dumps(events)


def test_api_tenant_isolation(client, manager):
    w = create(client, manager)
    other = {"Authorization": "Bearer demo-manager-b"}
    base = f"/agentic/workflows/{w['workflow_id']}"
    for path in [base, base + "/events"]:
        assert client.get(path, headers=other).status_code == 404
    assert (
        client.post(
            base + "/approval",
            headers={"Authorization": "Bearer demo-approver-b"},
            json={"payload_hash": w["payload_hash"]},
        ).status_code
        == 404
    )
    other_workflow = create(client, other)
    assert "bank-a" not in json.dumps(other_workflow)
