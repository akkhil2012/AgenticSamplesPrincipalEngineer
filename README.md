# AgenticSamplesPrincipalEngineer
AgenticSamplesPrincipalEngineer

## Small offline concept lab

task-09-least-privilege-and-least-agency

See [concept-lab/README.md](concept-lab/README.md) for the runnable demo, failure cases, tests, and production limitations.

```bash
cd concept-lab
python3 main.py
python3 -m unittest -v
```

Requires Python 3.11+. No packages or API keys required.

## Plain-English explanation

Intersect workload permissions with a request-specific capability and consume its action budget. I use this branch to demonstrate how an AI agent should have only the capabilities it needs, and how the implementation should enforce those limits instead of trusting model instructions alone.

**What is implemented:** A local [Python concept lab](concept-lab/main.py) with [tests](concept-lab/test_main.py) and synthetic inputs. It is not a deployed identity platform.

**Architecture:** [View the Mermaid diagram](docs/architecture.md).

**Run:**

```bash
git switch task-09-least-privilege-and-least-agency
cd concept-lab
python3 main.py
python3 -m unittest -v
```

**Production considerations:** A local capability object, not a signed bearer credential; counters need atomic storage across workers. I would integrate a trusted identity provider, centralized authorization policies, audited tool execution, and adversarial testing before production use.

## Interactive UI

See [concept-lab/README.md](concept-lab/README.md#streamlit-ui) for the optional Streamlit UI and launch instructions.
