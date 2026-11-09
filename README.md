# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-31-secure-communication-between-autonomous-agents

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English explanation

**Why this matters:** Authenticate local agent envelopes with HMAC, bind audience and expiry, and reject replay or tampering. I created this example to demonstrate the engineering principle with executable code instead of just describing it.

**What the code achieves:** The [Python concept lab](concept-lab/main.py) runs with synthetic local inputs and demonstrates a normal result. Its [tests](concept-lab/test_main.py) show expected behavior and important boundaries. This is not a live LLM-powered production service.

**Architecture:** [View the Mermaid flow diagram](docs/architecture.md). It explains the logical path from input through the example's checks to the result, including a failure branch.

**Run it:**

```bash
git switch task-31-secure-communication-between-autonomous-agents
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Python 3.11+ is required; no external API keys are needed for this concept lab. See [full technical instructions](concept-lab/README.md).

**Production considerations:** HMAC provides shared-key integrity, not transport confidentiality or independent workload identity. Production needs TLS/mTLS or workload credentials, key rotation, and a durable replay store. I would introduce real integrations, identity, state management, monitoring, and recovery testing according to the deployment requirements.

**Interview takeaway:** This is how I would explain secure communication between autonomous agents: show the behavior, identify the enforced boundary, and discuss the production trade-offs.
