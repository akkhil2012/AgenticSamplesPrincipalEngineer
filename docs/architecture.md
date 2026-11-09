# Task 39: durableagent database backed workflow state and recovery — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["durableagent database backed workflow state and recovery"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Use durable SQLite step records to resume a workflow and skip already committed local steps.

## Limits

Checkpoints follow function completion. External side effects can repeat after a crash before checkpoint; use idempotency/outbox and worker leases.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
