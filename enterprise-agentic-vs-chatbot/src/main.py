from collections import defaultdict, deque
import time
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.config import Settings
from src.state.repository import Repository
from src.governance.pdp import PDP
from src.governance.pep import PEP
from src.gateways.tool_gateway import ToolGateway
from src.gateways.model_gateway import ModelGateway
from src.knowledge.retrieval import KnowledgeService
from src.chatbot.service import ChatbotService
from src.agentic.workflow import WorkflowService
from src.chatbot.api import router as chatbot_router
from src.agentic.api import router as agentic_router
from src.governance.identity import authenticate
from src.observability.tracing import tracer


def create_app(settings=None):
    settings = settings or Settings()
    app = FastAPI(title="Chatbot vs Enterprise Agentic Platform", version="0.1.0")
    app.state.settings = settings
    repo = app.state.repo = Repository(settings.database_url)
    model = app.state.model = ModelGateway(settings)
    gateway = app.state.gateway = ToolGateway(settings, PEP(PDP()), KnowledgeService(settings.data_dir))
    app.state.chatbot = ChatbotService(model)
    app.state.workflows = WorkflowService(repo, gateway, model, settings)
    buckets = defaultdict(deque)

    @app.middleware("http")
    async def context(request: Request, call_next):
        request.state.correlation_id = str(uuid4())
        key = request.client.host if request.client else "local"
        if request.url.path.startswith("/agentic"):
            try:
                actor = authenticate(request.headers.get("authorization"), settings.demo_auth)
                key = actor.tenant + ":" + actor.user
            except Exception:
                response = JSONResponse({"detail": "Valid demo bearer token required"}, status_code=401)
                response.headers["X-Correlation-ID"] = request.state.correlation_id
                return response
        now = time.monotonic()
        # Bound memory even if many unauthenticated chatbot clients connect.
        for stale in [k for k, v in buckets.items() if not v or v[-1] <= now - 60]:
            del buckets[stale]
        bucket = buckets[key]
        while bucket and bucket[0] <= now - 60:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit:
            response = JSONResponse(
                {"detail": "Rate limit exceeded"}, status_code=429, headers={"Retry-After": "60"}
            )
        else:
            bucket.append(now)
            with tracer.start_as_current_span("http.request") as span:
                span.set_attribute("correlation_id", request.state.correlation_id)
                span.set_attribute("http.method", request.method)
                # Avoid URL paths, prompts and customer identifiers in spans.
                response = await call_next(request)
                span.set_attribute("http.status_code", response.status_code)
        response.headers["X-Correlation-ID"] = request.state.correlation_id
        return response

    @app.get("/health")
    def health():
        return {"status": "ok", "simulation": True, "model": settings.model}

    app.include_router(chatbot_router)
    app.include_router(agentic_router)
    return app


app = create_app()
