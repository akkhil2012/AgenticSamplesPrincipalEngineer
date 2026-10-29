"""Model reasoning suggests an action; the runtime validates and authorizes it."""

import json
import os
import re
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    action: str
    account_id: str | None = None
    response: str | None = None


def validate_decision(raw):
    if not isinstance(raw, dict):
        raise ValueError("Model decision must be an object")
    if raw.get("action") == "get_balance" and set(raw) == {"action", "account_id"}:
        account = raw["account_id"]
        if isinstance(account, str) and re.fullmatch(r"ACC[0-9]{3}", account):
            return Decision("get_balance", account_id=account)
    if raw.get("action") == "respond" and set(raw) == {"action", "response"}:
        response = raw["response"]
        if isinstance(response, str) and 0 < len(response.strip()) <= 4000:
            return Decision("respond", response=response)
    raise ValueError("Unsupported model action or invalid arguments")


class Model:
    def __init__(self, mode=None):
        self.mode = mode or os.getenv("LLM_MODE", "mock")
        if self.mode not in {"mock", "openai"}:
            raise ValueError("LLM_MODE must be mock or openai")

    def decide(self, message, history):
        if self.mode == "mock":
            if "previous question" in message.lower():
                response = (
                    "Your previous question was: " + history[-1]["user"]
                    if history
                    else "There is no previous question in this session."
                )
                return {"action": "respond", "response": response}
            accounts = set(re.findall(r"\bACC[0-9]{3}\b", message.upper()))
            if len(accounts) == 1:
                return {"action": "get_balance", "account_id": accounts.pop()}
            return {
                "action": "respond",
                "response": "Ask for the balance of one account, such as ACC123.",
            }
        return self._openai(message, history)

    def _openai(self, message, history):
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is required for openai mode")
        messages = [
            {
                "role": "system",
                "content": "You are a read-only banking assistant. Return exactly one JSON object: "
                '{"action":"get_balance","account_id":"ACC123"} for an account balance request, '
                'or {"action":"respond","response":"text"} for conversation and memory questions. '
                "Do not invent balances, claim completed actions, or request other tools. "
                "Account access is decided independently by the runtime.",
            }
        ]
        for turn in history:
            messages.extend(
                [
                    {"role": "user", "content": turn["user"]},
                    {"role": "assistant", "content": turn["assistant"]},
                ]
            )
        messages.append({"role": "user", "content": message})
        body = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": messages,
            "temperature": 0,
            "max_tokens": 300,
            "response_format": {"type": "json_object"},
        }
        url = (
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            + "/chat/completions"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + key,
            },
            method="POST",
        )
        # One bounded provider attempt. No silent fallback that could mask an operational failure.
        timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "10"))
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise ValueError("Model response too large")
        content = json.loads(raw)["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("Invalid model response content")
        return json.loads(content)
