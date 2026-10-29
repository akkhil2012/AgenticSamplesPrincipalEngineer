import time
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import select
from src.agentic.supervisor import Runtime, orchestrate
from src.contracts.schemas import Intent
from src.governance.audit import record
from src.governance.pdp import digest, valid_approval
from src.governance.pep import PolicyDenied
from src.state.models import Workflow

TRANSITIONS = {
    "CREATED": {"RUNNING", "CANCELLED"},
    "RUNNING": {"PENDING_APPROVAL", "COMPLETED", "FAILED"},
    "PENDING_APPROVAL": {"APPROVED", "REJECTED", "CANCELLED"},
    "APPROVED": {"COMPLETED", "FAILED", "CANCELLED"},
    "FAILED": {"RUNNING", "APPROVED", "CANCELLED"},
    "COMPLETED": set(),
    "REJECTED": set(),
    "CANCELLED": set(),
}


def transition(session, w, identity, status):
    if status not in TRANSITIONS[w.status]:
        raise HTTPException(409, "Invalid workflow transition")
    w.status = status
    record(session, w, identity, "supervisor", "transition", "ALLOW", "persisted", status=status)


def view(w):
    return {
        "workflow_id": w.id,
        "tenant": w.tenant,
        "requester": w.requester,
        "status": w.status,
        "correlation_id": w.correlation_id,
        "checkpoint": w.checkpoint,
        "campaign_draft": w.payload,
        "payload_hash": w.payload_hash,
        "approval": w.approval,
        "outcome": w.outcome,
        "error": w.error,
        "attempts": w.attempts,
    }


