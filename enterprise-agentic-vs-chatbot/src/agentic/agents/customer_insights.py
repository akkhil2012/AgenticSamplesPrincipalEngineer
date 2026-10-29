from src.agentic.agents.base import Specialist
from src.contracts.schemas import CustomerInsights


class CustomerInsightsAgent(Specialist):
    async def execute(self, state):
        customers = await self.tool("get_customer_profile")
        eligible = []
        for c in customers:
            if await self.tool("check_customer_eligibility", customer_id=c["id"]):
                eligible.append(c["id"])
        return CustomerInsights(eligible_ids=eligible, evaluated=len(customers)).model_dump()
