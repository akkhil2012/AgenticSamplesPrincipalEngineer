from src.state.models import AuditEvent

# Only allowlisted, non-PII facts enter evidence. Never store prompts, tool arguments or exceptions.
SAFE = {
    "attempt",
    "count",
    "status",
    "payload_hash",
    "latency_ms",
    "model",
    "prompt_tokens",
    "completion_tokens",
    "estimated_cost_usd",
    "fallback",
    "policy_ids",
    "stage",
}


def record(session, w, identity, agent, tool, decision, outcome, **details):
    session.add(
        AuditEvent(
            workflow_id=w.id,
            tenant=w.tenant,
            actor=identity.user,
            agent=agent,
            tool=tool,
            decision=decision,
            outcome=outcome,
            details={k: v for k, v in details.items() if k in SAFE},
        )
    )