class WorkflowService:
    def __init__(self, repo, gateway, model, settings):
        self.repo, self.gateway, self.model, self.settings = repo, gateway, model, settings

    async def create(self, request, identity, correlation_id):
        if identity.role != "campaign_manager":
            raise HTTPException(403, "campaign_manager role required")
        with self.repo.transaction() as session:
            existing = session.scalar(
                select(Workflow).where(
                    Workflow.tenant == identity.tenant,
                    Workflow.requester == identity.user,
                    Workflow.idempotency_key == request.idempotency_key,
                )
            )
            if existing:
                if existing.message != request.message:
                    raise HTTPException(409, "Idempotency key reused for a different request")
                return view(existing)
            w = Workflow(
                id=str(uuid4()),
                tenant=identity.tenant,
                requester=identity.user,
                idempotency_key=request.idempotency_key,
                message=request.message,
                correlation_id=correlation_id,
                checkpoint={},
                status="CREATED",
            )
            session.add(w)
            session.flush()
            record(session, w, identity, "supervisor", "create_workflow", "ALLOW", "created")
            wid = w.id
        return await self.run(wid, identity)

    async def run(self, wid, identity):
        with self.repo.transaction() as session:
            w = self.repo.visible(session, wid, identity)
            if identity.user != w.requester or identity.role != "campaign_manager":
                raise HTTPException(403, "Only requester can resume analysis")
            if w.status not in {"CREATED", "FAILED"} or w.approval:
                raise HTTPException(409, "Workflow cannot resume analysis")
            if w.attempts >= 3:
                raise HTTPException(409, "Workflow retry budget exhausted")
            transition(session, w, identity, "RUNNING")
            w.attempts += 1
            w.error = None
            try:
                if "activate" in w.message.lower():
                    record(
                        session,
                        w,
                        identity,
                        "supervisor",
                        "activate_campaign_simulated",
                        "DENY",
                        "approval_required",
                    )
                    raise PolicyDenied("Explicit independent approval required")
                model_result = await self.model.generate(w.message, structured=True)
                intent = Intent.model_validate_json(model_result.text)
                w.checkpoint = {**w.checkpoint, "model_usage": model_result.model_dump(exclude={"text"})}
                record(
                    session,
                    w,
                    identity,
                    "supervisor",
                    "model",
                    "ALLOW",
                    "success",
                    **model_result.model_dump(exclude={"text"}),
                )
                if intent.intent == "information":
                    answer = await self.model.generate(w.message)
                    record(
                        session,
                        w,
                        identity,
                        "supervisor",
                        "model",
                        "ALLOW",
                        "success",
                        **answer.model_dump(exclude={"text"}),
                    )
                    w.outcome = {"kind": "information", "text": answer.text, "business_actions": 0}
                    transition(session, w, identity, "COMPLETED")
                else:
                    await orchestrate(Runtime(session, w, identity, self.gateway, self.model))
                    transition(session, w, identity, "PENDING_APPROVAL")
            except Exception as exc:
                w.error = (
                    "Policy denied"
                    if isinstance(exc, PolicyDenied)
                    else "Execution failed safely; inspect audit and retry"
                )
                record(
                    session,
                    w,
                    identity,
                    "supervisor",
                    "workflow",
                    "DENY" if isinstance(exc, PolicyDenied) else "ALLOW",
                    "failed",
                )
                transition(session, w, identity, "FAILED")
            return view(w)

    async def approve(self, wid, identity, approval):
        error = None
        with self.repo.transaction() as session:
            w = self.repo.visible(session, wid, identity)
            if identity.role != "campaign_approver" or identity.user == w.requester:
                error = HTTPException(403, "Independent campaign_approver required")
            elif w.status != "PENDING_APPROVAL":
                error = HTTPException(409, "Workflow is not pending approval")
            elif approval.payload_hash != w.payload_hash or digest(w.payload) != w.payload_hash:
                error = HTTPException(409, "Approval payload mismatch")
            if error:
                record(session, w, identity, "human", "approval", "DENY", "rejected")
            elif approval.decision == "reject":
                transition(session, w, identity, "REJECTED")
                return view(w)
            else:
                w.approval = {
                    "approver": identity.user,
                    "tenant": identity.tenant,
                    "role": identity.role,
                    "payload_hash": approval.payload_hash,
                    "expires_at": time.time() + self.settings.approval_ttl,
                }
                transition(session, w, identity, "APPROVED")
        if error:
            raise error
        # A committed APPROVED checkpoint permits safe resume if the process exits here.
        return await self.execute(wid, identity)

    async def execute(self, wid, identity):
        error = None
        with self.repo.transaction() as session:
            w = self.repo.visible(session, wid, identity)
            if identity.role != "campaign_approver" or identity.user != (w.approval or {}).get("approver"):
                record(
                    session, w, identity, "campaign", "activate_campaign_simulated", "DENY", "unauthorized"
                )
                error = HTTPException(403, "Original independent approver required")
            elif w.status == "COMPLETED":
                return view(w)
            elif w.status not in {"APPROVED", "FAILED"} or not valid_approval(w):
                record(
                    session,
                    w,
                    identity,
                    "campaign",
                    "activate_campaign_simulated",
                    "APPROVAL_REQUIRED",
                    "invalid_approval",
                )
                error = HTTPException(409, "Valid unexpired payload-bound approval required")
            elif w.attempts >= 6:
                error = HTTPException(409, "Execution retry budget exhausted")
            else:
                if w.status == "FAILED":
                    transition(session, w, identity, "APPROVED")
                w.attempts += 1
                try:
                    w.outcome = await self.gateway.invoke(
                        session, w, identity, "campaign", "activate_campaign_simulated"
                    )
                    w.error = None
                    transition(session, w, identity, "COMPLETED")
                except Exception:
                    w.error = "Activation failed safely; revalidate approval before retry"
                    transition(session, w, identity, "FAILED")
            result = view(w)
        if error:
            raise error
        return result

    def cancel(self, wid, identity):
        with self.repo.transaction() as session:
            w = self.repo.visible(session, wid, identity)
            if identity.user != w.requester or identity.role != "campaign_manager":
                raise HTTPException(403, "Requester required")
            transition(session, w, identity, "CANCELLED")
            return view(w)
