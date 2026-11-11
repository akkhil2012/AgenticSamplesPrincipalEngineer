"""Deterministic provider doubles ONLY in tests; actual MCP and A2A transports."""

import json
import socket
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import uvicorn
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai.types.chat import ChatCompletion

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catalog
import coordinator
import llm
import specialist_server


class ScriptedProvider:
    """No network/credentials: verifies how SDK traffic and tool results are wired."""

    def __init__(self, fail=False, invalid=False):
        self.chat = SimpleNamespace(completions=self)
        self.fail = fail
        self.invalid = invalid
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("secret-provider-detail")
        messages = kwargs["messages"]
        specialist = "independent sourcing" in messages[0]["content"]
        count = sum(m["role"] == "tool" for m in messages)
        if specialist:
            actions = [
                ("search_quotes", {"query": "laptop"}),
                ("quote_cost", {"quote_id": "Q-103", "quantity": 100}),
            ]
        else:
            actions = [
                ("delegate_supplier_research", {"request": messages[1]["content"]})
            ]
        if count < len(actions):
            name, args = actions[count]
            if self.invalid:
                name = "not_a_tool"
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call-{count}",
                        "type": "function",
                        "function": {"name": name, "arguments": json.dumps(args)},
                    }
                ],
            }
            finish = "tool_calls"
        else:
            # Require actual protocol results to have reached the model context.
            assert messages[-1]["role"] == "tool"
            assert (
                "83500.00" in messages[-1]["content"]
                if specialist
                else "Q-103" in messages[-1]["content"]
            )
            message = {
                "role": "assistant",
                "content": "Q-103: 100 units; USD 83500.00. Test report.",
            }
            finish = "stop"
        return ChatCompletion.model_validate(
            {
                "id": "test",
                "object": "chat.completion",
                "created": 0,
                "model": "test-only",
                "choices": [{"index": 0, "message": message, "finish_reason": finish}],
            }
        )

    async def close(self):
        pass


@pytest.fixture
def peer(monkeypatch):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    monkeypatch.setattr(coordinator, "SPECIALIST_URL", f"http://127.0.0.1:{port}")
    server = uvicorn.Server(uvicorn.Config(specialist_server.app, log_level="critical"))
    thread = threading.Thread(
        target=server.run, kwargs={"sockets": [sock]}, daemon=True
    )
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.02)
    assert server.started
    yield port
    server.should_exit = True
    thread.join(timeout=5)
    sock.close()


@pytest.mark.asyncio
async def test_complete_a2a_mcp_roundtrip(peer, monkeypatch):
    provider = ScriptedProvider()
    monkeypatch.setattr(llm, "make_client", lambda: provider)
    result = await coordinator.recommend("100 laptops under USD 85000 within 12 days")
    assert "Q-103" in result["answer"]
    operations = [(e["protocol"], e["operation"]) for e in result["trace"]]
    assert ("A2A", "agent-card") in operations
    assert ("A2A", "message/send") in operations
    assert ("MCP", "initialize") in operations
    assert ("MCP", "tools/list") in operations
    assert operations.count(("MCP", "tools/call")) == 2
    task = next(e for e in result["trace"] if e["operation"] == "task/result")
    assert task["task_id"] and task["status"] == "completed"
    assert len(provider.calls) == 5


@pytest.mark.asyncio
async def test_failed_task_is_not_a_recommendation(peer, monkeypatch):
    coordinator_provider = ScriptedProvider()
    monkeypatch.setattr(llm, "make_client", lambda: ScriptedProvider(fail=True))
    with pytest.raises(llm.AgentFailure, match="did not complete") as caught:
        await coordinator.recommend("100 laptops", client=coordinator_provider)
    assert "secret-provider-detail" not in str(caught.value)


@pytest.mark.asyncio
async def test_mcp_reads_changed_csv_and_reports_tool_errors(tmp_path, monkeypatch):
    source = tmp_path / "quotes.csv"
    source.write_text(
        (catalog.ROOT / "data/example_quotes.csv")
        .read_text()
        .replace("Evergreen Systems,835,USD", "Evergreen Systems,810,USD")
    )
    monkeypatch.setenv("QUOTES_CSV", str(source))
    async with (
        stdio_client(
            StdioServerParameters(
                command=sys.executable,
                args=[str(catalog.ROOT / "mcp_server.py")],
                env={"QUOTES_CSV": str(source)},
            )
        ) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        tools = await session.list_tools()
        assert {t.name for t in tools.tools} == {"search_quotes", "quote_cost"}
        cost = await session.call_tool(
            "quote_cost", {"quote_id": "Q-103", "quantity": 100}
        )
        assert "81000.00" in cost.model_dump_json()
        bad = await session.call_tool(
            "quote_cost", {"quote_id": "missing", "quantity": 1}
        )
        assert bad.isError


@pytest.mark.asyncio
async def test_invalid_model_tool_and_provider_failure_are_safe():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_supplier_research",
                "parameters": {"type": "object"},
            },
        }
    ]

    async def dispatch(*args):
        pytest.fail("Invalid action must not execute")

    with pytest.raises(llm.AgentFailure, match="unavailable tool"):
        await llm.reason(
            "coordinator",
            "coordinator",
            "brief",
            tools,
            dispatch,
            [],
            ScriptedProvider(invalid=True),
        )
    with pytest.raises(llm.AgentFailure) as caught:
        await llm.reason(
            "coordinator",
            "coordinator",
            "brief",
            tools,
            dispatch,
            [],
            ScriptedProvider(fail=True),
        )
    assert "secret-provider-detail" not in str(caught.value)


def test_missing_key_has_no_mock_fallback(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(llm.AgentFailure, match="OPENAI_API_KEY"):
        llm.make_client()


def test_dataset_validation_and_exact_cost(tmp_path, monkeypatch):
    assert catalog.quote_cost("Q-103", 100)["subtotal"] == "83500.00"
    with pytest.raises(ValueError):
        catalog.quote_cost("Q-103", -1)
    bad = tmp_path / "bad.csv"
    bad.write_text("bad,columns\n1,2\n")
    monkeypatch.setenv("QUOTES_CSV", str(bad))
    with pytest.raises(ValueError, match="columns"):
        catalog.load_quotes()


@pytest.mark.asyncio
async def test_model_loop_stops_at_budget():
    class RepeatingProvider(ScriptedProvider):
        async def create(self, **kwargs):
            kwargs["messages"] = kwargs["messages"][:2]
            return await super().create(**kwargs)

    provider = RepeatingProvider()
    count = 0

    async def dispatch(name, args):
        nonlocal count
        count += 1
        return {"report": "Needs more research"}

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_supplier_research",
                "parameters": {"type": "object"},
            },
        }
    ]
    with pytest.raises(llm.AgentFailure, match="eight-step"):
        await llm.reason(
            "coordinator", "coordinator", "brief", tools, dispatch, [], provider
        )
    assert len(provider.calls) == count == 8


@pytest.mark.asyncio
async def test_model_arguments_are_validated_before_dispatch():
    async def dispatch(*args):
        pytest.fail("Invalid tool arguments must not execute")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_supplier_research",
                "parameters": {
                    "type": "object",
                    "properties": {"request": {"type": "integer"}},
                    "required": ["request"],
                },
            },
        }
    ]
    with pytest.raises(llm.AgentFailure, match="invalid tool arguments"):
        await llm.reason(
            "coordinator",
            "coordinator",
            "brief",
            tools,
            dispatch,
            [],
            ScriptedProvider(),
        )
