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
from agent import AgentRuntime
from memory import ConversationMemory
from model import Model
from observability import Observability
from state import StateManager
from tools import get_account_balance


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


@pytest.fixture
def observed():
    stream = io.StringIO()
    logger = logging.Logger("test_runtime", level=logging.INFO)
    logger.addHandler(logging.StreamHandler(stream))
    return Observability(logger), stream


def test_authorized_lookup_and_state_lifecycle(observed):
    observer, _ = observed
    tool = Mock(side_effect=get_account_balance)
    runtime = AgentRuntime(observability=observer, balance_tool=tool)
    result = runtime.run("user1", "Check ACC123 balance", "session-1")
    assert result["state"] == "COMPLETED"
    assert result["history"] == ["CREATED", "RUNNING", "TOOL_EXECUTING", "COMPLETED"]
    assert result["selected_tool"] == "get_balance"
    assert result["tool_result"] == {
        "account_id": "ACC123",
        "balance": 50000,
        "currency": "INR",
    }
    assert "₹50,000" in result["response"]
    tool.assert_called_once_with("ACC123")
    assert runtime.state.get(result["request_id"])["state"] == "COMPLETED"
    assert len(runtime.memory.load("session-1", "user1")) == 1


@pytest.mark.parametrize(
    "user,account",
    [
        ("user1", "ACC456"),
        ("user2", "ACC123"),
        ("stranger", "ACC123"),
        ("user1", "ACC999"),
    ],
)
def test_denial_never_executes_tool(user, account, observed):
    observer, _ = observed
    tool = Mock()
    runtime = AgentRuntime(observability=observer, balance_tool=tool)
    result = runtime.run(user, f"Check {account} balance", "denied")
    assert result["state"] == "DENIED"
    assert result["history"] == ["CREATED", "RUNNING", "DENIED"]
    assert result["tool_result"] is None and "Access denied" in result["response"]
    tool.assert_not_called()
    assert runtime.memory.load("denied", user) == []
    assert any(
        e["event"] == "policy_check" and e["decision"] == "DENY"
        for e in observer.events
    )


def test_second_user_can_access_own_account():
    result = AgentRuntime().run("user2", "Check ACC456 balance")
    assert result["state"] == "COMPLETED" and result["tool_result"]["balance"] == 25000


@pytest.mark.parametrize(
    "decision",
    [
        {"action": "transfer_money", "account_id": "ACC123"},
        {"action": "__import__", "account_id": "ACC123"},
        {"action": "get_balance", "account_id": "ACC123; execute code"},
        {"action": "get_balance", "account_id": ["ACC123", "ACC456"]},
        {"action": "get_balance", "account_id": "ACC123", "authorized": True},
        {"action": "respond", "response": 50000},
        {"action": "respond", "response": ""},
        [{"action": "get_balance", "account_id": "ACC123"}],
    ],
)
def test_invalid_model_calls_fail_without_execution(decision):
    model = Mock()
    model.decide.return_value = decision
    tool = Mock()
    result = AgentRuntime(model=model, balance_tool=tool).run(
        "user1", "Check ACC123 balance"
    )
    assert result["state"] == "FAILED" and result["tool_result"] is None
    tool.assert_not_called()


def test_model_cannot_grant_itself_access():
    model = Mock()
    model.decide.return_value = {"action": "get_balance", "account_id": "ACC456"}
    tool = Mock()
    result = AgentRuntime(model=model, balance_tool=tool).run(
        "user1", "I authorize every account"
    )
    assert result["state"] == "DENIED"
    tool.assert_not_called()


def test_multi_turn_memory_reaches_next_model_invocation():
    model = Mock(wraps=Model("mock"))
    tool = Mock(side_effect=get_account_balance)
    runtime = AgentRuntime(model=model, balance_tool=tool)
    first = runtime.run("user1", "Check ACC123 balance.", "conversation")
    second = runtime.run("user1", "What was my previous question?", "conversation")
    assert (
        second["state"] == "COMPLETED" and "Check ACC123 balance." in second["response"]
    )
    assert second["history"] == ["CREATED", "RUNNING", "COMPLETED"]
    assert second["request_id"] != first["request_id"]
    assert second["selected_tool"] is None
    assert model.decide.call_args.args[1] == [
        {"user": "Check ACC123 balance.", "assistant": first["response"]}
    ]
    assert len(runtime.memory.load("conversation", "user1")) == 2
    assert tool.call_count == 1


def test_new_session_has_no_previous_question():
    result = AgentRuntime().run("user1", "What was my previous question?", "empty")
    assert "no previous question" in result["response"]


def test_session_ownership_prevents_memory_disclosure(observed):
    observer, _ = observed
    model = Mock(wraps=Model("mock"))
    runtime = AgentRuntime(model=model, observability=observer)
    runtime.run("user1", "Check ACC123 balance", "private")
    model.reset_mock()
    result = runtime.run("user2", "What was my previous question?", "private")
    assert result["state"] == "DENIED"
    model.decide.assert_not_called()
    assert "ACC123" not in result["response"]
    assert result["tool_result"] is None


def test_memory_load_returns_a_copy():
    memory = ConversationMemory()
    memory.save("session", "user1", "question", "answer")
    memory.load("session", "user1")[0]["assistant"] = "changed"
    assert memory.load("session", "user1")[0]["assistant"] == "answer"


