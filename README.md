# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-40-memoryagent-short-term-vs-long-term-agent-memory

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English explanation

**Why this matters:** Separate expiring session context from explicit, consented long-term preferences. I created this example to demonstrate the engineering principle with executable code instead of just describing it.

**What the code achieves:** The [Python concept lab](concept-lab/main.py) runs with synthetic local inputs and demonstrates a normal result. Its [tests](concept-lab/test_main.py) show expected behavior and important boundaries. This is not a live LLM-powered production service.

**Architecture:** [View the Mermaid flow diagram](docs/architecture.md). It explains the logical path from input through the example's checks to the result, including a failure branch.

**Run it:**

```bash
git switch task-40-memoryagent-short-term-vs-long-term-agent-memory
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Python 3.11+ is required; no external API keys are needed for this concept lab. See [full technical instructions](concept-lab/README.md).

**Production considerations:** Local memory dictionaries; a production memory service needs deletion, provenance, field validation, access controls, and retention enforcement. I would introduce real integrations, identity, state management, monitoring, and recovery testing according to the deployment requirements.

**Interview takeaway:** This is how I would explain memoryagent short term vs long term agent memory: show the behavior, identify the enforced boundary, and discuss the production trade-offs.
