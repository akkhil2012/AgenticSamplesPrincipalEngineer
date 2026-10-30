import io
import json
import logging
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock
import urllib.request
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import REQUEST, Model, Task, BalanceResult, CreditResult
from multi_agent import SupervisorAgent, CreditAgent
from single_agent import BankingAgent
import tools


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def planner(capabilities, account="ACC123"):
    model = Mock()
    model.select.return_value = {"account_id": account, "capabilities": capabilities}
    return model


def assert_success(result, agent_count):
    assert result["status"] == "COMPLETED"
    assert result["results"]["balance"] == {
        "account_id": "ACC123",
        "balance": 50000,
        "currency": "INR",
    }
    assert result["results"]["credit"]["eligible"] is True
    assert "₹50,000" in result["response"]
    assert result["metrics"]["model_calls"] == 1
    assert result["metrics"]["tool_calls"] == 2
    assert result["metrics"]["agent_calls"] == agent_count
    assert result["metrics"]["duration_ms"] >= 0


def test_single_success():
    assert_success(BankingAgent().run("user1", REQUEST), 1)


def test_multi_success():
    assert_success(SupervisorAgent().run("user1", REQUEST), 3)


def test_equivalent_business_outcomes():
    single = BankingAgent().run("user1", REQUEST)
    multi = SupervisorAgent().run("user1", REQUEST)
    assert single["results"] == multi["results"]
    assert single["response"] == multi["response"]
    assert single["metrics"]["correlation_id"] != multi["metrics"]["correlation_id"]


def test_supervisor_delegates_scoped_tasks_to_correct_specialists():
    account, credit = Mock(), Mock()
    account.run.return_value = BalanceResult("ACC123", 50000, "INR")
    credit.run.return_value = CreditResult("ACC123", True, "Criteria met")
    result = SupervisorAgent(account_agent=account, credit_agent=credit).run(
        "user1", REQUEST
    )
    assert result["status"] == "COMPLETED"
    for specialist in [account, credit]:
        specialist.run.assert_called_once()
        assert specialist.run.call_args.args[0] == Task("user1", "ACC123")
        assert (
            specialist.run.call_args.args[1].correlation_id
            == result["metrics"]["correlation_id"]
        )


@pytest.mark.parametrize("architecture", [BankingAgent, SupervisorAgent])
@pytest.mark.parametrize("capabilities", [["balance"], ["credit"]])
def test_validated_model_plan_drives_routing_not_prompt_keywords(
    architecture, capabilities
):
    model = planner(capabilities)
    result = architecture(model=model).run(
        "user1", "Opaque instruction with no banking keywords"
    )
    assert result["status"] == "COMPLETED"
    assert set(result["results"]) == set(capabilities)
    assert result["metrics"]["model_calls"] == result["metrics"]["tool_calls"] == 1
    model.select.assert_called_once_with("Opaque instruction with no banking keywords")


def test_supervisor_does_not_call_unselected_specialist():
    account, credit = Mock(), Mock()
    credit.run.return_value = CreditResult("ACC123", True, "Criteria met")
    result = SupervisorAgent(
        model=planner(["credit"]), account_agent=account, credit_agent=credit
    ).run("user1", "opaque")
    assert result["status"] == "COMPLETED"
    account.run.assert_not_called()
    credit.run.assert_called_once()


def test_supervisor_never_invokes_specialist_tools_directly(monkeypatch):
    callers = []
    balance, eligibility = tools.get_balance, tools.check_credit_eligibility

    def capture_balance(task, metrics, agent):
        callers.append(agent)
        return balance(task, metrics, agent)

    def capture_credit(task, metrics, agent):
        callers.append(agent)
        return eligibility(task, metrics, agent)

    monkeypatch.setattr(tools, "get_balance", capture_balance)
    monkeypatch.setattr(tools, "check_credit_eligibility", capture_credit)
    assert SupervisorAgent().run("user1", REQUEST)["status"] == "COMPLETED"
    assert callers == ["AccountAgent", "CreditAgent"]


@pytest.mark.parametrize("order", [["balance", "credit"], ["credit", "balance"]])
def test_partial_specialist_failure_preserves_balance_and_correlation(order):
    result = SupervisorAgent(
        model=planner(order), credit_agent=CreditAgent(fail=True)
    ).run("user1", REQUEST)
    assert result["status"] == "PARTIAL"
    assert result["results"]["balance"]["balance"] == 50000
    assert "credit" not in result["results"]
    assert "eligibility is unavailable" in result["response"]
    assert "Eligible for a credit card" not in result["response"]
    assert result["errors"][0]["capability"] == "credit"
    assert result["errors"][0]["correlation_id"] == result["metrics"]["correlation_id"]
    assert (
        result["metrics"]["tool_calls"] == 1 and result["metrics"]["agent_calls"] == 3
    )


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        {"account_id": "ACC123", "eligible": "yes", "reason": "x"},
        {"account_id": "ACC456", "eligible": True, "reason": "x"},
        {"account_id": "ACC123", "eligible": True, "reason": "x", "approve": True},
    ],
)
def test_invalid_specialist_output_is_discarded(invalid):
    credit = Mock()
    credit.run.return_value = invalid
    result = SupervisorAgent(credit_agent=credit).run("user1", REQUEST)
    assert result["status"] == "PARTIAL" and set(result["results"]) == {"balance"}
    assert result["errors"][0]["code"] == "specialist_failed"