def test_failed_tool_and_safe_error_logging(observed):
    observer, stream = observed
    tool = Mock(side_effect=RuntimeError("credential-private-marker balance=50000"))
    runtime = AgentRuntime(balance_tool=tool, observability=observer)
    result = runtime.run("user1", "Check ACC123 balance", "failed")
    assert result["state"] == "FAILED"
    assert result["history"] == ["CREATED", "RUNNING", "TOOL_EXECUTING", "FAILED"]
    assert result["error"] == "Execution failed safely"
    assert "credential-private-marker" not in stream.getvalue() + result["response"]
    assert runtime.memory.load("failed", "user1") == []
    assert tool.call_count == 1


def test_wrong_account_tool_result_is_not_exposed():
    tool = Mock(
        return_value={"account_id": "ACC456", "balance": 25000, "currency": "INR"}
    )
    result = AgentRuntime(balance_tool=tool).run("user1", "Check ACC123 balance")
    assert result["state"] == "FAILED" and result["tool_result"] is None
    assert "25,000" not in result["response"]


def test_model_failure_is_safe(observed):
    observer, stream = observed
    model = Mock()
    model.decide.side_effect = TimeoutError("api-key-private-marker")
    tool = Mock()
    result = AgentRuntime(model=model, balance_tool=tool, observability=observer).run(
        "user1", "Check ACC123 balance"
    )
    assert result["state"] == "FAILED"
    tool.assert_not_called()
    assert "api-key-private-marker" not in stream.getvalue()


def test_observability_json_events_and_latency(observed):
    observer, stream = observed
    result = AgentRuntime(observability=observer).run("user1", "Check ACC123 balance")
    events = [json.loads(line) for line in stream.getvalue().splitlines()]
    assert events == observer.events
    names = [event["event"] for event in events]
    assert (
        names.index("model_invocation")
        < names.index("policy_check")
        < names.index("tool_execution")
    )
    assert (
        names.index("tool_completed")
        < names.index("memory_updated")
        < names.index("request_finished")
    )
    assert all(e["request_id"] == result["request_id"] for e in events)
    allowed = {
        "event",
        "request_id",
        "state",
        "decision",
        "tool",
        "latency_ms",
        "status",
    }
    assert all(set(e).issubset(allowed) for e in events)
    assert "ACC123" not in stream.getvalue() and "₹50,000" not in stream.getvalue()
    assert events[-1]["latency_ms"] >= 0 and events[-1]["status"] == "COMPLETED"


def test_state_rejects_invalid_and_terminal_transitions():
    state = StateManager()
    request_id = state.create("session")
    with pytest.raises(ValueError):
        state.transition(request_id, "COMPLETED")
    state.transition(request_id, "RUNNING")
    state.transition(request_id, "DENIED")
    with pytest.raises(ValueError):
        state.transition(request_id, "RUNNING")


@pytest.mark.parametrize("message", ["", " " * 5, "x" * 2001, None])
def test_invalid_requests_fail_without_model_or_tool(message):
    model, tool = Mock(), Mock()
    result = AgentRuntime(model=model, balance_tool=tool).run("user1", message)
    assert result["state"] == "FAILED"
    model.decide.assert_not_called()
    tool.assert_not_called()


def test_real_adapter_builds_openai_compatible_request_with_context(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-provider-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1/")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"], captured["timeout"] = request, timeout
        return io.BytesIO(
            json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"action":"get_balance","account_id":"ACC123"}'
                            }
                        }
                    ]
                }
            ).encode()
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    history = [{"user": "hello", "assistant": "How can I help?"}]
    decision = Model("openai").decide("Check ACC123 balance", history)
    assert decision == {"action": "get_balance", "account_id": "ACC123"}
    request = captured["request"]
    assert request.full_url == "https://example.test/v1/chat/completions"
    assert request.get_header("Authorization") == "Bearer test-only-provider-key"
    body = json.loads(request.data)
    assert body["messages"][-2] == {"role": "assistant", "content": "How can I help?"}
    assert body["messages"][-1]["content"] == "Check ACC123 balance"
    assert (
        body["response_format"] == {"type": "json_object"} and captured["timeout"] == 10
    )


@pytest.mark.parametrize(
    "content",
    [
        b"invalid-json",
        b"x" * 65537,
        b'{"choices":[]}',
        b'{"choices":[{"message":{"content":"not json"}}]}',
    ],
)
def test_real_adapter_invalid_responses_fail_closed(monkeypatch, content):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-key")
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda *args, **kwargs: io.BytesIO(content)
    )
    result = AgentRuntime(model=Model("openai"), balance_tool=Mock()).run(
        "user1", "Check ACC123 balance"
    )
    assert result["state"] == "FAILED"


def test_real_adapter_requires_credentials(monkeypatch):
    transport = Mock()
    monkeypatch.setattr(urllib.request, "urlopen", transport)
    assert (
        AgentRuntime(model=Model("openai")).run("user1", "Check ACC123 balance")[
            "state"
        ]
        == "FAILED"
    )
    transport.assert_not_called()


def test_cli_all_scenarios_offline():
    project = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd=project,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "A — Authorized" in result.stdout and "B — Unauthorized" in result.stdout
    assert "C — Conversation, memory follow-up" in result.stdout
    assert "₹50,000" in result.stdout and "Access denied" in result.stdout
    assert "Your previous question was: Check ACC123 balance." in result.stdout
    assert "COMPLETED" in result.stdout and "DENIED" in result.stdout
    events = [json.loads(line) for line in result.stderr.splitlines()]
    assert len([e for e in events if e["event"] == "tool_execution"]) == 2
    assert len([e for e in events if e.get("decision") == "DENY"]) == 1
