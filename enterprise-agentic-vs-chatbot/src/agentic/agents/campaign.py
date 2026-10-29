from src.agentic.agents.base import Specialist
from src.contracts.schemas import CampaignPayload, ComplianceResult, EngagementInsights, OfferInsights


class CampaignAgent(Specialist):
    async def execute(self, state):
        compliance = ComplianceResult.model_validate(state["compliance"])
        engagement = EngagementInsights.model_validate(state["engagement"])
        offers = OfferInsights.model_validate(state["offers"])
        ids = compliance.permitted_ids
        payload = CampaignPayload(
            tenant=self._runtime.w.tenant,
            customer_ids=ids,
            offers={cid: offers.offers[cid] for cid in ids},
            engagement={cid: engagement.scores[cid] for cid in ids},
            policy_sources=compliance.policy_sources,
        )
        draft = await self.tool("create_campaign_draft", payload=payload.model_dump())
        approval = await self.tool("submit_for_approval")
        return {**draft, **approval}
