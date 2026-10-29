import asyncio
import json
import time
from uuid import uuid4
from sqlalchemy import select
from src.contracts.schemas import CampaignPayload
from src.governance.audit import record
from src.governance.pdp import digest
from src.governance.pep import PolicyDenied
from src.state.models import Campaign
from src.observability.tracing import tracer


class ToolGateway:
    def __init__(self, settings, pep, knowledge):
        self.pep, self.knowledge = pep, knowledge
        self.customers = json.loads((settings.data_dir / "customers.json").read_text())
        self.engagement = json.loads((settings.data_dir / "engagement.json").read_text())
        self.offers = json.loads((settings.data_dir / "offers.json").read_text())
        self.failures = {}  # Server-side test fault injector. No public endpoint can set this.

    async def invoke(self, session, w, identity, agent, tool, **args):
        resource_tenant = args.get("tenant", w.tenant)
        self.pep.enforce(session, w, identity, agent, tool, resource_tenant)
        customer_id = args.get("customer_id")
        customer = None
        if customer_id:
            customer = next(
                (c for c in self.customers if c["id"] == customer_id and c["tenant"] == w.tenant), None
            )
            if customer is None:
                record(session, w, identity, agent, tool, "DENY", "resource_denied")
                raise PolicyDenied("Resource unavailable")
        for attempt in range(1, 4):
            start = time.perf_counter()
            try:
                with tracer.start_as_current_span("tool." + tool):
                    if self.failures.get(tool, 0) > 0:
                        self.failures[tool] -= 1
                        raise TimeoutError()
                    # Implementations are local, bounded fixture/SQL operations. Remote adapters must enforce I/O timeout.
                    result = self._execute(session, w, tool, customer, args)
                record(
                    session,
                    w,
                    identity,
                    agent,
                    tool,
                    "ALLOW",
                    "success",
                    attempt=attempt,
                    latency_ms=round((time.perf_counter() - start) * 1000, 3),
                )
                return result
            except TimeoutError:
                record(session, w, identity, agent, tool, "ALLOW", "timeout", attempt=attempt)
                if attempt == 3:
                    raise
                await asyncio.sleep(0.01 * attempt)
            except PolicyDenied:
                record(session, w, identity, agent, tool, "DENY", "business_policy_denied", attempt=attempt)
                raise
            except Exception:
                record(session, w, identity, agent, tool, "ALLOW", "failed", attempt=attempt)
                raise

    def _execute(self, session, w, tool, customer, args):
        policies = self.knowledge.retrieve(w.tenant)
        rules = {p["id"]: p["rules"] for p in policies}
        if tool == "get_customer_profile":
            return [c for c in self.customers if c["tenant"] == w.tenant] if customer is None else customer
        if tool == "check_customer_eligibility":
            return (
                customer["income"] >= rules["eligibility"]["min_income"]
                and customer["score"] >= rules["eligibility"]["min_score"]
            )
        if tool == "get_customer_engagement":
            row = next(
                (
                    e
                    for e in self.engagement
                    if e["tenant"] == w.tenant and e["customer_id"] == customer["id"]
                ),
                {},
            )
            return round(row.get("clicks", 0) / max(row.get("sent", 0), 1), 3)
        if tool == "recommend_offer":
            offer = next(
                o for o in self.offers if o["tenant"] == w.tenant and o["segment"] == customer["segment"]
            )
            return offer["id"]
        if tool == "check_marketing_consent":
            return bool(customer["consent"]) and not customer["excluded"]
        if tool == "create_campaign_draft":
            payload = CampaignPayload.model_validate(args["payload"]).model_dump()
            if payload["tenant"] != w.tenant or not payload["customer_ids"]:
                raise PolicyDenied("Empty or invalid tenant campaign")
            # Recheck deterministic eligibility/consent at the consequential boundary.
            for cid in payload["customer_ids"]:
                c = next((c for c in self.customers if c["tenant"] == w.tenant and c["id"] == cid), None)
                if (
                    not c
                    or not c["consent"]
                    or c["excluded"]
                    or c["income"] < rules["eligibility"]["min_income"]
                    or c["score"] < rules["eligibility"]["min_score"]
                ):
                    raise PolicyDenied("Campaign policy violation")
            existing = session.scalar(select(Campaign).where(Campaign.workflow_id == w.id))
            if existing and existing.payload_hash != digest(payload):
                raise PolicyDenied("Immutable draft conflict")
            if not existing:
                existing = Campaign(
                    id=str(uuid4()),
                    workflow_id=w.id,
                    tenant=w.tenant,
                    payload_hash=digest(payload),
                    status="DRAFT",
                )
                session.add(existing)
                session.flush()
            w.payload, w.payload_hash = payload, digest(payload)
            return {"campaign_id": existing.id, "payload_hash": existing.payload_hash}
        if tool == "submit_for_approval":
            return {"approval_required": True, "payload_hash": w.payload_hash}
        if tool == "activate_campaign_simulated":
            # PDP has already revalidated approver, expiry, hash, tenant and workflow state.
            campaign = session.scalar(
                select(Campaign).where(Campaign.workflow_id == w.id, Campaign.tenant == w.tenant)
            )
            if not campaign or campaign.payload_hash != digest(w.payload):
                raise PolicyDenied("Draft integrity check failed")
            for cid in w.payload["customer_ids"]:
                c = next((c for c in self.customers if c["tenant"] == w.tenant and c["id"] == cid), None)
                if (
                    not c
                    or not c["consent"]
                    or c["excluded"]
                    or c["income"] < rules["eligibility"]["min_income"]
                    or c["score"] < rules["eligibility"]["min_score"]
                ):
                    raise PolicyDenied("Customer no longer eligible")
            current_sources = [{"id": p["id"], "version": p["version"]} for p in policies]
            if sorted(current_sources, key=lambda x: x["id"]) != sorted(
                w.payload["policy_sources"], key=lambda x: x["id"]
            ):
                raise PolicyDenied("Policies changed; new proposal required")
            campaign.status = "SIMULATED_ACTIVE"
            return {
                "campaign_id": campaign.id,
                "status": campaign.status,
                "simulation": True,
                "customer_count": len(w.payload["customer_ids"]),
            }
        raise PolicyDenied("Unknown tool")
