from src.agentic.agents.base import Specialist
from src.contracts.schemas import CustomerInsights, EngagementInsights


class EngagementAgent(Specialist):
    async def execute(self, state):
        ids = CustomerInsights.model_validate(state["customer_insights"]).eligible_ids
        scores = {cid: await self.tool("get_customer_engagement", customer_id=cid) for cid in ids}
        return EngagementInsights(scores=scores).model_dump()
