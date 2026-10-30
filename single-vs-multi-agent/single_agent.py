from metrics import Metrics
from models import Model, Task, BalanceResult, CreditResult, finish, select_plan
import tools


class BankingAgent:
    description = "One agent understands the request, executes banking tools and combines their results."

    def __init__(self, model=None):
        self.model = model or Model()

    def run(self, user_id, message):
        metrics = Metrics()
        metrics.agent_started("BankingAgent")
        try:
            plan = select_plan(self.model, message, metrics, "BankingAgent")
        except Exception:
            metrics.error("BankingAgent", "planning", "planning_failed")
            return finish("BankingAgent", None, {}, metrics)
        task, results = Task(user_id, plan.account_id), {}
        dispatch = {
            "balance": (tools.get_balance, BalanceResult),
            "credit": (tools.check_credit_eligibility, CreditResult),
        }
        for capability in plan.capabilities:
            function, contract = dispatch[capability]
            try:
                results[capability] = contract.validate(
                    function(task, metrics, "BankingAgent"), task.account_id
                )
            except Exception as error:
                metrics.error(
                    "BankingAgent",
                    capability,
                    "access_denied"
                    if isinstance(error, tools.AccessDenied)
                    else "tool_failed",
                )
        return finish("BankingAgent", plan, results, metrics)
