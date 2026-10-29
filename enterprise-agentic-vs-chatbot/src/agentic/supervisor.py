from dataclasses import dataclass
from typing import Any
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.agentic.agents.customer_insights import CustomerInsightsAgent
from src.agentic.agents.engagement import EngagementAgent
from src.agentic.agents.offers import OfferAgent
from src.agentic.agents.compliance import ComplianceAgent
from src.agentic.agents.campaign import CampaignAgent
from src.governance.audit import record


@dataclass
class Runtime:
    session: Any
    w: Any
    identity: Any
    gateway: Any
    model: Any


async def orchestrate(runtime):
    def bound(cls, name):
        return cls(name=name).bind(runtime)

    supervisor = SequentialAgent(
        name="supervisor",
        sub_agents=[
            bound(CustomerInsightsAgent, "customer_insights"),
            ParallelAgent(
                name="parallel_analysis",
                sub_agents=[bound(EngagementAgent, "engagement"), bound(OfferAgent, "offers")],
            ),
            bound(ComplianceAgent, "compliance"),
            bound(CampaignAgent, "campaign"),
        ],
    )
    sessions = InMemorySessionService()
    await sessions.create_session(
        app_name="campaign_demo",
        user_id=runtime.identity.user,
        session_id=runtime.w.id,
        state=runtime.w.checkpoint,
    )
    runner = Runner(agent=supervisor, app_name="campaign_demo", session_service=sessions)
    try:
        async for event in runner.run_async(
            user_id=runtime.identity.user,
            session_id=runtime.w.id,
            new_message=types.Content(
                role="user", parts=[types.Part(text="Run the governed campaign workflow.")]
            ),
        ):
            if event.actions.state_delta:
                runtime.w.checkpoint = {**runtime.w.checkpoint, **event.actions.state_delta}
                runtime.session.flush()
                record(
                    runtime.session,
                    runtime.w,
                    runtime.identity,
                    event.author,
                    "agent_result",
                    "ALLOW",
                    "checkpoint",
                )
    finally:
        await runner.close()
