# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-14-reproducible-evaluation-before-promotion

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English walkthrough

### What problem am I solving?

Run a fixed golden dataset and block promotion on a safety regression even when aggregate accuracy is high. My intention here is to make the engineering idea easy to demonstrate and test, rather than explain it only through slides.

### What functionality does the code provide?

This branch contains a small offline Python concept lab with a runnable example, automated tests, and an expected JSON result. The example helps show the normal path and how boundary conditions are handled. It uses synthetic inputs, not a live production AI platform.

### Architecture diagram

[View the Mermaid architecture and flow](docs/architecture.md).

### Run the example

```bash
git switch task-14-reproducible-evaluation-before-promotion
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Python 3.11+ is needed. The concept lab requires no paid model or API key. See [technical documentation](concept-lab/README.md).

### What is still needed in production?

Two illustrative cases, not sufficient release coverage. Add held-out domain, adversarial, latency, cost, and subgroup evaluations. Depending on the scenario, I would add real integrations, authenticated identities, persistence, observability, and recovery tests.

**Interview takeaway:** I can explain reproducible evaluation before promotion with a concrete example and discuss the trade-offs between a teaching demo and a deployable enterprise solution.

## Interactive UI

See [concept-lab/README.md](concept-lab/README.md#streamlit-ui) for the optional Streamlit UI and launch instructions.
