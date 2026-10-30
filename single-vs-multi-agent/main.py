from metrics import configure_logging
from models import REQUEST
from single_agent import BankingAgent
from multi_agent import SupervisorAgent, CreditAgent


def show(result):
    print("\n" + result["architecture"] + " — " + result["status"], flush=True)
    print(result["response"], flush=True)
    metrics = result["metrics"]
    print(
        f"Correlation: {metrics['correlation_id']} | Duration: {metrics['duration_ms']:.3f} ms | "
        f"Model calls: {metrics['model_calls']} | Tool calls: {metrics['tool_calls']} | Agent calls: {metrics['agent_calls']}",
        flush=True,
    )
    for error in result["errors"]:
        print(
            f"Error: {error['capability']} / {error['code']} / {error['correlation_id']}",
            flush=True,
        )


def main():
    configure_logging()
    print("Synthetic banking request: " + REQUEST, flush=True)
    single = BankingAgent().run("user1", REQUEST)
    multi = SupervisorAgent().run("user1", REQUEST)
    show(single)
    show(multi)
    print(
        "\nObserved metrics for this run (sequential, in-process; not a benchmark):",
        flush=True,
    )
    print("Architecture       Duration ms  Model  Tool  Agent", flush=True)
    for label, result in [("Single", single), ("Multi", multi)]:
        m = result["metrics"]
        print(
            f"{label:18} {m['duration_ms']:11.3f} {m['model_calls']:6} {m['tool_calls']:5} {m['agent_calls']:6}",
            flush=True,
        )
    print(
        "\nFailure demonstration: CreditAgent fails before its tool is invoked.",
        flush=True,
    )
    show(SupervisorAgent(credit_agent=CreditAgent(fail=True)).run("user1", REQUEST))
    print(
        "\nBoth architectures use the same data, rules and validated planning contract. "
        "Multiple agents add explicit delegation boundaries, not automatic intelligence, reliability or scaling.",
        flush=True,
    )


if __name__ == "__main__":
    main()
