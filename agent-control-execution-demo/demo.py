"""Exercise all four scenarios through real FastAPI routes without running a separate server."""

import json
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from main import create_app

SAMPLES = Path(__file__).with_name("samples")


def sample(name):
    return json.loads((SAMPLES / name).read_text())


def run_demo():
    # A fresh disposable database makes this demonstration repeatable.
    with tempfile.TemporaryDirectory(prefix="control-execution-") as directory:
        app = create_app(Path(directory) / "demo.db")
        with TestClient(app) as client:
            base = "/execution/agents/loan-agent-001"
            control = "/control/agents/loan-agent-001/configuration"
            registered = client.post("/control/agents", json=sample("register.json"))
            assert registered.status_code == 201, registered.text
            first = client.post(base + "/applications", json=sample("application.json"))
            assert first.status_code == 200, first.text
            assert first.json()["recommendation"] == "APPROVE"
            assert first.json()["status"] == "PENDING_HUMAN_APPROVAL"
            print("1. Successful execution:", json.dumps(first.json()))
            assert client.put(control, json=sample("disable.json")).status_code == 200
            disabled = client.post(
                base + "/applications", json=sample("application.json")
            )
            assert disabled.status_code == 403, disabled.text
            print("2. Disabled agent:", json.dumps(disabled.json()["detail"]))
            assert (
                client.put(control, json=sample("raise_threshold.json")).status_code
                == 200
            )
            changed = client.post(
                base + "/applications", json=sample("application.json")
            )
            assert (
                changed.status_code == 200
                and changed.json()["recommendation"] == "REJECT"
            ), changed.text
            print("3. Updated credit policy:", json.dumps(changed.json()))
            denied = client.post(
                base + "/actions", json=sample("unauthorized_action.json")
            )
            assert denied.status_code == 403, denied.text
            events = client.get(
                "/execution/audit",
                params={"execution_id": denied.json()["detail"]["execution_id"]},
            ).json()
            assert any(
                e["action"] == "disburse_loan" and e["decision"] == "DENY"
                for e in events
            )
            print("4. Unauthorized disbursement:", json.dumps(denied.json()["detail"]))
            print(
                "Denied action durably audited. All four scenarios passed; no loan was approved or disbursed."
            )


if __name__ == "__main__":
    run_demo()
