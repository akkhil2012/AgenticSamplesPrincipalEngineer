# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-36-protecting-agents-from-malicious-tool-responses

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English explanation

**Why this matters:** Accept only structured tool data and prevent returned text from becoming executable instructions. I created this example to demonstrate the engineering principle with executable code instead of just describing it.

**What the code achieves:** The [Python concept lab](concept-lab/main.py) runs with synthetic local inputs and demonstrates a normal result. Its [tests](concept-lab/test_main.py) show expected behavior and important boundaries. This is not a live LLM-powered production service.

**Architecture:** [View the Mermaid flow diagram](docs/architecture.md). It explains the logical path from input through the example's checks to the result, including a failure branch.

**Run it:**

```bash
git switch task-36-protecting-agents-from-malicious-tool-responses
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Python 3.11+ is required; no external API keys are needed for this concept lab. See [full technical instructions](concept-lab/README.md).

**Production considerations:** Strict structured outputs reduce this attack surface; this does not detect all prompt injection in free text or validate the truth of returned data. I would introduce real integrations, identity, state management, monitoring, and recovery testing according to the deployment requirements.

**Interview takeaway:** This is how I would explain protecting agents from malicious tool responses: show the behavior, identify the enforced boundary, and discuss the production trade-offs.
