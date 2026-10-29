from src.governance.pdp import Decision
from src.governance.audit import record


class PolicyDenied(Exception):
    pass


class PEP:
    def __init__(self, pdp):
        self.pdp = pdp

    def enforce(self, session, workflow, identity, agent, action, resource_tenant):
        decision = self.pdp.evaluate(identity, agent, action, resource_tenant, workflow)
        record(session, workflow, identity, agent, action, decision.value, "policy_evaluated")
        if decision != Decision.ALLOW:
            raise PolicyDenied(decision.value)
