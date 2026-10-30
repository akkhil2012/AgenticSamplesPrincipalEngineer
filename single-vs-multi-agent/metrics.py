import json
import logging
import time
from uuid import uuid4


class Metrics:
    """One correlation context per top-level request, shared with delegated specialists."""

    def __init__(self):
        self.correlation_id = str(uuid4())
        self.started = time.perf_counter()
        self.model_calls = 0
        self.tool_calls = 0
        self.agent_calls = 0
        self.errors = []
        self.events = []

    def log(self, event, agent, capability=None, status=None):
        entry = {"correlation_id": self.correlation_id, "event": event, "agent": agent}
        if capability is not None:
            entry["capability"] = capability
        if status is not None:
            entry["status"] = status
        self.events.append(entry)
        logging.getLogger("banking_comparison").info(json.dumps(entry))

    def agent_started(self, agent):
        self.agent_calls += 1
        self.log("agent_started", agent)

    def error(self, agent, capability, code):
        self.errors.append(
            {
                "correlation_id": self.correlation_id,
                "agent": agent,
                "capability": capability,
                "code": code,
            }
        )
        self.log("execution_error", agent, capability, code)

    def snapshot(self):
        return {
            "correlation_id": self.correlation_id,
            "duration_ms": round((time.perf_counter() - self.started) * 1000, 3),
            "model_calls": self.model_calls,
            "tool_calls": self.tool_calls,
            "agent_calls": self.agent_calls,
        }


def configure_logging():
    logger = logging.getLogger("banking_comparison")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
