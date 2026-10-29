from copy import deepcopy
from uuid import uuid4

TRANSITIONS = {
    "CREATED": {"RUNNING"},
    "RUNNING": {"TOOL_EXECUTING", "COMPLETED", "FAILED", "DENIED"},
    "TOOL_EXECUTING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
    "DENIED": set(),
}


class StateManager:
    def __init__(self):
        self.requests = {}

    def create(self, session_id):
        request_id = str(uuid4())
        self.requests[request_id] = {
            "request_id": request_id,
            "session_id": session_id,
            "state": "CREATED",
            "selected_tool": None,
            "tool_result": None,
            "error": None,
            "history": ["CREATED"],
            "latency_ms": None,
        }
        return request_id

    def transition(self, request_id, target):
        record = self.requests[request_id]
        if target not in TRANSITIONS[record["state"]]:
            raise ValueError("Invalid execution state transition")
        record["state"] = target
        record["history"].append(target)

    def get(self, request_id):
        return deepcopy(self.requests[request_id])
