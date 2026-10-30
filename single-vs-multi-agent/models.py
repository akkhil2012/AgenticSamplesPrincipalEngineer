import json
import os
import re
import urllib.request
from dataclasses import asdict, dataclass

CAPABILITIES = ("balance", "credit")
REQUEST = "Check my account balance for ACC123 and tell me whether I am eligible for a credit card."


@dataclass(frozen=True)
class Task:
    user_id: str
    account_id: str


@dataclass(frozen=True)
class Plan:
    account_id: str
    capabilities: tuple[str, ...]

    @classmethod
    def validate(cls, raw):
        if not isinstance(raw, dict) or set(raw) != {"account_id", "capabilities"}:
            raise ValueError("Invalid plan shape")
        account, capabilities = raw["account_id"], raw["capabilities"]
        if not isinstance(account, str) or not re.fullmatch(r"ACC[0-9]{3}", account):
            raise ValueError("Invalid account")
        if (
            not isinstance(capabilities, list)
            or not 1 <= len(capabilities) <= 2
            or any(type(c) is not str or c not in CAPABILITIES for c in capabilities)
            or len(set(capabilities)) != len(capabilities)
        ):
            raise ValueError("Invalid capability selection")
        return cls(account, tuple(capabilities))


@dataclass(frozen=True)
class BalanceResult:
    account_id: str
    balance: int
    currency: str

    @classmethod
    def validate(cls, raw, account):
        raw = asdict(raw) if type(raw) is cls else raw
        if (
            not isinstance(raw, dict)
            or set(raw) != {"account_id", "balance", "currency"}
            or raw["account_id"] != account
            or raw["currency"] != "INR"
            or type(raw["balance"]) is not int
            or raw["balance"] < 0
        ):
            raise ValueError("Invalid account result")
        return cls(**raw)


@dataclass(frozen=True)
class CreditResult:
    account_id: str
    eligible: bool
    reason: str

    @classmethod
    def validate(cls, raw, account):
        raw = asdict(raw) if type(raw) is cls else raw
        if (
            not isinstance(raw, dict)
            or set(raw) != {"account_id", "eligible", "reason"}
            or raw["account_id"] != account
            or type(raw["eligible"]) is not bool
            or not isinstance(raw["reason"], str)
            or not 0 < len(raw["reason"]) <= 500
        ):
            raise ValueError("Invalid eligibility result")
        return cls(**raw)


class Model:
    """The mock supplies a structured fixture plan; orchestration never routes on prompt keywords."""

    def __init__(self, mode=None):
        self.mode = mode or os.getenv("LLM_MODE", "mock")
        if self.mode not in {"mock", "openai"}:
            raise ValueError("Invalid LLM_MODE")

    def select(self, message):
        if self.mode == "mock":
            accounts = set(re.findall(r"\bACC[0-9]{3}\b", message.upper()))
            if len(accounts) != 1:
                raise ValueError("Mock scenario requires one account")
            # A deterministic model double for this banking use case, not a general language parser.
            return {"account_id": accounts.pop(), "capabilities": ["balance", "credit"]}
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("Missing API key")
        body = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "temperature": 0,
            "max_tokens": 200,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": 'Return a JSON object with exactly account_id and capabilities; for example {"account_id":"ACC123","capabilities":["balance","credit"]}. '
                    "Select only the needed capabilities: balance retrieves an account balance; "
                    "credit checks credit card eligibility. Choose one or both, with no duplicate or unknown capability. "
                    "Use the account referenced in the request. Do not provide financial results or permissions.",
                },
                {"role": "user", "content": message},
            ],
        }
        url = (
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            + "/chat/completions"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + key,
            },
        )
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "10"))
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("Response too large")
        return json.loads(json.loads(raw)["choices"][0]["message"]["content"])


def finish(architecture, plan, results, metrics):
    if not metrics.errors:
        status = "COMPLETED"
    elif results:
        status = "PARTIAL"
    elif all(e["code"] == "access_denied" for e in metrics.errors):
        status = "DENIED"
    else:
        status = "FAILED"
    sentences = []
    if "balance" in results:
        sentences.append(
            f"Account {plan.account_id} balance: ₹{results['balance'].balance:,}."
        )
    elif plan and "balance" in plan.capabilities:
        sentences.append("Account balance is unavailable.")
    if "credit" in results:
        credit = results["credit"]
        sentences.append(
            ("Eligible" if credit.eligible else "Not eligible")
            + " for a credit card under the illustrative rules. "
            + credit.reason
        )
    elif plan and "credit" in plan.capabilities:
        sentences.append(
            "Credit card eligibility is unavailable; no eligibility conclusion was made."
        )
    metrics.log("agent_finished", architecture, status=status)
    return {
        "architecture": architecture,
        "account_id": plan.account_id if plan else None,
        "status": status,
        "results": {k: asdict(v) for k, v in results.items()},
        "response": " ".join(sentences) or "The request could not be completed safely.",
        "errors": list(metrics.errors),
        "metrics": metrics.snapshot(),
    }


def select_plan(model, message, metrics, agent):
    if not isinstance(message, str) or not 0 < len(message.strip()) <= 2000:
        raise ValueError("Invalid request")
    metrics.model_calls += 1
    metrics.log("model_invocation", agent)
    return Plan.validate(model.select(message))
