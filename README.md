# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-18-supervisor-agent-architecture

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English explanation

**Why this matters:** Use a capability registry to route requests through a supervisor without exposing every tool to every specialist. I created this example to demonstrate the engineering principle with executable code instead of just describing it.

**What the code achieves:** The [Python concept lab](concept-lab/main.py) runs with synthetic local inputs and demonstrates a normal result. Its [tests](concept-lab/test_main.py) show expected behavior and important boundaries. This is not a live LLM-powered production service.

**Architecture:** [View the Mermaid flow diagram](docs/architecture.md). It explains the logical path from input through the example's checks to the result, including a failure branch.

**Run it:**

```bash
git switch task-18-supervisor-agent-architecture
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Python 3.11+ is required; no external API keys are needed for this concept lab. See [full technical instructions](concept-lab/README.md).

**Production considerations:** Capability selection is explicit; a real supervisor can use an evaluated classifier or model, with authenticated specialist identities. I would introduce real integrations, identity, state management, monitoring, and recovery testing according to the deployment requirements.

**Interview takeaway:** This is how I would explain supervisor agent architecture: show the behavior, identify the enforced boundary, and discuss the production trade-offs.

## Interactive UI

See [concept-lab/README.md](concept-lab/README.md#streamlit-ui) for the optional Streamlit UI and launch instructions.
