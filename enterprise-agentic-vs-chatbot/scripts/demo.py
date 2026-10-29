import os
from uuid import uuid4
import httpx

base = os.getenv("API_BASE_URL", "http://localhost:8000")
manager = {"Authorization": "Bearer demo-manager-a"}
approver = {"Authorization": "Bearer demo-approver-a"}
message = "Identify eligible customers and prepare a premium upgrade campaign."
with httpx.Client(base_url=base, timeout=90) as client:
    chat = client.post("/chatbot/query", json={"message": message})
    chat.raise_for_status()
    print("Chatbot business actions:", chat.json()["business_actions"])
    response = client.post(
        "/agentic/requests", headers=manager, json={"message": message, "idempotency_key": str(uuid4())}
    )
    response.raise_for_status()
    workflow = response.json()
    assert workflow["status"] == "PENDING_APPROVAL", workflow["error"]
    print("Prepared:", workflow["workflow_id"], workflow["status"])
    result = client.post(
        f"/agentic/workflows/{workflow['workflow_id']}/approval",
        headers=approver,
        json={"payload_hash": workflow["payload_hash"]},
    )
    result.raise_for_status()
    assert result.json()["status"] == "COMPLETED"
    print("Approved simulated outcome:", result.json()["outcome"])
