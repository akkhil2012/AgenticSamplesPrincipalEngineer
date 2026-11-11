"""A2A 0.3 JSON-RPC service, using the official SDK's task lifecycle."""

import uvicorn
from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentSkill, DataPart, Part, TextPart
from a2a.utils import new_agent_text_message, new_task
from catalog import ROOT
from dotenv import load_dotenv
from llm import AgentFailure
from sourcing import research

load_dotenv(ROOT / ".env")


class SourcingExecutor(AgentExecutor):
    async def execute(self, context, event_queue):
        task = context.current_task
        if task is None:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()
        trace = []
        try:
            question = context.get_user_input()
            if not question.strip() or len(question) > 12000:
                raise AgentFailure(
                    "Delegated request must contain 1 to 12000 characters."
                )
            report = await research(question, trace)
            await updater.add_artifact(
                [
                    Part(root=TextPart(text=report)),
                    Part(root=DataPart(data={"trace": trace})),
                ],
                name="supplier-research",
            )
            await updater.complete()
        except Exception:  # noqa: BLE001 - redact external failures at the public boundary
            # Keep raw provider/tool exception details out of protocol responses.
            await updater.failed(
                new_agent_text_message(
                    "Supplier research failed. Check the API key, provider, and quote dataset.",
                    context_id=task.context_id,
                    task_id=task.id,
                )
            )

    async def cancel(self, context, event_queue):
        # This blocking POC does not advertise cancellation or streaming support.
        from a2a.types import UnsupportedOperationError
        from a2a.utils.errors import ServerError

        raise ServerError(error=UnsupportedOperationError())


card = AgentCard(
    name="Supplier Research Agent",
    description="Researches supplier quotes, availability, lead times and evidence-based costs.",
    url="http://127.0.0.1:9001/",
    version="1.0.0",
    protocol_version="0.3.0",
    capabilities=AgentCapabilities(streaming=False, push_notifications=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain", "application/json"],
    skills=[
        AgentSkill(
            id="supplier-research",
            name="Supplier research",
            description="Compares supplier options against a buyer's constraints using a quote workspace.",
            tags=["procurement", "quotes", "sourcing"],
            examples=[
                "Research 100 business laptops within USD 85000, delivered in 12 days."
            ],
        )
    ],
)

app = A2AStarletteApplication(
    agent_card=card,
    http_handler=DefaultRequestHandler(
        agent_executor=SourcingExecutor(), task_store=InMemoryTaskStore()
    ),
).build()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9001, log_level="warning")
