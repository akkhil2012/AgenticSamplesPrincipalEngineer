from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from demo import run_demo, sample
from main import create_app

CONTROL = "/control/agents/loan-agent-001/configuration"
APPLICATIONS = "/execution/agents/loan-agent-001/applications"
ACTIONS = "/execution/agents/loan-agent-001/actions"


def apply(client, **changes):
    return client.post(APPLICATIONS, json={**sample("application.json"), **changes})


def test_success_and_execution_snapshot(registered):
    response = apply(registered)
    assert response.status_code == 200
    result = response.json()
    assert result["recommendation"] == "APPROVE"
    assert result["status"] == "PENDING_HUMAN_APPROVAL"
    assert result["configuration_version"] == "1.0"
    record = registered.get("/execution/records/" + result["execution_id"]).json()
    assert record["configuration_snapshot"]["minimum_credit_score"] == 700
    events = registered.get(
        "/execution/audit", params={"execution_id": result["execution_id"]}
    ).json()
    assert [(e["action"], e["decision"]) for e in events] == [
        ("evaluate", "ALLOW"),
        ("recommend", "ALLOW"),
        ("execution_result", "ALLOW"),
    ]
    assert all(
        {"customer_id", "credit_score", "loan_amount"}.isdisjoint(event)
        for event in events
    )
    assert all(
        "C101" not in event["reason"] and "750" not in event["reason"]
        for event in events
    )


def test_disabled_agent_never_runs(registered, app, monkeypatch):
    assert registered.put(CONTROL, json=sample("disable.json")).status_code == 200

    def must_not_run(*args):
        pytest.fail("Disabled agent was called")

    monkeypatch.setattr(app.state.orchestrator.executor.agent, "evaluate", must_not_run)
    result = apply(registered)
    assert result.status_code == 403 and result.json()["detail"]["status"] == "BLOCKED"
    assert result.json()["detail"]["configuration_version"] == "1.1"
    wid = result.json()["detail"]["execution_id"]
    assert registered.get("/execution/records/" + wid).json()["status"] == "BLOCKED"
    events = registered.get("/execution/audit", params={"execution_id": wid}).json()
    assert events[0]["decision"] == "DENY"


def test_updated_policy_changes_subsequent_execution_and_retains_old_version(
    registered,
):
    first = apply(registered).json()
    change = {
        "expected_active_version": "1.0",
        "configuration": {
            **sample("register.json")["configuration"],
            "version": "2.0",
            "minimum_credit_score": 800,
        },
    }
    assert registered.put(CONTROL, json=change).status_code == 200
    second = apply(registered).json()
    assert first["recommendation"] == "APPROVE" and second["recommendation"] == "REJECT"
    assert (
        second["configuration_version"] == "2.0"
        and second["agent_version"] == first["agent_version"] == "1.0"
    )
    assert (
        registered.get("/execution/records/" + first["execution_id"]).json()[
            "configuration_snapshot"
        ]["minimum_credit_score"]
        == 700
    )
    assert (
        registered.get("/control/agents/loan-agent-001/configurations/1.0").json()[
            "minimum_credit_score"
        ]
        == 700
    )
    assert [
        c["version"]
        for c in registered.get("/control/agents/loan-agent-001/configurations").json()
    ] == ["1.0", "2.0"]


@pytest.mark.parametrize("action", ["disburse_loan", "approve_loan", "delete_records"])
def test_unauthorized_action_is_denied_and_audited(registered, action):
    response = registered.post(
        ACTIONS, json={"action": action, "application": sample("application.json")}
    )
    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["status"] == "BLOCKED" and detail["recommendation"] is None
    events = registered.get(
        "/execution/audit", params={"execution_id": detail["execution_id"]}
    ).json()
    assert events[0]["action"] == action and events[0]["decision"] == "DENY"


def test_governance_checks_each_step(registered):
    conf = {
        **sample("register.json")["configuration"],
        "version": "1.1",
        "allowed_actions": ["evaluate"],
    }
    assert (
        registered.put(
            CONTROL, json={"expected_active_version": "1.0", "configuration": conf}
        ).status_code
        == 200
    )
    result = apply(registered)
    assert result.status_code == 403
    events = registered.get(
        "/execution/audit",
        params={"execution_id": result.json()["detail"]["execution_id"]},
    ).json()
    assert [(e["action"], e["decision"]) for e in events[:2]] == [
        ("evaluate", "ALLOW"),
        ("recommend", "DENY"),
    ]


def test_empty_policy_denies_every_action(registered):
    conf = {
        **sample("register.json")["configuration"],
        "version": "1.1",
        "allowed_actions": [],
    }
    assert (
        registered.put(
            CONTROL, json={"expected_active_version": "1.0", "configuration": conf}
        ).status_code
        == 200
    )
    assert apply(registered).status_code == 403


@pytest.mark.parametrize(
    "score,amount,expected",
    [
        (700, 500000, "APPROVE"),
        (699, 300000, "REJECT"),
        (750, 500000.01, "REJECT"),
        (650, 600000, "REJECT"),
    ],
)
def test_rule_boundaries(registered, score, amount, expected):
    result = apply(registered, credit_score=score, loan_amount=amount)
    assert result.status_code == 200 and result.json()["recommendation"] == expected


