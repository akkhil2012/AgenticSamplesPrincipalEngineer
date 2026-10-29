import json
import logging


class Observability:
    """Only allowlisted metadata enters logs. No prompts, balances, secrets or raw errors."""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("minimal_agent_runtime")
        self.events = []

    def emit(
        self,
        event,
        request_id,
        state,
        *,
        decision=None,
        tool=None,
        latency_ms=None,
        status=None,
    ):
        entry = {"event": event, "request_id": request_id, "state": state}
        for key, value in {
            "decision": decision,
            "tool": tool,
            "latency_ms": latency_ms,
            "status": status,
        }.items():
            if value is not None:
                entry[key] = value
        self.events.append(entry)
        self.logger.info(json.dumps(entry, separators=(",", ":")))


def configure_logging():
    logger = logging.getLogger("minimal_agent_runtime")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
