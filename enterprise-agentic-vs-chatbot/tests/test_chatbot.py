from conftest import create
from sqlalchemy import select, func
from src.state.models import Campaign, Workflow


def test_same_request_chatbot_has_no_business_execution(client, app, manager):
    message = "Identify eligible customers and prepare a premium upgrade campaign."
    result = client.post("/chatbot/query", json={"message": message}).json()
    assert result["business_actions"] == 0
    assert "guidance only" in result["text"]
    assert result["model"] == "mock" and result["estimated_cost_usd"] == 0
    with app.state.repo.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Campaign)) == 0
        assert session.scalar(select(func.count()).select_from(Workflow)) == 0
    assert create(client, manager, message)["status"] == "PENDING_APPROVAL"


def test_information_no_tools(client, manager):
    w = create(client, manager, "What is a premium credit card upgrade campaign?")
    assert w["status"] == "COMPLETED" and w["outcome"]["business_actions"] == 0
    events = client.get(f"/agentic/workflows/{w['workflow_id']}/events", headers=manager).json()
    assert not any(e["tool"] in {"get_customer_profile", "create_campaign_draft"} for e in events)
