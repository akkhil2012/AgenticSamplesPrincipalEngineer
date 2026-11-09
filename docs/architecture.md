# Task 21: handling partial failures in multi agent workflows — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["handling partial failures in multi agent workflows"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Collect independent successes and failures, then retry only failed idempotent work.

## Limits

Retries assume idempotent tasks. Distributed recovery needs durable results, retry limits, and compensation for irreversible actions.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
