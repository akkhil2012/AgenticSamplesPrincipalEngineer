"""Session-local Streamlit interface for the synthetic banking runtime."""

from uuid import uuid4

import streamlit as st
from agent import AgentRuntime
from model import Model


def reset_session():
    # Never cache a runtime globally: memory and request data belong to one browser.
    st.session_state.runtime = AgentRuntime(model=Model(mode="mock"))
    st.session_state.session_id = str(uuid4())
    st.session_state.turns = []


def main():
    st.set_page_config(page_title="Agent Runtime Lab", page_icon="🏦", layout="wide")
    if "runtime" not in st.session_state:
        reset_session()

    with st.sidebar:
        st.title("Runtime settings")
        st.caption("Synthetic banking demo · no API key required")
        user_id = st.selectbox(
            "Demo user",
            ["user1", "user2", "stranger"],
            key="demo_user",
            on_change=reset_session,
        )
        st.info("user1 → ACC123\n\nuser2 → ACC456\n\nstranger → no account access")
        st.caption(
            "Demo identities are selectable for learning; this is not authentication."
        )
        st.button("New conversation", on_click=reset_session, use_container_width=True)
        st.caption(f"Session: {st.session_state.session_id}")
        st.caption("Model: deterministic mock. No provider calls are made by this UI.")

    st.title("Agent Runtime Lab")
    st.write(
        "Ask a question. Follow the policy decision, tool execution, and memory behind the answer."
    )
    st.caption(
        "All accounts and balances are synthetic. Conversation data stays in this browser session's server memory until reset or session expiry."
    )
    chat, inspector = st.columns([3, 2], gap="large")
    prompt = None
    with chat:
        st.subheader("Banking assistant")
        examples = st.columns(3)
        for column, label, message in zip(
            examples,
            ["Check ACC123", "Check ACC456", "Recall previous question"],
            [
                "Check ACC123 balance.",
                "Check ACC456 balance.",
                "What was my previous question?",
            ],
        ):
            if column.button(label, use_container_width=True):
                prompt = message
        for turn in st.session_state.turns:
            with st.chat_message("user"):
                st.write(turn["message"])
            with st.chat_message("assistant"):
                st.write(turn["result"]["response"])
                st.caption(
                    f"{turn['result']['state']} · {turn['result']['latency_ms']} ms"
                )
        typed = st.chat_input(
            "Ask for an account balance or recall your previous question",
            max_chars=2000,
        )
        prompt = typed or prompt
        if prompt and prompt.strip():
            with st.spinner("Running agent…"):
                result = st.session_state.runtime.run(
                    user_id, prompt, st.session_state.session_id
                )
            st.session_state.turns.append({"message": prompt, "result": result})
            st.rerun()

    with inspector:
        st.subheader("Request inspector")
        if not st.session_state.turns:
            st.info("Send a request to inspect its execution.")
            return
        turns = st.session_state.turns
        selected = st.selectbox(
            "Request",
            range(len(turns)),
            index=len(turns) - 1,
            format_func=lambda i: f"Turn {i + 1} · {turns[i]['result']['state']}",
        )
        result = turns[selected]["result"]
        events = [
            event
            for event in st.session_state.runtime.observability.events
            if event["request_id"] == result["request_id"]
        ]
        status = result["state"]
        if status == "COMPLETED":
            st.success(status)
        elif status == "DENIED":
            st.warning(f"{status} · {result['error']}")
        else:
            st.error(f"{status} · {result['error']}")
        st.write(" → ".join(result["history"]))
        metrics = st.columns(2)
        metrics[0].metric("Latency", f"{result['latency_ms']} ms")
        metrics[1].metric(
            "Tool calls", sum(e["event"] == "tool_execution" for e in events)
        )
        st.caption(f"Request: {result['request_id']}")
        st.write("Selected tool:", result["selected_tool"] or "None")
        with st.expander("Safe runtime events", expanded=True):
            st.json(events)
        with st.expander("Conversation memory"):
            st.caption(
                "Only successful turns enter model context. Denied and failed requests remain visible in chat but are excluded from memory."
            )
            st.json(
                st.session_state.runtime.memory.load(
                    st.session_state.session_id, user_id
                )
            )


if __name__ == "__main__":
    main()
