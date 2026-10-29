from collections.abc import AsyncGenerator
from typing import Any
from pydantic import PrivateAttr
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from src.observability.tracing import tracer


class Specialist(BaseAgent):
    _runtime: Any = PrivateAttr()

    def bind(self, runtime):
        self._runtime = runtime
        return self

    async def execute(self, state):
        raise NotImplementedError

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        with tracer.start_as_current_span("agent." + self.name):
            # Read-only analyses can resume from persisted validated outputs.
            if self.name in self._runtime.w.checkpoint and self.name in {
                "customer_insights",
                "engagement",
                "offers",
            }:
                output = self._runtime.w.checkpoint[self.name]
            else:
                output = await self.execute(ctx.session.state)
            yield Event(author=self.name, actions=EventActions(state_delta={self.name: output}))

    async def tool(self, tool, **args):
        r = self._runtime
        return await r.gateway.invoke(r.session, r.w, r.identity, self.name, tool, **args)
