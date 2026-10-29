import os
import uuid
import httpx
import streamlit as st

st.set_page_config(page_title="Chatbot vs Agentic Platform", layout="wide")
st.title("Banking campaign: conversation and governed execution")
st.caption("Synthetic data · simulated activation · public demo identities")
base = os.getenv("API_BASE_URL", "http://localhost:8000")
tenant = st.sidebar.selectbox("Tenant", ["a", "b"])
manager = f"demo-manager-{tenant}"
approver = f"demo-approver-{tenant}"
role = st.sidebar.selectbox("Act as", [manager, approver, "demo-compliance-a"])
headers = {"Authorization": f"Bearer {role}"}


def api(method, path, **kwargs):
    try:
        response = httpx.request(method, base + path, headers=headers, timeout=90, **kwargs)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as error:
        text = error.response.text if isinstance(error, httpx.HTTPStatusError) else "Backend unavailable"
        st.error(text)
        return None


prompt = st.text_area(
    "Same request for both systems", "Identify eligible customers and prepare a premium upgrade campaign."
)
if st.button("Run comparison", type="primary"):
    st.session_state.chat = api("POST", "/chatbot/query", json={"message": prompt})
    st.session_state.workflow = api(
        "POST", "/agentic/requests", json={"message": prompt, "idempotency_key": str(uuid.uuid4())}
    )
left, right = st.columns(2)
with left:
    st.subheader("Traditional chatbot")
    result = st.session_state.get("chat")
    if result:
        st.write(result["text"])
        st.json({k: v for k, v in result.items() if k != "text"})
with right:
    st.subheader("Enterprise agentic platform")
    current = st.session_state.get("workflow")
    wid = st.text_input("Resume workflow ID", value=current["workflow_id"] if current else "")
    if wid and st.button("Refresh from durable backend"):
        current = api("GET", f"/agentic/workflows/{wid}")
        st.session_state.workflow = current
    if current and wid == current["workflow_id"]:
        st.write("Workflow", wid, "Status", current["status"])
        events = api("GET", f"/agentic/workflows/{wid}/events")
        if events:
            st.dataframe(events, hide_index=True)
            model_events = [e["details"] for e in events if e["tool"] == "model"]
            st.metric(
                "Estimated model cost (USD)",
                f"{sum(e.get('estimated_cost_usd', 0) for e in model_events):.6f}",
            )
            st.metric("Model latency (ms)", round(sum(e.get("latency_ms", 0) for e in model_events), 2))
        st.write("Validated agent results and enterprise record references")
        st.json(current["checkpoint"])
        st.write("Exact campaign draft for review")
        st.json(current["campaign_draft"] or {})
        st.write("Payload SHA-256", current["payload_hash"])
        st.json(current["approval"] or {})
        if current["status"] == "PENDING_APPROVAL":
            st.info("Switch Act as to the independent approver, review the payload, then approve.")
            decision = st.radio("Decision", ["approve", "reject"], horizontal=True)
            if st.button("Submit independent decision", disabled=role != approver):
                updated = api(
                    "POST",
                    f"/agentic/workflows/{wid}/approval",
                    json={"payload_hash": current["payload_hash"], "decision": decision},
                )
                if updated:
                    st.session_state.workflow = updated
                    st.rerun()
        if current["status"] in {"APPROVED", "FAILED"}:
            path = "execute" if current["approval"] else "retry"
            if st.button("Resume safely"):
                updated = api("POST", f"/agentic/workflows/{wid}/{path}")
                if updated:
                    st.session_state.workflow = updated
                    st.rerun()
        if current["error"]:
            st.error(current["error"])
        st.write("Business outcome")
        st.json(current["outcome"] or {})
