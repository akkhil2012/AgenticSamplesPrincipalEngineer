# Task 33: two level authorization in agentic platforms — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["two level authorization in agentic platforms"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Authorize both delegation to an agent and the later resource-level tool action.

## Limits

Local policy illustration; a production PDP must receive verified identities and fresh resource attributes at both boundaries.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
