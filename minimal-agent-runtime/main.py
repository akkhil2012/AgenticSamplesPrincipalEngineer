"""Run all three requested scenarios. Business responses are separate from safe JSON logs."""

from agent import AgentRuntime
from observability import configure_logging


def show(label, result):
    print("\n" + label, flush=True)
    print("Lifecycle:", " → ".join(result["history"]), flush=True)
    print(
        "Request:", result["request_id"], "Session:", result["session_id"], flush=True
    )
    print(
        "Selected tool:",
        result["selected_tool"],
        "Latency:",
        result["latency_ms"],
        "ms",
        flush=True,
    )
    print("Response:", result["response"], flush=True)


def main():
    configure_logging()
    runtime = AgentRuntime()
    print(
        "Synthetic banking demo. JSON events go to stderr; user-facing responses go to stdout.",
        flush=True,
    )
    success = runtime.run("user1", "Check the balance of account ACC123.", "scenario-a")
    show("A — Authorized balance lookup", success)
    denied = runtime.run("user1", "Check the balance of account ACC456.", "scenario-b")
    show("B — Unauthorized account lookup", denied)
    first = runtime.run("user1", "Check ACC123 balance.", "scenario-c")
    show("C — Conversation, first turn", first)
    second = runtime.run("user1", "What was my previous question?", "scenario-c")
    show("C — Conversation, memory follow-up", second)
    print(
        "\nSession C memory contains",
        len(runtime.memory.load("scenario-c", "user1")),
        "interactions.",
        flush=True,
    )


if __name__ == "__main__":
    main()
