# AgenticSamplesPrincipalEngineer

## Task 03 — Control Plane vs. Execution Plane

A minimal runnable Python loan recommendation demo with FastAPI, versioned agent configuration, deterministic governance, SQLite execution evidence and tests.

See [setup, architecture and all four demonstration scenarios](agent-control-execution-demo/README.md).

## Small offline concept lab

task-03-control-plane-vs-execution-plane

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## What this branch achieves — explained simply

Publish immutable configuration versions while checking live revocation at execution time. I use a compact Python example so we can see the engineering behavior instead of relying on an abstract description.

The implementation runs locally, returns an example result, and provides tests for its behavior. The interesting part is the **decision boundary**: what is allowed to continue, and what must be rejected or handled safely.

### Architecture

[View the Mermaid architecture diagram](docs/architecture.md).

### Run it

```bash
git switch task-03-control-plane-vs-execution-plane
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. For the concept lab, no model API key is needed. Read [the technical lab README](concept-lab/README.md) for full details.

### Where I would take this next

In-memory configuration distribution; production requires authenticated publication, durable versions, and revocation availability handling. Before calling this production-ready, I would evaluate authentication, persistence, operational monitoring, failure recovery, and performance requirements.

**Interview takeaway:** This branch makes **control plane vs execution plane** tangible through executable Python and testable boundaries.

## Interactive UI

See [concept-lab/README.md](concept-lab/README.md#streamlit-ui) for the optional Streamlit UI and launch instructions.
