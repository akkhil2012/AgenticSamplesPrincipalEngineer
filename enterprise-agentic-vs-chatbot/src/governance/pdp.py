import hashlib
import json
import time
from enum import StrEnum


class Decision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


PERMISSIONS = {
    "customer_insights": {"get_customer_profile", "check_customer_eligibility"},
    "engagement": {"get_customer_engagement"},
    "offers": {"recommend_offer"},
    "compliance": {"check_marketing_consent"},
    "campaign": {"create_campaign_draft", "submit_for_approval", "activate_campaign_simulated"},
}


def digest(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def valid_approval(w):
    a = w.approval or {}
    return (
        w.payload is not None
        and a.get("payload_hash") == digest(w.payload) == w.payload_hash
        and a.get("tenant") == w.tenant
        and a.get("approver") != w.requester
        and a.get("role") == "campaign_approver"
        and a.get("expires_at", 0) > time.time()
    )


class PDP:
    def evaluate(self, identity, agent, action, resource_tenant, workflow):
        if identity.tenant != resource_tenant or identity.tenant != workflow.tenant:
            return Decision.DENY
        if action not in PERMISSIONS.get(agent, set()):
            return Decision.DENY
        if action == "activate_campaign_simulated":
            if identity.role != "campaign_approver" or identity.user != (workflow.approval or {}).get(
                "approver"
            ):
                return Decision.DENY
            return (
                Decision.ALLOW
                if workflow.status == "APPROVED" and valid_approval(workflow)
                else Decision.APPROVAL_REQUIRED
            )
        if identity.role != "campaign_manager" or identity.user != workflow.requester:
            return Decision.DENY
        return Decision.ALLOW
