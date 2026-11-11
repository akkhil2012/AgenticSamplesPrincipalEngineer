"""Bounded, real Chat Completions tool loop shared by two independent agents."""

import json
import os
import time

from jsonschema import ValidationError, validate
from openai import AsyncOpenAI


class AgentFailure(RuntimeError):
    """A safe public failure; provider exception bodies never leave this module."""


def make_client():
    if not os.getenv("OPENAI_API_KEY"):
        raise AgentFailure(
            "Set OPENAI_API_KEY in the local .env file before running agents."
        )
    return AsyncOpenAI(timeout=40, max_retries=0)


def event(trace, protocol, operation, **details):
    trace.append({"protocol": protocol, "operation": operation, **details})


async def reason(role, system, question, tools, dispatch, trace, client=None):
    """Tool selection and answers come from the LLM, not keyword routing."""
    owned = client is None
    client = client or make_client()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    schemas = {t["function"]["name"]: t["function"]["parameters"] for t in tools}
    tool_calls = 0
    try:
        for step in range(8):
            start = time.perf_counter()
            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                messages=messages,
                tools=tools,
                tool_choice="auto",
                parallel_tool_calls=False,
                max_completion_tokens=2200,
            )
            message = response.choices[0].message
            event(
                trace,
                "LLM",
                "completion",
                agent=role,
                step=step + 1,
                elapsed_ms=round((time.perf_counter() - start) * 1000),
                model=response.model,
            )
            if not message.tool_calls:
                if not message.content or not message.content.strip():
                    raise AgentFailure("The model returned no usable answer.")
                return message.content
            messages.append(message.model_dump(exclude_none=True))
            for call in message.tool_calls:
                tool_calls += 1
                if tool_calls > 12:
                    raise AgentFailure("Agent reached its twelve-tool-call limit.")
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments)
                    if name not in schemas:
                        raise AgentFailure("The model selected an unavailable tool.")
                    validate(args, schemas[name])
                except (ValueError, ValidationError):
                    raise AgentFailure(
                        "The model returned invalid tool arguments."
                    ) from None
                result = await dispatch(name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result),
                    }
                )
        raise AgentFailure(
            "Agent reached its eight-step reasoning limit. Narrow the request."
        )
    except AgentFailure:
        raise
    except Exception:  # noqa: BLE001 - redact external failures at the public boundary
        raise AgentFailure(
            "Agent execution failed. Check provider configuration and local services."
        ) from None
    finally:
        if owned:
            await client.close()
