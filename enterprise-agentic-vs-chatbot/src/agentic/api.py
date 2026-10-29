import asyncio
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from src.contracts.schemas import Request as CampaignRequest, Approval
from src.dependencies import identity
from src.agentic.workflow import view
from src.state.models import AuditEvent

router = APIRouter(prefix="/agentic", tags=["agentic"])


@router.post("/requests")
def create(body: CampaignRequest, request: Request, actor=Depends(identity)):
    return asyncio.run(request.app.state.workflows.create(body, actor, request.state.correlation_id))


@router.get("/workflows/{wid}")
def get(wid: str, request: Request, actor=Depends(identity)):
    repo = request.app.state.repo
    with repo.sessions() as session:
        return view(repo.visible(session, wid, actor))


@router.get("/workflows/{wid}/events")
def events(wid: str, request: Request, actor=Depends(identity)):
    repo = request.app.state.repo
    with repo.sessions() as session:
        repo.visible(session, wid, actor)
        rows = session.scalars(
            select(AuditEvent)
            .where(AuditEvent.workflow_id == wid, AuditEvent.tenant == actor.tenant)
            .order_by(AuditEvent.id)
        ).all()
        return [
            {
                "id": e.id,
                "workflow_id": e.workflow_id,
                "timestamp": e.timestamp.isoformat(),
                "actor": e.actor,
                "tenant": e.tenant,
                "agent": e.agent,
                "tool": e.tool,
                "decision": e.decision,
                "outcome": e.outcome,
                "details": e.details,
            }
            for e in rows
        ]


@router.post("/workflows/{wid}/approval")
def approve(wid: str, body: Approval, request: Request, actor=Depends(identity)):
    return asyncio.run(request.app.state.workflows.approve(wid, actor, body))


@router.post("/workflows/{wid}/execute")
def execute(wid: str, request: Request, actor=Depends(identity)):
    return asyncio.run(request.app.state.workflows.execute(wid, actor))


@router.post("/workflows/{wid}/retry")
def retry(wid: str, request: Request, actor=Depends(identity)):
    return asyncio.run(request.app.state.workflows.run(wid, actor))


@router.post("/workflows/{wid}/cancel")
def cancel(wid: str, request: Request, actor=Depends(identity)):
    return request.app.state.workflows.cancel(wid, actor)
