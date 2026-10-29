from src.agentic.agents.base import Specialist
from src.contracts.schemas import CustomerInsights, OfferInsights
from src.governance.audit import record


class OfferAgent(Specialist):
    async def execute(self, state):
        ids = CustomerInsights.model_validate(state["customer_insights"]).eligible_ids
        offers = {cid: await self.tool("recommend_offer", customer_id=cid) for cid in ids}
        r = self._runtime
        policies = r.gateway.knowledge.retrieve(r.w.tenant)
        context = "\n".join(f"[{p['id']} v{p['version']}] {p['text']}" for p in policies)
        # Retrieval-augmented explanation only. Selection/authorization never depend on generated text.
        explanation = await r.model.generate(
            "Explain these segment-based offer recommendations using only the "
            "following policy context. Describe recommendations, not completed actions.\n"
            + context
            + "\nOffer catalog references: "
            + ", ".join(sorted(set(offers.values())))
        )
        record(
            r.session,
            r.w,
            r.identity,
            self.name,
            "model",
            "ALLOW",
            "success",
            **explanation.model_dump(exclude={"text"}),
        )
        return OfferInsights(offers=offers, rationale=explanation.text).model_dump()
