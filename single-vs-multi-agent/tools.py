from models import Task

OWNERS = {"ACC123": "user1"}
ACCOUNT_DATA = {
    "ACC123": {"balance": 50000, "credit_score": 760, "monthly_income": 100000}
}


class AccessDenied(Exception):
    pass


def authorized_data(task: Task, metrics, agent, capability):
    # Ownership metadata is checked BEFORE the financial record is read.
    allowed = (
        isinstance(task.user_id, str)
        and bool(task.user_id)
        and OWNERS.get(task.account_id) == task.user_id
    )
    metrics.log("policy_check", agent, capability, "ALLOW" if allowed else "DENY")
    if not allowed:
        raise AccessDenied("Account access denied")
    return ACCOUNT_DATA[task.account_id]


def get_balance(task: Task, metrics, agent):
    metrics.tool_calls += 1
    metrics.log("tool_invocation", agent, "balance")
    data = authorized_data(task, metrics, agent, "balance")
    return {
        "account_id": task.account_id,
        "balance": data["balance"],
        "currency": "INR",
    }


def check_credit_eligibility(task: Task, metrics, agent):
    metrics.tool_calls += 1
    metrics.log("tool_invocation", agent, "credit")
    data = authorized_data(task, metrics, agent, "credit")
    eligible = data["credit_score"] >= 700 and data["monthly_income"] >= 50000
    return {
        "account_id": task.account_id,
        "eligible": eligible,
        "reason": "Credit score and monthly income meet the thresholds."
        if eligible
        else "Credit score or monthly income is below the required threshold.",
    }
