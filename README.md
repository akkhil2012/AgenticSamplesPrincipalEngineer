# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-01-enterprise-agentic-ai-platform-vs-chatbot

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## What this branch achieves — explained simply

Compare a text-only reply with a governed tool action and a recorded result. I use a compact Python example so we can see the engineering behavior instead of relying on an abstract description.

The implementation runs locally, returns an example result, and provides tests for its behavior. The interesting part is the **decision boundary**: what is allowed to continue, and what must be rejected or handled safely.

### Architecture

[View the Mermaid architecture diagram](docs/architecture.md).

### Run it

```bash
git switch task-01-enterprise-agentic-ai-platform-vs-chatbot
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. For the concept lab, no model API key is needed. Read [the technical lab README](concept-lab/README.md) for full details.

### Where I would take this next

The chatbot and intent are scripted. A production platform needs authenticated callers, durable state, and real tool adapters. Before calling this production-ready, I would evaluate authentication, persistence, operational monitoring, failure recovery, and performance requirements.

**Interview takeaway:** This branch makes **enterprise agentic ai platform vs chatbot** tangible through executable Python and testable boundaries.
