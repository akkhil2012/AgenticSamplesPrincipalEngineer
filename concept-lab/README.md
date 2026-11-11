# Task 35: Dynamic tool discovery and governance

Discover only approved tool versions, then recheck revocation at invocation time.

## Run locally

Requires Python 3.11 or newer. The command-line lab needs no third-party packages, API keys, network calls, or paid model services.

```bash
git clone https://github.com/akkhil2012/AgenticSamplesPrincipalEngineer.git
cd AgenticSamplesPrincipalEngineer
git switch task-35-dynamic-tool-discovery-and-governance
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

Discover only approved tool versions, then recheck revocation at invocation time.

The demo uses small synthetic fixtures and scripted/injected decisions. Any model-like decision is a deterministic stand-in. The boundary logic is executable; no model training or inference is required for this concept.

## Interview walkthrough

- State the invariant this implementation enforces.
- Walk through one successful request and the failing test cases.
- Explain which inputs must come from a trusted identity or policy service.
- Discuss state ownership, concurrency, crash recovery, latency, and cost.
- Separate the behavior demonstrated here from the production work below.

## Limits and production extension

In-memory tool metadata. Production needs signed manifests, schema review, tenant allowlists, provenance, and catalog refresh rules.

This is an educational implementation, not a production security product. Extend the relevant boundary with real authenticated adapters and evaluate failure behavior before deployment.

## Verification

The demo and the tests in this folder passed with Python 3.12.14. UUID values in audit traces can differ between runs.

## Streamlit UI

From `concept-lab`, install the optional UI dependency and launch:

```bash
python3 -m pip install -r requirements-ui.txt
python3 -m streamlit run streamlit_app.py
```

The UI runs this branch's demo, displays its JSON result and expected example,
and lets you select an individual boundary test or run the whole suite. The guide
and implementation are available alongside the results. Demo and test runs use
fresh Python processes with a 30-second limit, so state does not persist across
runs. The UI uses the same offline synthetic fixtures as the command-line lab.
