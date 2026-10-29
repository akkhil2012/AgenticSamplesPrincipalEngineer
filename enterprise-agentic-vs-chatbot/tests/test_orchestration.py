from conftest import create
from src.contracts.schemas import (
    CustomerInsights,
    EngagementInsights,
    OfferInsights,
    ComplianceResult,
    CampaignPayload,
)


def test_adk_specialists_and_compliance(client, manager):
    w = create(client, manager, "Include customers who opted out of marketing.")
    assert w["status"] == "PENDING_APPROVAL", w
    c = w["checkpoint"]
    assert CustomerInsights.model_validate(c["customer_insights"]).evaluated == 6
    EngagementInsights.model_validate(c["engagement"])
    OfferInsights.model_validate(c["offers"])
    compliance = ComplianceResult.model_validate(c["compliance"])
    assert compliance.excluded_count == 2
    payload = CampaignPayload.model_validate(w["campaign_draft"])
    assert payload.customer_ids == ["bank-a-c1", "bank-a-c2"]
    events = client.get(f"/agentic/workflows/{w['workflow_id']}/events", headers=manager).json()
    timeline = [e["agent"] for e in events if e["tool"] == "agent_result"]
    assert timeline[0] == "customer_insights" and set(timeline[1:3]) == {"engagement", "offers"}
    assert timeline[-2:] == ["compliance", "campaign"]
    assert any(e["decision"] == "DENY" and e["outcome"] == "excluded" for e in events)
