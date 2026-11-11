# AgenticSamplesPrincipalEngineer

## Task 05 — Single-Agent vs. Multi-Agent Architecture

A minimal Python banking comparison with structured model planning, a single banking agent, supervisor/specialist delegation, measured invocation counts, and partial failure handling.

See [the project README, runnable demo and architecture trade-offs](single-vs-multi-agent/README.md).

## Small offline concept lab

task-05-single-agent-vs-multi-agent-architecture

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English explanation

### The problem I am solving

Compare a single agent with specialist delegation and distinct tool boundaries. This branch makes the idea easier to understand by putting it into a small Python example that I can run and explain step by step.

### What functionality is delivered?

The branch contains an offline concept lab: [the Python demo](concept-lab/main.py), [tests](concept-lab/test_main.py), and [expected output](concept-lab/expected_output.json). It is useful for seeing the intended behavior and the failure boundaries without depending on a live AI model or cloud services.

### Architecture and flow

[Open the architecture diagram](docs/architecture.md). Start with the sample input, follow the code through its checks, and compare the output with the expected result. The diagram is a simplified conceptual view, not a claim that each box is a deployed service.

### Run locally

```bash
git switch task-05-single-agent-vs-multi-agent-architecture
cd concept-lab
python3 main.py
python3 -m unittest -v
```

The concept lab uses Python 3.11+ and does not require model API keys. See the [technical README](concept-lab/README.md) for details.

### How I would extend it for production

Local specialists simulate separate identities; this does not measure model quality or distributed orchestration overhead. I would add real authenticated adapters, monitoring, recovery, and operational testing where the use case requires them.

**My takeaway:** single agent vs multi agent architecture is easier to evaluate when we can demonstrate the happy path and the boundary conditions in executable code.

## Interactive UI

See [concept-lab/README.md](concept-lab/README.md#streamlit-ui) for the optional Streamlit UI and launch instructions.
