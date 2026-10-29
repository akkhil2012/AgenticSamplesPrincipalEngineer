from src.agentic.agents.base import Specialist
from src.contracts.schemas import CustomerInsights, ComplianceResult
from src.governance.audit import record


class ComplianceAgent(Specialist):
    async def execute(self, state):
        ids = CustomerInsights.model_validate(state["customer_insights"]).eligible_ids
        permitted = []
        for cid in ids:
            allowed = await self.tool("check_marketing_consent", customer_id=cid)
            if allowed:
                permitted.append(cid)
            else:
                r = self._runtime
                record(
                    r.session, r.w, r.identity, self.name, "consent_exclusion", "DENY", "excluded", count=1
                )
        r = self._runtime
        policies = r.gateway.knowledge.retrieve(r.w.tenant)
        return ComplianceResult(
            permitted_ids=permitted,
            excluded_count=len(ids) - len(permitted),
            policy_sources=[{"id": p["id"], "version": p["version"]} for p in policies],
        ).model_dump()
