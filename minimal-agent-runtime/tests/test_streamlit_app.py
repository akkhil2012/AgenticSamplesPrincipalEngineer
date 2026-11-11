"""Exercise actual Streamlit reruns and runtime policy through the UI."""

from pathlib import Path

import pytest

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_chat_policy_memory_and_reset():
    app = AppTest.from_file(str(APP)).run()
    assert not app.exception
    app.button[0].click().run()  # ACC123
    assert "₹50,000" in app.chat_message[1].markdown[0].value
    app.button[1].click().run()  # ACC456 is denied for user1
    runtime = app.session_state.runtime
    assert len(runtime.memory.load(app.session_state.session_id, "user1")) == 1
    assert (
        sum(e["event"] == "tool_execution" for e in runtime.observability.events) == 1
    )
    app.button[2].click().run()  # Previous successful question
    assert "Check ACC123 balance." in app.chat_message[-1].markdown[0].value
    assert not app.exception
    old_session = app.session_state.session_id
    app.sidebar.button[0].click().run()
    assert not app.chat_message
    assert app.session_state.session_id != old_session
    assert not app.session_state.runtime.observability.events


def test_identity_change_and_browser_isolation():
    app = AppTest.from_file(str(APP)).run()
    app.button[0].click().run()
    app.selectbox(key="demo_user").select("user2").run()
    assert not app.chat_message
    app.button[1].click().run()
    assert app.session_state.turns[-1]["result"]["state"] == "COMPLETED"
    other = AppTest.from_file(str(APP)).run()
    assert not other.chat_message
    assert other.session_state.runtime is not app.session_state.runtime
    app.selectbox(key="demo_user").select("stranger").run()
    app.chat_input[0].set_value("Check ACC123 balance").run()
    assert app.session_state.turns[-1]["result"]["state"] == "DENIED"
    assert not any(
        e["event"] == "tool_execution"
        for e in app.session_state.runtime.observability.events
    )
    assert not app.exception


def test_tool_failure_is_safe():
    app = AppTest.from_file(str(APP)).run()

    def fail(account_id):
        raise RuntimeError("private provider error")

    app.session_state.runtime.tools["get_balance"] = fail
    app.chat_input[0].set_value("Check ACC123 balance").run()
    assert app.session_state.turns[-1]["result"]["state"] == "FAILED"
    assert "private provider error" not in str(app.session_state.turns)
    assert not app.exception