@pytest.mark.parametrize("architecture", [BankingAgent, SupervisorAgent])
@pytest.mark.parametrize(
    "user,account", [("user2", "ACC123"), ("user1", "ACC999"), (None, "ACC999")]
)
def test_authorization_before_financial_record_access(
    monkeypatch, architecture, user, account
):
    class ForbiddenFinancialData:
        def __getitem__(self, key):
            pytest.fail("Unauthorized caller accessed financial data")

    monkeypatch.setattr(tools, "ACCOUNT_DATA", ForbiddenFinancialData())
    result = architecture(model=planner(["balance", "credit"], account)).run(
        user, "opaque"
    )
    assert result["status"] == "DENIED"
    assert not result["results"]
    assert all(e["code"] == "access_denied" for e in result["errors"])


@pytest.mark.parametrize(
    "raw",
    [
        {"account_id": "ACC123", "capabilities": ["disburse"]},
        {"account_id": "ACC123", "capabilities": ["credit", "credit"]},
        {"account_id": "ACC123", "capabilities": []},
        {"account_id": "ACC123;exec()", "capabilities": ["balance"]},
        {"account_id": "ACC123", "capabilities": [["balance"]]},
    ],
)
def test_invalid_plan_never_reaches_specialists(raw):
    model, account, credit = Mock(), Mock(), Mock()
    model.select.return_value = raw
    result = SupervisorAgent(
        model=model, account_agent=account, credit_agent=credit
    ).run("user1", "opaque")
    assert result["status"] == "FAILED"
    assert (
        result["metrics"]["model_calls"] == 1 and result["metrics"]["tool_calls"] == 0
    )
    account.run.assert_not_called()
    credit.run.assert_not_called()


@pytest.mark.parametrize(
    "score,income,expected",
    [(700, 50000, True), (699, 100000, False), (760, 49999, False)],
)
def test_illustrative_eligibility_boundaries(monkeypatch, score, income, expected):
    monkeypatch.setitem(
        tools.ACCOUNT_DATA,
        "ACC123",
        {"balance": 50000, "credit_score": score, "monthly_income": income},
    )
    assert (
        BankingAgent().run("user1", REQUEST)["results"]["credit"]["eligible"]
        is expected
    )


def test_tool_failure_is_counted_and_safe_in_single(monkeypatch):
    def broken(task, metrics, agent):
        metrics.tool_calls += 1
        raise RuntimeError("private-secret-marker")

    monkeypatch.setattr(tools, "check_credit_eligibility", broken)
    result = BankingAgent().run("user1", REQUEST)
    assert result["status"] == "PARTIAL" and result["metrics"]["tool_calls"] == 2
    assert "private-secret-marker" not in json.dumps(result)


def test_specialists_log_their_own_execution(caplog):
    with caplog.at_level(logging.INFO, logger="banking_comparison"):
        result = SupervisorAgent(credit_agent=CreditAgent(fail=True)).run(
            "user1", REQUEST
        )
    events = [json.loads(record.message) for record in caplog.records]
    assert all(
        e["correlation_id"] == result["metrics"]["correlation_id"] for e in events
    )
    assert any(
        e["agent"] == "AccountAgent"
        and e["event"] == "agent_finished"
        and e["status"] == "COMPLETED"
        for e in events
    )
    assert any(
        e["agent"] == "CreditAgent"
        and e["event"] == "agent_finished"
        and e["status"] == "FAILED"
        for e in events
    )
    assert any(e["event"] == "execution_error" for e in events)
    assert "50000" not in " ".join(e["event"] for e in events)


def test_real_model_request_is_openai_compatible(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1/")
    captured = {}

    def fake(request, timeout):
        captured["request"], captured["timeout"] = request, timeout
        content = json.dumps(
            {"account_id": "ACC123", "capabilities": ["balance", "credit"]}
        )
        return io.BytesIO(
            json.dumps({"choices": [{"message": {"content": content}}]}).encode()
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake)
    result = BankingAgent(model=Model("openai")).run("user1", REQUEST)
    assert_success(result, 1)
    request = captured["request"]
    assert request.full_url == "https://example.test/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-key"
    assert json.loads(request.data)["messages"][-1]["content"] == REQUEST
    assert captured["timeout"] == 10


@pytest.mark.parametrize("response", [b"invalid-json", b"x" * 65537])
def test_invalid_provider_output_fails_safely(monkeypatch, response):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda *args, **kwargs: io.BytesIO(response)
    )
    result = SupervisorAgent(model=Model("openai")).run("user1", REQUEST)
    assert result["status"] == "FAILED" and result["metrics"]["tool_calls"] == 0


def test_missing_real_key_fails_without_network(monkeypatch):
    network = Mock()
    monkeypatch.setattr(urllib.request, "urlopen", network)
    result = BankingAgent(model=Model("openai")).run("user1", REQUEST)
    assert result["status"] == "FAILED" and result["metrics"]["model_calls"] == 1
    network.assert_not_called()


def test_cli_demonstrates_both_architectures_and_partial_failure():
    project = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "BankingAgent — COMPLETED" in result.stdout
    assert "SupervisorAgent — COMPLETED" in result.stdout
    assert "SupervisorAgent — PARTIAL" in result.stdout
    assert (
        "eligibility is unavailable" in result.stdout
        and "Observed metrics" in result.stdout
    )
    events = [json.loads(line) for line in result.stderr.splitlines()]
    assert len({e["correlation_id"] for e in events}) == 3
