# Task 18: supervisor agent architecture — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["supervisor agent architecture"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Use a capability registry to route requests through a supervisor without exposing every tool to every specialist.

## Limits

Capability selection is explicit; a real supervisor can use an evaluated classifier or model, with authenticated specialist identities.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
