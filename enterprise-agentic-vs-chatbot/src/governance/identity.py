import secrets
from dataclasses import dataclass
from fastapi import HTTPException


@dataclass(frozen=True)
class Identity:
    user: str
    tenant: str
    role: str


# Deliberately public, synthetic demo identities. Never use for production authentication.
DEMO_USERS = {
    "demo-manager-a": Identity("manager-a", "bank-a", "campaign_manager"),
    "demo-approver-a": Identity("approver-a", "bank-a", "campaign_approver"),
    "demo-compliance-a": Identity("compliance-a", "bank-a", "compliance_officer"),
    "demo-manager-b": Identity("manager-b", "bank-b", "campaign_manager"),
    "demo-approver-b": Identity("approver-b", "bank-b", "campaign_approver"),
}


def authenticate(header: str | None, enabled: bool) -> Identity:
    if enabled and header and header.startswith("Bearer "):
        for token, identity in DEMO_USERS.items():
            if secrets.compare_digest(header[7:], token):
                return identity
    raise HTTPException(401, "Valid demo bearer token required; DEMO_AUTH must be enabled")