def test_no_automatic_final_approval_even_when_human_flag_false(registered):
    conf = {
        **sample("register.json")["configuration"],
        "version": "1.1",
        "requires_human_approval": False,
    }
    registered.put(
        CONTROL, json={"expected_active_version": "1.0", "configuration": conf}
    )
    result = apply(registered).json()
    assert (
        result["recommendation"] == "APPROVE"
        and result["status"] == "RECOMMENDATION_ONLY"
    )
    assert (
        registered.post(
            ACTIONS,
            json={"action": "approve_loan", "application": sample("application.json")},
        ).status_code
        == 403
    )


def test_invalid_agent_output_cannot_authorize_actions(registered, app, monkeypatch):
    def malicious(application, minimum_credit_score, maximum_loan_amount):
        return {
            "recommendation": "APPROVE",
            "reason": "pretend",
            "status": "FINAL_APPROVED",
        }

    monkeypatch.setattr(app.state.orchestrator.executor.agent, "evaluate", malicious)
    response = apply(registered)
    assert response.status_code == 500
    assert response.json()["detail"]["status"] == "FAILED"
    assert "FINAL_APPROVED" not in response.text
    assert (
        registered.get(
            "/execution/records/" + response.json()["detail"]["execution_id"]
        ).json()["status"]
        == "FAILED"
    )


def test_agent_failure_record_is_safe(registered, app, monkeypatch):
    def broken(*args):
        raise RuntimeError("secret-do-not-log-C101")

    monkeypatch.setattr(app.state.orchestrator.executor.agent, "evaluate", broken)
    response = apply(registered)
    assert response.status_code == 500 and "secret-do-not-log" not in response.text
    assert "secret-do-not-log" not in registered.get("/execution/audit").text


def test_version_conflicts_and_validation(registered):
    base = sample("register.json")["configuration"]
    assert (
        registered.post("/control/agents", json=sample("register.json")).status_code
        == 409
    )
    assert (
        registered.put(
            CONTROL, json={"expected_active_version": "1.0", "configuration": base}
        ).status_code
        == 409
    )
    assert (
        registered.put(
            CONTROL,
            json={
                "expected_active_version": "0.9",
                "configuration": {**base, "version": "2.0"},
            },
        ).status_code
        == 409
    )
    assert (
        registered.put(
            CONTROL,
            json={
                "expected_active_version": "1.0",
                "configuration": {
                    **base,
                    "version": "2.0",
                    "allowed_actions": ["disburse_loan"],
                },
            },
        ).status_code
        == 422
    )
    assert registered.get(CONTROL).json()["version"] == "1.0"


def test_registered_capabilities_bound_later_policy(client):
    document = sample("register.json")
    document["capabilities"] = ["evaluate"]
    document["configuration"]["allowed_actions"] = ["evaluate"]
    assert client.post("/control/agents", json=document).status_code == 201
    assert (
        client.put(
            CONTROL,
            json={
                "expected_active_version": "1.0",
                "configuration": {
                    **sample("register.json")["configuration"],
                    "version": "2.0",
                },
            },
        ).status_code
        == 422
    )


def test_restart_preserves_registry_versions_execution_and_audit(registered, db_path):
    first = apply(registered).json()
    with TestClient(create_app(db_path)) as restarted:
        assert restarted.get(CONTROL).json()["version"] == "1.0"
        assert (
            restarted.get("/execution/records/" + first["execution_id"]).json()[
                "recommendation"
            ]
            == "APPROVE"
        )
        assert (
            len(
                restarted.get(
                    "/execution/audit", params={"execution_id": first["execution_id"]}
                ).json()
            )
            == 3
        )


def test_concurrent_updates_detect_lost_update(registered):
    def update(version):
        return registered.put(
            CONTROL,
            json={
                "expected_active_version": "1.0",
                "configuration": {
                    **sample("register.json")["configuration"],
                    "version": version,
                },
            },
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as workers:
        assert sorted(workers.map(update, ["1.1", "2.0"])) == [200, 409]


@pytest.mark.parametrize(
    "changes",
    [
        {"loan_amount": 0},
        {"loan_amount": -1},
        {"loan_amount": "NaN"},
        {"credit_score": 900},
        {"credit_score": "750"},
        {"customer_id": ""},
        {"status": "FINAL_APPROVED"},
    ],
)
def test_input_validation(registered, changes):
    assert apply(registered, **changes).status_code == 422


def test_unknown_resources_and_registry_listing(client, registered):
    assert len(client.get("/control/agents").json()) == 1
    assert (
        client.get("/control/agents/loan-agent-001").json()["name"]
        == "LoanApprovalAgent"
    )
    assert (
        client.post(
            "/execution/agents/missing/applications", json=sample("application.json")
        ).status_code
        == 404
    )
    assert client.get("/execution/records/missing").status_code == 404
    assert (
        client.get("/control/agents/loan-agent-001/configurations/9.0").status_code
        == 404
    )


def test_all_four_demo_scenarios(capsys):
    run_demo()
    assert "All four scenarios passed" in capsys.readouterr().out
