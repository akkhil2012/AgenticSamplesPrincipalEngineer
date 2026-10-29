from copy import deepcopy


class ConversationMemory:
    """Short-term context, keyed by session and bound to the trusted caller identity."""

    def __init__(self):
        self.sessions = {}

    def load(self, session_id, user_id):
        existing = self.sessions.get(session_id)
        if existing and existing["owner"] != user_id:
            raise PermissionError("Session belongs to another user")
        if existing is None:
            self.sessions[session_id] = {"owner": user_id, "turns": []}
        return deepcopy(self.sessions[session_id]["turns"])

    def save(self, session_id, user_id, message, response):
        self.load(session_id, user_id)
        self.sessions[session_id]["turns"].append(
            {"user": message, "assistant": response}
        )
