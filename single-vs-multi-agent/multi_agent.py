from metrics import Metrics
from models import Model, Task, BalanceResult, CreditResult, finish, select_plan
import tools


class AccountAgent:
    description = "Account specialist: retrieve an authorized account balance; no credit responsibility."

    def run(self, task: Task, metrics: Metrics):
        metrics.agent_started("AccountAgent")
        try:
            result = BalanceResult.validate(
                tools.get_balance(task, metrics, "AccountAgent"), task.account_id
            )
        except Exception:
            metrics.log("agent_finished", "AccountAgent", "balance", "FAILED")
            raise
        metrics.log("agent_finished", "AccountAgent", "balance", "COMPLETED")
        return result


class CreditAgent:
    description = "Credit specialist: evaluate illustrative card eligibility; no balance responsibility."

    def __init__(self, fail=False):
        self.fail = fail

    def run(self, task: Task, metrics: Metrics):
        metrics.agent_started("CreditAgent")
        try:
            if self.fail:
                raise RuntimeError("Simulated specialist failure")
            result = CreditResult.validate(
                tools.check_credit_eligibility(task, metrics, "CreditAgent"),
                task.account_id,
            )
        except Exception:
            metrics.log("agent_finished", "CreditAgent", "credit", "FAILED")
            raise
        metrics.log("agent_finished", "CreditAgent", "credit", "COMPLETED")
        return result


class SupervisorAgent:
    description = "Plan, delegate typed tasks and aggregate validated specialist results; never invoke their tools."

    def __init__(self, model=None, account_agent=None, credit_agent=None):
        self.model = model or Model()
        self.account_agent = account_agent or AccountAgent()
        self.credit_agent = credit_agent or CreditAgent()

    def run(self, user_id, message):
        metrics = Metrics()
        metrics.agent_started("SupervisorAgent")
        try:
            plan = select_plan(self.model, message, metrics, "SupervisorAgent")
        except Exception:
            metrics.error("SupervisorAgent", "planning", "planning_failed")
            return finish("SupervisorAgent", None, {}, metrics)
        task, results = Task(user_id, plan.account_id), {}
        specialists = {
            "balance": (self.account_agent, BalanceResult),
            "credit": (self.credit_agent, CreditResult),
        }
        for capability in plan.capabilities:
            specialist, contract = specialists[capability]
            metrics.log("delegation", "SupervisorAgent", capability)
            try:
                # Only the scoped task crosses this boundary, not the entire request or other agent's output.
                raw = specialist.run(task, metrics)
                results[capability] = contract.validate(raw, task.account_id)
            except Exception as error:
                metrics.error(
                    type(specialist).__name__,
                    capability,
                    "access_denied"
                    if isinstance(error, tools.AccessDenied)
                    else "specialist_failed",
                )
        return finish("SupervisorAgent", plan, results, metrics)
