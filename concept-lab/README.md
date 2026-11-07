# Task 53: Promptshield prompt injection defense for autonomous agents

Keep retrieved instructions as untrusted data and require an independent execution allowlist for proposed actions.

## Run locally

Requires Python 3.11 or newer. No third-party packages, API keys, network calls, or paid model services.

```bash
git clone https://github.com/akkhil2012/AgenticSamplesPrincipalEngineer.git
cd AgenticSamplesPrincipalEngineer
git switch task-53-promptshield-prompt-injection-defense-for-autonomous-agents
cd concept-lab
python3 main.py
python3 -m unittest -v
```

## Read and experiment

1. Run `main.py` and compare its JSON output with `expected_output.json`.
2. Read the functions in `main.py` in the order used by `demo()`.
3. Read the tests for the failure/boundary cases, then change an input and rerun.
4. Explain why the failure is stopped before a result or side effect is accepted.

## What this demonstrates

Keep retrieved instructions as untrusted data and require an independent execution allowlist for proposed actions.

The demo uses small synthetic fixtures and scripted/injected decisions. Any model-like decision is a deterministic stand-in. The boundary logic is executable; no model training or inference is required for this concept.

## Interview walkthrough

- State the invariant this implementation enforces.
- Walk through one successful request and the failing test cases.
- Explain which inputs must come from a trusted identity or policy service.
- Discuss state ownership, concurrency, crash recovery, latency, and cost.
- Separate the behavior demonstrated here from the production work below.

## Limits and production extension

This demonstrates containment if a model proposes a malicious action; it does not detect all injection or prove model resistance. Add egress controls and adversarial evaluation.

This is an educational implementation, not a production security product. Extend the relevant boundary with real authenticated adapters and evaluate failure behavior before deployment.

## Verification

The demo and the tests in this folder passed with Python 3.12.14. UUID values in audit traces can differ between runs.
