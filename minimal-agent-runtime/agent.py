import re
import time
from uuid import uuid4
from memory import ConversationMemory
from model import Model, validate_decision
from observability import Observability
from policy import authorize
from state import StateManager
from tools import get_account_balance, validate_balance_result


class AgentRuntime:
    def __init__(
        self, model=None, memory=None, state=None, observability=None, balance_tool=None
    ):
        self.model = model or Model()
        self.memory = memory or ConversationMemory()
        self.state = state or StateManager()
        self.observability = observability or Observability()
        # Fixed dispatch map: never eval, exec, getattr or arbitrary imports from model text.
        self.tools = {"get_balance": balance_tool or get_account_balance}

    def run(self, user_id, message, session_id=None):
        start = time.perf_counter()
        session_id = session_id or str(uuid4())
        request_id = self.state.create(session_id)
        record = self.state.requests[request_id]
        response = "The request could not be completed safely."

        def event(name, **metadata):
            self.observability.emit(name, request_id, record["state"], **metadata)

        def transition(target):
            self.state.transition(request_id, target)
            event("state_changed")

        event("request_received")
        transition("RUNNING")
        try:
            if (
                not isinstance(user_id, str)
                or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", user_id)
                or not isinstance(session_id, str)
                or not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", session_id)
                or not isinstance(message, str)
                or not 0 < len(message.strip()) <= 2000
            ):
                raise ValueError("Invalid request")
            try:
                history = self.memory.load(session_id, user_id)
            except PermissionError:
                event("session_policy", decision="DENY")
                transition("DENIED")
                record["error"] = "Session access denied"
                response = "Access denied for this session."
            else:
                event("memory_loaded")
                event("model_invocation")
                decision = validate_decision(self.model.decide(message, history))
                event(
                    "model_decision",
                    tool=decision.action if decision.action == "get_balance" else None,
                )
                if decision.action == "get_balance":
                    record["selected_tool"] = "get_balance"
                    # Policy Enforcement Point: gate immediately before the only sensitive tool call.
                    allowed = authorize(user_id, decision.account_id)
                    event(
                        "policy_check",
                        decision="ALLOW" if allowed else "DENY",
                        tool="get_balance",
                    )
                    if not allowed:
                        transition("DENIED")
                        record["error"] = "Account access denied"
                        response = "Access denied. You are not authorized to view this account."
                    else:
                        transition("TOOL_EXECUTING")
                        event("tool_execution", tool="get_balance")
                        result = self.tools["get_balance"](decision.account_id)
                        result = validate_balance_result(result, decision.account_id)
                        record["tool_result"] = result
                        event("tool_completed", tool="get_balance")
                        response = f"The balance of account {decision.account_id} is ₹{result['balance']:,}."
                else:
                    response = decision.response
                if record["state"] != "DENIED":
                    self.memory.save(session_id, user_id, message, response)
                    event("memory_updated")
                    transition("COMPLETED")
        except Exception:
            # Provider/tool exceptions may contain balances, credentials or raw prompts: discard them.
            record["error"] = "Execution failed safely"
            transition("FAILED")
            response = "The request could not be completed safely."
            event("execution_error")
        finally:
            record["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
            event(
                "request_finished",
                status=record["state"],
                latency_ms=record["latency_ms"],
            )
        return {**self.state.get(request_id), "response": response}
